from django.contrib import admin

from .models import UploadLogo, TopOffers, BottomOffers, SitePage


class TopOffersAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')

class BottomOffersAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')

class SitePageAdmin(admin.ModelAdmin):
	change_form_template = "admin_copies/editor/change_form.html"
	list_display = ["show_on_page","page_name", "page_type", "date", "modified"]

	class Meta:
		model = SitePage

	class Media:
		js = (
			'js/sitepageadmin.js',       
		)
admin.site.register(SitePage, SitePageAdmin)
admin.site.register(UploadLogo)
admin.site.register(TopOffers, TopOffersAdmin)
admin.site.register(BottomOffers, BottomOffersAdmin)