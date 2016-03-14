from django.contrib import admin
from .models import SendSMS, SmsHistory, SmsSetting, SmsMarketing
from .forms import SmsMarketingForm, SendSMSForm
from django.contrib.auth.models import User
import urllib2
import urllib
# Register your models here.


class SmsHistoryAdmin(admin.ModelAdmin):
	list_display = ['number','recipient','sms_subject','sms_text','sms_type','date']
	list_filter = ('sms_type',)
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('number', 'recipient','sms_subject','sms_text','date')
		return self.readonly_fields	

class SmsSettingAdmin(admin.ModelAdmin):
	list_display = ['sms_username','sms_api','sms_sender']
	
	def has_add_permission(self, request):
		num_objects = self.model.objects.count()
		if num_objects >= 1:
			return False
		else:
			return True

class SmsMarketingAdmin(admin.ModelAdmin):
	change_form_template = "admin/sms/SmsMarketing/change_form.html"
	form = SmsMarketingForm
	list_display = ['sms_subject','sms_text','date']
	list_filter = ('sms_subject',)
	def get_form(self, request, obj=None, **kwargs):
		users = User.objects.all()
		if request.method == 'POST':
			form = SmsMarketingForm(request.POST)
			if form.is_valid():
				subject = form.cleaned_data['sms_subject']
				message = form.cleaned_data['sms_text']
				for user in users:
					if not user.is_staff and not user.is_superuser:
						obj = SendSMS()
						obj.sendsms(message,user)
						SmsHistory.objects.create(
							number=user,
							recipient=user.get_full_name(),
							sms_subject=subject, 
							sms_text=message,
							sms_type = "SMS Marketing"
							)	
			else:
				return SmsMarketingForm
		return SmsMarketingForm	

class SendSMSAdmin(admin.ModelAdmin):
	change_form_template = "admin/sms/SmsMarketing/change_form.html"
	form = SendSMSForm
	list_display = ['user','sms_subject','sms_text','date1']
	list_filter = ('sms_subject',)
	def get_form(self, request, obj=None, **kwargs):
		if request.method == 'POST':
			form = SendSMSForm(request.POST)
			if form.is_valid():
				user = form.cleaned_data['user']
				subject = form.cleaned_data['sms_subject']
				message = form.cleaned_data['sms_text']
				#obj = SendSMS()
				#result = obj.sendsms(message, user)
				#if result:
				new_user = User.objects.get(username=user)
				SmsHistory.objects.create(
					number=user,
					recipient=new_user.get_full_name(),
					sms_subject=subject, 
					sms_text=message,
					sms_type = "Indivisual SMS"
					)					
			else:
				return SendSMSForm
		return SendSMSForm	


admin.site.register(SendSMS, SendSMSAdmin)
admin.site.register(SmsHistory, SmsHistoryAdmin)
admin.site.register(SmsSetting, SmsSettingAdmin)
admin.site.register(SmsMarketing, SmsMarketingAdmin)