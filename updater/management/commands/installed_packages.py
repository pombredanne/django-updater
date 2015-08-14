# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _
from ...package import get_requirements


class Command(BaseCommand):

    def handle(self, *args, **options):

        for package, version in get_requirements().iteritems():
            print(package, version)
