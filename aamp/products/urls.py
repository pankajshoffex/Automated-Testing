from django.conf.urls import include, url

from .views import ProductDetailView, ProductListView, ProductColorView, category_list, product_rating, availability, Wishlist, add_wishlist

urlpatterns = [

	url(r'^availability/$', availability, name='availability'),
	url(r'^$', ProductListView.as_view(), name="product_list"),
	url(r'^wishlist/$', Wishlist.as_view(), name="wishlist"),
	url(r'^wishlist/(?P<pk>\d+)/$', add_wishlist, name="add_wishlist"),
	url(r'^rating/(?P<pk>\d+)/$', product_rating, name="rating"),
	url(r'^color_view/$', ProductColorView.as_view(), name="color_view"),
    url(r'^(?P<slug>[-\w]+)/$', ProductDetailView.as_view(), name="product_detail"),
    url(r'^category/(?P<slug>[-\w]+)/$', category_list, name="single_category_products"),
]