from django.conf.urls import url


from .views import signup, signup_mobile, login_user, user_account, order_history, user_settings

urlpatterns = [
    url(r'^signup/$', signup, name="signup" ),
    url(r'^login/$', login_user, name="login_user" ),
    url(r'^mobile/$', signup_mobile, name="signup_mobile" ),
    url(r'^personal/$', user_account, name="user_account" ),
    url(r'^order-history/$', order_history, name="order_history" ),
    url(r'^user-settings/$', user_settings, name="user_settings" ),
]