# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse
import requests
from requests.exceptions import RequestException
from updater.conf import settings
from updater.models import Status


def check_domain(domain, token):
    base_url = "{site}{url}".format(site=domain, url=reverse("updater_run", kwargs={"token": token}))
    http_url, https_url = "://".join(["http", base_url]), "://".join(["https", base_url])
    if is_reachable_url(https_url + "?health=1"):
        return https_url
    elif is_reachable_url(http_url + "?health=1"):
        return http_url
    return False


def register_site(domain, url, updater_token):
    status = Status.objects.get()

    data = {"name": domain, "base_url": url.replace(status.site_token + "/", "")}
    headers = {"Authorization": "Token " + updater_token}
    try:
        r = requests.post(settings.UPDATER_BASE_URL + "/api/v1/sites/", data=data, headers=headers)

        if r.status_code != 201:
            return False, r.content

        json = r.json()

        status.registered = True
        status.site_token = json["site_token"]
        status.save()
    except (RequestException, ValueError) as e:
        return False, e.msg
    return True, "This site is now registered at djangoupdater.com"


def is_reachable_url(url):
    try:
        r = requests.get(url=url, timeout=2.0)
        if r.status_code == 200:
            return True
    except RequestException as e:
        pass
    return False