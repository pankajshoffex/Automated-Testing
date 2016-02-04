from django.conf.urls import url


from .views import signup, signup_mobile

urlpatterns = [
    url(r'^signup/$', signup, name="signup" ),
    url(r'^mobile/$', signup_mobile, name="signup_mobile" ),
]