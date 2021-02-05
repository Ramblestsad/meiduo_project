#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-05 18:30:59
LastEditTime: 2021-02-05 18:40:39
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


def get_breadcrumb(category):
    """获取面包屑导航

    Args:
        category (类别对象): 一级，二级，三级
    return:
        breadcrumb:一级：返回一级，二级：返回一级 + 二级，三级：返回一，二，三级
    """

    breadcrumb = dict(
        cat1='',
        cat2='',
        cat3=''
    )

    if category.parent == None:  # category=一级
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:  # category=二级
        cat2 = category.parent
        breadcrumb['cat1'] = cat2.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = category
    else:  # category=二级
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb
