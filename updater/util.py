# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.exceptions import RequestException
import logging

from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django import conf

from .conf import settings

logger = logging.getLogger(__name__)


class RequestsRetryAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super(RequestsRetryAdapter, self).__init__(*args, **kwargs)
        self.max_retries = Retry(total=self.max_retries, backoff_factor=5)


def retry_session():
    """
    requests doesn't support retries out of the box.
    :return: Request Session object
    """
    session = requests.Session()
    session.mount("https://", RequestsRetryAdapter())
    session.mount("http://", RequestsRetryAdapter())
    return session


def send_notification(result):
    """
    Sends a notification.
    :param result: Dictionary containing all updates and security issues
    :return: True if all notifcations have been sent successfully
    """
    # only mails are supported right now. This might change, so we go for the more generic `send_notification`
    # as method name, but use it as a proxy to send_mail
    return send_mail(result)


def send_mail(result):
    """
    Sends a notification email.
    :param result: Dictionary containing all updates and security issues
    :return: :bool: True if mail has been send successfully
    """

    subject = "Important: Security updates on %s" % result["site"] if result["security_issues"] \
        else "Updates available on %s" % result["site"]
    txt_message = render_to_string("summary.txt", result)
    html_message = render_to_string("summary.html", result)
    if settings.UPDATER_USE_NOTIFICATION_SERVICE:
        data = {"subject": subject, "result": result, "mail_to": settings.UPDATER_EMAILS}
        headers = {"Authorization": "Token " + settings.UPDATER_TOKEN}
        session = retry_session()
        try:
            r = session.post("https://djangoupdater.com/api/v1/notification/", data=data, headers=headers)
            if r.status_code != 201:
                raise RequestException("Invalid status code %s" % r.status_code)
            return True
        except RequestException:
            logger.error("Unable to send mail through Django Updater service", exc_info=True)
            return False
    else:
        mail = EmailMultiAlternatives(
            subject, txt_message, conf.settings.SERVER_EMAIL, settings.UPDATER_EMAILS)
        mail.attach_alternative(html_message, 'text/html')
        mail.send(fail_silently=False)
        return True