from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from UI.models import UploadLogo, SitePage, PointOfInterest


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

def poi_list(request):
    pois = PointOfInterest.objects.all()
    return render(request, 'poi_list.html', {'pois': pois})