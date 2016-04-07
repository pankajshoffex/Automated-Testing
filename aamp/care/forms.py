from django import forms
from .models import CarePointBankDetail, CarePointDocuments



class CareChangePasswordForm(forms.Form):
	password1 = forms.CharField(max_length=50, label="Old Password", widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=50, label="New Password", widget=forms.PasswordInput())

class CareChangePasswordForm(forms.Form):
	password1 = forms.CharField(max_length=50, label="Old Password", widget=forms.PasswordInput())
	password2 = forms.CharField(max_length=50, label="New Password", widget=forms.PasswordInput())

class CarePointBankDetailForm(forms.ModelForm):
	class Meta:
		model = CarePointBankDetail
		fields = [
			'pan_no', 
			'vat_no', 
			'benifit_name',
			'acc_no',
			'neft', 
			'ifsc_code', 
			'acc_type', 
			'bank_name', 
			'branch',
		]
		widgets={
			'pan_no': forms.TextInput(attrs={ 'class': 'form-control', }),
			'vat_no': forms.TextInput(attrs={ 'class': 'form-control', }),
			'benifit_name': forms.TextInput(attrs={ 'class': 'form-control', }),
			'acc_no': forms.TextInput(attrs={ 'class': 'form-control', }),
			'neft': forms.TextInput(attrs={ 'class': 'form-control', }),
			'ifsc_code': forms.TextInput(attrs={ 'class': 'form-control', }),
			'acc_type': forms.Select(attrs={ 'class': 'form-control'}),
			'bank_name': forms.TextInput(attrs={ 'class': 'form-control', }),
			'branch': forms.TextInput(attrs={ 'class': 'form-control', }),
		}

class CarePointDocumentsForm(forms.ModelForm):
	class Meta:
		model = CarePointDocuments
		fields = [
			'id_proof',
			'pan_card',
			'bank_pass',
			]



