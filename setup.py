#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import updater

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = updater.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-updater',
    version=version,
    description="""Helps you to keep your Django installation up to date""",
    long_description=readme + '\n\n' + history,
    author='Jannis Gebauer',
    author_email='ja.geb@me.com',
    url='https://github.com/jayfk/django-updater',
    packages=[
        'updater',
    ],
    include_package_data=True,
    install_requires=[
        "django",
        "requests",
        "pip"
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-updater',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
