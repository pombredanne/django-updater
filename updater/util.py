# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals
import logging

from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django import conf

from .conf import settings

logger = logging.getLogger(__name__)


def send_notification(result):
    """
    Sends a notification.
    :param result: Dictionary containing all updates and security issues
    :return: True if all notifcations have been sent successfully
    """
    # only mails are supported right now. This might change, so we go for the more generic `send_notification`
    # as method name, but use it as a proxy to send_mail
    return send_mail(result, mail_from=conf.settings.SERVER_EMAIL, mail_to=settings.UPDATER_EMAILS)


def send_mail(result, mail_from, mail_to, fail_sitently=False):
    """
    Sends a notification email.
    :param result: Dictionary containing all updates and security issues
    :return: :bool: True if mail has been send successfully
    """

    subject = "Important: Security updates on %s" % result["site"] if result["security"] \
        else "Updates available on %s" % result["site"]
    txt_message = render_to_string("summary.txt", result)
    html_message = render_to_string("summary.html", result)
    mail = EmailMultiAlternatives(
        subject, txt_message, mail_from, mail_to)
    mail.attach_alternative(html_message, 'text/html')
    return mail.send(fail_silently=fail_sitently)