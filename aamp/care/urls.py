from django.conf.urls import include, url
from .views import index, care_orders, care_commission, care_wallet

urlpatterns = [
	url(r'^$', index, name='care_dashboard'),
	url(r'^orders/$', care_orders, name='care_orders'),
	url(r'^commission/$', care_commission, name='care_commission'),
	url(r'^wallet/$', care_wallet, name='care_wallet'),
]