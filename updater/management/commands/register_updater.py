# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import sys

from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.conf import settings as django_settings
from django.contrib.sites.shortcuts import get_current_site

from updater.models import Status
from updater.register import check_host, register_site


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--host", default=False, type=str)
        parser.add_argument('--noinput', default=False, dest="noinput", action='store_true',
                            help="Do NOT prompt the user for input of any kind.")

    def handle(self, *args, **options):

        host = options["host"] or get_current_site(None)

        if "django.contrib.admin" in django_settings.INSTALLED_APPS:
            self.stdout.write("It looks like you have Django's admin installed. This management command is intended to "
                              "be used as a fallback if the admin is not used. You can use Django "
                              "Updaters admin page at: {host}{admin_url}".format(
                host=host, admin_url=reverse("admin:updater_status_changelist")))

            if not options["noinput"]:
                if get_input("Abort: (y/n) ") in ["y" or "yes"]:
                    sys.exit(1)

        self.stdout.write("\nPlease note: The Django Updater service won't work on a dev environment.\n\n")
        status = Status.objects.get()

        url = check_host(host, token=status.site_token)

        if not url:
            self.stdout.write("\nUnable to find the host for this installation, tried {0}".format(host))
            self.stdout.write("This happens when you don't use Django's site framework, or you haven't set up "
                              "any sites yet. The host is usually your domain name, e.g 'example.com' or "
                              "'www.example.com'.")
            if options["noinput"]:
                # return early if noinput is set
                sys.exit(1)

        while not url:
            try:
                host = get_input("Host: ")
            except KeyboardInterrupt:
                sys.exit(1)
            url = check_host(host=host, token=status.site_token)

        self.stdout.write("Contacting online service to register this site.")
        base_url = url.replace(status.site_token + "/", "")
        success, data = register_site(host, base_url)
        if not success:
            self.stderr.write(str(data))
            sys.exit(1)
        self.stdout.write(str(data))
        sys.exit(0)


def get_input(prompt):
    # py2 and py3 compatible input prompt
    if sys.version_info[0] >= 3:
        return input(prompt)
    return raw_input(prompt)
