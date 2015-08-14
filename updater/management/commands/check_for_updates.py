# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from django.core.management.base import BaseCommand, CommandError
from ...package import run_check


class Command(BaseCommand):

    def handle(self, *args, **options):
        run_check()