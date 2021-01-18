from django.http.response import JsonResponse
from django.urls import reverse
from django import http
from django.shortcuts import render, redirect
from django.views import View
import re
import json
import logging
from django.db import DatabaseError
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from users.models import User, Address
from meiduo_mall.utils.views import LoginRequiredJsonMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_url, check_verify_token
from . import constants


# Create your views here.


# 创建日志输出器
logger = logging.getLogger('django')


class UpdateDestroyAddressView(LoginRequiredJsonMixin, View):
    """修改和删除地址"""

    def put(self, request, address_id):
        """更新地址"""

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        # 构造响应数据
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})

    def delete(self, request, address_id):

        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)

            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})

class AddressCreateView(LoginRequiredJsonMixin, View):
    """新增收货地址"""

    def post(self, request):

        # 判断是否超过地址上限：最多20个
        count = request.user.addresses.count()  # related_name='addresses'
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '用户地址数量超限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存传入的地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )

            # 设置默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
        }

        # 响应新增地址结果：需要将新增的地址返回给前端渲染
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):

        # 获取当前登录用户对象
        login_user = request.user

        # 使用 login_user 和 is_deleted=False 作为条件查询
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        # 将用户地址模型列表转字典：因为 Vue.js 不认识 QuerySet模型列表，Jinja2、Django 模板引擎认识
        address_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)

        # 构造 context
        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_list,
        }

        return render(request, 'user_center_site.html', context)


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):

        # 接收参数
        token = request.GET.get('token')

        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token')

        # 从token中提取用户的信息user_id ==> user
        user = check_verify_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')

        # 将 table users_user 中 email_active 设置为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        # 响应结果：重定向到用户中心
        return redirect(reverse('users:info'))


class EmailView(LoginRequiredJsonMixin, View):
    """添加邮箱"""

    def put(self, request):
        """添加邮箱后端逻辑"""

        # 接收参数
        json_str = request.body.decode()  # body 类型是 byte
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 将用户传入的email保存到用户数据库（users_user）的email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 发送邮箱验证邮件
        verify_url = generate_verify_url(request.user)
        # send_verify_email(email, verify_url)  # 错误的写法
        send_verify_email.delay(email, verify_url)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """展示用户中心页面"""

        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))

        # login_url = '/login/' 不用传，在dev settings文件中定义了默认值
        # redirect_field_name = '' 不用传， REDIRECT_FIELD_NAME='next' 为默认值

        # 若 LoginRequiredMixin 判断出用户已登录，则request.user就是登陆用户对象
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


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
        _next = request.GET.get('next')
        if _next:
            # 重定向到nt
            response = redirect(_next)
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
        if not all([username, password, password2, mobile, allow, ]):
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
            user = User.objects.create_user(
                username=username, password=password, mobile=mobile)
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
