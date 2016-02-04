from django.contrib import admin

# Register your models here.
from .models import SignUp, HomePageSlider


admin.site.register(HomePageSlider)
admin.site.register(SignUp)


