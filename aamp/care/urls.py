from django.conf.urls import include, url
from .views import index, care_orders, care_commission, care_wallet, care_faqs, care_contact, care_my_account, care_myArea, care_dashboard

urlpatterns = [
	url(r'^$', index, name='care_login'),
	url(r'^dashboard/$', care_dashboard, name='care_dashboard'),
	url(r'^orders/$', care_orders, name='care_orders'),
	url(r'^commission/$', care_commission, name='care_commission'),
	url(r'^wallet/$', care_wallet, name='care_wallet'),
	url(r'^faqs/$', care_faqs, name='care_faqs'),
	url(r'^contact/$', care_contact, name='care_contact'),
	url(r'^account/$', care_my_account, name='care_my_account'),
	url(r'^myarea/$', care_myArea, name='care_myArea'),

]