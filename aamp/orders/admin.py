from django.contrib import admin

# Register your models here.
from .models import UserAddress, Order, UserComplaint, AdminComplaint
from .forms import OrderForm
from sms.models import SendSMS, SmsHistory
from django.contrib.auth.models import User

class OrderAdmin(admin.ModelAdmin):
	form = OrderForm
	list_display = ['detail', 'status', '__unicode__', 'customer_name', 'mobile_no', 'order_total', 'payment', 'invoice',]
	list_filter = ('payment',)
	search_fields = [
		'order_id',
		'status', 
		'payment', 
		'shipping_total_price', 
		'billing_address__mobile', 
		'billing_address__full_name']
	class Meta:
		model = Order

	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('status', 'order_id','order_total','payment','shipping_total_price','shipping_address','billing_address','cart')
		return self.readonly_fields	

	def has_delete_permission(self, request, obj=None):
		return False	

	def has_add_permission(self, request, obj=None):
		return False	


class UserAddressAdmin(admin.ModelAdmin):
	class Meta:
		model = UserAddress
	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('__unicode__', 'full_name','user','type','street','postcode','mobile')
		return self.readonly_fields	

	def has_delete_permission(self, request, obj=None):
		return True	

	def has_add_permission(self, request, obj=None):
		return False	

class UserComplaintAdmin(admin.ModelAdmin):
	class Meta:
		model = UserComplaint

	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('__unicode__', 'order_id','reason','order_name','order_price','user')
		return self.readonly_fields	

	def has_delete_permission(self, request, obj=None):
		return True

	def has_add_permission(self, request, obj=None):
		return False	

class AdminComplaintAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'admin_order_id', 'admin_order_name', 'admin_order_price', 'admin_user',]
	class Meta:
		model = AdminComplaint

	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('__unicode__', 'admin_order_id','admin_reason','admin_order_name','admin_order_price','admin_user')
		return self.readonly_fields	

	def has_delete_permission(self, request, obj=None):
		return True	

	def has_add_permission(self, request, obj=None):
		return False		


admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserComplaint, UserComplaintAdmin)
admin.site.register(AdminComplaint, AdminComplaintAdmin)