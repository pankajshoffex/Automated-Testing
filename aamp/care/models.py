from __future__ import unicode_literals

from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.



def user_pic_upload_to(instance, filename):
	title = instance.user.username
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extention)
	return "CarePoint/%s/%s" %(slug, new_filename)

GENDER_TYPE = (
	('male', 'Male'),
	('female', 'Female'),
	)

class CarePointUserProfile(models.Model):
	user = models.OneToOneField(User)
	firstname = models.CharField(max_length=50, blank=True, null=True)
	lastname = models.CharField(max_length=50, blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	mobile_no = models.CharField(max_length=10, blank=True, null=True)
	dob = models.DateField(blank=True, null=True)
	gender = models.CharField(max_length=20, choices=GENDER_TYPE, default='male', blank=True, null=True)
	profile_pic = models.ImageField(upload_to=user_pic_upload_to, blank=True, null=True)
	is_care = models.BooleanField(default=False)


	def __unicode__(self):
		return self.firstname

	def get_full_name(self):
		return "%s %s" %(self.firstname, self.lastname)

def care_point_post_saved_receiver(sender, instance, created, *args, **kwargs):
	user = instance
	bank_detail = CarePointBankDetail.objects.get_or_create(user=user)
	bank_docs = CarePointDocuments.objects.get_or_create(user=user)


post_save.connect(care_point_post_saved_receiver, sender=CarePointUserProfile)

ACC_TYPE = (
	('saving', 'Saving'),
	('current', 'Current'),
	)

class CarePointBankDetail(models.Model):
	user = models.OneToOneField(CarePointUserProfile)
	pan_no = models.CharField(max_length=50)
	vat_no = models.CharField(max_length=50)
	benifit_name = models.CharField(max_length=50)
	acc_no = models.CharField(max_length=50)
	neft = models.CharField(max_length=50)
	ifsc_code = models.CharField(max_length=50)
	acc_type = models.CharField(max_length=50, choices=ACC_TYPE, default='saving')
	bank_name = models.CharField(max_length=50)
	branch = models.CharField(max_length=50)

	def __unicode__(self):
		return self.user.firstname

def user_doc_upload_to(instance, filename):
	title = instance.user.firstname
	slug = slugify(title)
	file_extention = filename.split(".")[1]
	new_filename = "%s-%s.%s" %(slug, instance.id, file_extention)
	return "CarePoint/Docs/%s/%s" %(slug, new_filename)

class CarePointDocuments(models.Model):
	user = models.OneToOneField(CarePointUserProfile)
	id_proof = models.FileField(upload_to=user_doc_upload_to, blank=True, null=True)
	pan_card = models.FileField(upload_to=user_doc_upload_to, blank=True, null=True)
	bank_pass = models.FileField(upload_to=user_doc_upload_to, blank=True, null=True)

	def __unicode__(self):
		return self.user.firstname

class Taluka(models.Model):
	user = models.OneToOneField(CarePointUserProfile)
	taluka = models.CharField(max_length=100)

	def __unicode__(self):
		return self.taluka

class CarePointPincode(models.Model):
	taluka = models.ForeignKey(Taluka)
	pincode = models.CharField(max_length=6, unique=True)
	location = models.CharField(max_length=120, blank=True, null=True)

	def __unicode__(self):
		return self.pincode

class Faqs(models.Model):
	question = models.CharField(max_length=200, blank=True, null=True)
	answer = models.TextField(max_length=200, blank=True, null=True)
	pub_date = models.DateTimeField('date_published')

	def __unicode__(self):
		return self.question

	class Meta:
		ordering = ['-pub_date']