from django import http
from django.shortcuts import render
from django.views import View
from django.core.cache import cache
import logging

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE
# Create your views here.


# 创建日志器
logger = logging.getLogger('django')


class AreasView(View):
    """省市区三级联动"""

    def get(self, request):

        # 判断当前要查省份数据 or 市区数据：即有没有area_id 参数
        area_id = request.GET.get('area_id')

        if not area_id:  # 查询省份数据
            # 获取并判断是否有缓存
            province_list = cache.get('province_list')

            if not province_list:
                try:
                    # Area.objects.filter(属性名__条件表达式=值)
                    # parent 就是 tb_areas 中的 parent_id
                    province_model_list = Area.objects.filter(
                        parent__isnull=True)  # QuerySet {models}

                    # 将 模型列表 转换成 字典列表：models to dict
                    province_list = []
                    for province_model in province_model_list:
                        province_dict = {
                            "id": province_model.id,
                            "name": province_model.name,
                        }
                        province_list.append(province_dict)

                    # 缓存省份字典列表数据: 默认存储到别名为 default 的cache配置中
                    cache.set('province_list', province_list, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})

            # 响应省级Json数据
            return http.JsonResponse({'code': RETCODE.OK,
                                      'errmsg': 'OK',
                                      'province_list': province_list})

        else:  # 查询市区数据
            # 判断是否有缓存
            sub_data = cache.get('sub_area_' + area_id)

            if not sub_data:

                try:
                    parent_model = Area.objects.get(id=area_id)  # QuerySet
                    sub_model_list = parent_model.subs.all()  # QuerySet

                    # 将子集模型列表转换为列表
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            "id": sub_model.id,
                            "name": sub_model.name,
                        }
                        subs.append(sub_dict)

                    # 构造子集Json数据
                    sub_data = {
                        "id": parent_model.id,
                        "name": parent_model.name,
                        "subs": subs,
                    }

                    # 缓存市、区县
                    cache.set('sub_area_' + area_id, sub_data, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询市、区县数据错误'})

            # 响应城市 or 区县 JSON 数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
