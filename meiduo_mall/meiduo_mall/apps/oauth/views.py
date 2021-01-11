from typing import final
from django.conf import settings
from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django import http
import logging

from meiduo_mall.utils.response_code import RETCODE

# Create your views here.


# 创建日志输出器
logger = logging.getLogger('django')


class QQAuthURLView(View):
    """提供QQ登录扫码页面"""

    def get(self, request):

        # 接收next or /
        _next = request.GET.get('next')

        # 创建QQLoginTool对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=_next)
        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, "errmsg": 'OK', "login_url": login_url})


class QQAuthUserView(View):
    """处理QQ登录回调: oauth_callback"""

    def get(self, request):
        """QQ登录回调业务逻辑"""

        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 创建QQLoginTool对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            # 使用 code 获取 access_token
            access_token = oauth.get_access_token(code)
            # 使用 access_token 获取 openid
            open_id = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 使用openid判断该QQ用户是否绑定过美多商城的用户
        pass
