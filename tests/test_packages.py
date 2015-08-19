#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import responses
"""
test_django-updater
------------

Tests for `django-updater` models module.
"""

from django.test import TestCase
from mock import Mock, patch

class PackageTestCase(TestCase):

    def setUp(self):
        self.maxDiff = 4000
        self.requests_json = {
                "name": "requests",
                "backports": False,
                "end_of_life": [],
                "releases": [
                    {
                        "version": "1.4",
                        "fixes": [
                            "requests_security_fix"
                        ],
                        "url": "requests_url",
                        "created": "2015-03-14"
                    },
                ]
        }

        self.django_json = {
                "name": "Django",
                "backports": True,
                "end_of_life": ["1.2"],
                "releases": [
                    {
                        "version": "1.4",
                        "fixes": [
                            "django_security_fix"
                        ],
                        "url": "django_url",
                        "created": "2015-03-14"
                    },
                    {
                        "version": "1.3.2",
                        "fixes": [
                            "django_security_fix"
                        ],
                        "url": "django_url",
                        "created": "2015-03-14"
                    },
                ]
        }

    @patch("piprot.piprot.get_version_and_release_date")
    @patch("updater.package.get_tracked_package")
    @patch("updater.package.get_tracked_package_names")
    @patch("updater.package.get_requirements")
    def test_check_packages_tracked_packages(self, requirements, tracked_package_names, tracked_package, get_version_and_release_date):
        requirements.return_value = [("Django", "1.3"), ("requests", "0.1")]
        tracked_package_names.return_value = ["Django", "requests",]
        tracked_package.side_effect = iter([self.django_json, self.requests_json])
        get_version_and_release_date.return_value = (None, None)

        from updater.package import get_updates

        result = get_updates()

        self.assertEqual(len(result["security_issues"]), 2)
        self.assertEqual(len(result["updates"]), 0)
        self.assertEqual(result, {"security_issues": [
            {"package": "Django", "used_version": "1.3", "tracked": True, "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["django_security_fix",], "version": "1.3.2", "url": "django_url"}]},
            {"package": "requests", "used_version": "0.1", "tracked": True, "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["requests_security_fix",], "version": "1.4", "url": "requests_url"}]}
        ], "updates": []})

    @patch("piprot.piprot.get_version_and_release_date")
    @patch("updater.package.get_tracked_package")
    @patch("updater.package.get_tracked_package_names")
    @patch("updater.package.get_requirements")
    def test_check_packages_tracked_packages_eol(self, requirements, tracked_package_names, tracked_package,
        get_version_and_release_date):

        requirements.return_value = [("Django", "1.2.7"), ("requests", "0.1")]
        tracked_package_names.return_value = ["Django", "requests",]
        tracked_package.side_effect = iter([self.django_json, self.requests_json])
        get_version_and_release_date.return_value = (None, None)

        from updater.package import get_updates

        result = get_updates()

        self.assertEqual(len(result["security_issues"]), 2)
        self.assertEqual(len(result["updates"]), 0)
        self.assertEqual(result, {"security_issues": [
            {"package": "Django", "used_version": "1.2.7", "tracked": True, "latest_version": None,
             "latest_version_date": None, "end_of_life": True, "security_releases": [],},
            {"package": "requests", "used_version": "0.1", "tracked": True, "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["requests_security_fix",], "version": "1.4", "url": "requests_url"}]}
        ], "updates": []})

    @patch("piprot.piprot.get_version_and_release_date")
    @patch("updater.package.get_tracked_package")
    def test_check_package(self, tracked_package, get_version_and_release_date):
        tracked_package.return_value = self.django_json
        get_version_and_release_date.return_value = (None, None)

        from updater.package import get_package_updates

        tracked_packages = ["Django"]

        result = get_package_updates(package="Django", version="1.2.7", tracked_packages=tracked_packages, )

        self.assertEqual(len(result["security_releases"]), 0)
        self.assertEqual(result["end_of_life"], True)
        self.assertEqual(result["tracked"], True)
        self.assertEqual(result["used_version"], "1.2.7")
        self.assertEqual(result, {"used_version": "1.2.7", "security_releases": [], "tracked": True, "latest_version": None,
           "latest_version_date": None, "package": "Django", "end_of_life": True})


        # ##########
        # Django 1.3.2 vs tracked 1.3.2
        # #########
        tracked_packages = ["Django"]

        result = get_package_updates(package="Django", version="1.3.2", tracked_packages=tracked_packages, )

        self.assertEqual(len(result["security_releases"]), 0)
        self.assertEqual(result["end_of_life"], False)
        self.assertEqual(result["tracked"], True)
        self.assertEqual(result["used_version"], "1.3.2")

        # ##########
        # Django 1.3.3 vs tracked 1.3.2
        # #########
        tracked_packages = ["Django"]

        result = get_package_updates(package="Django", version="1.3.3", tracked_packages=tracked_packages, )

        self.assertEqual(len(result["security_releases"]), 0)
        self.assertEqual(result["end_of_life"], False)
        self.assertEqual(result["tracked"], True)
        self.assertEqual(result["used_version"], "1.3.3")

        # ##########
        # RANDOM PACKAGE
        # #########
        tracked_packages = ["Django"]

        result = get_package_updates(package="RandomPackage", version="1.2.7", tracked_packages=tracked_packages, )

        self.assertEqual(len(result["security_releases"]), 0)
        self.assertEqual(result["end_of_life"], None)
        self.assertEqual(result["tracked"], False)
        self.assertEqual(result["used_version"], "1.2.7")

    def test_has_backported_bugs(self):
        from updater.package import _has_backported_bugs

        self.assertEqual(True, _has_backported_bugs("1.4.12", "1.7.3", backports=True))
        self.assertEqual(True, _has_backported_bugs("1.4.12", "1.7", backports=True))
        self.assertEqual(False, _has_backported_bugs("1.4.12", "1.7", backports=False))

    def test_is_eol(self):
        from updater.package import _is_eol
        self.assertEqual(True, _is_eol("1.4", ["1.4", "1.5", "1.6"]))
        self.assertEqual(True, _is_eol("1.4.11", ["1.4"]))
        self.assertEqual(True, _is_eol("1.4-rc1", ["1.4"]))

    @responses.activate
    def test_get_tracked_package_names(self,):
        responses.add(responses.GET, 'https://djangoupdater.com/api/v1/packages/',
                  body='[{"name": "Django"},{"name": "requests"}]', status=200,
                  content_type='application/json')

        from updater.package import get_tracked_package_names

        self.assertEqual(get_tracked_package_names(), ["Django", "requests"])

        # todo add more tests in case of failures


    @responses.activate
    def test_get_tracked_package(self):
        responses.add(responses.GET, 'https://djangoupdater.com/api/v1/packages/Django/',
                  body='{"name":"Django","backports":true,"end_of_life":["1.6","1.5","1.3","1.2","1.1","1.0"],"releases":'
                       '[{"version":"1.7.9","fixes":["Denial-of-service possibility by filling session store","Header '
                       'injection possibility since validators accept newlines in input"],"url":'
                       '"https://docs.djangoproject.com/en/1.8/releases/1.7.9/","created":"2015-08-10"}]}', status=200,
                  content_type='application/json')

        from updater.package import get_tracked_package

        self.assertEqual(get_tracked_package("Django"), {
            "name": "Django", "backports": True, "end_of_life": ["1.6","1.5","1.3","1.2","1.1","1.0"],
            "releases": [{"version":"1.7.9","fixes":["Denial-of-service possibility by filling session store",
                                                     "Header injection possibility since validators accept newlines in input"],
                          "url":"https://docs.djangoproject.com/en/1.8/releases/1.7.9/","created":"2015-08-10"}],})

        # todo add more tests in case of failures

    @patch("pip.get_installed_distributions")
    def test_get_requirements(self, pip):
        #patching pip
        class Package(object):
            def __init__(self, key, version):
                self.key = key
                self.version = version
        pip.return_value = ([Package("Django", "1.2"), Package("requests", "0.1")])

        from updater.package import get_requirements
        requirements = list(get_requirements())
        self.assertEqual(requirements, [("Django", "1.2"), ("requests", "0.1")])

    @patch("updater.package.get_updates")
    def test_run_check(self, get_updates):
        from updater.package import run_check
        from updater.models import Notification
        from django.utils import timezone

        # do nothing, all empty
        get_updates.return_value = {"security_issues": [], "updates": []}
        self.assertEqual(False, run_check())

        # notify on sec issue
        Notification.objects.all().delete()
        get_updates.return_value = {"security_issues": ["this one thing"], "updates": []}
        self.assertEqual(True, run_check())
        self.assertEqual(1, Notification.objects.filter(security_issue=True).count())

        #notify on updates
        Notification.objects.all().delete()
        get_updates.return_value = {"security_issues": [], "updates": ["this one update"]}
        self.assertEqual(True, run_check())
        self.assertEqual(1, Notification.objects.all().count())

        #don't notify on updates -> Notifcation exists
        Notification.objects.all().delete()
        Notification.objects.create()
        get_updates.return_value = {"security_issues": [], "updates": ["this one update"]}
        self.assertEqual(False, run_check())
        self.assertEqual(1, Notification.objects.all().count())

        #notify on updates -> Notifcation exists, but is old
        Notification.objects.all().delete()
        Notification.objects.create(created=timezone.now() - timezone.timedelta(days=8))
        get_updates.return_value = {"security_issues": [], "updates": ["this one update"]}
        self.assertEqual(True, run_check())
        self.assertEqual(2, Notification.objects.all().count())

        #don't notify on updates -> Notifcation exists, but is old
        Notification.objects.all().delete()
        Notification.objects.create(created=timezone.now() - timezone.timedelta(days=6))
        get_updates.return_value = {"security_issues": [], "updates": ["this one update"]}
        self.assertEqual(False, run_check())
        self.assertEqual(1, Notification.objects.all().count())

    def tearDown(self):
        pass
