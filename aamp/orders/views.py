from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, FormView
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
		return context

# def invoice(request, oid, **kwargs):
# 	context = {}
# 	try:
# 		user_checkout = SignUp.objects.get(user=request.user)
# 	except SignUp.DoesNotExist:
# 		pass
# 	except:
# 		user_checkout = None
# 	print oid
# 	obj = Order.objects.get(user=user_checkout, id=oid)
# 	context['order'] = obj
# 	template = "orders/order_summary_short.html"
# 	return easy_pdf.rendering.render_to_pdf(template, context, encoding=u'utf-8', **kwargs)




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
		user = User.objects.get(username=self.request.user.username)
		user.first_name = form.cleaned_data["name"]
		user.save()
		self.request.session["diff"] = form.cleaned_data["different"]

		if form.cleaned_data["type"] == "billing":
			form.instance.type = "billing"
		elif form.cleaned_data["type"] == "shipping":
			form.instance.type = "shipping"
		else:
			pass			

		if self.request.session.get("diff") == True:
			user_address = UserAddress(user=self.get_checkout_user())
			user_address.type = "shipping"
			user_address.street = form.cleaned_data['street']
			user_address.postcode = form.cleaned_data['postcode']
			user_address.save()
		

		return super(UserAddressCreateView, self).form_valid(form, *args, **kwargs)

class AddressSelectFormView(CartOrderMixin, FormView):
	form_class = AddressForm
	template_name = "orders/address_select.html"

	def dispatch(self, *args, **kwargs):
		b_address, s_address = self.get_addresses()

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

