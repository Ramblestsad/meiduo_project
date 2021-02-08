#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-08 18:20:32
LastEditTime: 2021-02-08 19:38:28
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from django_redis import get_redis_connection
import pickle
import base64


def merge_cart_cookie_redis(request, user, response):
    """合并cookie&redis购物车

    Args:
        request: [description]
        user: [description]
        response: [description]
    """

    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get('carts')

    # 判断cookie中的购物车数据是否存在, 不存在，不合并
    if not cookie_cart_str:
        return response

    # 1. encode carts_str to bytes
    cookie_cart_str_bytes = cookie_cart_str.encode()
    # 2. decode with base64.b64decode
    cookie_cart_dict_bytes = base64.b64decode(cookie_cart_str_bytes)
    # 3. pickle loads data
    cookie_cart_dict = pickle.loads(cookie_cart_dict_bytes)

    # 准备新的数据容器，保存新的：sku_id, selected, unselected
    new_cart_dict = {}
    new_selected_add =[]
    new_selected_rem = []

    # 遍历出cookie中的购物车数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']

        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # 根据新的数据结构，合并到redis
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    pl.hmset('carts_%s' % user.id, new_cart_dict)
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)

    pl.execute()

    # 删除cookie
    response.delete_cookie('carts')

    return response
