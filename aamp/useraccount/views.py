from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# Create your views here.

from products.models import Product
import urllib2
import urllib
import base64
import hmac, base64, struct, time
import hashlib, random, datetime
from .models import SignUp, HomePageSlider
from UI.models import UploadLogo, TopOffers, BottomOffers
from sms.models import SmsSetting, SmsHistory, SendSMS
from products.models import Category
from orders.models import Order


def index(request):
	context = {}
	slider = True
	image = HomePageSlider.objects.all().order_by("-id")
	products = Product.objects.all().order_by("?")[:20]
	offers = TopOffers.objects.all()
	bt_offer = BottomOffers.objects.all()

	demo = {}

	cat = Category.objects.all()
	for c in cat:
		if c.is_root_node():
			demo[c] = Product.objects.filter(categories__in=c.get_descendants(include_self=True)).order_by("?")[:6] 


	context['cat'] = demo
	context['bottom'] = bt_offer
	context['offers'] = offers
	context['slider'] = slider
	context['himage'] = image
	context['products'] = products
	return render(request, "home.html", context)


def login_user(request):
	if not request.user.is_authenticated():
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					print request.GET.get('next')
					if request.GET.get('next') is not None or request.GET.get('next') != 'None':
						print request.GET.get('next')
						return HttpResponseRedirect(request.GET.get('next'))
					else:
						print request.GET.get('next')
						return HttpResponseRedirect("/")
				else:
					messages.error(request, "Your account is not active.")
			else:
				messages.error(request, "Your Username and/or Password were incorrect")
	else:
		return HttpResponseRedirect('/')

	return render(request, "account/login.html", {'next': request.GET.get('next') })


def get_token():
    intervals_no=random.randrange(1,10000)
    secret = 'MZXW633PN5XW6MZX'
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = ord(h[19]) & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def signup_mobile(request):
	if request.is_ajax():
		data = ""
		cnt = ""
		mobile = request.GET.get('mobile')
		if mobile:
			cnt = SignUp.objects.filter(mobile_no=mobile).count()
			if cnt > 0:
				cnt = "yes"
				data = "no"
			else:
				request.session['mobile'] = mobile
				token = get_token()
				print token
				msg_token = str(token)
				request.session['var'] = msg_token
				obj = SendSMS()
				new_msg = "Dear %s ,your OTP is: %s  www.shoffex.com" %(mobile, msg_token)
				obj.sendsms(new_msg,mobile)
				data = "yes"
				cnt = "no"
		else:
			data = "no"

		return JsonResponse({'data': data, 'count': cnt})

	# return render(request, "account/mobile_no.html", {'form': form})

def signup(request):
	print request.POST.get('next')
	request.session.set_expiry(300)
	if request.is_ajax():
		data = ""
		token = request.GET.get('data')
		if token == request.session.get('var'):
			data = "yes"
		else:
			data = "no"

		return JsonResponse({'token': data})

	if request.method == 'POST':
		mobile = request.POST.get('mobile_no')
		password = request.POST.get('sign_password')
		otp = request.POST.get('otp')
		if otp == request.session.get('var'):
			new_user = User.objects.create_user(username=mobile)
			new_user.set_password(password)
			new_user.save()
			
			if new_user:
				data = SignUp(user=new_user)
				data.mobile_no = mobile
				data.save()
				obj = SendSMS()
				msg = "Dear Customer your account in Shoffex.com is successfully created. Your username:" + mobile + ". Cheers!!!"
				result = obj.sendsms(msg, numbers=mobile)
				if result:
					SmsHistory.objects.create(
						number=data.mobile_no,
						recipient=new_user.get_full_name(),
						sms_subject="New Account Created", 
						sms_text=msg,
						sms_type = "New User"
						)
				user = authenticate(username=mobile, password=password)
				if user is not None:
					if user.is_active:
						login(request, user)
						if request.POST.get('next') is not None and request.POST.get('next') != 'None':
							return HttpResponseRedirect(request.POST.get('next'))
						else:
							return HttpResponseRedirect("/")
		else:
			messages.error(request, "Incorrect verification code")
			return HttpResponseRedirect("/accounts/login")

	return HttpResponseRedirect("account:login")


@login_required(login_url='/accounts/login/')
def user_account(request):
	return render(request, 'account/User_Account.html', {})


@login_required
def order_tracking(request):
	context = {}	
	
	order = Order.objects.filter(user=request.user)
	count = order.count()
	context['order'] = order
	context['count'] = range(0, count)

	return render(request, "account/order_tracking.html", context)

@login_required(login_url='/accounts/login/')
def user_settings(request):
	context = {}
	data = SignUp.objects.filter(user=request.user)
	if data:
		for mobile in data:
			context['mobile_no'] = mobile.mobile_no
	else:
		context['mobile_no'] = "--"

	if request.is_ajax():
		name = request.GET.get('name')
		email = request.GET.get('email')
		mobile = request.GET.get('mobile')
		password = request.GET.get('password')
		new_password = request.GET.get('new_password')
		token = "False"
		user = User.objects.get(username=request.user.username)
		if name:
			user.first_name = name
			user.save()
			token = "True"
			return JsonResponse({"data": token, "name": name})

		elif email:
			user.email = email
			user.save()
			token = "True"
			return JsonResponse({"data": token, "email": email})

		elif mobile:
			up, mp = SignUp.objects.get_or_create(user=user)
			if not mp:
				up.mobile_no = mobile
				up.save()
				token = "True"
				print "success"
			return JsonResponse({"data": token, "mobile": mobile})

		elif password:
			if user.check_password(password):
				user.set_password(new_password)
				user.save()
				token = "True"
			return JsonResponse({"data": token, "new_password": new_password})

		else:
			token = "False"
		return JsonResponse({"data": token})
	return render(request, 'account/user_settings.html', context)


### Forget Password ##########

def forget_pass(request):
	
	return render(request, "forget_pass.html",{})

def pass_reset(request):
	if request.is_ajax():
		data = ""
		exist_mob = ""
		# mobile = request.POST.get("mobile")
		mobile = request.GET.get('mobile')
		print mobile
		otp = request.POST.get("otp")
		if mobile:
			try:
				exist_mob = SignUp.objects.get(mobile_no=mobile)
				request.session['mobile2'] = mobile
				token = get_token()
				print token
				msg_token = str(token)
				request.session['var2'] = msg_token
				data = "yes"
			except:
				data = "no"
		else:
			data = "no"
	return JsonResponse({'data': data,})

def replace_pass(request):
	print request.POST.get('next')
	otp = request.POST.get('otp')
	if request.is_ajax():
		data = ""
		token = request.GET.get('data')
		if token == request.session.get('var2'):
			data = "yes"
		else:
			data = "no"

		return JsonResponse({'token': data})

	if request.method == 'POST':
		mobile = request.POST.get('mobile_no')
		password = request.POST.get('reset_password')
		if otp == request.session.get('var2'):
			try:
				exist_user = User.objects.get(username=mobile)
			except:
				messages.error(request, "Account does not exist...")
				return HttpResponseRedirect("/accounts/password/")
			exist_user.set_password(password)
			exist_user.save()
			messages.success(request, "Password updated successfully.")
		else:
			messages.error(request, "Incorrect verification code")
			return HttpResponseRedirect("/accounts/password")
	return HttpResponseRedirect("/")
	