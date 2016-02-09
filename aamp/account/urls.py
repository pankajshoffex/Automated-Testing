from django.conf.urls import url


from .views import signup, signup_mobile, login_user

urlpatterns = [
    url(r'^signup/$', signup, name="signup" ),
    url(r'^login/$', login_user, name="login_user" ),
    url(r'^mobile/$', signup_mobile, name="signup_mobile" ),
]