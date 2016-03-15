from django.conf.urls import include, url

from .views import ProductDetailView, ProductListView, ProductColorView, category_list, product_rating

urlpatterns = [
	url(r'^$', ProductListView.as_view(), name="product_list"),
	url(r'^rating/(?P<pk>\d+)/$', product_rating, name="rating"),
	url(r'^color_view/$', ProductColorView.as_view(), name="color_view"),
    url(r'^(?P<slug>[-\w]+)/$', ProductDetailView.as_view(), name="product_detail"),
    url(r'^category/(?P<slug>[-\w]+)/$', category_list, name="single_category_products"),
]