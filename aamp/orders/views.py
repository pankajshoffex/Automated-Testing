from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
from products.models import Availability
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AddressForm, UserAddressForm, OrderForm
from .mixins import CartOrderMixin, LoginRequiredMixin
from .models import UserAddress, Order, UserComplaint, AdminComplaint
from useraccount.models import SignUp
from easy_pdf.views import PDFTemplateView, PDFTemplateResponseMixin
import easy_pdf
import datetime

class InvoicePDFView(LoginRequiredMixin, PDFTemplateView):
	template_name = "pdf/invoice.html"

	def get_context_data(self, pk, **kwargs):
		context = super(InvoicePDFView, self).get_context_data(**kwargs)
		# print self.request.session.get("demo")
		# context["order"] = self.request.session.get("demo")
		# print context["order"]
		# try:
		# 	user_checkout = SignUp.objects.get(user=request.user)
		# except SignUp.DoesNotExist:
		# 	pass
		# except:
		# 	user_checkout = None
		# 	print pk

		obj = Order.objects.get(pk=pk)
		context['order'] = obj
		context['now'] = datetime.datetime.now().date()
		return context

class OrderDetail(LoginRequiredMixin, DetailView):
	model = Order
	template_name = "orders/order_detail.html"

	def dispatch(self, request, *args, **kwargs):
		
		# try:
		# 	user_checkout = SignUp.objects.get(user=request.user)
		# except SignUp.DoesNotExist:
		# 	pass
		# except:
		# 	user_checkout = None

		obj = self.get_object()
		print obj

		if self.request.user.is_authenticated():
			if obj.user == request.user:
				return super(OrderDetail, self).dispatch(request, *args, **kwargs)
			else:
				raise Http404
		else:
			return HttpResponseRedirect("/")
		

class OrderList(LoginRequiredMixin, ListView):
	queryset = Order.objects.all()

	def get_queryset(self):
		# user_checkout = SignUp.objects.get(user=self.request.user)
		return super(OrderList, self).get_queryset().filter(user=self.request.user)


class UserAddressCreateView(LoginRequiredMixin, CreateView):
	form_class = UserAddressForm
	template_name = "forms.html"
	success_url = "/checkout/address/"

	def get_checkout_user(self):
		user_checkout = self.request.user
		return user_checkout

	def form_valid(self,form, *args, **kwargs):
		form.instance.user = self.get_checkout_user()
		if form.cleaned_data["different"] == True:
			form.instance.type = "billing"
			user_address = UserAddress(user=self.get_checkout_user())
			user_address.type = "shipping"
			user_address.full_name = form.cleaned_data['full_name']
			user_address.street = form.cleaned_data['street']
			user_address.postcode = form.cleaned_data['postcode']
			user_address.mobile = form.cleaned_data['mobile']
			pin = Availability.objects.filter(pin=user_address.postcode)
			if pin:
				user_address.save()
				super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)
				return redirect('checkout')
			else:
				messages.error(self.request,"postcode is not available for shipping.")
				return redirect("user_address_create")
		else:
			form.instance.type = "billing"
			super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)
			return redirect('user_shipping_address_create')

		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

class UserShippingAddressCreateView(LoginRequiredMixin, CreateView):
	form_class = UserAddressForm
	template_name = "orders/user_address_form.html"
	success_url = "/checkout/address/"

	def get_checkout_user(self):
		user_checkout = self.request.user
		return user_checkout

	def form_valid(self,form, *args, **kwargs):
		form.instance.user = self.get_checkout_user()	
		form.instance.type = "shipping"
		super(UserShippingAddressCreateView, self).form_valid(form, *args, **kwargs)			
		return redirect('checkout')

class UserAddressUpdateView(LoginRequiredMixin, UpdateView):
	model = UserAddress
	fields = ["full_name", "street", "postcode", "mobile"]
	template_name = "orders/user_address_update_form.html"
	success_url = "/checkout/address/"

	def get_checkout_user(self):
		user_checkout = self.request.user
		return user_checkout

	def form_valid(self,form, *args, **kwargs):
		form.instance.user = self.get_checkout_user()
		if form.is_valid():
			form.instance.full_name = form.cleaned_data['full_name']
			form.instance.street = form.cleaned_data['street']
			form.instance.postcode = form.cleaned_data['postcode']
			form.instance.mobile = form.cleaned_data['mobile']
			pin = Availability.objects.filter(pin=form.instance.postcode)
			if pin:
				form.save()
				super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)
				return redirect('order_address')
			else:
				messages.error(self.request, "postcode is not available for shipping.")
				return redirect("user_address_update", pk=form.instance.pk)
		return super(UserAddressUpdateView, self).form_valid(form, *args, **kwargs)


