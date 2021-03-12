#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-10 15:33:39
Description: None
Version: 1.0
License: None
"""


from django.urls import re_path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import statistical, users, specs, images


urlpatterns = [
    # 登录
    re_path(r'^authorizations/$', obtain_jwt_token),
    # --------数据统计--------
    # 1.用户总量
    re_path(r'^statistical/total_count/$',
            statistical.UserCountView.as_view()),
    # 2.日新增用户
    re_path(r'^statistical/day_increment/$',
            statistical.DayIncreView.as_view()),
    # 3.日活用户
    re_path(r'^statistical/day_active/$', statistical.DayActiveView.as_view()),
    # 4.日下单用户
    re_path(r'^statistical/day_orders/$', statistical.DayOrderView.as_view()),
    # 5.月增用户
    re_path(r'^statistical/month_increment/$',
            statistical.MonthIncreUserView.as_view()),
    # 6.日分类商品访问量
    re_path(r'^statistical/goods_day_views/$',
            statistical.GoodsCategoryDailyView.as_view()),

    # --------用户管理--------
    # 1.查询用户：单一或所有
    re_path(r'^users/$', users.UsersView.as_view()),

    # --------规格路由表，SPU商品信息--------
    re_path(r'^goods/simple/$', specs.SpecsView.as_view({'get': 'simple'})),
]

# ------规格表路由------
router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, basename='specs')
# print(router.urls)
urlpatterns = urlpatterns + router.urls

# ------图片表路由------
router = DefaultRouter()
router.register('skus/images', images.ImagesView, basename='images')
# print(router.urls)
urlpatterns = urlpatterns + router.urls
