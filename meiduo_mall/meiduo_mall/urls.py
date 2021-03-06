"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.urls.conf import include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Haystack
    re_path(r'^search/', include('haystack.urls')),

    # users
    re_path(r'^', include(('users.urls', 'users'), namespace='users')),
    # index
    re_path(r'^', include(('contents.urls', 'contents'), namespace='contents')),
    # verificaitons
    re_path(r'^', include(('verifications.urls', 'verifications'), namespace='verifications')),
    # oauth
    re_path(r'^', include('oauth.urls')),
    # areas
    re_path(r'^', include('areas.urls')),
    # goods
    re_path(r'^', include(('goods.urls', 'goods'), namespace='goods')),
    # carts
    re_path(r'^', include(('carts.urls', 'carts'), namespace='carts')),
    # orders
    re_path(r'^', include(('orders.urls', 'orders'), namespace='orders')),
    # payment
    re_path(r'^', include(('payment.urls', 'payment'), namespace='payment')),
    # background admin
    re_path(r'^meiduo_admin/', include(('meiduo_admin.urls', 'admin'), namespace='meiduo_admin'))
]
