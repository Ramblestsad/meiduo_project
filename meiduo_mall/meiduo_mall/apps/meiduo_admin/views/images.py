#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 15:12:41
Description: None
Version: 1.0
License: None
"""


from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from meiduo_admin.utils import PageNum
from goods.models import SKUImage, SKU
from meiduo_admin.serializers.images import ImagesSerializer, SKUSerializer


class ImagesView(ModelViewSet):
    """图片表管理"""

    permission_classes = [IsAdminUser]

    queryset = SKUImage.objects.all().order_by('sku_id')
    serializer_class = ImagesSerializer
    pagination_class = PageNum

    def simple(self, request):
        """获取SKU商品信息"""

        skus = SKU.objects.all().order_by()

        # 序列化返回
        ser = SKUSerializer(skus, many=True)

        return Response(ser.data)

    # 封装序列化器create方法后，ModelViewSet的父类create方法就可以完成业务逻辑
    # def create(self, request, *args, **kwargs):
    #     """重写create方法以存图片入FastDFS"""

    #     # 1.获取前端数据
    #     data = request.data

    #     # 2.验证数据
    #     ser = self.get_serializer(data=data)
    #     ser.is_valid()

    #     # # 3.简历fastdfs客户端
    #     # client = Fdfs_client(settings.FASTDFS_PATH)
    #     # file = request.FILES.get('image')

    #     # # 4.上传图片
    #     # result = client.upload_appender_by_buffer(file.read())

    #     # # 5.判断是否上传成功
    #     # if result['Status'] != 'Upload successed.':
    #     #     return Response({'error': '图片上传失败'})

    #     # # 6.保存图片表
    #     # img = SKUImage.objects.create(
    #     #     sku=ser.validated_data['sku'], image=result['Remote file_id'])

    #     ser.save()  # 调用序列化器的create的方法

    #     # 7.返回保存后的图片数据
    #     return Response(ser.data, status=201)
