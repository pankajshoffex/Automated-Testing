from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.edit import FormMixin

# Create your views here.

from orders.mixins import CartOrderMixin, LoginRequiredMixin
from orders.models import  Order, UserAddress
from products.models import Variation
from .models import Cart, CartItem
from useraccount.models import SignUp


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
			cart.tax_percentage = 0.075
			cart.save()
			cart_id = cart.id
			self.request.session["cart_id"] = cart_id
		
		cart = Cart.objects.get(id=cart_id)
		if self.request.user.is_authenticated():
			cart.user = self.request.user
			cart.save()
		return cart

	def get(self, request, *args, **kwargs):
		cart = self.get_object()
		item_id = request.GET.get("item")
		print item_id
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
			except:
				cart_total = None

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
				"cart_total": cart_total,
				"tax_total": tax_total,
				"flash_message": flash_message,
				"total_items": total_items,
			}
			return JsonResponse(data)

		context = {
			"object": self.get_object()
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
		new_order = self.get_order()

		if self.request.user.is_authenticated():
			user_checkout = SignUp.objects.get(user=self.request.user)
			if new_order.billing_address == None or new_order.shipping_address == None:
			 	return redirect("order_address")

			new_order.user = user_checkout
			new_order.save()
		return get_data




class CheckoutFinalView(CartOrderMixin, View):
	def post(self, request, *args, **kwargs):
		order = self.get_order()
		if request.POST.get("payment_token") == "ABC":
			order.mark_completed()
			messages.success(request, "Thank you for your order.")
			del request.session["cart_id"]
			del request.session["order_id"]
		return redirect("order_detail", pk=order.pk)

	def get(self, request, *args, **kwargs):
		return redirect("checkout")


