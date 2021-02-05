from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from contents.models import ContentCategory
from contents.utils import get_categories
# Create your views here.


class IndexView(View):
    """index advertisements"""

    def get(self, request):
        """index.html"""

        # 查询并展示商品分类

        categories = get_categories()

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
