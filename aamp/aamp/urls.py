"""aamp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from useraccount.views import index

from products.views import demo

from carts.views import CartView, ItemCountView, CheckoutView, CheckoutFinalView
from orders.views import (
                AddressSelectFormView, 
                UserAddressCreateView, 
                OrderList, 
                OrderDetail,
                InvoicePDFView)

urlpatterns = [
    url(r'^$', index, name="home"),
    url(r'^demo/$', demo, name="demo"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('useraccount.urls', namespace="account")),
    url(r'^products/', include('products.urls', namespace="products")),
    url(r'^ui/', include('UI.urls', namespace="ui")),
    url(r'^categories/', include('products.urls_categories', namespace="categories")),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^orders/$', OrderList.as_view(), name="orders"),
    url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name="order_detail"),
    url(r'^cart/$', CartView.as_view(), name="cart"),
    url(r'^cart/count/$', ItemCountView.as_view(), name="item_count"),
    url(r'^checkout/$', CheckoutView.as_view(), name="checkout"),
    url(r'^checkout/address/$', AddressSelectFormView.as_view(), name="order_address"),
    url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name="user_address_create"),
    url(r'^checkout/final/$', CheckoutFinalView.as_view(), name="checkout_final"),
    url(r'^invoice/(?P<pk>\d+)/$', InvoicePDFView.as_view(), name='invoice'),

    url(r'^social_accounts/', include('allauth.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Shoffex Online Retails India Pvt Ltd'
