from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from .models import CarePointUserProfile, Taluka, CarePointPincode, CarePointBankDetail, CarePointDocuments, Faqs
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.core.mail import send_mail
from django.db.models import Q
# Create your views here.
from .forms import CareChangePasswordForm, CarePointBankDetailForm, CarePointDocumentsForm
from orders.models import Order, UserAddress
from products.models import Category
from .mixins import LoginRequiredMixin
from products.models import Availability
from itertools import chain

import base64
import hmac, base64, struct, time
import hashlib, random, datetime
from django.views.generic.detail import DetailView
import datetime
import time




def mkDateTime(dateString,strFormat="%Y-%m-%d"):
    # Expects "YYYY-MM-DD" string
    # returns a datetime object
    eSeconds = time.mktime(time.strptime(dateString,strFormat))
    return datetime.datetime.fromtimestamp(eSeconds)

def formatDate(dtDateTime,strFormat="%Y-%m-%d"):
    # format a datetime object as YYYY-MM-DD string and return
    return dtDateTime.strftime(strFormat)

def mkFirstOfMonth(dtDateTime):
    #what is the first day of the current month
    #format the year and month + 01 for the current datetime, then form it back
    #into a datetime object
    return mkDateTime(formatDate(dtDateTime,"%Y-%m-01"))

def mkLastOfMonth(dtDateTime):
    dYear = dtDateTime.strftime("%Y")        #get the year
    dMonth = str(int(dtDateTime.strftime("%m"))%12+1)#get next month, watch rollover
    dDay = "1"                               #first day of next month
    nextMonth = mkDateTime("%s-%s-%s"%(dYear,dMonth,dDay))#make a datetime obj for 1st of next month
    delta = datetime.timedelta(seconds=1)    #create a delta of 1 second
    return nextMonth - delta 


