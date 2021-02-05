from django.shortcuts import render
from django.views import View
from django import http

from goods.models import GoodsCategory
from contents.utils import get_categories
# Create your views here.


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""

        # 校验参数category_id的范围
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except  GoodsCategory.DoesNotExist as e:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 查询商品分类
        categories = get_categories()

        # 构造context
        context = {
            'categories': categories
        }

        return render(request, 'list.html', context)
