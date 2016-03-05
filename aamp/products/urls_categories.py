from django.conf.urls import include, url

from .views import show_demo

urlpatterns = [
	url(r'^xyz/$', show_demo, name="xyz"),
]