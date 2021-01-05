#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# 自定义用户认证authenticate backend 实现多账户登录


from django.contrib.auth.backends import ModelBackend
import re

from users.models import User


def get_user_by_account(account):
    """
    通过账号获取用户
    :param account: 用户名或手机号
    :return: user
    """

    # 校验username 是 用户名还是手机号
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证厚度那"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写用户认证方法
        :param username: username or mobile
        :param password: 密码明文
        :param kwargs: 额外参数
        :return: user
        """

        user = get_user_by_account(username)

        # 若可以查询到用户，校验密码是否正确
        if user and user.check_password(password):
            return user
        else:
            return None

        # 返回user
