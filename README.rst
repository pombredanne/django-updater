![Logo](https://djangoupdater.com/static/images/logo.png)

![Fury](https://badge.fury.io/py/django-updater.png)
![Travis](https://travis-ci.org/jayfk/django-updater.png?branch=master)

django-updater helps you to keep your Django installation up to date. It warns you when a new security related release
comes out and when your Django version hits end of life.

Documentation
-------------

The full documentation is at https://django-updater.readthedocs.org.

Quickstart
----------

Install django-updater::

    pip install django-updater

Then, add it to your `INSTALLED_APPS`

    INSTALLED_APPS = (
        ...
        "updater",
     )

And run the migrations with

    python manage.py migrate updater


Usage
--------

In order to check for updates `django-updater` has to be called periodically. There are three ways to accomplish that:

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

If you are using `Celery` and have a celery beat daemon running (e.g you are using @periodic_tasks), enable Celery support in your settings with

     DJANGO_UPDATER_CELERY = True


And you are good to go!

Cronjob
-------

You can use a cronjob to check for updates. through a management command.

To set up a cronjob, run::

     crontab -e

And then add::

     * * * * * python /path/to/your/apps/manage.py check_updates


If you are using a virtual environment, you might need to point to the python executable your virtual environment is using::

     * * * * * /path/to/virtual/environment/bin/python /path/to/your/apps/manage.py check_updates


If all this fails, or you want to start the process from a remote host, you can call the remote url.

To do that, run::

     python manage.py updater_token

Copy the token and create a crontab like this:

      * * * * * curl https://domain.com/updater/check/<YOUR_TOKEN>/
