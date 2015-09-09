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
from django.template.loader import render_to_string

class PackageTestCase(TestCase):

    def setUp(self):
        pass

    def test_get_summary_txt(self):

        # #############
        # Two security updates (none EOL)
        # #############
        result = {"security": [
            {"package": "Django", "used_version": "1.3",  "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["django_security_fix",], "version": "1.3.2", "url": "django_url"}]},
            {"package": "requests", "used_version": "0.1",  "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["requests_security_fix",], "version": "1.4", "url": "requests_url"}]}
        ], "updates": []}

        summary = render_to_string("summary.txt", result)

        self.assertEquals(True,  "Affected packages are Django and requests." in summary)
        self.assertEquals(True,  "Security Issues" in summary)
        self.assertEquals(True,  "Package: Django" in summary)
        self.assertEquals(True,  "Used Version: 1.3" in summary)
        self.assertEquals(True,  "Release: 1.3.2" in summary)
        self.assertEquals(True,  "URL: django_url" in summary)
        self.assertEquals(True,  "- django_security_fix" in summary)

        self.assertEquals(True, "Affected packages are Django and requests." in summary)
        self.assertEquals(True,  "Security Issues" in summary)
        self.assertEquals(True,  "Package: requests" in summary)
        self.assertEquals(True,  "Used Version: 0.1" in summary)
        self.assertEquals(True,  "Release: 1.3.2" in summary)
        self.assertEquals(True,  "URL: django_url" in summary)
        self.assertEquals(True,  "- requests_security_fix" in summary)

        # #############
        # Two security updates (Django EOL)
        # #############
        result = {"security": [
            {"package": "Django", "used_version": "1.2",  "latest_version": None,
             "latest_version_date": None, "end_of_life": True, "security_releases": []},
            {"package": "requests", "used_version": "0.1",  "latest_version": None,
             "latest_version_date": None, "end_of_life": False, "security_releases": [
                {"fixes": ["requests_security_fix",], "version": "1.4", "url": "requests_url"}]}
        ], "updates": []}

        summary = render_to_string("summary.txt", result)

        self.assertEquals(True,  "Affected packages are Django and requests." in summary)
        self.assertEquals(True,  "Security Issues" in summary)
        self.assertEquals(True,  "Package: Django" in summary)
        self.assertEquals(True,  "Used Version: 1.2" in summary)
        self.assertEquals(True,  "Django 1.2 is no longer supported" in summary)



    def tearDown(self):
        pass
