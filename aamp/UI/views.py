from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from UI.models import UploadLogo, PointOfInterest


def index(request):
	logo_data = UploadLogo.objects.all()
	for i in logo_data:
		logo = i
		print i
	return render(request, "home.html", {"logo":logo})

def poi_list(request):
    pois = PointOfInterest.objects.all()
    return render(request, 'poi_list.html', {'pois': pois})
