from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import EmptyPage, Paginator

from goods.models import GoodsCategory
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class HotGoodsView(View):
    """热销排行"""

    def get(self, request, category_id):

        # 根据category_id，sales查询前两位sku
        skus = SKU.objects.filter(
            category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 序列化模型列表转字典，构造JSON
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            }
            hot_skus.append(sku_dict)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""

        # 校验参数category_id的范围
        try:
            # 3级类别
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist as e:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 获取sort参数
        sort = request.GET.get('sort', 'default')
        # 根据sort选择排序字段, 必须是模型类的属性
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:  # 只要不是 ?sort=price/hot，都是default
            sort = 'default'
            sort_field = 'create_time'

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航: 一级 > 二级 > 三级(category)
        breadcrumb = get_breadcrumb(category)

        # 分页和排序
        # 排序：category查询sku, 一查多
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        # skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        # 分页
        # 创建分页器: Paginator('data', 'data/page')
        paginator = Paginator(skus, 5)  # 将skus进行分页，每页5条
        # 获取用户要看的页码的数据
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseForbidden('Not Found!')
        # 获取总页数
        total_pages = paginator.num_pages

        # 构造context
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_pages': total_pages,
            'page_num': page_num,
            'sort': sort,
            'category_id': category_id,
        }

        return render(request, 'list.html', context)
