from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
# Create your models here.

class SitePageManager(models.Manager):
	def active(self, *args, **kwargs):
		return super(SitePageManager, self).filter(show_on_page=True)

def logo_image_upload_to(instance, filename):
	title = "logo"
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extention)
	return "products/%s/%s" %(slug, new_filename)


class UploadLogo(models.Model):
	logo = models.ImageField(upload_to=logo_image_upload_to,)
	
	def __unicode__(self):
		return unicode(self.logo)

def top_offers_image_upload_to(instance, filename):
	title = "offer"
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extention)
	return "offers/%s/%s" %(slug, new_filename)


class TopOffers(models.Model):
	title = models.CharField(max_length=120)
	offer = models.ImageField(upload_to=top_offers_image_upload_to, help_text='for better display upload 270px width and 190px height image')
	url = models.URLField()
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title

class BottomOffers(models.Model):
	title = models.CharField(max_length=120)
	offer = models.ImageField(upload_to=top_offers_image_upload_to, help_text='for better display upload 570px width and 180px height image')
	url = models.URLField()
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title


class SitePage(models.Model):
	page_name = models.CharField(max_length=120)
	page_type = models.CharField(max_length=120,choices=[('ContentBased', 'Content Based'), ('RedirectToLink', 'Redirect To Link')],default='ContentBased')
	url = models.URLField(blank=True)
	content = models.TextField(max_length=10000, blank=True)	
	date = models.DateTimeField(auto_now_add=True, auto_now=False)
	modified = models.DateTimeField(auto_now_add=False, auto_now=True)
	show_on_page = models.BooleanField(default=True)

	objects = SitePageManager()

	def __unicode__(self):
		return self.page_name

	def save(self, *args, **kwargs):
		if not self.date:
			self.date = timezone.now()

		self.modified = timezone.now()
		return super(SitePage, self).save(*args, **kwargs)