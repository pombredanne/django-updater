# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from pkg_resources import parse_version
from piprot import piprot
import pip
import logging
from requests.exceptions import RequestException

from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site

from .conf import settings
from .models import Notification
from .util import retry_session, send_notification

logger = logging.getLogger(__name__)


def run_check(site=None):
    """
    Main entrypoint for all update checks. Fetches issues and updates and decides if a notification is sent.
    :param site: (Optional) Site ID
    :return: True, if a notifaction has been sent. False otherwise
    """
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
        send_notification(result, site)
        Notification.objects.create(security_issue=result["security_issues"] != [])
    return notify


def get_updates():
    """
    :return: Dictionary containing all information about all installed packages
    """
    dic = {"security_issues": [], "updates": []}

    tracked_packages = get_tracked_package_names()
    for package, version in get_requirements():
        checked_package = get_package_updates(package, version, tracked_packages, )
        if checked_package:
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
    """
    :param package: String package name
    :param version: String package version
    :param tracked_packages: List of tracked packages
    :return: Dictionary
    """
    dic = {"used_version": version, "security_releases": [], "tracked": False, "latest_version": None,
           "latest_version_date": None, "package": package, "end_of_life": None}

    if package in tracked_packages:
        # the package is tracked with security releases. Mark it and load additional data.
        dic["tracked"] = True
        tracked_package = get_tracked_package(package)

        if tracked_package is None:
            return False

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
    Queries the Django Updater API and returns a list of tracked packages
    :return: A list of tracked packages.
    """
    try:
        data = retry_session().get(settings.UPDATER_TRACKED_PACKAGES_URL)
        json = data.json()
        return [p["name"] for p in json]
    except (ValueError, RequestException) as e:
        # ValueError is raised if no JSON object could be decoded
        logger.error("Unable to get tracked package names", exc_info=True)
        return []


def get_tracked_package(package):
    """
    Queries the Django Updater API for a specific package
    :param package: String name of package
    :return: Dictionary containing all known security issues for the package, or None
    """
    try:
        data = retry_session().get("{base}{package}/".format(base=settings.UPDATER_TRACKED_PACKAGES_URL, package=package))
        return data.json()
    except (ValueError, RequestException) as e:
        # ValueError is raised if no JSON object could be decoded
        logger.error("Unable to get tracked package {}".format(package), exc_info=True)
        return None


def get_requirements():
    """
    :return: Iterator that return a tuple of the form (package_name, version)
    """
    for item in pip.get_installed_distributions():
        yield item.key, item.version