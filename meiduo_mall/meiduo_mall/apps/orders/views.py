from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
from django import http
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
import json

from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJsonMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """展示订单商品评价页面"""

        # 接收、校验参数
        order_id = request.GET.get('order_id')
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')

        # 查询订单中未被评价的商品信息
        try:
            uncomment_goods = OrderGoods.objects.filter(
                order_id=order_id, is_commented=False)
        except Exception:
            return http.HttpResponseServerError('订单商品信息出错')

        # 构造待评价商品数据
        uncomment_goods_list = []

        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id': goods.order.order_id,
                'sku_id': goods.sku.id,
                'name': goods.sku.name,
                'price': str(goods.price),
                'default_image_url': goods.sku.default_image.url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            })

        # 构造context渲染模板
        context = {
            'uncomment_goods_list': uncomment_goods_list,
        }

        return render(request, "goods_judge.html", context)

    def post(self, request):
        """评价订单商品"""

        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(
                order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')

        # 保存订单商品评价数据
        OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
            comment=comment,
            score=score,
            is_anonymous=is_anonymous,
            is_commented=True
        )

        # 累计评论数据
        sku.comments += 1
        sku.save()
        sku.spu.comments += 1
        sku.spu.save()

        # 如果所有订单商品都已评价，则修改订单状态为已完成
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            OrderInfo.objects.filter(order_id=order_id).update(
                status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request, page_num):
        """提供我的订单展示页面"""

        user = request.user

        # 校验参数: page_num
        try:
            pass
        except Exception as e:
            return http.HttpResponseForbidden('page_num参数有误')

        # 查询订单
        orders = user.orderinfo_set.all().order_by("-create_time")

        # 遍历所有订单
        for order in orders:

            # 绑定订单状态: 数字 --> name
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定订单支付方式: 数字 --> name
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]

            # 动态绑定 sku_list 至 order
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:

                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        # 分页
        page_num = int(page_num)
        try:
            paginator = Paginator(orders, 5)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')

        # 构造context渲染
        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }

        return render(request, 'user_center_order.html', context)


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
