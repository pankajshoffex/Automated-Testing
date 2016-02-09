from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
# Register your models here.
from .models import SignUp, HomePageSlider


class MobileInline(admin.TabularInline):
	model = SignUp
	can_delete = False
	max_num = 1
	fk_name = 'user'
	verbose_name_plural = _('User Mobile')

class UserAdmin(UserAdmin):
	inlines = (MobileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(HomePageSlider)


