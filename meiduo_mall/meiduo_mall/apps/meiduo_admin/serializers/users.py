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
        fields = ('id', 'username', 'mobile', 'email', 'password')
        # 为字段添加额外验证内容,
        # 主键id默认有read_only: True选项，不参与反序列化
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8
            },
            'username': {
                'max_length': 20,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        """
            重写保存create方法，加密password
            !!!IMPORTANT: DRF 增、改都在serializer中完成
        """

        # user = super().create(validated_data=validated_data)
        # # Django框架自带用户模型类方法set_password对密码进行加密
        # user.set_password(validated_data['password'])
        # user.save()

        # Method 2:
        user = User.objects.create_user(**validated_data)

        return user
