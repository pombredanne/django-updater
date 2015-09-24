# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand
from ...models import Status
from ...register import check_domain, register_site
from updater.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import sys


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--token", default=False, type=str)

    def handle(self, *args, **options):

        if not settings.UPDATER_TOKEN and not options["token"]:
            self.stdout.write("whoop, need token")
            return

        status = Status.objects.get()

        updater_token = options["token"] or settings.UPDATER_TOKEN

        # building urls
        domain = get_current_site(None)

        url = check_domain(domain, token=status.site_token)

        if not url:
            self.stdout.write("Unable to find the correct domain name for this installation, tried {0}".format(domain))
            self.stdout.write("Please note: The Django Updater service won't work on a dev environment.")

        while not url:
            try:
                domain = get_input("Domain: ")
            except KeyboardInterrupt:
                return
            url = check_domain(domain=domain, token=status.site_token)

        self.stdout.write("Contacting online service to register this site.")
        success, msg = register_site(domain, url, updater_token)
        self.stdout.write(msg)


def get_input(prompt):
    # py2 and py3 compatible input prompt
    if sys.version_info[0] >= 3:
        return input(prompt)
    return raw_input(prompt)
