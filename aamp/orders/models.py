from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils.html import mark_safe

# Create your models here.
from carts.models import Cart, Shipping
from useraccount.models import SignUp
from django.contrib.auth.models import User
import random 


ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'),
)


class UserAddress(models.Model):
	full_name = models.CharField(max_length=120)
	user = models.ForeignKey(User)
	type = models.CharField(max_length=120, choices=ADDRESS_TYPE, default='billing', blank=True, null=True)
	street = models.TextField()
	postcode = models.CharField(max_length=6)
	mobile = models.CharField(max_length=10)

	def __unicode__(self):
		return self.street

	def get_address(self):
		return "%s<br/> %s<br/> %s<br/> %s<br/>" %(self.full_name, self.street, self.postcode, self.mobile)


ORDER_STATUS_CHOICES = (
	('received', 'Received'),
	('dispatched', 'Dispatched'),
	('intransist', 'Intransist'),
	('delivered', 'Delivered'),
	('cancelled', 'Cancelled'),
)

class Order(models.Model):
	order_id = models.CharField(max_length=10, unique=True)
	status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='received')
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(User, null=True)
	billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True)
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
	shipping_total_price = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
	order_total = models.DecimalField(decimal_places=2, max_digits=50)
	payment = models.CharField(max_length=120, blank=True, null=True)
	timestamp = models.DateField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return str(self.order_id)

	class Meta:
		ordering = ['-id']

	def save(self, *args, **kwargs):
		super(Order, self).save(*args, **kwargs)
		order_id = "OD%s" %(random.randrange(1, 100000))
		self.order_id = order_id
		super(Order, self).save()

	def invoice(self):
		url = '<a href="/invoice/%s" target="_blank">Invoice</a>' %(self.pk)
		return mark_safe(url)

	def detail(self):
		url = '<a href="/adminorders/%s">Detail</a>' %(self.pk)
		return mark_safe(url)

	def get_absolute_url(self):
		return reverse("order_detail", kwargs={"pk": self.pk})

	def mark_completed(self):
		self.status = "received"
		self.save()

	def payment_method(self, method):
		self.payment = method
		self.save()

	def customer_name(self):
		data = ""
		if self.user:
			data = self.billing_address.full_name #user.user.get_full_name()
		else:
			data = "-"
		return str(data)

	def mobile_no(self):
		data = ""
		if self.user:
			data = self.billing_address.mobile #user.user.get_full_name()
		else:
			data = "-"
		return str(data)

	def products(self):
		data = self.cart.cartitem_set.all()
		print data
		li = ""
		for i in data:
			print i.item.product.title
			li = mark_safe("<a href='%s' target='_blank'>%s</a><br/>" %(i.item.get_absolute_url(), i.item.get_title()))
			return li


def order_pre_save(sender, instance, *args, **kwargs):
	shipping_total_price = instance.shipping_total_price
	cart_total = instance.cart.total
	order_total = Decimal(shipping_total_price) + Decimal(cart_total)
	instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)


class UserComplaint(models.Model):
	order_id = models.IntegerField(blank=True)
	reason = models.TextField(max_length=300, blank=False)
	order_name = models.CharField(max_length=300, blank=True)
	order_price = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
	user = models.CharField(max_length=300, blank=True)

	def __unicode__(self):
		return str(self.order_id)

class AdminComplaint(models.Model):
	admin_order_id = models.IntegerField(blank=True)
	admin_reason = models.TextField(max_length=300, blank=False)
	admin_order_name = models.CharField(max_length=300, blank=True)
	admin_order_price = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
	admin_user = models.CharField(max_length=300, blank=True)

	def __unicode__(self):
		return str(self.admin_user)

