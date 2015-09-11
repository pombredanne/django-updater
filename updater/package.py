# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import pip
import logging

from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

from .conf import settings
from .models import Notification
from .util import send_notification
import requests

logger = logging.getLogger(__name__)


def run_check(token=None):
    """
    Main entrypoint for all update checks. Fetches issues and updates and decides if a notification is sent.
    :param site: (Optional) site token
    :return: True, if a notifaction has been sent. False otherwise
    """
    result = get_updates(token=token)
    notify = False
    if not result["notified"]:
        if result["security"]:
            # if we have a security issue we'll notify no matter what
            notify = True
        elif result["updates"] and settings.UPDATER_NOTIFY_ON_UPDATES:
            # only notify if we a) have updates b) NOTIFY_ON_UPDATES is set c) the last notification is old enough
            delta = timezone.timedelta(days=settings.UPDATER_DAYS_BETWEEN_NOTIFICATION, hours=1)
            if not Notification.objects.filter(created__gte=timezone.now() - delta).exists():
                notify = True

        if notify:
            result["site"] = get_current_site(None)
            send_notification(result)
            Notification.objects.create(security_issue=result["security"] != [])

    return result["notified"] or notify


def get_updates(token=None):
    """
    :return: Dictionary containing all information about all installed packages
    """
    headers = {}
    if settings.UPDATER_TOKEN:
        headers["Authorization"] = "Token " + settings.UPDATER_TOKEN

    data = {"packages": get_packages(), "token": token}
    r = requests.post(settings.UPDATER_BASE_URL + "/api/v1/packages/", json=data, headers=headers)
    return r.json()


def get_packages():
    """
    :return: A dictionary containing installed packages
    """
    return dict((i.key, i.version) for i in pip.get_installed_distributions())