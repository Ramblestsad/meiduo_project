#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-01-04 17:25:29
LastEditTime: 2021-01-04 17:25:30
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
"""


# Celery 配置文件

# 指定中间人、消息队列、任务队列、容器，使用redis
broker_url = "redis://127.0.0.1/10"
