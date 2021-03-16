#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-16 20:16:57
Description: None
Version: 1.0
License: None
"""

from rest_framework import serializers

from users.models import User


class AdministratorSerializer(serializers.ModelSerializer):
    """administrator管理序列化器"""

    class Meta:

        model = User
        fields = "__all__"
        extra_kwargs= {
            'password': {
                "write_only": True
            }
        }

    # 重写父类方法，增加管理员权限属性
    def create(self, validated_data):

        # 添加管理员字段
        validated_data['is_staff'] = True
        # 调用父类方法创建管理员用户
        administrator = super().create(validated_data)
        # 用户密码加密
        password = validated_data['password']
        administrator.set_password(password)
        administrator.save()

        return administrator

    # 重写父类方法，增加管理员权限属性
    def update(self, instance, validated_data):

        # 调用父类方法得到管理员用户
        administrator = super().update(instance, validated_data)
        # 用户密码加密
        password = validated_data['password']
        administrator.set_password(password)
        administrator.save()

        return administrator
