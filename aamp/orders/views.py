from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
# Create your views here.

from .forms import AddressForm, UserAddressForm
from .mixins import CartOrderMixin, LoginRequiredMixin
from .models import UserAddress, Order
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
		try:
			user_checkout = SignUp.objects.get(user=request.user)
		except SignUp.DoesNotExist:
			pass
		except:
			user_checkout = None
			print pk

		obj = Order.objects.get(pk=pk)
		context['order'] = obj
		context['now'] = datetime.datetime.now().date()
		return context

class OrderDetail(LoginRequiredMixin, DetailView):
	model = Order
	template_name = "orders/order_detail.html"

	def dispatch(self, request, *args, **kwargs):
		
		try:
			user_checkout = SignUp.objects.get(user=request.user)
		except SignUp.DoesNotExist:
			pass
		except:
			user_checkout = None

		obj = self.get_object()
		print obj

		if self.request.user.is_authenticated():
			if obj.user == user_checkout and user_checkout is not None:
				return super(OrderDetail, self).dispatch(request, *args, **kwargs)
			else:
				raise Http404
		else:
			return HttpResponseRedirect("/")
		

class OrderList(LoginRequiredMixin, ListView):
	queryset = Order.objects.all()

	def get_queryset(self):
		user_checkout = SignUp.objects.get(user=self.request.user)
		return super(OrderList, self).get_queryset().filter(user=user_checkout)


class UserAddressCreateView(LoginRequiredMixin, CreateView):
	form_class = UserAddressForm
	template_name = "forms.html"
	success_url = "/checkout/address/"

	def get_checkout_user(self):
		user_checkout = SignUp.objects.get(user=self.request.user)
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
			user_address.save()
			super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)
			return redirect('checkout')
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
		user_checkout = SignUp.objects.get(user=self.request.user)
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
		user_checkout = SignUp.objects.get(user=self.request.user)

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

