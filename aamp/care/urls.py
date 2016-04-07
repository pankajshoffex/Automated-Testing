from django.conf.urls import include, url
from .views import (
	care_user_login, 
	CareOrderListView, 
	CareCommission, 
	CareWallet, 
	CareFaqsListView, 
	care_contact, 
	care_my_account, 
	care_myArea, 
	CareDashboard,
	change_password,
	update_user_information,
	care_query_send,
	care_forget_pass,
	update_bank_detail_information,
	upadate_bank_docs,
	CareOrderDetailView,
	)

urlpatterns = [
	url(r'^$', care_user_login, name='care_login'),
	url(r'^faqs/$', CareFaqsListView.as_view(), name='care_faqs'),
	url(r'^forget/', care_forget_pass, name='care_forget_pass'),
	url(r'^dashboard/$', CareDashboard.as_view(), name='care_dashboard'),
	url(r'^orders/$', CareOrderListView.as_view(), name='care_orders'),
	url(r'^orders/(?P<pk>\d+)/$', CareOrderDetailView.as_view(), name='care_order_detail'),
	url(r'^commission/$', CareCommission.as_view(), name='care_commission'),
	url(r'^wallet/$', CareWallet.as_view(), name='care_wallet'),
	url(r'^contact/$', care_contact, name='care_contact'),
	url(r'^account/$', care_my_account, name='care_my_account'),
	url(r'^myarea/$', care_myArea, name='care_myArea'),
	url(r'^change_password/$', change_password, name='change_password'),
	url(r'^update_info/$', update_user_information, name='update_info'),
	url(r'^query_send/$', care_query_send, name='query_send'),
	url(r'^update_bank_info/$', update_bank_detail_information, name='update_bank_info'),
	url(r'^update_bank_docs/$', upadate_bank_docs, name='upadate_bank_docs'),


]