from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
# Create your views here.

from products.models import Product
from .forms import SignUpForm, MobileNoForm
import urllib2
import urllib
import base64
import hmac, base64, struct, time
import hashlib, random, datetime
from .models import SignUp, HomePageSlider



def index(request):
	context = {}
	slider = True
	image = HomePageSlider.objects.all().order_by("-id")

	products = Product.objects.all().order_by("?")[:20]

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
					print "hello"
					if request.GET.get('next') is not None and request.GET.get('next') != 'None':
						data = base64.urlsafe_b64decode(str(request.GET.get('next')))
						print data
						return HttpResponseRedirect(data)
					else:
						return HttpResponseRedirect('/')
					# if request.POST.get('next') is not None and request.POST.get('next') != 'None':
					# 	return HttpResponseRedirect(request.POST.get('next'))
				else:
					messages.error(request, "Your account is not active.")
			else:
				messages.error(request, "Your Username and/or Password were incorrect")
	else:
		return HttpResponseRedirect('/')

	return render(request, "account/login.html", {})


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
				sendSMS('sotari.biz@gmail.com', 'da1e1331d30c4dcff5a4780b52fa9fb327764bb1', mobile,'TXTLCL', msg_token)
			return HttpResponseRedirect("/account/signup/")
	else:
		form = MobileNoForm()

	return render(request, "account/mobile_no.html", {'form': form})

def signup(request):
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
	else:
		form = SignUpForm(request)

	mobile = request.session.get('mobile')
	print request.session.get('var')
	if not request.session.get('var'):
		return HttpResponseRedirect(reverse('account:signup_mobile'))
	return render(request, 'account/signup.html', {'form': form, 'mobile': mobile})


