from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
import random
import logging

from verifications.libs.captcha.captcha import captcha
from . import constants
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.yuntongxun.ccp_sms import CCP


# Create your views here.


# 创建日志输出器
logger = logging.getLogger('django')

class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """SMS code

        Args:
            request ([obj]): 请求对象
            mobile ([str]): 手机号
        Return:
            [json]: JSON

        """

        # 接收、校验参数: img_code, uuid
        image_code_client = request.GET.get('image_code')  # str
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少参数')

        # 提取image code
        redis_conn = get_redis_connection('verify_code')  # 连接redis别名为 verify_code的2号库
        image_code_server = redis_conn.get('img_%s' % uuid)  # byte

        if image_code_server is None:
            return http.JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "图形验证码已失效"})

        # 删除image code
        redis_conn.delete('img_%s' % uuid)

        # 对比image code
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({"code": RETCODE.IMAGECODEERR, "errmsg": "输入图形验证码有误"})

        # 生成SMS code: random 6 integers
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 保存SMS code
        redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 发送SMS code
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
        #                         constants.SEND_SMS_TEMPLATE_ID)
        # 容联云通讯目前有bug

        # 响应结果
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "发送短信成功"})


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """image code

        Args:
            request ([obj]): 请求对象
            uuid ([str]): 唯一识别ID

        Returns:
            [img/jgp]: image code
        """

        # 接收、校验参数
        # uuid urls路径参数校验

        # 主体业务逻辑：生成、保存、响应图形验证码
        # 生成
        text, image = captcha.generate_captcha()

        # 保存
        redis_conn = get_redis_connection('verify_code')  # 连接redis别名为 verify_code的2号库
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应
        return http.HttpResponse(image, content_type='image/jpg')
