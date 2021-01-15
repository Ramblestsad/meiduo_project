#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-01-04 17:32:10
LastEditTime: 2021-01-04 17:32:10
LastEditors: Chris W.
Description: None
Version: 1.0
License: MIT License
Copyright 2021 Chris W.
"""


from celery_tasks.sms.yuntongxun.ccp_sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 定义任务
# bind: 保证task对象会作为第一个参数自动传入
# name: 异步任务别名
# retry_backoff: 异常自动重试时间间隔 第n次(retry_backoff * 2^(n-1))s
# max_retries: 异常自动重试次数上限
@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    """发送SMS code的异步任务"""

    try:
        send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                constants.SEND_SMS_TEMPLATE_ID)

        return send_ret
    except Exception as e:
        # 有异常自动重试3次
        raise self.retry(exc=e, max_retries=3)
