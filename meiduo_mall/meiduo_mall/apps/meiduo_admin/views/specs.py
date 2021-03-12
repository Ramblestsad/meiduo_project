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

from goods.models import SPUSpecification
from meiduo_admin.serializers.specs import SpecsSerializer
from meiduo_admin.utils import PageNum


class SpecsView(ModelViewSet):
    """商品规格的增删改查"""

    queryset = SPUSpecification.objects.all().order_by('id')
    serializer_class = SpecsSerializer
    pagination_class = PageNum
