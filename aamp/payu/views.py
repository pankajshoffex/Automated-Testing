from django.shortcuts import render, redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.lorem_ipsum import sentence as lorem_ipsum

# Create your views here.
from payu.forms import PayUOrderForm, PayUForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from payu.gateway import check_hash, get_hash, payu_url, verify_hash
from orders.models import Order
from uuid import uuid4
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from sms.models import SmsSetting, SmsHistory, SendSMS
from products.models import Product




def order_checkout(request):
	if request.method == 'POST':
		order_form = PayUOrderForm(request.POST)
		if order_form.is_valid():
			initial = order_form.cleaned_data
			initial.update({'key': settings.PAYU_MERCHANT_KEY,
							'surl': request.build_absolute_uri(reverse('payu:order_success')),
							'furl': request.build_absolute_uri(reverse('payu:order_success')),
							'curl': request.build_absolute_uri(reverse('payu:order_cancel')),
							'hash': get_hash(initial)})
			# Once you have all the information that you need to submit to payu
			# create a payu_form, validate it and render response using
			# template provided by PayU.
			payu_form = PayUForm(initial)
			if payu_form.is_valid():
				data = payu_form.cleaned_data["hash"]
				context = {'form': payu_form,
						   'action': payu_url()}
				return render(request, 'payu_form.html', context)
			else:
				messages.error('Something went wrong! Looks like initial data\
						used for payu_form is failing validation')
				return HttpResponse(status=500)
	else:
		if request.session.get("order_id"):
			order = Order.objects.get(id=request.session.get("order_id"))
		else:
			return HttpResponseRedirect("/")

		initial = {'txnid': uuid4().hex,
				'productinfo': lorem_ipsum(),
				'amount': order.order_total,
				'firstname': order.billing_address.full_name,
				'phone': order.billing_address.mobile,
				'address1': order.billing_address.street,
				'zipcode': order.billing_address.postcode}
		order_form = PayUOrderForm(initial=initial)
	context = {'form': order_form}
	return render(request, 'checkout.html', context)

@csrf_exempt
def success_response(request):
	hash_value = check_hash(request.POST)
	if check_hash(request.POST):
		order = Order.objects.get(id=request.session.get("order_id"))
		order.mark_completed()
		order.payment_method("PAYU")
		data = order.cart.cartitem_set.all()
		if data:
			for i in data:
				try:
					product = Product.objects.get(id=i.item.product.id)
					product.quantity = product.quantity - i.quantity
					product.save()
				except:
					pass
		messages.success(request, "Thank you for your order.")
		msg = "Your order id is %s was successfully created, payment type is %s, your total amount is %s , Have a nice day,Shoffex." % ( request.POST.get('txnid') ,order.payment,order.order_total)
		if request.user.is_authenticated():
			obj = SendSMS()
			result = obj.sendsms(msg, request.user)
			if result:
				SmsHistory.objects.create(
					number=order.billing_address.mobile,
					recipient=request.user.get_full_name(),
					sms_subject="Order Completed", 
					sms_text=msg,
					sms_type="Order Created"
					)
		del request.session["cart_id"]
		del request.session["order_id"]
		return redirect("order_detail", pk=order.pk)
	else:
		return HttpResponse("Transaction has Unsuccessful.")


@csrf_exempt
def failure(request):
	if request.method == 'POST':
		return render(request, 'failure.html')
	else:
		raise Http404

@csrf_exempt
def cancel(request):
	if request.method == 'POST':
		return render(request, 'cancel.html')
	else:
		raise Http404



