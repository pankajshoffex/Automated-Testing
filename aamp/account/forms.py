from django import forms
from django.core.signing import Signer

from .models import SignUp


class MobileNoForm(forms.Form):
	mobile = forms.CharField(
		required=True, 
		label="Mobile No", 
		max_length=10
	)

class SignUpForm(forms.ModelForm):
	otp = forms.CharField(required=True, label ='Verification Code', widget=forms.TextInput(attrs={'id': 'otp'}))
	password = forms.CharField(label='Password', widget=forms.PasswordInput)
	
	class Meta:
		model = SignUp
		fields = ("mobile_no",)

	def __init__(self, request, *args, **kwargs):
		self.request = request
		super(SignUpForm, self).__init__(*args, **kwargs)
		self.initial['mobile_no'] = self.request.session.get('mobile')
		


	def save(self, commit=True):
		user = super(SignUpForm, self).save(commit=False)
		signer = Signer()
		pass_word = signer.sign(self.cleaned_data['password'])
		user.password = pass_word
		if commit:
			user.save()
		return user



