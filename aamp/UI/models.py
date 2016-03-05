from __future__ import unicode_literals
from geoposition.fields import GeopositionField
from django.db import models
from django.utils.text import slugify
# Create your models here.

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

class PointOfInterest(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=10)
    position = GeopositionField(blank=True)

    class Meta:
        verbose_name_plural = 'points of interest'