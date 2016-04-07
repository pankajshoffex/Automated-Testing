from __future__ import unicode_literals

from django.db import models
import urllib2
import urllib
from django.contrib.auth.models import User
from useraccount.models import SignUp
# Create your models here.
class SendSMS(models.Model):
	user = models.ForeignKey(SignUp)
	date1 = models.DateTimeField(auto_now_add=True, auto_now=False)
	sms_subject = models.CharField(max_length=80)
	sms_text = models.CharField(max_length=512)

	def __unicode__(self):
		return self.user.mobile_no

	def sendsms(self,message, numbers):
		sms_config = SmsSetting.objects.get()
		data =  urllib.urlencode({'username': sms_config.sms_username, 'hash': sms_config.sms_hashcode, 'numbers': numbers,
			'message' : message, 'sender': sms_config.sms_sender})
		data = data.encode('utf-8')
		request = urllib2.Request(sms_config.sms_api)
		f = urllib2.urlopen(request, data)
		fr = f.read()
		return(fr)

class SmsHistory(models.Model):
	number = models.CharField(max_length=10)
	recipient = models.CharField(max_length=50)
	sms_subject = models.CharField(max_length=80)
	sms_text = models.CharField(max_length=512)
	sms_type = models.CharField(max_length=32)
	date = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.number

class SmsSetting(models.Model):
	sms_username = models.CharField(max_length=120)
	sms_hashcode = models.CharField(max_length=200)
	sms_sender = models.CharField(max_length=120)
	sms_api = models.CharField(max_length=200)

	def __unicode__(self):
		return self.sms_username

class SmsMarketing(models.Model):
	date = models.DateTimeField(auto_now_add=True, auto_now=False)
	sms_subject = models.CharField(max_length=80)
	sms_text = models.CharField(max_length=512)

	def __unicode__(self):
		return self.sms_subject

class BulkSms(models.Model):
	name = models.CharField(max_length=30)
	numbers = models.CharField(max_length=30)
	date = models.DateField(auto_now_add=True, auto_now=False)
	def __unicode__(self):
		return self.numbers

class BulkSmsHistory(models.Model):
	number = models.CharField(max_length=10)
	recipient = models.CharField(max_length=50)
	sms_subject = models.CharField(max_length=80)
	sms_text = models.CharField(max_length=512)
	sms_type = models.CharField(max_length=32)
	date = models.DateTimeField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return self.number

class AdminContact(models.Model):
	name = models.CharField(max_length=120, blank=True, null=True)
	number = models.CharField(max_length=10, blank=True, null=True)

	def __unicode__(self):
		return self.name