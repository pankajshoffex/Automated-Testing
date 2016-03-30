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

from aamp.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import views

from carts.views import CartView, ItemCountView, CheckoutView, CheckoutFinalView
from orders.views import (
				AddressSelectFormView, 
				UserAddressCreateView,
				UserShippingAddressCreateView, 
				OrderList, 
				OrderDetail,
				InvoicePDFView,
				UserAddressUpdateView,
				cancel_order,
				admin_orders,
				admin_cancel_order
				)

sitemaps = {
			  'products' : ProductSitemap,
			  'categories': CategorySitemap,
			  'staticPages': StaticViewSitemap
			}

urlpatterns = [
	url(r'^$', index, name="home"),
	url(r'^admin/', admin.site.urls),
	url(r'^accounts/', include('useraccount.urls', namespace="account")),
	url(r'^products/', include('products.urls', namespace="products")),
	url(r'^ui/', include('UI.urls', namespace="ui")),

	url('', include('django.contrib.auth.urls', namespace='auth')),

	url(r'^orders/$', OrderList.as_view(), name="orders"),
	url(r'^orders/(?P<pk>\d+)/$', OrderDetail.as_view(), name="order_detail"),
	url(r'^cancel/(?P<pk>\d+)/$', cancel_order, name="cancel_order"),
	url(r'^adminorders/(?P<pk>\d+)/$', admin_orders, name="admin_orders"),
	url(r'^admincancel/(?P<pk>\d+)/$', admin_cancel_order, name="admin_cancel_order"),

	url(r'^cart/$', CartView.as_view(), name="cart"),
	url(r'^cart/count/$', ItemCountView.as_view(), name="item_count"),
	url(r'^checkout/$', CheckoutView.as_view(), name="checkout"),
	url(r'^checkout/address/$', AddressSelectFormView.as_view(), name="order_address"),
	url(r'^checkout/address/add/$', UserAddressCreateView.as_view(), name="user_address_create"),
	url(r'^checkout/address/change/(?P<pk>\d+)/$', UserAddressUpdateView.as_view(), name="user_address_update"),
	url(r'^checkout/shipping_address/add/$', UserShippingAddressCreateView.as_view(), name="user_shipping_address_create"),
	url(r'^checkout/final/$', CheckoutFinalView.as_view(), name="checkout_final"),
	
	url(r'^invoice/(?P<pk>\d+)/$', InvoicePDFView.as_view(), name='invoice'),

	url(r'^payu/', include('payu.urls', namespace='payu')),

	url(r'^social_accounts/', include('allauth.urls')),

	url(r'^care/', include('care.urls', namespace="care")),

	### SiteMap Indexing ########
	url(r'^sitemap.xml/$', views.index, {'sitemaps': sitemaps}),
	url(r'^sitemap-(?P<section>.+).xml/$', views.sitemap, {'sitemaps': sitemaps}),
	url(r'^robots.txt/', include('robots.urls')),

]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Shoffex Online Retails India Pvt Ltd'
