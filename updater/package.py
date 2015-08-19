# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from pkg_resources import parse_version
from piprot import piprot
from .conf import settings
from django import conf
from .models import Notification
from django.utils import timezone
import requests
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import pip


def run_check():

    result = get_updates()
    notify = False
    if result["security_issues"]:
        # if we have a security issue we'll notify no matter what
        notify = True
    elif result["updates"] and settings.UPDATER_NOTIFY_ON_UPDATES:
        # only notify if we a) have updates b) NOTIFY_ON_UPDATES is set c) the last notification is old enough
        delta = timezone.timedelta(days=settings.UPDATER_DAYS_BETWEEN_NOTIFICATION, hours=1)
        if not Notification.objects.filter(created__gte=timezone.now() - delta).exists():
            notify = True

    if notify:
        result["site"] = get_current_site(None)
        subject = "Important: Security updates on %s" % result["site"] if result["security_issues"] \
            else "Updates available on %s" % result["site"]
        mail = EmailMultiAlternatives(
            subject, render_to_string("summary.txt", result), conf.settings.SERVER_EMAIL, settings.UPDATER_EMAILS)
        mail.attach_alternative(render_to_string("summary.html", result), 'text/html')
        mail.send(fail_silently=False)
        Notification.objects.create(security_issue=result["security_issues"] != [])
    return notify



def get_updates():

    dic = {"security_issues": [], "updates": []}

    tracked_packages = get_tracked_package_names()
    for package, version in get_requirements():
        checked_package = get_package_updates(package, version, tracked_packages, )
        if len(checked_package["security_releases"]) > 0 or checked_package["end_of_life"]:
            dic["security_issues"].append(checked_package)
        elif settings.UPDATER_USE_PIPROT and checked_package["latest_version"] is not None and \
                        parse_version(checked_package["latest_version"]) > parse_version(version):
            dic["updates"].append(checked_package)

    return dic


def _major_version(version):
    # get the major version
    try:
        return ".".join([str(int(v)) for v in parse_version(version)[0:2]])
    except ValueError:
        return ""


def _has_backported_bugs(version, tracked_version, backports):
    # if the package backports bugs, we don't need to add the bugs from the next major version.
    # That is, if e.g Django 1.4 is a LTS, we don't need to security related fixes from 1.5, 1.6 and 1.7
    # since they are all backported.
    return backports and _major_version(version) != _major_version(tracked_version)


def _is_eol(version, end_of_life):
    return _major_version(version) in end_of_life


def get_package_updates(package, version, tracked_packages):

    dic = {"used_version": version, "security_releases": [], "tracked": False, "latest_version": None,
           "latest_version_date": None, "package": package, "end_of_life": None}

    if package in tracked_packages:
        # the package is tracked with security releases. Mark it and load additional data.
        dic["tracked"] = True
        tracked_package = get_tracked_package(package)

        dic["end_of_life"] = _is_eol(version, tracked_package["end_of_life"])

        if not dic["end_of_life"]:
            # check for security releases
            for security_release in tracked_package["releases"]:
                if parse_version(version) < parse_version(security_release["version"]):

                    if _has_backported_bugs(version, security_release["version"], tracked_package["backports"]):
                        continue

                    dic["security_releases"].append({
                        "fixes": security_release["fixes"],
                        "version": security_release["version"], "url": security_release["url"]
                    })

    if settings.UPDATER_USE_PIPROT:
        try:
            # todo make this more robust, with retries etc.
            dic["latest_version"], dic["latest_version_date"] = piprot.get_version_and_release_date(package,
                                                                                                verbose=True)
        except AttributeError:
            # until https://github.com/sesh/piprot/issues/48 is resolved
            pass

    return dic


def get_tracked_package_names():
    """
    :return: A list of tracked packages.
    """
    # todo make this more robust, with retries etc.
    data = requests.get(settings.UPDATER_TRACKED_PACKAGES_URL)
    json = data.json()
    return [p["name"] for p in json]


def get_tracked_package(package):
    # todo make this more robust, with retries etc.
    data = requests.get("{base}{package}/".format(base=settings.UPDATER_TRACKED_PACKAGES_URL, package=package))
    return data.json()


def get_requirements():

    for item in pip.get_installed_distributions():
        yield item.key, item.version