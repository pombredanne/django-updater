# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from ...models import Token
from django.contrib.sites.shortcuts import get_current_site


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not Token.objects.all().exists():
            Token.object.create()
        token = Token.objects.all().first().token
        print("Your token is {token}".format(token=token))
        print("You can use it to call the Django Updater process by visiting: {site}{url}".
              format(site=get_current_site(None), url=reverse("updater_run", kwargs={"token": token})))
