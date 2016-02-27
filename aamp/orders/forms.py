from django import forms

from .models import UserAddress
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from account.models import SignUp



class AddressForm(forms.Form):
	billing_address = forms.ModelChoiceField(
		queryset = UserAddress.objects.filter(type="billing"),
		widget = forms.RadioSelect,
		empty_label = None,
	)
	shipping_address = forms.ModelChoiceField(
		queryset=UserAddress.objects.filter(type="shipping"),
		widget = forms.RadioSelect,
		empty_label = None,
	)


class UserAddressForm(forms.ModelForm):
	name = forms.CharField(
		required=True, 
		label="Full Name", 
		max_length=120
	)
	different = forms.BooleanField(label="Same address for shipping", initial=True)
	class Meta:
		model = UserAddress
		fields = [
			'street',
			'postcode',
			'type'			
		]

	


