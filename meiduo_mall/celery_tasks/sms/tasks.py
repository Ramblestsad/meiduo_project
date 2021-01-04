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

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """发送SMS code的异步任务"""

    send_ret = CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                            constants.SEND_SMS_TEMPLATE_ID)

    return send_ret
