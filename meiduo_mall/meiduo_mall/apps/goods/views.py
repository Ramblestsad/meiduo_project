from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import EmptyPage, Paginator
from django.utils import timezone
from datetime import datetime

from goods.models import GoodsCategory
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import SKU, GoodsVisitCount
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


class DetailVisitView(View):
    """统计分类商品的访问量"""

    def post(self, request, category_id):
        """
        如果访问记录存在，说明今天不是第一次访问，不新建记录，访问量直接累加。
        如果访问记录不存在，说明今天是第一次访问，新建记录并保存访问量。
        """

        # 接收、校验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('category_id不存在')

        # 获取当天日期
        t = timezone.localtime()
        today_str = "%d-%02d-%02d" % (t.year, t.month, t.day)
        today_date = datetime.strptime(today_str, '%Y-%m-%d')

        # 判断当天指定分类商品对应纪录是否存在
        try:
            # 若存在，则直接获取记录对应的对象
            counts_data = GoodsVisitCount.objects.get(
                date=today_date, category_id=category.id)
        except GoodsVisitCount.DoesNotExist:
            # 若不尊在，则创建记录对应的对象
            counts_data = GoodsVisitCount()

        counts_data.category = category
        counts_data.count += 1
        counts_data.date = today_date
        try:
            counts_data.save()
        except Exception as e:
            return http.HttpResponseServerError('服务器异常')

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""

        # 接收参数、校验参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            # return http.HttpResponseNotFound('sku_id不存在')
            return render(request, '404.html')

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 构造context
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        return render(request, 'detail.html', context)


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
