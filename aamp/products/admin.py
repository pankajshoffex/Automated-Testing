from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils.safestring import mark_safe
# Register your models here.
from .models import (
        Product, 
        Variation, 
        ProductImage, 
        Category, 
        ProductColor,
        ShoesSize,
        ShirtSize,
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
    
    inlines = [
        VariationInline,
        ProductImageInline,
    ]
    fieldsets = (
        ('Product Name', {
            'fields': (('title', 'active'),),
        }),
        ('Product Price', {
            'fields': ('price',),
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
            'fields': (('categories', 'default'), ),
        }),
    )
    resource_class = ProductResource

    class Meta:
        model = Product




# class ProductAdmin(ImportExportModelAdmin):
#     resource_class = ProductResource
#     pass 

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductColor)
# admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(ShoesSize)
admin.site.register(ShirtSize)
admin.site.register(ProductImage)

