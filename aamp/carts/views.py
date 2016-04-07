from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin
from decimal import Decimal

# Create your views here.

from orders.mixins import CartOrderMixin, LoginRequiredMixin
from orders.models import  Order, UserAddress
from products.models import Variation, Product
from .models import Cart, CartItem, Shipping, TaxInc
from useraccount.models import SignUp
from sms.models import SmsSetting, SmsHistory, SendSMS, AdminContact
from care.models import CarePointPincode, Taluka 


class ItemCountView(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			cart_id = self.request.session.get("cart_id")
			if cart_id == None:
				count = 0
			else:
				cart = Cart.objects.get(id=cart_id)
				count = cart.items.count()
			request.session["cart_item_count"] = count
			return JsonResponse({"count": count})
		else:
			raise Http404
					
class CartView(SingleObjectMixin, View):
	model = Cart
	template_name = "carts/view.html"

	def get_object(self):
		self.request.session.set_expiry(0) # 5 minutes
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			cart = Cart()
			cart.tax_percentage = 0.07
			cart.save()
			cart_id = cart.id
			self.request.session["cart_id"] = cart_id
		
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated():
			cart.user = self.request.user
			cart.save()
		return cart

	def add_shipping(self, total):
		cart = self.get_object()
		ship = Shipping.objects.get()
		print type(ship.to_val)
		total = Decimal(total)
		if ship.from_val < total and ship.to_val > total:
			data = cart.cartitem_set.all()
			product_shipping_list = []
			for i in data:
				if i.item.product.single_shipping:
					product_shipping_list.append(i.item.product.single_shipping)
			if product_shipping_list:
				print "indivisual shipping"
				shipping = min(product_shipping_list)
				shipping_total = round(Decimal(total) + Decimal(shipping), 2)
			else:
				print "common shipping"
				shipping = ship.ship_val
				shipping_total = round(Decimal(total) + Decimal(shipping), 2)
		else:
			print "free shipping"
			shipping = 0.00
			shipping_total = total

		return shipping, shipping_total

	def get(self, request, *args, **kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item")
		delete_item = request.GET.get("delete", False)
		flash_message = ""
		item_added = False
		if item_id:
			item_instance = get_object_or_404(Variation, id=item_id)
			qty = request.GET.get("qty", 1)
			try:
				if int(qty) < 1:
					delete_item = True
			except:
				raise Http404

			cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item_instance)
			if created:
				flash_message = "Successfully added to the cart"
				item_added = True
			if delete_item:
				flash_message = "Item remove successfully."
				cart_item.delete()
			else:
				if not created:
					flash_message = "Quantity has been updated successfully."
				cart_item.quantity = qty
				cart_item.save()
			if not request.is_ajax():
				return HttpResponseRedirect(reverse("cart"))
				#return cart_item.cart.get_absolute_url()

		shipping_cost = None
		shipping = None
		shipping, shipping_cost = self.add_shipping(cart.total)
		request.session['shipping'] = unicode(shipping)
		request.session['shipping_cost'] = unicode(shipping_cost)
		if request.is_ajax():
			try:
				total = cart_item.line_item_total
			except:
				total = None

			try:
				subtotal = cart_item.cart.subtotal
			except:
				subtotal = None
			try:
				cart_total = cart_item.cart.total
				shipping, shipping_cost = self.add_shipping(cart_total)

			except:
				cart_total = None
				shipping = None
			try:
				tax_total = cart_item.cart.tax_total
			except:
				tax_total = None

			try:
				total_items = cart_item.cart.items.count()
			except:
				total_items = 0

			data = {
				"deleted": delete_item, 
				"item_added": item_added,
				"line_total": total,
				"subtotal": subtotal,
				"cart_total": shipping_cost,
				"tax_total": tax_total,
				"flash_message": flash_message,
				"total_items": total_items,
				"shipping": shipping,
			}
			return JsonResponse(data)

		context = {
			"object": self.get_object(),
			"shipping": shipping,
			"shipping_cost": shipping_cost,
		}
		template = self.template_name
		return render(request, template, context)

class CheckoutView(LoginRequiredMixin, CartOrderMixin, DetailView):
	model = Cart
	template_name = "carts/checkout_view.html"

	def get_object(self):
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			return redirect("cart")
		
		cart = Cart.objects.get(id=cart_id)
		return cart

	def get_context_data(self, *args, **kwargs):
		context = super(CheckoutView, self).get_context_data(*args, **kwargs)
		context["order"] = self.get_order()
		return context


	def get_success_url(self):
		return reverse("checkout")


	def get(self, request, *args, **kwargs):
		get_data = super(CheckoutView, self).get(request, *args, **kwargs)
		cart = self.get_object()

		if cart == None:
			return redirect("cart")
		if cart.cartitem_set.all().count() == 0:
			return redirect("cart")
		new_order = self.get_order()
		if request.session.get('shipping') and request.session.get('shipping_cost'):
			shipping = Decimal(request.session.get('shipping'))
			order_total = Decimal(request.session.get('shipping_cost'))
			new_order.shipping_total_price = shipping
			new_order.save() 

		# if self.request.user.is_authenticated():
		# 	user_checkout = SignUp.objects.get(user=self.request.user)
			if new_order.billing_address == None or new_order.shipping_address == None:
				return redirect("order_address")

			new_order.user = request.user
			new_order.save()
		return get_data




class CheckoutFinalView(CartOrderMixin, View):
	def post(self, request, *args, **kwargs):
		order = self.get_order()
		data = order.cart.cartitem_set.all()
		if data:
			for i in data:
				try:
					product = Product.objects.get(id=i.item.product.id)
					product.quantity = product.quantity - i.quantity
					product.save()
				except:
					pass
		user_pincode = order.billing_address.postcode
		obj = SendSMS()
		admin_obj = AdminContact.objects.all()
		admin_msg = "Received  order from %s of order ID is %s. Of Rs. %s." % (order.billing_address.mobile, order.order_id, order.order_total )
		if admin_obj:
			for item in admin_obj:
				print item.number
				result1 = obj.sendsms(admin_msg, item.number)
		try:
			care_pincode = CarePointPincode.objects.get(pincode=user_pincode)
			if care_pincode:
				care_taluka = Taluka.objects.get(taluka=care_pincode.taluka)
				msg = "Received  order from %s of order id %s Of Rs. %s From:- %s" % (order.billing_address.full_name, order.order_id, order.order_total, order.billing_address.postcode)
				result = obj.sendsms(msg, care_taluka.user.mobile_no)
				if result:
					SmsHistory.objects.create(
						number=order.billing_address.mobile,
						recipient=care_taluka.user.get_full_name(),
						sms_subject="Order Completed",
						sms_text=msg,
						sms_type="Order Created"
						)				
		except:
			pass
		if request.POST.get("payment_token") == "COD":
			order.mark_completed()
			order.payment_method("COD")
			messages.success(request, "Thank you for your order.")
			msg = "Your order id is %s was successfully created, payment type is %s, your total amount = %s . Have a nice day!!! Shoffex.com" % ( order.id,order.payment,order.order_total)
			result = obj.sendsms(msg, self.request.user)
			if result:
				SmsHistory.objects.create(
					number=order.billing_address.mobile,
					recipient=self.request.user.get_full_name(),
					sms_subject="Order Completed", 
					sms_text=msg,
					sms_type="Order Created"
					)
			del request.session["cart_id"]
			del request.session["order_id"]
		else:
			pass

		return redirect("order_detail", pk=order.pk)

	def get(self, request, *args, **kwargs):
		return redirect("checkout")
