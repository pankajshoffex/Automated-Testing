from django.conf.urls import include, url
from UI import views
from .views import index, poi_list

urlpatterns = [
	url(r'^logo/$', views.index, name="index"),
	url(r'^map/$', views.poi_list, name="map"),
]