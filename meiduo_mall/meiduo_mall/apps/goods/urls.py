from django.urls import path, re_path

from . import views


urlpatterns = [
    # 商品列表页
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$',
            views.ListView.as_view(), name='list'),
    # 热销排行
    re_path(r'^hot/(?P<category_id>\d+)/', views.HotGoodsView.as_view()),
]
