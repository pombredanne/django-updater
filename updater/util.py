# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class RequestsRetryAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super(RequestsRetryAdapter, self).__init__(*args, **kwargs)
        self.max_retries = Retry(total=self.max_retries, backoff_factor=5)


def retry_session():
    """
    requests doesn't support retries out of the box.
    :return: Request Session object
    """
    session = requests.Session()
    session.mount("https://", RequestsRetryAdapter())
    session.mount("http://", RequestsRetryAdapter())
    return session