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
from  django.contrib.contenttypes.models import ContentType


class PermissionsSerializer(serializers.ModelSerializer):
    """权限管理序列化器"""

    class Meta:

        model = Permission
        fields = "__all__"


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型序列化器"""

    name = serializers.CharField()

    class Meta:

        model = ContentType
        fields = ('id', 'name')
