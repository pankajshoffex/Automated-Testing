from django.contrib import admin

# Register your models here.
from .models import UserAddress, Order, UserComplaint, AdminComplaint
from .forms import OrderForm
from sms.models import SendSMS, SmsHistory
from django.contrib.auth.models import User

class OrderAdmin(admin.ModelAdmin):
	form = OrderForm
	list_display = ['__unicode__', 'customer_name', 'mobile_no', 'order_total', 'payment',  'status', 'invoice','detail',]
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

	def get_form(self, request, obj=None, **kwargs):
		obj = SendSMS()
		if request.method == 'POST':
			form = OrderForm(request.POST)
			result = ""
			if form.is_valid():
				status = form.cleaned_data['status']
				if status == "received":
					message = "Hi %s your order id is %s of Rs. %s is received Happy Shopping!!! Shoffex.com" %(form.instance.user, form.instance, form.instance.order_total)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "dispatched":
					message = "Dear %s your order %s is dispatched through. Have a nice day!!! Shoffex.com." %(form.instance.user, form.instance)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "intransist":
					message = "Dear %s your order %s is intransist. The order will be delivered in given time. Have a nice day!!! Shoffex.com." %(form.instance.user, form.instance)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "delivered":
					message = "Dear %s Thank you for shopping with Shoffex.com Your order is delivered successfully!!! Cheers" %(form.instance.user)
					print message
				if status == "cancelled":
					message = "Dear %s Your order has been is cancelled www.shofex.com" %(form.instance.user)
					print message
					result = obj.sendsms(message,form.instance.user)
				if result:
					user = User.objects.get(username=form.instance.user)
					SmsHistory.objects.create(
						number=form.instance.user,
						recipient=user.get_full_name(),
						sms_subject=status,
						sms_text=message,
						sms_type = "User Order Status"
						)
			else:
				return OrderForm
		return OrderForm

	def get_readonly_fields(self, request, obj=None):
		if obj: # editing an existing object
			return self.readonly_fields + ('__unicode__', 'order_id','order_total','payment','shipping_total_price','shipping_address','billing_address','user','cart')
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