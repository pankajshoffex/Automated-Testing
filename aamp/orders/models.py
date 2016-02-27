from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save

# Create your models here.
from carts.models import Cart
from account.models import SignUp


ADDRESS_TYPE = (
	('billing', 'Billing'),
	('shipping', 'Shipping'),
)


class UserAddress(models.Model):
	user = models.ForeignKey(SignUp)
	type = models.CharField(max_length=120, choices=ADDRESS_TYPE, default='billing')
	street = models.TextField()
	postcode = models.CharField(max_length=120)

	def __unicode__(self):
		return self.street

	def get_address(self):
		return "%s<br/> %s<br/> %s<br/>" %(self.user.user.get_full_name(), self.street, self.postcode)


ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('completed', 'Completed'),

)

class Order(models.Model):
	status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
	cart = models.ForeignKey(Cart)
	user = models.ForeignKey(SignUp, null=True)
	billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True)
	shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True)
	shipping_total_price = models.DecimalField(decimal_places=2, max_digits=50, default=5.99)
	order_total = models.DecimalField(decimal_places=2, max_digits=50)
	timestamp = models.DateField(auto_now_add=True, auto_now=False)

	def __unicode__(self):
		return str(self.cart.id)

	class Meta:
		ordering = ['-id']

	def get_absolute_url(self):
		return reverse("order_detail", kwargs={"pk": self.pk})

	def mark_completed(self):
		self.status = "completed"
		self.save()

	def customer_name(self):
		data = ""
		if self.user:
			data = self.user.user.get_full_name()
		else:
			data = "-"
		return str(data)



def order_pre_save(sender, instance, *args, **kwargs):
	shipping_total_price = instance.shipping_total_price
	cart_total = instance.cart.total
	order_total = Decimal(shipping_total_price) + Decimal(cart_total)
	instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)
