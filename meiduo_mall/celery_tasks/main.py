#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-01-04 17:19:58
LastEditTime: 2021-01-04 17:19:59
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
"""


# Celery 入口
from celery import Celery


# 生产者：创建Celery 实例
celery_app = Celery("meiduo")

# 加载配置
celery_app.config_from_object('celery_tasks.config')

# 注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])
