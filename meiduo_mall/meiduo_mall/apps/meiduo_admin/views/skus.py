#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-13 17:18:07
Description: None
Version: 1.0
License: None
"""

from os import truncate
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action

from meiduo_admin.utils import PageNum
from meiduo_admin.serializers.skus import SKUSerializer, SKUCategorySerailizer, SPUSpecsSerializer
from goods.models import SKU, GoodsCategory, SPU


class SKUView(ModelViewSet):
    """SKUS管理"""

    permission_classes = [IsAdminUser]

    # queryset = SKU.objects.all().order_by('id')
    serializer_class = SKUSerializer
    pagination_class = PageNum

    def get_queryset(self):
        """SKU获取单一信息"""

        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all().order_by('id')
        else:
            return SKU.objects.filter(name__contains=keyword).order_by('id')

    @action(methods=['get'], detail=False)
    def categories(self, request):
        """获取SKU三级分类"""

        data = GoodsCategory.objects.filter(subs__id=None)
        ser = SKUCategorySerailizer(data, many=True)

        return Response(ser.data)

    def SPUspecs(self, request, pk):
        """获取前端返回的SPU规格信息"""

        # 1.查询spu对象
        spu = SPU.objects.get(id=pk)

        # 2.关联查询所关联的规格表
        data = spu.specs.all().order_by('id')

        # 3.直接序列化返回规格表并嵌套规格选项表
        ser = SPUSpecsSerializer(data, many=True)

        return Response(ser.data)
