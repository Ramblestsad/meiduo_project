from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from goods.models import GoodsChannelGroup, GoodsChannel, GoodsCategory
from contents.models import ContentCategory, Content
# Create your views here.


class IndexView(View):
    """index advertisements"""

    def get(self, request):
        """index.html"""

        # 查询并展示商品分类

        # 准备商品分类的对应的字典
        categories = OrderedDict()

        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        # 遍历所有频道 37个一级类别
        for channel in channels:
            # 获取当前channel所在的组id
            group_id = channel.group_id
            # 构造基本数据框架: 11 groups
            if group_id not in categories:
                categories[group_id] = {'channels': [], 'sub_cats': []}

            # 查询当前频道对应的一级类别: 频道就是一级类别，一一对应
            cat1 = channel.category

            # 将 cat1 添加至 categories
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url,
            })

            # 构建当前类别的子类别数据: sub_cats
            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append(cat3)
                categories[group_id]['sub_cats'].append(cat2)

        # 查询首页广告数据

        # 查询广告所有类别：tb_contents_category
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(
                status=True).order_by('sequence')

        # 使用广告类别查询其对应的广告内容：tb_contents

        # 构建后台渲染context
        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context)
