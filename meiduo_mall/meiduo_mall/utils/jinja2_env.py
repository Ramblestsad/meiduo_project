#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2020-12-21 18:42:39
LastEditTime: 2020-12-21 18:59:55
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2020 Chris W.
"""


from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse


def jinja2_environment(**options):

    # create env object
    env = Environment(**options)

    # custom grammar: {{ url('') }} {{ static('') }}
    env.globals.update({
        'static':staticfiles_storage.url,
        'url':reverse,
    })

    # return env object
    return env
