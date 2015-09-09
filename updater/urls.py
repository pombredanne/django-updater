# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .views import run_view
from django.conf.urls import url

urlpatterns = [
    url(r'run/(?P<token>[0-9a-f-]{36})/$', run_view, name="updater_run"),
]