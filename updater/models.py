# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from uuid import uuid4
from django.utils import timezone


class StatusManager(models.Manager):
    """
    Singleton Manager implementation
    """

    def get(self):
        return self.get_or_create(pk=1)[0]


class Status(models.Model):
    """
    Holds the settings/status of the current installation
    """

    registered = models.BooleanField(default=False)
    site_token = models.CharField(max_length=36, default=uuid4)
    objects = StatusManager()

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


class Notification(models.Model):

    created = models.DateTimeField(default=timezone.now)
    security_issue = models.BooleanField(default=False)