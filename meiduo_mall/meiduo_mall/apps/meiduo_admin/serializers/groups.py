#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 19:45:33
Description: None
Version: 1.0
License: None
"""

from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupsSerializer(serializers.ModelSerializer):
    """分录group管理序列化器"""

    class Meta:

        model = Group
        fields = "__all__"
