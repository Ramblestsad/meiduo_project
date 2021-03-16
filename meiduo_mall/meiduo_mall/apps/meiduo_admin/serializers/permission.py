#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 18:36:54
Description: None
Version: 1.0
License: None
"""

from rest_framework import serializers
from django.contrib.auth.models import Permission


class PermissionsSerializer(serializers.ModelSerializer):
    """权限管理序列化器"""

    class Meta:

        model = Permission
        fields = "__all__"
