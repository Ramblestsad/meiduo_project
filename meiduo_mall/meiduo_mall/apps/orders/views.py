from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
from django import http
from django.utils import timezone
import json

from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJsonMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class OrderCommitView(LoginRequiredJsonMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单基本信息和商品信息"""

        # 接收、校验参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 获取登录用户
        user = request.user
        # 获取order_id：时间+user_id
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 保存订单基本信息（一）
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=Decimal(0.00),
            freight=Decimal(10.00),
            pay_method=pay_method,
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        )

        # 保存订单商品信息（多）
        # 查询购物车中被勾选的商品sku数据
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        # 构造购物车中被勾选的商品数据
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 获取被勾选商品的sku_ids
        sku_ids = new_cart_dict.keys()
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)

            # 获取需提交订单中商品的数量
            sku_count = new_cart_dict[sku.id]
            # 判断商品数量是否大于库存
            if sku_count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足！'})

            # SKU更新库存与销量: stock、sales
            sku.stock -= sku_count
            sku.sales += sku_count
            sku.save()
            # SPU更新销量：sales
            sku.spu.sales += sku_count
            sku.spu.save()

            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=sku_count,
                price=sku.price,
            )

            # 累加订单商品的数量和总价到OrderInfo
            order.total_count += sku_count
            order.total_amount += sku_count * sku.price
        # 加上运费 per one order
        order.total_amount += order.freight
        order.save()

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *redis_selected)
        pl.srem('selected_%s' % user.id, *redis_selected)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order.order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """查询并展示要结算的订单数据"""

        # 获取登录用户
        user = request.user

        # 查询用户收货地址
        try:
            address = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            # 若没有查询出地址，则可以去编辑收货地址
            address = None

        # 查询购物车中被勾选的商品sku数据
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        redis_selected = redis_conn.smembers('selected_%s' % user.id)

        # 构造购物车中被勾选的商品数据
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 获取被勾选商品的sku_ids
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        # 遍历skus，为每个sku补充count，amount字段
        total_count = 0
        total_amount = Decimal(0.00)

        for sku in skus:
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count  # Decimal类型

            total_count += sku.count
            total_amount += sku.amount  # 类型不同 Decimal + float 不可行

        # 指定默认邮费
        freight = Decimal(10.00)

        # 构造context
        context = {
            'addresses': address,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }

        return render(request, 'place_order.html', context)
