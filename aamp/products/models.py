from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from useraccount.models import SignUp

# Create your models here.
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField


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
		qs = (products_one).exclude(id=instance.id).distinct()
		return qs


class Product(models.Model):
	title = models.CharField(max_length=120)
	slug = models.SlugField(max_length=120, blank=True)
	short_description = models.TextField(blank=True, null=True)
	long_description = models.TextField(blank=True, null=True)
	quantity = models.PositiveIntegerField(blank=True, null=True)
	price = models.DecimalField(decimal_places=2, max_digits=20)
	sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
	categories = TreeManyToManyField('Category')
	color = models.ManyToManyField('ProductColor', blank=True)
	shoessizes = models.ManyToManyField('ShoesSize', blank=True)
	shirtsizes = models.ManyToManyField('ShirtSize', blank=True)
	active = models.BooleanField(default=True)
	meta_keywords = models.CharField(max_length=250, blank=True, help_text="Maximum keywords should be 10 and seperate by comma")
	meta_description = models.CharField(max_length=160, blank=True, help_text="Description should be within 160 characters.")
	single_shipping = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
	objects = ProductManager()

	class Meta:
		ordering = ["-title"]

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("products:product_detail", kwargs={"slug": self.slug})

	def get_image_url(self): 
		img = self.productimage_set.first()
		if img:
			return img.image.url
		return img # None

	def save(self, *args, **kwargs):
		super(Product, self).save(*args, **kwargs)
		if self.price:
			slug = slugify(self.title)
			self.slug = "%s-%s-%s" %(slug, int(self.price), self.pk)
		else:
			slug = slugify(self.title)
			self.slug = "%s-%s-%s" %(slug, self.pk)
		super(Product, self).save(*args, **kwargs)

	def admin_thumbnail(self):
		img = self.productimage_set.first()
		
		
		if img:
			img2 = mark_safe(u'<img src="' + str(img.image.url) +'" width="100" height="100" />')
			return img2
		return img


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

	def add_to_cart(self):
		return "%s?item=%s&qty=1" %(reverse("cart"), self.id)

	def remove_from_cart(self):
		return "%s?item=%s&qty=1&delete=True" %(reverse("cart"), self.id)

	def get_title(self):
		return "%s - %s" %(self.product.title, self.title)




def product_post_saved_receiver(sender, instance, created, *args, **kwargs):
	product = instance
	variations = product.variation_set.all()
	if variations.count() == 0:
		new_var = Variation()
		new_var.product = product
		new_var.title = "Default"
		new_var.price = product.price
		new_var.sale_price = product.sale_price
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

	def admin_thumbnail(self):
		return self.product.admin_thumbnail()


class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    image = models.ImageField(upload_to='categories', blank=True, null=True)
    slug = models.SlugField()

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
    	return self.name

    def save(self, *args, **kwargs):
    	super(Category, self).save(*args, **kwargs)
    	slug = slugify(self.name)
    	self.slug = "%s-%s" %(slug, self.pk)
    	super(Category, self).save(*args, **kwargs)	


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


class ProductRating(models.Model):
	product = models.ForeignKey(Product)
	user = models.ForeignKey(SignUp)
	rate = models.PositiveIntegerField()
	title = models.CharField(max_length=120)
	desc = models.TextField()
	name = models.CharField(max_length=50)


	def __unicode__(self):
		return self.title

