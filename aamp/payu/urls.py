from django.conf.urls import include, url
from .views import order_checkout, success_response, failure, cancel 

urlpatterns = [
	url(r'^order_checkout/$', order_checkout, name='order_checkout'),
	url(r'^success/$', success_response, name='order_success'),
	url(r'^failure/$', failure, name='order_failure'),
	url(r'^cancel/$', cancel, name='order_cancel'),
]