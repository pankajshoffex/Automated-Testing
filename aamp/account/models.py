from __future__ import unicode_literals

from django.db import models



class SignUp(models.Model):
	mobile_no = models.CharField(max_length=10, unique=True)
	password = models.CharField(max_length=50)

	def __unicode__(self):
		return self.mobile_no