from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
from django import http
from django.utils import timezone
from django.db import transaction
import json

from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJsonMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功页面"""

    def get(self, request):
        """提供提交订单成功页面"""

        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }

        return render(request, 'order_success.html', context)


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

        # 显式的开启一次事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()

            # 暴力回滚
            try:

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
                    # 每个商品都有多次下单机会，直到库存不足
                    while True:

                        sku = SKU.objects.get(id=sku_id)

                        # 获取原始的库存与销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 获取需提交订单中商品的数量
                        sku_count = new_cart_dict[sku.id]
                        # 判断商品数量是否大于库存
                        if sku_count > origin_stock:
                            # 库存不足，回滚
                            transaction.savepoint_rollback(save_id)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足！'})

                        # SKU更新库存与销量: stock、sales
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(
                            stock=new_stock, sales=new_sales)
                        # 如果在跟新数据时，原始数据变化了，返回0；表示有资源抢夺
                        if result == 0:
                            continue

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

                        # 下单成功, 记得break
                        break

                # 加上运费 per one order
                order.total_amount += order.freight
                order.save()

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '订单提交失败'})

            # 显示的提交一次事务
            transaction.savepoint_commit(save_id)

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
