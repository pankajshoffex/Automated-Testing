from django.conf.urls import include, url

from .views import ProductDetailView, ProductListView, VariationListView, ProductColorView

urlpatterns = [
	url(r'^$', ProductListView.as_view(), name="product_list"),
	url(r'^color_view/$', ProductColorView.as_view(), name="color_view"),
    url(r'^(?P<slug>[-\w]+)/$', ProductDetailView.as_view(), name="product_detail"),
    url(r'^(?P<pk>\d+)/inventory/$', VariationListView.as_view(), name="product_inventory"),
]