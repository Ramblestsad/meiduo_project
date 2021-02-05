from django.urls import path, re_path

from . import views


urlpatterns = [
    # 商品列表页
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$',
            views.ListView.as_view(), name='list'),
]
