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

    @patch("pip.get_installed_distributions")
    def test_get_packages(self, pip):
        #patching pip
        class Package(object):
            def __init__(self, key, version):
                self.key = key
                self.version = version
        pip.return_value = ([Package("Django", "1.2"), Package("requests", "0.1")])

        from updater.package import get_packages
        requirements = get_packages()
        self.assertEqual(requirements, {"Django": "1.2", "requests": "0.1"})

    @patch("updater.package.get_updates")
    def test_run_check(self, get_updates):
        from updater.package import run_check
        from updater.models import Notification
        from django.utils import timezone

        # do nothing, all empty
        get_updates.return_value = {"security": [], "updates": [], "notified": False}
        self.assertEqual(False, run_check())

        # notify on sec issue
        Notification.objects.all().delete()
        get_updates.return_value = {"security": ["this one thing"], "updates": [], "notified": False}
        self.assertEqual(True, run_check())
        self.assertEqual(1, Notification.objects.filter(security_issue=True).count())

        #notify on updates
        Notification.objects.all().delete()
        get_updates.return_value = {"security": [], "updates": ["this one update"], "notified": False}
        self.assertEqual(True, run_check())
        self.assertEqual(1, Notification.objects.all().count())

        #don't notify on updates -> Notifcation exists
        Notification.objects.all().delete()
        Notification.objects.create()
        get_updates.return_value = {"security": [], "updates": ["this one update"], "notified": False}
        self.assertEqual(False, run_check())
        self.assertEqual(1, Notification.objects.all().count())

        #notify on updates -> Notifcation exists, but is old
        Notification.objects.all().delete()
        Notification.objects.create(created=timezone.now() - timezone.timedelta(days=8))
        get_updates.return_value = {"security": [], "updates": ["this one update"], "notified": False}
        self.assertEqual(True, run_check())
        self.assertEqual(2, Notification.objects.all().count())

        #don't notify on updates -> Notifcation exists, but is old
        Notification.objects.all().delete()
        Notification.objects.create(created=timezone.now() - timezone.timedelta(days=6))
        get_updates.return_value = {"security": [], "updates": ["this one update"], "notified": False}
        self.assertEqual(False, run_check())
        self.assertEqual(1, Notification.objects.all().count())

    def tearDown(self):
        pass
