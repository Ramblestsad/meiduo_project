from django.urls import path, re_path

from . import views


urlpatterns = [
    # 商品列表页
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$',
            views.ListView.as_view(), name='list'),
    # 热销排行
    re_path(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情
    re_path(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    # 统计分类商品访问量
    re_path(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
    # 详情页商品评价
    re_path(r'^comments/(?P<sku_id>\d+)/$', views.GoodsCommentView.as_view()),
]
