from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.safestring import mark_safe

# Register your models here.
from mptt.admin import DraggableMPTTAdmin
from .models import (
		Product, 
		Variation, 
		ProductImage, 
		Category, 
		ProductColor,
		ShoesSize,
		ShirtSize,
		ProductRating,
		Availability,
		Whishlist,
	)


class ProductImageInline(admin.TabularInline):
	model = ProductImage
	fields = ('image', 'render_image',)
	readonly_fields = ('render_image',)
	extra = 0
	min_num = 1
	max_num = 4


	def render_image(self, obj):
		return mark_safe("""<img src="%s" width="100" height="100" />""" % obj.image.url)



class VariationInline(admin.TabularInline):
	model = Variation
	extra = 0

class ProductResource(resources.ModelResource):

	class Meta:
		model = Product
		skip_unchanged = True
		report_skipped = False
		exclude = ('long_description',)


class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	change_form_template = "admin_copies/editor/change_form.html"
	list_display = ['__unicode__', 'price','active','admin_thumbnail',]
	list_filter = ('categories',)
	search_fields = ['title', 'price', 'sale_price', 'quantity']
	
	inlines = [
		VariationInline,
		ProductImageInline,
	]
	fieldsets = (
		('Product Name', {
			'fields': (('title', 'quantity', 'active'),),
		}),
		('Product Price', {
			'fields': (('price', 'sale_price', 'single_shipping'),),
		}),
		('Product Description', {
			'classes': ('collapse',),
			'fields': ('short_description', 'long_description',),
		}),
		('Product color(s)', {
			'classes': ('collapse',),
			'fields': ('color',),
		}),
		('Product Size(s)', {
			'classes': ('collapse',),
			'fields': (('shoessizes', 'shirtsizes'),),
		}),
		('Association', {
			'classes': ('collapse',),
			'fields': ('categories',),
		}),
		('Search Engine Optimization', {
			'classes': ('collapse',),
			'fields': (('meta_keywords', 'meta_description'), ),
		}),
	)
	resource_class = ProductResource

	class Meta:
		model = Product


class ProductRatingAdmin(admin.ModelAdmin):
	list_display = ['name', 'title', 'rate']


class WhishlistAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'whishlist_date']

# class ProductAvailability(resources.ModelResource):

# 	class Meta:
# 		model = Availability
# 		skip_unchanged = True
# 		report_skipped = False
# 		exclude = ('id')


class AvailabilityAdmin(ImportExportModelAdmin, admin.ModelAdmin):
	list_display = ['__unicode__', 'location',]
	class Meta:
		model = Availability

admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductColor)
admin.site.register(ShoesSize)
admin.site.register(ShirtSize)
admin.site.register(ProductImage)
admin.site.register(Whishlist)
admin.site.register(ProductRating, ProductRatingAdmin)
admin.site.register(Category, 
	DraggableMPTTAdmin,
	list_display=(
		'tree_actions',
		'indented_title',
		# ...more fields if you feel like it...
	),
	list_display_links=(
		'indented_title',
	),)

