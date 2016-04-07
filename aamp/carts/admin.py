from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem, Shipping, TaxInc


class CartItemInline(admin.TabularInline):
	model = CartItem

class CartAdmin(admin.ModelAdmin):
	inlines = [
		CartItemInline,
	]
	class Meta:
		model = Cart

class ShippingAdmin(admin.ModelAdmin):
	model = Shipping

	def has_add_permission(self, request):
		obj = Shipping.objects.all()
		if obj:
			return False
		else:
			return True

class TaxIncAdmin(admin.ModelAdmin):
	model = TaxInc

	def has_add_permission(self, request):
		tax_obj = TaxInc.objects.all()
		if tax_obj:
			return False
		else:
			return True
				
admin.site.register(Cart, CartAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(TaxInc, TaxIncAdmin)