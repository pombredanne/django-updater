# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.contrib import admin
from django.template.response import TemplateResponse
from .models import Status
from django.conf.urls import url


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

        context = dict(
            self.admin_site.each_context(request),
            opts=self.opts,
            status=Status.objects.get()
        )
        return TemplateResponse(request, "admin/status.html", context)

admin.site.register(Status, StatusAdmin)