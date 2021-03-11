#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-11 18:33:42
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers

from users.models import User


class UsersSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email')
