from django.contrib.sitemaps import Sitemap
from products.models import Product, Category
from django.core.urlresolvers import reverse
from datetime import datetime

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    
    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return '/Product/info/%d' % obj.id

    def lastmod(self, obj):
        return datetime.now()

class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return '/category/info/%d' % obj.id

    def lastmod(self, obj):
        return datetime.now()

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return datetime.now()