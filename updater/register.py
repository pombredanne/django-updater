# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import requests
from requests.exceptions import ConnectionError, RequestException
from django.core.urlresolvers import reverse

from updater.conf import settings
from updater.models import Status


def check_host(host, token, proto=None):
    base_url = "{host}{url}".format(host=host, url=reverse("updater_run", kwargs={"token": token}))
    http_url, https_url = "://".join(["http", base_url]), "://".join(["https", base_url])
    if proto is None:
        if is_reachable_url(https_url + "?health=1"):
            return https_url
        elif is_reachable_url(http_url + "?health=1"):
            return http_url
    else:
        return is_reachable_url(proto + base_url + "?health=1")
    return False


def register_site(host, base_url):
    status = Status.objects.get()

    data = {"name": host, "base_url": base_url}
    headers = {"Authorization": "Token " + settings.UPDATER_TOKEN}
    try:
        r = requests.post(settings.UPDATER_BASE_URL + "/api/v1/sites/", data=data, headers=headers)

        if r.status_code == 403:
            return False, "Invalid token."
        if r.status_code != 201:
            return False, r.content

        json = r.json()

        status.registered = True
        status.site_token = json["site_token"]
        status.save()
        return True, "This site is now registered at djangoupdater.com"
    except ConnectionError:
        return False, "Unable to connect to the online service. Please try again later."
    except (RequestException, ValueError) as e:
        return False, e


def get_site_status(updater_token, site_token):

    service_url = "/".join([settings.UPDATER_BASE_URL, "api/v1/sites", site_token, ""])
    headers = {"Authorization": "Token " + updater_token}
    try:
        r = requests.get(service_url, headers=headers)

        if r.status_code == 200:
            return True, r.json()
        elif r.status_code in [403, 404]:
            return False, r.status_code
    except ConnectionError:
        return False, "Unable to connect to the online service. Please try again later."
    except RequestException as e:
        return False, e


def is_reachable_url(url):
    try:
        r = requests.get(url=url, timeout=2.0)
        if r.status_code == 200:
            return True
    except RequestException as e:
        pass
    return False