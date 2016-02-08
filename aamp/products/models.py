from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.utils.text import slugify


# Create your models here.


class ProductQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(active=True)


class ProductManager(models.Manager):
	def get_queryset(self):
		return ProductQuerySet(self.model, using=self._db)

	def all(self, *args, **kwargs):
		return self.get_queryset().active()

	def get_related(self, instance):
		products_one = self.get_queryset().filter(categories__in=instance.categories.all())
		products_two = self.get_queryset().filter(default=instance.default)
		qs = (products_one | products_two).exclude(id=instance.id).distinct()
		return qs


class Product(models.Model):
	title = models.CharField(max_length=120)
	short_description = models.TextField(blank=True, null=True)
	long_description = models.TextField(blank=True, null=True)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	categories = models.ManyToManyField('Category')
	color = models.ManyToManyField('ProductColor', blank=True)
	shoessizes = models.ManyToManyField('ShoesSize', blank=True)
	shirtsizes = models.ManyToManyField('ShirtSize', blank=True)
	default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)
	active = models.BooleanField(default=True)

	objects = ProductManager()

	class Meta:
		ordering = ["-title"]

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("products:product_detail", kwargs={"pk": self.pk})

	def get_image_url(self): 
		img = self.productimage_set.first()
		if img:
			return img.image.url
		return img # None



class Variation(models.Model):
	product = models.ForeignKey(Product)
	title = models.CharField(max_length=120)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
	active = models.BooleanField(default=True)
	inventory = models.IntegerField(null=True, blank=True)

	def __unicode__(self):
		return self.title

	def get_price(self):
		if self.sale_price is not None:
			return self.sale_price
		else:
			return self.price

	def get_absolute_url(self):
		return self.product.get_absolute_url()

	def get_html_price(self):
		if self.sale_price is not None:
			html_text = "<span class='sale_price'>%s</span> <span class='og-price'>%s</span>" %(self.sale_price, self.price)
		else:
			html_text = "<span class='price'>%s</span>" %(self.price)
		return mark_safe(html_text)



def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
	product = instance
	variations = product.variation_set.all()
	if variations.count() == 0:
		new_var = Variation()
		new_var.product = product
		new_var.title = "Default"
		new_var.price = product.price
		new_var.save()


post_save.connect(product_post_saved_receiver, sender=Product)


def product_image_upload_to(instance, filename):
	title = instance.product.title
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extention)
	return "products/%s/%s" %(slug, new_filename)


class ProductImage(models.Model):
	product = models.ForeignKey(Product)
	image = models.ImageField(
		upload_to=product_image_upload_to,
		height_field="height_field", 
		width_field="width_field")
	height_field = models.IntegerField(default=300)
	width_field = models.IntegerField(default=300)

	def __unicode__(self):
		return self.product.title


class Category(models.Model):
	title = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(unique=True)
	description = models.TextField(null=True, blank=True)
	active = models.BooleanField(default=True)
	timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("categories:category_detail", kwargs={"slug": self.slug})



class ProductColor(models.Model):
	title = models.CharField(max_length=120)
	active = models.BooleanField(default=True, blank=True)

	def __unicode__(self):
		return self.title


class ShoesSize(models.Model):
	title = models.CharField(max_length=120)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title

class ShirtSize(models.Model):
	title = models.CharField(max_length=120)
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title



