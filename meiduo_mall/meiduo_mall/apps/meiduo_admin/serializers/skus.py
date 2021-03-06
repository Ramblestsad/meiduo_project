#!/usr/bin/env python
# -*- encoding: utf-8 -*-


"""
Author: Chris W.
Date: 2021-03-13 17:20:27
Description: None
Version: 1.0
License: None
"""


from rest_framework import serializers
from django.db import transaction

from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption, SKUSpecification
from celery_tasks.static_file.tasks import get_detail_html


class SKUSpecsSerializer(serializers.ModelSerializer):
    """SKU具体规格表序列化器"""

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:

        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    # sku_specification表中关联了sku，related_name: specs
    specs = SKUSpecsSerializer(read_only=True, many=True)

    class Meta:

        model = SKU
        fields = "__all__"
        read_only_fields = ('spu', 'category')

    # @transaction.atomic() 第一种方式开启事务
    def create(self, validated_data):
        """
            保存SKU到SKU表
            保存SKU具体规格
        """

        specs = self.context['request'].data.get('specs')

        # 开启事务: 第二种方法
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()

            try:
                # 保存SKU
                sku = SKU.objects.create(**validated_data)
                # 保存SKU具体规格
                for spec in specs:
                    SKUSpecification.objects.create(
                        spec_id=spec['spec_id'], option_id=spec['option_id'], sku=sku)
            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                # 提交
                transaction.savepoint_commit(save_point)

                # 静态化SKU的detail.html
                get_detail_html.delay(sku.id)

                return sku

    def update(self, instance, validated_data):
        """
            更新SKU表
            更新SKU规格表
        """

        specs = self.context['request'].data.get('specs')

        # 开启事务: 第二种方法
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()

            try:
                # 修改SKU表
                SKU.objects.filter(id=instance.id).update(**validated_data)

                # 修改SKU规格表
                for spec in specs:
                    # SKUSpecification.objects.filter(sku=instance).update(**spec)
                    SKUSpecification.objects.create(
                        sku=instance, spec_id=spec['spec_id'], option_id=spec['option_id'])

            except:
                # 回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')

            else:
                # 提交
                transaction.savepoint_commit(save_point)

                # 静态化SKU的detail.html
                get_detail_html.delay(instance.id)

                return instance


class SKUCategorySerailizer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:

        model = GoodsCategory
        fields = '__all__'


class SpecsOptionSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""

    class Meta:

        model = SpecificationOption
        fields = "__all__"


class SPUSpecsSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""

    options = SpecsOptionSerializer(many=True)
    # specsoption_set = SpecificationOption(many=True) tip: 没有指定副表 relateed_name时

    class Meta:

        model = SPUSpecification
        fields = "__all__"
