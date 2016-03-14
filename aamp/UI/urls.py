from django.conf.urls import include, url
from UI import views
from .views import index, info

urlpatterns = [
	url(r'^logo/$', views.index, name="index"),
	url(r'^info/$', info, name="info"),
]