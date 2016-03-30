from django.shortcuts import render

# Create your views here.


def index(request):
	return render(request, "care_login.html", {})

def care_dashboard(request):
	return render(request, "care/index.html", {})

def care_orders(request):
	return render(request, "care/care_orders.html", {})

def care_commission(request):
	return render(request, "care/care_commission.html", {})

def care_wallet(request):
	return render(request, "care/care_wallet.html", {})

def care_faqs(request):
	return render(request, "care/care_faqs.html", {})

def care_contact(request):
	return render(request, "care/care_contact.html", {})

def care_my_account(request):
	return render(request, "care/care_my_account.html", {})
	
def care_myArea(request):
	return render(request, "care/care_myArea.html", {})

