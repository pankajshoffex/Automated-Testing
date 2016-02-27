from django.contrib import admin

# Register your models here.
from .models import UserAddress, Order

class OrderAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'customer_name', 'user', 'status', 'order_total']
	class Meta:
		model = Order

admin.site.register(UserAddress)
admin.site.register(Order, OrderAdmin)