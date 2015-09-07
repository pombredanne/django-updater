# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.conf import BaseSettings, settings as django_settings


class Settings(BaseSettings):

    UPDATER_USE_PIPROT = getattr(django_settings, "UPDATER_USE_PIPROT", True)
    UPDATER_ALLOWED_IPS = getattr(django_settings, "UPDATER_ALLOWED_IPS", ["*"])
    UPDATER_ALLOWED_DOMAINS = getattr(django_settings, "UPDATER_ALLOWED_DOMAINS", ["*"])
    UPDATER_TRACKED_PACKAGES_URL = getattr(django_settings, "UPDATER_TRACKED_PACKAGES_URL",
                                           "https://djangoupdater.com/api/v1/packages/")
    UPDATER_DAYS_BETWEEN_NOTIFICATION = getattr(django_settings, "UPDATER_DAYS_BETWEEN_NOTIFICATION", 7)
    UPDATER_NOTIFY_ON_UPDATES = getattr(django_settings, "UPDATER_NOTIFY_ON_UPDATES", True)
    UPDATER_EMAILS = getattr(django_settings, "UPDATER_EMAILS", [mail for name, mail in django_settings.ADMINS])
    UPDATER_TOKEN = getattr(django_settings, "UPDATER_TOKEN", False)

settings = Settings()