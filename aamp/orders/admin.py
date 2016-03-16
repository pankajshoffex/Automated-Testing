from django.contrib import admin

# Register your models here.
from .models import UserAddress, Order
from .forms import OrderForm
from sms.models import SendSMS

class OrderAdmin(admin.ModelAdmin):
	form = OrderForm
	list_display = ['__unicode__', 'customer_name', 'mobile_no', 'products', 'order_total', 'payment',  'status', 'invoice']
	list_filter = ('payment',)
	search_fields = [
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
			if form.is_valid():
				status = form.cleaned_data['status']
				if status == "received":
					message = "Hi %s your order id is %s of Rs. %s is received Happy Shopping!!! Shoffex.com" %(form.instance.user, form.instance, form.instance.order_total)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "dispatched":
					message = "Dear %s your order %s is dispatched through. Have a nice day, Shoffex.com." %(form.instance.user, form.instance)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "intransist":
					message = "Dear %s your order %s is intransist. will be delivered in given time. Have a nice day, Shoffex.com." %(form.instance.user, form.instance)
					print message
					result = obj.sendsms(message,form.instance.user)
				if status == "delivered":
					message = "Dear %s Thank you for shopping with Shoffex.com Your order is delivered successfully!!! Cheers" %(form.instance.user)
					print message
				if status == "cancelled":
					message = "Dear %s Your order is cancelled" %(form.instance.user)
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

admin.site.register(UserAddress)
admin.site.register(Order, OrderAdmin)