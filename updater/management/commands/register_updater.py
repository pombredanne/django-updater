# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from ...models import Token
from updater.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import requests
from requests.exceptions import RequestException
import sys


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--token", default=False, type=str)

    def handle(self, *args, **options):

        if not settings.UPDATER_TOKEN and not options["token"]:
            self.stdout.write("whoop, need token")
            return

        # create the view token
        if not Token.objects.all().exists():
            Token.object.create()

        token = Token.objects.all().first().token

        updater_token = options["token"] or settings.UPDATER_TOKEN

        # building urls
        domain = get_current_site(None)

        url = hit_updater_view(domain, token=token)

        if not url:
            self.stdout.write("Unable to find the correct domain name for this installation, tried {0}".format(domain))
            self.stdout.write("Please note: The Django Updater service won't work on a dev environment.")

        while not url:
            try:
                domain = get_input("Domain: ")
            except KeyboardInterrupt:
                return
            url = hit_updater_view(domain=domain, token=token)

        base_url = url.split("/updater/")[0]
        self.stdout.write("This site is reachable at {base}".format(base=base_url))

        self.stdout.write("Contacting online service to register this site.")

        data = {"name": domain, "url": url}
        headers = {"Authorization": "Token " + updater_token}
        r = requests.post("https://djangoupdater.com/api/v1/sites/", data=data, headers=headers)
        if r.status_code != 201:
            self.stdout.write("There was an error adding this site")
            self.stdout.write(r.text)
            return

        self.stdout.write("This site is now registered at djangoupdater.com")
        self.stdout.write("All went well!")


def hit_updater_view(domain, token):
    base_url = "{site}{url}".format(site=domain, url=reverse("updater_run", kwargs={"token": token}))
    http_url, https_url = "://".join(["http", base_url]), "://".join(["https", base_url])
    if is_reachable_url(http_url + "?health=1"):
        return http_url
    elif is_reachable_url(https_url + "?health=1"):
        return https_url
    return False


def is_reachable_url(url):
    try:
        r = requests.get(url=url)
        if r.status_code == 200:
            return True
    except RequestException as e:
        pass
    return False

def get_input(prompt):
    # py2 and py3 compatible input prompt
    if sys.version_info[0] >= 3:
        return input(prompt)
    return raw_input(prompt)
