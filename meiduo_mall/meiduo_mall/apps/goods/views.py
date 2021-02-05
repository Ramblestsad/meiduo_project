from django.shortcuts import render
from django.views import View
from django import http

from goods.models import GoodsCategory
from contents.utils import get_categories
from goods.utils import get_breadcrumb
# Create your views here.


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""

        # 校验参数category_id的范围
        try:
            # 3级类别
            category = GoodsCategory.objects.get(id=category_id)
        except  GoodsCategory.DoesNotExist as e:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航: 一级 > 二级 > 三级(category)
        breadcrumb = get_breadcrumb(category)

        # 构造context
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }

        return render(request, 'list.html', context)
