from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# Create your views here.

from products.models import Product
from .forms import SignUpForm, MobileNoForm
import urllib2
import urllib
import base64
import hmac, base64, struct, time
import hashlib, random, datetime
from .models import SignUp, HomePageSlider
from UI.models import UploadLogo


def index(request):
	context = {}
	slider = True
	image = HomePageSlider.objects.all().order_by("-id")
	logo = ""
	products = Product.objects.all().order_by("?")[:20]

	logo_data = UploadLogo.objects.all()
	for i in logo_data:
		logo1 = i
		logo = "media/" + str(logo1)

	context['slider'] = slider
	context['himage'] = image
	context['products'] = products
	context['logo'] = logo 
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


def sendSMS(uname, hashCode, numbers, sender, message):
    #data =  urllib.urlencode({'username': sotari.biz@gmail.com, 'hash': hashCode, 'numbers': numbers, 'message' : message, 'sender': sender})
    data =  urllib.urlencode({'username': uname, 'hash': hashCode, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib2.Request("http://api.textlocal.in/send/?")
    f = urllib2.urlopen(request, data)
    fr = f.read()
    return(fr)

def signup_mobile(request):
	if request.method == 'POST':
		form = MobileNoForm(request.POST)
		if form.is_valid():
			mobile = form.cleaned_data["mobile"]
			data = SignUp.objects.filter(mobile_no=mobile).count()
			if data > 0:
				messages.error(request, 'This Mobile No is already exist.')
				return HttpResponseRedirect(reverse('account:signup_mobile'))
			else:
				request.session['mobile'] = mobile
				token = get_token()
				msg_token = str(token)
				request.session['var'] = msg_token
				# sendSMS('sotari.biz@gmail.com', 'da1e1331d30c4dcff5a4780b52fa9fb327764bb1', mobile,'TXTLCL', msg_token)
			return HttpResponseRedirect("/accounts/signup/")
	else:
		form = MobileNoForm()
	return render(request, "account/mobile_no.html", {'form': form})

def signup(request):
	print request.session.get('next_url')
	if request.is_ajax():
		data = ""
		token = request.GET.get('data')
		if token == request.session.get('var'):
			data = "yes"
		else:
			data = "no"

		return JsonResponse({'token': data})

	if request.method == 'POST':
		form = SignUpForm(request, request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['mobile_no']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					print request.session.get('next_url')
					if request.session.get('next_url') is not None or request.session.get('next_url') != 'None':
						return HttpResponseRedirect("/checkout/")
					else:
						return HttpResponseRedirect("/")
	else:
		form = SignUpForm(request)

	mobile = request.session.get('mobile')
	print request.session.get('var')
	if not request.session.get('var'):
		if request.GET.get('next') is not None:
			url = "account:signup_mobile"
			request.session['next_url'] = request.GET.get('next')
		else:
			url = "account:signup_mobile"
		return HttpResponseRedirect(reverse(url))
	return render(request, 'account/signup.html', {'form': form, 'mobile': mobile})

@login_required(login_url='/accounts/login/')
def user_account(request):
	return render(request, 'account/User_Account.html', {})
	
@login_required(login_url='/accounts/login/')
def order_history(request):
	return render(request, 'account/order_history.html', {})

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