class AddressSelectFormView(CartOrderMixin, FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"

	def get_context_data(self, *args, **kwargs):
		context = super(AddressSelectFormView, self).get_context_data(*args, **kwargs)
		cart_id = self.request.session.get("cart_id")
		if cart_id == None:
			context['data'] = False
		else:
			context['data'] = True
		return context
		

	def dispatch(self, *args, **kwargs):
		if self.request.user.is_authenticated():
			b_address, s_address = self.get_addresses()
		else:
			return HttpResponseRedirect('/')

		if b_address.count() == 0 :
			messages.success(self.request, "Please add a billing address before continuing")
			return redirect("user_address_create")
		elif s_address.count() == 0:
			messages.success(self.request, "Please add a shipping address before continuing")
			return redirect("user_address_create")
		else:
			return super(AddressSelectFormView, self).dispatch(*args, **kwargs)

	def get_addresses(self, *args, **kwargs):
		user_checkout = self.request.user

		b_address = UserAddress.objects.filter(
			user=user_checkout,
			type='billing',
		)

		s_address = UserAddress.objects.filter(
			user=user_checkout,
			type='shipping',
		)
		return b_address, s_address


	def get_form(self, *args, **kwargs):
		form = super(AddressSelectFormView, self).get_form(*args, **kwargs)
		b_address, s_address = self.get_addresses()

		form.fields["billing_address"].queryset = b_address
		form.fields["shipping_address"].queryset = s_address
		return form

	def form_valid(self, form, *args, **kwargs):
		billing_address = form.cleaned_data["billing_address"]
		shipping_address = form.cleaned_data["shipping_address"]
		order = self.get_order()
		order.billing_address = billing_address
		order.shipping_address = shipping_address
		order.save()
		return super(AddressSelectFormView, self).form_valid(form, *args, **kwargs)

	def get_success_url(self, *args, **kwargs):
		return "/checkout/"


def cancel_order(request,pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		reason_choice = request.POST.get("reason_choice")
		reason_text = request.POST.get("reason_text")
		order_id = order.id
		order_price = order.order_total
		product = order.cart.cartitem_set.all()
		for i in product:
			order_name = i.item.product.title
		instance = UserComplaint()
		if reason_choice:
			instance.reason = reason_choice
		else:
			instance.reason = reason_text
		instance.order_id = order_id
		instance.order_price = order_price
		instance.order_name = order_name
		instance.user = order.user
		order.status = "cancelled"
		order.save()
		instance.save()
		messages.success(request, "your order has been cancelled.")
		return redirect("orders")
	return render(request, "orders/cancel_order.html", {})

@staff_member_required
def admin_orders(request, pk):
	order = get_object_or_404(Order, pk=pk)
	form = OrderForm(request.POST or None, instance=order)
	if form.is_valid():
		if order.status == "cancelled":
			return redirect('admin_cancel_order', pk=order.pk)
		else:
			form.save()
			messages.success(request, "status has been changed.")
			return redirect("/admin/orders/order/")
	return render(request, "orders/admin_orders.html", {'form':form, 'order':order})

@staff_member_required
def admin_cancel_order(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		reason_choice = request.POST.get("reason_choice")
		reason_text = request.POST.get("reason_text")
		admin_order_id = order.id
		admin_order_price = order.order_total
		product = order.cart.cartitem_set.all()
		for i in product:
			order_name = i.item.product.title
		instance = AdminComplaint()
		if reason_choice:
			instance.admin_reason = reason_choice
		else:
			instance.admin_reason = reason_text
		instance.admin_order_id = admin_order_id
		instance.admin_order_price = admin_order_price
		instance.admin_order_name = order_name
		instance.admin_user = request.user
		order.status = "cancelled"
		order.save()
		instance.save()
		messages.success(request, "Order has been cancelled.")
		return redirect("/admin/orders/order/")
	return render(request, "orders/admin_cancel_order.html",{'order':order})

@login_required
def feedback(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		feedback = request.POST.get('feedback')
		name = request.POST.get('name')
		mobile = request.POST.get('mobile')
		print email, feedback, name, mobile
		send_mail('Feedback', feedback, email, ['abhilash.shoffex@gmail.com'], fail_silently=False)
	return render(request, "orders/user_feedback.html", {})


@login_required
def get_feedback(request):
	return render(request, "orders/feedback_submited.html", {})