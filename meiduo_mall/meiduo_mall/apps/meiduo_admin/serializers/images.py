#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-12 15:19:26
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from django.conf import settings
from rest_framework.response import Response

from goods.models import SKUImage, SKU


class ImagesSerializer(serializers.ModelSerializer):
    """SKU图片表序列化器"""

    class Meta:

        model = SKUImage
        fields = "__all__"

    def create(self, validated_data):
        """封装保存图片的业务逻辑"""

        # 3.建立fastdfs客户端
        client = Fdfs_client(settings.FASTDFS_PATH)
        # request = self.context['request']
        file = self.context['request'].FILES.get('image')

        # 4.上传图片
        result = client.upload_appender_by_buffer(file.read())

        # 5.判断是否上传成功
        if result['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})

        # 6.保存图片表
        img = SKUImage.objects.create(
            sku=validated_data['sku'], image=result['Remote file_id'])

        return img


class SKUSerializer(serializers.ModelSerializer):
    """SKU商品信息序列化器"""

    class Meta:

        model = SKU
        fields = ('id', 'name')
