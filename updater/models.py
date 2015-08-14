# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from uuid import uuid4
from django.utils import timezone


class Token(models.Model):

    token = models.CharField(max_length=36, default=uuid4)


class Notification(models.Model):

    created = models.DateTimeField(default=timezone.now)
    security_issue = models.BooleanField(default=False)