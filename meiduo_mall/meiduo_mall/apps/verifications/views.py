from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from . import constants


# Create your views here.


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        description:
        param {uuid: 通用唯一标识码}
        return {image.jpg}
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
