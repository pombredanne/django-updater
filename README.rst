WARNING
-------

This repo is currently a work in progress and may break with every release. Don't rely on it for now.

.. image:: https://djangoupdater.com/static/images/logo.png
    :target: https://djangoupdater.com

------

.. image:: https://badge.fury.io/py/django-updater.png
    :target: https://pypi.python.org/pypi/django-updater
.. image:: https://travis-ci.org/jayfk/django-updater.svg?branch=master
    :target: https://travis-ci.org/jayfk/django-updater

Django Updater helps you to keep your Django installation up to date. It warns you when a new security related release comes out and when your Django version hits end of life.

Documentation
-------------

The full documentation is at https://django-updater.readthedocs.org.

Quickstart
----------

Install django-updater::

    pip install django-updater

Then, add it to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        "updater",
    )

And run the migrations with::

    python manage.py migrate updater


Screenshots
-----------
.. image:: https://djangoupdater.com/static/images/security_mail.png

------

.. image:: https://djangoupdater.com/static/images/update_mail.png

Usage
--------

In order to check for updates Django Updater has to be called periodically. There are three ways to accomplish that:

- Using the service on djangoupdater.com (not yet implemented)
- Running a periodic `Celery` task
- Create a cronjob

With Djangoupdater.com
----------------------
Warning: The service is not live, yet.

Create an account on djangoupdater.com, and copy the token from your dashboard.

To register your site, run

    python manage.py register_updater --token=<YOUR_TOKEN>


The service will now try to contact your site. If all went well, the command should terminate with

    All went well!

Celery
------

If you are using `Celery` and have a celery beat daemon running, enable Celery support in your settings with::

     from datetime import timedelta

     CELERYBEAT_SCHEDULE = {
         'run-django-updater': {
             'task': 'updater.tasks.run_check',
             'schedule': timedelta(days=1),
         },
     }


And you are good to go!

Cronjob
-------

You can use a cronjob to check for updates once a day.

To set up a cronjob, run::

     crontab -e

And then add::

     30 2 * * * python /path/to/your/apps/manage.py check_for_updates


If you are using a virtual environment, you might need to point to the python executable your virtual environment is using::

     30 2 * * * /path/to/virtual/environment/bin/python /path/to/your/apps/manage.py check_for_updates


If all this fails, or you want to start the process from a remote host, you can call the remote url.

To do that, run::

     python manage.py updater_token

Copy the token and create a cronjob like this::

      30 2 * * * curl https://domain.com/updater/run/<YOUR_TOKEN>/
