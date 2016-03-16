from django import forms

from .models import UserAddress
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from useraccount.models import SignUp
from .models import Order



class AddressForm(forms.Form):
	billing_address = forms.ModelChoiceField(
		queryset = UserAddress.objects.filter(type="billing"),
		widget = forms.RadioSelect(attrs={'checked': 'checked', 'class': 'billing', "name": "billing_selected"}),
		empty_label = None,
	)
	shipping_address = forms.ModelChoiceField(
		queryset=UserAddress.objects.filter(type="shipping"),
		widget = forms.RadioSelect(attrs={'checked': 'checked', 'class': 'shipping', "name": "shipping_selected"}),
		empty_label = None,
	)


class UserAddressForm(forms.ModelForm):
	different = forms.BooleanField(label="Same address for shipping", initial=True, required=False)
	class Meta:
		model = UserAddress
		fields = [
			'full_name',
			'street',
			'postcode',
			'type',
			'mobile',			
		]
		widgets={
			'full_name': forms.TextInput(attrs={ 'class': 'form-control', }),
			'street': forms.Textarea(attrs={ 'class': 'form-control', 'rows':1, 'cols':10},),
			'postcode': forms.TextInput(attrs={ 'id': 'postcode', 'class': 'form-control' }),
			'type': forms.Select(attrs={ 'class': 'form-control'}),
			'mobile': forms.TextInput(attrs={ 'id': 'mobile', 'class': 'form-control', }),
		}

	
class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = '__all__'


