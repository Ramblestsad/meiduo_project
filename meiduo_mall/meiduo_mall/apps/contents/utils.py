#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-05 17:58:25
LastEditTime: 2021-02-05 17:59:43
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


from collections import OrderedDict

from goods.models import GoodsChannel

def get_categories():
    """获取商品分类"""

    categories = OrderedDict()

    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历所有频道 37个一级类别
    for channel in channels:
        # 获取当前channel所在的组id
        group_id = channel.group_id
        # 构造基本数据框架: 11 groups
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 查询当前频道对应的一级类别: 频道就是一级类别，一一对应
        cat1 = channel.category

        # 将 cat1 添加至 categories
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url,
        })

        # 构建当前类别的子类别数据: sub_cats
        for cat2 in cat1.subs.all():
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    return categories
