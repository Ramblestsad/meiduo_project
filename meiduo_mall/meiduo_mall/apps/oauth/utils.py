#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-01-12 16:41:25
LastEditTime: 2021-01-12 17:02:57
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from itsdangerous import BadData, TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from . import constants_oauth


def generate_access_token(openid):
    """签名、序列化openid

    Args:
        openid ([str]): openid
    Return:
        token ([token]): encrypted openid
    """

    # 创建序列化器对象
    # s = Serializer('秘钥：越复杂越安全', ‘过期时间’)
    s = Serializer(settings.SECRET_KEY, constants_oauth.ACCESS_TOKEN_EXPIRES)

    # 准备待序列化的字典数据
    data = {'openid': openid}

    # 调用dumps方法进行序列化: 类型是 byte
    token =s.dumps(data)

    # 返回序列化后的数据
    return token.decode()

def check_access_token(access_token_openid):
    """反序列化openid

    Args:
        access_token_openid ([str]): encryted openid
    Return:
        openid ([str]): openid
    """

    # 创建序列化对象：序列化与反序列化的对象参数必须一样
    s = Serializer(settings.SECRET_KEY, constants_oauth.ACCESS_TOKEN_EXPIRES)

    # 反序列化
    try:
        data = s.loads(access_token_openid)
    except BadData:  #openid密文过期
        return None
    else:
        # 返回openid明文
        return data.get('openid')