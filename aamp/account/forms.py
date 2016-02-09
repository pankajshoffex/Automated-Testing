from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from .models import SignUp


class MobileNoForm(forms.Form):
	mobile = forms.CharField(
		required=True, 
		label="Mobile No", 
		max_length=10
	)

class SignUpForm(forms.ModelForm):
	otp = forms.CharField(required=True, label ='Verification Code', widget=forms.TextInput(attrs={'id': 'otp'}))
	password1 = forms.CharField(widget=forms.PasswordInput(
		attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password")
	)
	password2 = forms.CharField(widget=forms.PasswordInput(
		attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)")
	)
	
	class Meta:
		model = SignUp
		fields = ("mobile_no",)

	def __init__(self, request, *args, **kwargs):
		self.request = request
		super(SignUpForm, self).__init__(*args, **kwargs)
		self.initial['mobile_no'] = self.request.session.get('mobile')
		


	def save(self, commit=True):
		data = super(SignUpForm, self).save(commit=False)
		mobile = self.cleaned_data['mobile_no']
		password = self.cleaned_data['password1']
		try:
			user = User.objects.create_user(username=mobile, password=password)
			data.user = user
		except:
			pass
		if commit:
			data.save()
		return data



