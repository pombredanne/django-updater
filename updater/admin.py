# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.contrib import admin
from django.template.response import TemplateResponse
from .models import Status
from updater.conf import settings
from django.conf.urls import url
from django.contrib.admin.templatetags.admin_static import static
from django.conf import settings as django_settings


class StatusAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        return [
            url(r'^$', self.admin_site.admin_view(self.view), name="updater_status_changelist"),
        ]

    def view(self, request):
        request.current_app = self.admin_site.name
        status = Status.objects.get()
        # this won't work on django 1.9 since jquery is bundled in /vendor/
        # see: https://github.com/django/django/blob/stable/1.9.x/django/contrib/admin/options.py
        jquery = static("admin/js/jquery.min.js") if django_settings.DEBUG else static("admin/js/jquery.js")
        context = dict(
            self.admin_site.each_context(request),
            opts=self.opts,
            status=status,
            token=settings.UPDATER_TOKEN,
            service_url="/".join([settings.UPDATER_BASE_URL, "api/v1/sites", status.site_token, ""]),
            js=[
                jquery,
                static("admin/js/jquery.init.js"),
            ]
        )

        return TemplateResponse(request, "admin/status.html", context)

admin.site.register(Status, StatusAdmin)