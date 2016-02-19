from django.conf.urls import include, url
from UI import views
from .views import index

urlpatterns = [
	url(r'^logo/$', views.index, name="index"),
]