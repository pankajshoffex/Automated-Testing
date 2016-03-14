from django import forms
from .models import SmsMarketing, SendSMS

class SmsMarketingForm(forms.ModelForm):
	class Meta:
		model = SmsMarketing
		fields = ['sms_subject','sms_text']
		widgets = { 
		'sms_text': forms.Textarea()
		}

class SendSMSForm(forms.ModelForm):
	class Meta:
		model = SendSMS
		fields = ['user','sms_subject','sms_text']
		widgets = { 
		'sms_text': forms.Textarea()
		}
