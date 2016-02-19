from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from UI.models import UploadLogo


def index(request):
	logo_data = UploadLogo.objects.all()
	for i in logo_data:
		logo = i
		print i
	return render(request, "home.html", {"logo":logo})