def care_user_login(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				try:
					care_user = CarePointUserProfile.objects.get(user=user)
					if care_user.is_care:	
						login(request, user)
						return HttpResponseRedirect('/care/dashboard/')
					else:
						return HttpResponse("You are not care point user..")
				except:
					return HttpResponse("You are not care point user..")
			else:
				return HttpResponse('User not active.')

		else:
			return HttpResponse("invalid user...")



	return render(request, "care_login.html", {})

@login_required(login_url='/care/')
def change_password(request):
	if request.method == "POST":
		form = CareChangePasswordForm(request.POST)
		if form.is_valid():
			user = User.objects.get(username=request.user.username)
			data = user.check_password(form.cleaned_data['password1'])
			if data:
				user.set_password(form.cleaned_data['password2'])
				user.save()
			else:
				return HttpResponse('Old password did not match...')
	else:
		form = CareChangePasswordForm()

	return render(request, "care/care_change_password.html", {'form': form})


class CareDashboard(LoginRequiredMixin, ListView):
	model = Order
	template_name = "care/index.html"

	def get_context_data(self, *args, **kwargs):
		context = super(CareDashboard, self).get_context_data(*args, **kwargs)
		qs = self.get_queryset()
		order_count = qs.filter(status='delivered').count()
		orders = qs.filter(status='delivered')
		total_commission = 0.00
		for order in orders:
			total_commission += order.get_commission()

		qs1 = qs.filter(status='received')
		qs2 = qs.filter(status='dispatched')
		qs3 = qs.filter(status='intransist')

		query = qs1 | qs2 | qs3

		pending_order_count = query.count()
		total_pending_commission = 0.00
		for order in query.all():
			total_pending_commission += order.get_commission()

		context['total_pending_commission'] = total_pending_commission
		context['pending_order_count'] = pending_order_count
		context['order_count'] = order_count
		context['total_commission'] = total_commission
		return context

	def get_queryset(self, *args, **kwargs):
		qs = super(CareDashboard, self).get_queryset(*args, **kwargs)
		care_point_user = CarePointUserProfile.objects.filter(user=self.request.user)
		taluka = Taluka.objects.filter(user=care_point_user)
		pincodes = CarePointPincode.objects.filter(taluka=taluka)

		qs = self.model.objects.none()

		for pin in pincodes:
			ba = UserAddress.objects.filter(type='billing', postcode=pin)
			for i in ba:
				qs = qs | self.model.objects.filter(billing_address=i)
		return qs


class CareOrderListView(LoginRequiredMixin, ListView):
	model = Order
	template_name = "care/care_orders.html"

	def get_context_data(self, *args, **kwargs):
		context = super(CareOrderListView, self).get_context_data(*args, **kwargs)
		ORDER_STATUS_CHOICES = (
			('all', 'All'),
			('received', 'Received'),
			('dispatched', 'Dispatched'),
			('intransist', 'Intransist'),
			('delivered', 'Delivered'),
			('cancelled', 'Cancelled'),
		)
		context['status'] = ORDER_STATUS_CHOICES
		return context


	def get_queryset(self, *args, **kwargs):
		qs = super(CareOrderListView, self).get_queryset(*args, **kwargs)
		care_point_user = CarePointUserProfile.objects.filter(user=self.request.user)
		taluka = Taluka.objects.filter(user=care_point_user)
		pincodes = CarePointPincode.objects.filter(taluka=taluka)

		qs = self.model.objects.none()

		for pin in pincodes:
			ba = UserAddress.objects.filter(type='billing', postcode=pin)
			for i in ba:
				qs = qs | self.model.objects.filter(billing_address=i)
		query = self.request.GET.get("q")
		if query:
			qs = qs.filter(
					Q(status__icontains=query) |
					Q(payment__icontains=query) |
					Q(billing_address__postcode__icontains=query)|
					Q(order_id__icontains=query) |
					Q(billing_address__full_name__icontains=query)|
					Q(order_id__icontains=query) |
					Q(billing_address__mobile__icontains=query)|
					Q(order_total__icontains=query)
				)
		query2 = self.request.GET.get('status_selector')
		if query2 == "all":
			query2 = None
		if query2:
			qs = qs.filter(
					Q(status__icontains=query2)
				)
		query_from = self.request.GET.get('from')
		query_to = self.request.GET.get('to')
		if query_from and query_to:
			qs = qs.filter(
					Q(timestamp__range=[query_from, query_to])
				)
		return qs

class CareCommission(LoginRequiredMixin, ListView):
	model = Category
	template_name = "care/care_commission.html"


class CareWallet(LoginRequiredMixin, ListView):
	model = Order
	template_name = "care/care_wallet.html"

	def get_context_data(self, *args, **kwargs):
		context = super(CareWallet, self).get_context_data(*args, **kwargs)
		qs = self.get_queryset()
		order_count = qs.filter(status='delivered').count()
		orders = qs.filter(status='delivered')
		total_commission = 0.00
		for order in orders:
			total_commission += order.get_commission()

		from_date = mkFirstOfMonth(datetime.datetime.now())
		to_date = mkLastOfMonth(datetime.datetime.now())

		monthly_order_count = qs.filter(status='delivered', timestamp__range=[from_date, to_date]).count()
		monthly_orders = qs.filter(status='delivered', timestamp__range=[from_date, to_date])
		monthly_order_commission = 0.00
		for order in monthly_orders:
			monthly_order_commission += order.get_commission()

		m_total_commission = 0.00
		for order in monthly_orders:
			m_total_commission += order.get_commission()

		fdate = self.request.GET.get("from")
		tdate = self.request.GET.get("to")
		if fdate and tdate:
			m_total_commission = 0.00
			monthly_orders = qs.filter(status='delivered', timestamp__range=[fdate, tdate])
			for order in monthly_orders:
				m_total_commission += order.get_commission()


		context["m_total_commission"] = m_total_commission
		context["monthly_orders"] = monthly_orders
		context["monthly_order_count"] = monthly_order_count
		context["monthly_commission"] = monthly_order_commission
		context['order_count'] = order_count
		context['total_commission'] = total_commission
		return context

	def get_queryset(self, *args, **kwargs):
		qs = super(CareWallet, self).get_queryset(*args, **kwargs)
		care_point_user = CarePointUserProfile.objects.filter(user=self.request.user)
		taluka = Taluka.objects.filter(user=care_point_user)
		pincodes = CarePointPincode.objects.filter(taluka=taluka)

		qs = self.model.objects.none()

		for pin in pincodes:
			ba = UserAddress.objects.filter(type='billing', postcode=pin)
			for i in ba:
				qs = qs | self.model.objects.filter(billing_address=i)

		return qs




class CareFaqsListView(ListView):
	model = Faqs
	template_name = "care/care_faqs.html"


@login_required(login_url='/care/')
def care_contact(request):
	user_info = CarePointUserProfile.objects.filter(user=request.user)

	for i in user_info:
		if i.email:
			email = i.email
			name = i.get_full_name()
		else:
			email = "None"
			name = i.get_full_name()

	if not request.user.is_anonymous() and not request.user.is_superuser:
		if request.method == "POST":
			# email = 
			question = request.POST.get("que")
			message = "Query form " + name + " is \n" + question + "\n Reply to: " + email
			send_mail('Care Point Query', message, email, ['abhilash.shoffex@gmail.com'], fail_silently=False)
	return render(request, "care/care_contact.html", {})



@login_required(login_url='/care/')
def care_my_account(request):
	context = {}
	user = CarePointUserProfile.objects.get(user=request.user)
	bank_detail = CarePointBankDetail.objects.get(user=user)
	form = CarePointBankDetailForm(instance=bank_detail)

	# docs_img = CarePointDocuments.objects.get_or_create(user=user)
	bank_docs = CarePointDocuments.objects.get(user=user)
	docs = CarePointDocumentsForm(instance=bank_docs)

	context["care_user"] = user
	context["form"] = form
	context["docs"] = docs
	# context["docs_img"] = docs_img
	return render(request, "care/care_my_account.html", context)
	

@login_required(login_url='/care/')
def update_user_information(request):
	if request.method == "POST":
		firstname = request.POST.get('firstname')
		lastname = request.POST.get('lastname')
		email = request.POST.get('email')
		dob = request.POST.get('dob')
		mobile = request.POST.get('mobile_no')
		gender = request.POST.get('gender')
		pic = request.FILES.get('image')

		user = CarePointUserProfile.objects.get(user=request.user)
		user.firstname = firstname
		user.lastname = lastname
		user.email = email
		user.dob = dob
		user.mobile_no = mobile
		user.gender = gender
		user.profile_pic = pic
		user.save()
		
	return HttpResponseRedirect(reverse('care:care_my_account'))

@login_required(login_url='/care/')
def update_bank_detail_information(request):
	user = CarePointUserProfile.objects.get(user=request.user)
	care_bank = get_object_or_404(CarePointBankDetail, user=user)
	form = CarePointBankDetailForm(request.POST or None, instance=care_bank)
	if form.is_valid():
		form.save()
		messages.success(request, "bank Detail has been changed.")
	return HttpResponseRedirect(reverse('care:care_my_account'))

@login_required(login_url='/care/')
def upadate_bank_docs(request):
	user = CarePointUserProfile.objects.get(user=request.user)
	care_bank_doc = get_object_or_404(CarePointDocuments, user=user)
	form = CarePointDocumentsForm(request.POST or None, request.FILES, instance=care_bank_doc)
	if form.is_valid():
		form.save()
		messages.success(request, "bank Documents has been changed.")
	return HttpResponseRedirect(reverse('care:care_my_account'))


@login_required(login_url='/care/')	
def care_myArea(request):
	context = {}
	care_point_user = CarePointUserProfile.objects.filter(user=request.user)
	taluka = Taluka.objects.filter(user=care_point_user)
	pincode = CarePointPincode.objects.filter(taluka=taluka)
	context['taluka'] = taluka
	context['pincode'] = pincode
	return render(request, "care/care_myArea.html", context)


@login_required(login_url='/care/')
def care_query_send(request):
	return render(request, "care/care_query_send.html", {})

def get_token():
    intervals_no=random.randrange(1,10000)
    secret = 'MZXW633PN5XW6MZX'
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def care_forget_pass(request):
	if request.is_ajax():
		data = ''
		exist_mob = ''
		mobile = request.GET.get("mobile")
		print mobile
		if mobile:
			try:
				user_mob = CarePointUserProfile.objects.get(mobile_no=mobile)
				request.session['mobile'] = mobile
				token = get_token()
				print token
				msg_token = str(token)
				request.session['var'] = msg_token
				data = "yes"
			except:
				data = "no"
		else:
			data = "no"
		return JsonResponse({'data':data,})
	otp = request.POST.get("otp")

	if request.method == "POST":
		print request.session.get('var')
		mobile = request.POST.get("mobile")
		print mobile
		password = request.POST.get("reset_pass")
		if otp == request.session.get('var'):
			print "true"
			ex_user = CarePointUserProfile.objects.get(mobile_no=mobile)
			print "hello"
			ex_user.user.set_password(password)
			ex_user.user.save()
			messages.success(request, "Password updated successfully.")
			return HttpResponseRedirect("/care/")
		else:
			print "else"
			messages.error(request, "Incorrect verification code")
			return HttpResponseRedirect("/care/forget/")
	return render(request, 'care_forget_pass.html',{})


class CareOrderDetailView(DetailView):
	model = Order
	template_name = "care/care_order_detail.html"

	def get_context_data(self, *args, **kwargs):
		context = super(CareOrderDetailView, self).get_context_data(*args, **kwargs)
		instance = self.get_object()
		data = instance.cart.cartitem_set.all()
		context["items"] = data
		return context



