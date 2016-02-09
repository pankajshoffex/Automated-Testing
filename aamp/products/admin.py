from django.contrib import admin
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
	extra = 0
	min_num = 1
	max_num = 4

class VariationInline(admin.TabularInline):
	model = Variation
	extra = 0

class ProductAdmin(admin.ModelAdmin):
    change_form_template = "admin_copies/editor/change_form.html"
    list_display = ['__unicode__', 'price', 'active']
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
    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductColor)
# admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(ShoesSize)
admin.site.register(ShirtSize)
admin.site.register(ProductImage)

