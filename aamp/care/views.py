from django.shortcuts import render

# Create your views here.


def index(request):
	return render(request, "care/index.html", {})


def care_orders(request):
	return render(request, "care/care_orders.html", {})

def care_commission(request):
	return render(request, "care/care_commission.html", {})

def care_wallet(request):
	return render(request, "care/care_wallet.html", {})

