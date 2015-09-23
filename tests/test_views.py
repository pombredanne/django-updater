#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.urlresolvers import reverse
from mock import patch
"""
test_django-updater
------------

Tests for `django-updater` views module.
"""

from django.test import TestCase, Client

class ViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    @patch("updater.package.run_check")
    def test_run_view(self, run_check):
        from updater.models import Status
        from updater.conf import Settings
        UPDATER_ALLOWED_DOMAINS = ["*"]

        # token does not exist
        response = self.client.get(reverse("updater_run", kwargs={"token": "11111111-2222-3333-4444-555555555555"}))
        self.assertEquals(403, response.status_code)

        # token exists
        status = Status.objects.get()

        status.site_token = "11111111-2222-3333-4444-555555555555"
        status.save()

        run_check.return_value = True
        response = self.client.get(reverse("updater_run", kwargs={"token": "11111111-2222-3333-4444-555555555555"}))
        self.assertEquals(200, response.status_code)
        self.assertContains(response, "ok")

        # not yet implemented UPDATER_ALLOWED_DOMAINS
        response = self.client.get(reverse("updater_run", kwargs={"token": "11111111-2222-3333-4444-555555555555"}))

    def tearDown(self):
        pass
