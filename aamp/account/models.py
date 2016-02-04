from __future__ import unicode_literals
from django.utils.text import slugify
from django.db import models



class SignUp(models.Model):
	mobile_no = models.CharField(max_length=10, unique=True)
	password = models.CharField(max_length=50)

	def __unicode__(self):  # __str__ python 3
		return self.mobile_no

def image_upload_to(instance, filename):
	title = instance.title
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s.%s" %(instance.id, file_extention)
	return "imageslider/%s/%s" %(slug, new_filename)


class HomePageSlider(models.Model):
	title = models.CharField(max_length=120)
	image = models.ImageField(upload_to=image_upload_to)
	url = models.URLField()
	active = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title