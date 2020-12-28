#!/usr/bin/env python
# -*- encoding: utf-8 -*-


from django.urls import path, re_path
from . import views

urlpatterns = [
    # index advertisement '/'
    re_path(r'^$', views.IndexView.as_view(), name='index'),
]
