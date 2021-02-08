from django import http
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
import json, base64, pickle

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """保存商品至购物车"""

        # 接收、校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)  # 非必传参数

        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数ski_id错误')

        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 若已登录，操作redis数据库
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 保存商品数据: 以redis hash类型的HINCRBY方式：有则加count无则加key
            pl.hincrby('carts_%s'% user.id, sku_id, count)
            # 保存selected商品勾选状态
            if selected:
                pl.sadd('selected_%s'% user.id, sku_id)

            pl.execute()

            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',})
        else:
            # 若未登录，操作cookie购物车
            # 获取cookie中的购物车数据并判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 1. encode carts_str to bytes
                cart_str_bytes = cart_str.encode()
                # 2. decode with base64.b64decode
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 3. pickle loads data
                cart_dict = pickle.loads(cart_dict_bytes)
                pass
            else:
                cart_dict = {}

            # 判断当前要添加的商品sku_id在cart_dict中是否存在
            if sku_id in cart_dict:
                # sku_id已存在，增量计算
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            # carts_dict ==> carts_str
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            cart_str = cart_str_bytes.decode()

            # 将carts_dict 写入cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK',})
            response.set_cookie('carts', cart_str)

            # 响应结果
            return response

    def get(self, request):
        """查询购物车数据"""

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询redis购物车
            redis_conn = get_redis_connection('carts')

            # 查询hash数据：user_id, sku_id, count
            redis_cart = redis_conn.hgetall('carts_%s'% user.id)  # dict
            # 查询set数据: selected
            cart_selected = redis_conn.smembers('selected_%s'% user.id)  # set

            # 合并redis_cart 和 redis_selected, 与未登录用户cookie购物车一致
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected,
                }
        else:
            # 用户未登录，查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 1. encode carts_str to bytes
                cart_str_bytes = cart_str.encode()
                # 2. decode with base64.b64decode
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 3. pickle loads data
                cart_dict = pickle.loads(cart_dict_bytes)
                pass
            else:
                cart_dict = {}

        # 构造响应数据
        # 获取cart_dict中的所有key(sku_id)
        sku_ids = cart_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id':sku.id,
                'name':sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url':sku.default_image.url,
                'price':str(sku.price), # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount':str(float(sku.price) * int(cart_dict.get(sku.id).get('count'))),
            })

        context = {
            'cart_skus':cart_skus,
        }

        return render(request, 'cart.html', context)
