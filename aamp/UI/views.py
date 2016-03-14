from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from UI.models import UploadLogo, SitePage


def index(request):
	logo_data = UploadLogo.objects.all()
	for i in logo_data:
		logo = i
		print i
	return render(request, "home.html", {"logo":logo})

def info(request):
	id = request.GET["id"]
	pages = SitePage.objects.active().filter(id=id)
	return render(request,"info.html",{"pages" : pages})