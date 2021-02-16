from django.shortcuts import render
from django.views import View
from django import http
from django.conf import settings
import os
from alipay import AliPay

from meiduo_mall.utils.views import LoginRequiredJsonMixin, LoginRequiredMixin
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
from payment.models import Payment
# Create your views here.


class PaymentStatusView(LoginRequiredJsonMixin, View):
    """保存订单支付结果"""

    def get(self, request):

        # 获取所有查询字符串参数
        query_dict = request.GET

        # 将所有参数转为标准dict类型
        data = query_dict.dict()

        # 从参数中提取并移除（pop）sign参数
        signature = data.pop('sign')

        # 使用SDK对象调用验证接口，得到验证结果
        app_private_key_string = open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "keys/app_private_key.pem")).read()
        alipay_public_key_string = open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=app_private_key_string,
            alipay_public_key_path=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        success = alipay.verify(data, signature)

        # 如果验证通过，需要将支付宝的支付状态进行处理(修改订单状态)
        order_id = data.get('out_trade_no')
        trade_id = data.get('trade_no')
        if success:
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id,
            )

            # 修改订单状态：unpaid --> uncomment
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

            # 构造context渲染
            context = {
                'trade_id': trade_id,
            }

            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseForbidden('非法请求！')


class PaymentView(LoginRequiredJsonMixin, View):
    """订单支付功能：对接支付宝"""

    def get(self, request, order_id):

        # 校验参数
        user = request.user
        try:
            order = OrderInfo.objects.get(
                order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 创建对接支付宝的接口的SDK对象
        app_private_key_string = open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "keys/app_private_key.pem")).read()
        alipay_public_key_string = open(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "keys/alipay_public_key.pem")).read()
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # SDK对象对接支付宝支付的接口，得到登录页地址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=str(order_id),
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        # 拼接登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
