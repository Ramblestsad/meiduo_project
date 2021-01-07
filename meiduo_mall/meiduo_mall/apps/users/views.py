from django.http.response import JsonResponse
from django.urls import reverse
from django import http
from django.shortcuts import render, redirect
from django.views import View
import re
from django.db import DatabaseError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from users.models import User


# Create your views here.


class UserInfoView(LoginRequiredMixin , View):
    """用户中心"""

    def get(self, request):
        """展示用户中心页面"""

        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))

        # login_url = '/login/' 不用传，在dev settings文件中定义了默认值
        # redirect_field_name = '' 不用传， REDIRECT_FIELD_NAME='next' 为默认值

        return render(request, 'user_center_info.html')


class LogoutView(View):
    """用户退出登录"""

    def get(self, request):
        """退出登录逻辑"""

        # 清理session
        logout(request)

        # 退出登录，重定向到登录页
        response = redirect(reverse('contents:index'))

        # 退出登录时清除cookie中的username
        response.delete_cookie('username')

        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """提供用户登录界面"""

        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录逻辑"""

        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')

        # 认证用户：使用账号查询用户是否存在，若存在，再校验密码是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {"account_errmsg": "账号或密码错误"})

        # 状态保持
        login(request, user)
        # 使用remembered确定状态保持周期（实现记住登录）
        if remembered != 'on':
            # 没有记住登录：状态保持在浏览器会话结束后销毁
            request.session.set_expiry(0)  # 单位是秒
        else:
            # 记住登录：状态保持周期为2 weeks - 默认为两周
            request.session.set_expiry(None)

        # 响应结果
        # 先取出next
        nt = request.GET.get('next')
        if nt:
            # 重定向到nt
            response = redirect(nt)
        else:
            # 重定向到首页
            response = redirect(reverse('contents:index'))

        # 首页右上角展示用户名信息：缓存用户名到cookie中
        response.set_cookie("username", user.username, max_age=3600 * 24 * 14)

        # 响应结果
        return response


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """axios

        Args:
            request ([obj]): 请求对象
            username ([str]): 用户名

        Returns:
            [type]: JSON
        """

        # 接收和校验参数, 通过urls路径参数实现

        # 查询数据 --> MySQL, filter返回 查询结果集
        count = User.objects.filter(username=username).count()

        # 响应结果
        return JsonResponse({"code": RETCODE.OK, "errmsg": 'OK', "count": count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        """axios

        Args:
            request ([obj]): 请求对象
            mobile ([str]): 手机号

        Returns:
            [json]: JSON
        """

        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({"code": RETCODE.OK, "errmsg": 'OK', "count": count})


class RegisterView(View):

    def get(self, request):
        """display register.html"""

        return render(request, 'register.html')

    def post(self, request):
        """register"""

        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        # sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 校验参数: 前后端校验分开，避免恶意用户越过前端逻辑发请求，保证服务器安全，前后端校验逻辑相同
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow,]):
            return http.HttpResponseForbidden('缺少必须参数')

        # 1. 判断用户名是否是5-20个字符
        if not re.match(r'^[0-9A-Za-z_-]{5,20}$', username):
            return http.HttpResponseForbidden('非法用户名，请输入5-20个字符a-z,A-Z,0-9,_-')

        # 2. 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('非法密码，请输入8-20个字符a-z,A-Z,0-9')

        # 3. 判断两次密码是否一致
        if password2 != password:
            return http.HttpResponseNotFound('两次输入密码不一致')

        # 4. 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('无效手机号码')

        # # 5. 判断短信验证码是否正确
        # redis_conn = get_redis_connection('verify_code')
        # sms_code_server = redis_conn.get('sms_%s' % mobile)

        # if sms_code_server is None:
        #     return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        # if sms_code_client != sms_code_server.decode():
        #     return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 6. 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')

        # 保存注册数据 --> MySQL
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        # 登入用户，实现状态保持
        login(request, user)

        # 响应结果 redirect --> index.html
        response = redirect(reverse('contents:index'))

        # 首页右上角展示用户名信息：缓存用户名到cookie中
        response.set_cookie("username", user.username, max_age=3600 * 24 * 14)

        # 响应结果
        return response
