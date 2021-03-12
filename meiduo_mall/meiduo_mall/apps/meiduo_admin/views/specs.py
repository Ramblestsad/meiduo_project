#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 13:32:46
Description: None
Version: 1.0
License: None
"""


from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from goods.models import SPUSpecification, SPU
from meiduo_admin.serializers.specs import SpecsSerializer, SPUSerializer
from meiduo_admin.utils import PageNum


class SpecsView(ModelViewSet):
    """商品规格的增删改查"""

    queryset = SPUSpecification.objects.all().order_by('spu_id')
    serializer_class = SpecsSerializer
    pagination_class = PageNum

    def simple(self, request):
        """
            获取SPU商品信息
        """

        spus = SPU.objects.all().order_by('id')
        ser = SPUSerializer(spus, many=True)

        return Response(ser.data)
