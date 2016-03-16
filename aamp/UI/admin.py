from django.contrib import admin
from .models import UploadLogo, TopOffers, BottomOffers, SitePage, PointOfInterest


class TopOffersAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')

class BottomOffersAdmin(admin.ModelAdmin):
    list_display = ('title', 'active')

class SitePageAdmin(admin.ModelAdmin):
	change_form_template = "admin_copies/editor/change_form.html"
	list_display = ["page_name", "page_type", "date", "modified",'show_on_page','is_it_location']

	class Meta:
		model = SitePage

	class Media:
		js = (
			'js/sitepageadmin.js',       
		)

class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'position','position_map',)

    def position_map(self, instance):
        if instance.position is not None:
            return '<img src="http://maps.googleapis.com/maps/api/staticmap?center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'latitude': instance.position.latitude,
                'longitude': instance.position.longitude,
                'zoom': 15,
                'width': 80,
                'height': 80,
                'scale': 2
            }
    position_map.allow_tags = True



admin.site.register(PointOfInterest, PointOfInterestAdmin)
admin.site.register(SitePage, SitePageAdmin)
admin.site.register(UploadLogo)
admin.site.register(TopOffers, TopOffersAdmin)
admin.site.register(BottomOffers, BottomOffersAdmin)