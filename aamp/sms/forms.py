from django import forms
from .models import SmsMarketing, SendSMS, BulkSms
from useraccount.models import SignUp

class SmsMarketingForm(forms.ModelForm):
	class Meta:
		model = SmsMarketing
		fields = ['sms_subject','sms_text']
		widgets = { 
		'sms_text': forms.Textarea()
		}

class SendSMSForm(forms.ModelForm):
	select_users = forms.ModelMultipleChoiceField(queryset=SignUp.objects.all(), widget=forms.CheckboxSelectMultiple)
	class Meta:
		model = SendSMS
		fields = ['sms_subject','sms_text']
		widgets = { 
		'sms_text': forms.Textarea()
		}
	def __init__(self, *args, **kwargs):
		super(SendSMSForm, self).__init__(*args, **kwargs)
		self.fields['select_users'].choices = [(item.mobile_no, item.mobile_no) for item in SignUp.objects.all()]

class BulkSmsForm(forms.ModelForm):
	sms_subject = forms.CharField()
	sms_text = forms.CharField(widget=forms.Textarea())
	class Meta:
		model = BulkSms
		exclude = ['numbers','name','date']