# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import json

from django.contrib import admin
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf.urls import url
from django.contrib.admin.templatetags.admin_static import static
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.template.loader import render_to_string

from updater.models import Status
from updater.conf import settings
from updater.register import get_site_status, register_site
from updater.package import get_packages


class StatusAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        return [
            url(r'^$', self.admin_site.admin_view(self.status_view), name="updater_status_changelist"),
            url(r'^registration/$', self.admin_site.admin_view(self.registration_status_view),
                name="updater_status_registration"),
        ]

    def status_view(self, request):
        request.current_app = self.admin_site.name


        # this won't work on django 1.9 since jquery is bundled in /vendor/
        # see: https://github.com/django/django/blob/stable/1.9.x/django/contrib/admin/options.py
        jquery = static("admin/js/jquery.min.js") if django_settings.DEBUG else static("admin/js/jquery.js")
        context = dict(
            self.admin_site.each_context(request),
            opts=self.opts,
            token=settings.UPDATER_TOKEN,
            packages=json.dumps(get_packages()),
            update_url="/".join([settings.UPDATER_BASE_URL, "api/v1/packages/"]),
            registration_url=reverse("admin:updater_status_registration"),
            js=[
                jquery,
                static("admin/js/jquery.init.js"),
            ]
        )

        return TemplateResponse(request, "admin/status.html", context)

    def registration_status_view(self, request):
        request.current_app = self.admin_site.name
        status = self.get_registration_status(request)
        return JsonResponse({
            "errors": status["errors"],
            "content": render_to_string("admin/registration.html", status)
        })

    def get_registration_status(self, request, retries=0, reg_msg=None):

        if retries >= 3:
            #
            return {"errors": True, "status": reg_msg}

        try:
            # check that the view can be resolved, use a bogus uuid4
            reverse("updater_run", kwargs={"token": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"})
        except NoReverseMatch:
            # reverse_url not set
            return {"errors": True, "status": "Add <code>url(r'^updater/', include('updater.urls'))</code> to "
                                              "<code>urls.py</code> and try again."}

        if not settings.UPDATER_TOKEN:
            # UPDATER_TOKEN is not set
            return {"errors": True, "status": "Add <code>UPDATER_TOKEN</code> to your settings file "
                                              "and try again."}

        status = Status.objects.get()

        if not status.registered:
            # site is not registered, do that now
            return self.get_registration_status(request, retries=retries + 1, reg_msg=self.register(request))

        # site is registered, get the status
        success, data = get_site_status(settings.UPDATER_TOKEN, status.site_token)

        if not success and data == 404:
            # site does not exist, re-register
            return self.get_registration_status(request, retries=retries + 1, reg_msg=self.register(request))
        elif not success and data == 403:
            # UPDATER_TOKEN is not good
            return {"errors": True, "status": "Your token <code>{token}</code> is invalid.<br/>"
                                              "Please check you subscription status and make sure that the token "
                                              "matches exactly the one from your "
                                              "<a target='blank' href='https://djangoupdater.com/users/'>"
                                              "dashboard</a>.".format(token=settings.UPDATER_TOKEN)}
        elif not success:
            # totally failed, data is the request exception
            return {"errors": True, "status": data}

        # all good
        return {"errors": False, "status": data}

    def register(self, request):
        # the site is not yet registered, do that now
        proto = "http://" if request.is_secure else "https://"
        base_url = reverse("updater_run", kwargs={"token": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}).replace(
            "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/", ""
        )
        base_url = "".join([proto, request.META["HTTP_HOST"], base_url])
        return register_site(host=request.META["HTTP_HOST"], base_url=base_url)[1]


admin.site.register(Status, StatusAdmin)
