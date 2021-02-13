from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal

from meiduo_mall.utils.views import LoginRequiredMixin
from users.models import Address
from goods.models import SKU
# Create your views here.


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
        redis_selected = redis_conn.smembers('selected_%s' %user.id)

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
