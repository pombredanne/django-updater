# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
from .models import Status
from django.core.exceptions import PermissionDenied
from .conf import settings
from django.http import HttpResponse
from .package import run_check


def run_view(request, token):

    if not is_allowed_domain(request) or not is_allowed_ip(request):
        raise PermissionDenied

    if not Status.objects.filter(site_token=token).exists():
        raise PermissionDenied

    if not request.GET.get("health", False):
        run_check(token=request.GET.get("ntoken", None))
    return HttpResponse("ok")


def is_allowed_domain(request, allowed_domains=settings.UPDATER_ALLOWED_DOMAINS):
    # todo reverse the calling ip and add it to ALLOWED_IPS
    return allowed_domains == ["*"]


def is_allowed_ip(request, allowed_ips=settings.UPDATER_ALLOWED_IPS):
    return "*" in allowed_ips or get_client_ip(request) in allowed_ips


def get_client_ip(request):
    """
    http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    :param request:
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

