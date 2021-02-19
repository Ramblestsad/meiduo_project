#!/usr/bin/env python
# -*- encoding: utf-8 -*-


'''
Author: Chris W.
Date: 2021-02-19 12:27:47
LastEditTime: 2021-02-19 12:28:18
LastEditors: Chris W.
Description: databases(mysql) config
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
'''


class MasterSlaveDBRouter(object):
    """数据库读写路由"""

    def db_for_read(self, model, **hints):
        """读"""
        return "slave"

    def db_for_write(self, model, **hints):
        """写"""
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """是否运行关联操作"""
        return True
