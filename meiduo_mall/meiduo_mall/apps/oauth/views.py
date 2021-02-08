from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.contrib.auth import login
import logging
import re
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User
from carts.utils import merge_cart_cookie_redis
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
        try:
            oauth_user = OAuthQQUser.objects.get(openid=open_id)
        except OAuthQQUser.DoesNotExist:  # openid 未绑定meiduo商城用户
            access_token_openid = generate_access_token(open_id)
            context = {'access_token_openid': access_token_openid}

            return render(request, 'oauth_callback.html', context)
        else:  # openid 已绑定meiduo商城用户
            # 实现状态保持
            # oauth_user.user 从QQ登陆登陆模型类找到对应的用户模型类对象
            login(request, oauth_user.user)

            # 重定向到state
            _next = request.GET.get('state')
            response = redirect(_next)

            # 将用户名写入cookie中
            response.set_cookie(
                'username', oauth_user.user.username, max_age=3600 * 24 * 14)

            # 用户登录成功 ==> 合并cookie购物车&redis购物车
            response = merge_cart_cookie_redis(
                request=request, user=oauth_user.user, response=response)

            # 响应QQ登陆结果
            return response

    def post(self, request):
        """绑定openid到meiduo商城用户"""

        # 接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        # sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, pwd]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', pwd):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # 判断短信验证码是否一致
        # redis_conn = get_redis_connection('verify_code')
        # sms_code_server = redis_conn.get('sms_%s' % mobile)
        # if sms_code_server is None:
        #     return render(request, 'oauth_callback.html', {'sms_code_errmsg':'无效的短信验证码'})
        # if sms_code_client != sms_code_server.decode():
        #     return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 判断openid是否有效：错误提示放在sms_code_errmsg位置
        open_id = check_access_token(access_token_openid)
        if not open_id:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})

        # 使用手机号查询对应的用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:  # 如果手机号用户不存：新建用户
            user = User.objects.create_user(
                username=mobile, password=pwd, mobile=mobile)
        else:  # 如果手机号对应用户存在：校验密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '账号或密码错误'})

        # 将新建、已存在用户绑定至openid
        # oauth_qq_user = OAuthQQUser(user=user, openid=open_id)
        # oauth_qq_user.save()
        try:
            oauth_qq_user = OAuthQQUser.objects.create(
                user=user, openid=open_id)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号或密码错误'})

        # 状态保持
        login(request, oauth_qq_user)

        # 重定向到state
        _next = request.GET.get('state')
        response = redirect(_next)

        # 用户名写入cookie中
        response.set_cookie(
            'username', oauth_qq_user.user.username, max_age=3600 * 24 * 14)

        # 用户登录成功 ==> 合并cookie购物车&redis购物车
        response = merge_cart_cookie_redis(
            request=request, user=user, response=response)

        # 响应结果
        return response
