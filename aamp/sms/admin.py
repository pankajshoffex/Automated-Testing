from django.contrib import admin
from .models import SendSMS, SmsHistory, SmsSetting, SmsMarketing, BulkSmsHistory, BulkSms
from .forms import SmsMarketingForm, SendSMSForm, BulkSmsForm
from django.contrib.auth.models import User
import urllib2
import urllib
from datetime import date
from import_export.admin import ImportExportModelAdmin
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
	list_display = ['sms_subject','sms_text','date1']
	list_filter = ('sms_subject',)
	def get_form(self, request, obj=None, **kwargs):
		if request.method == 'POST':
			form = SendSMSForm(request.POST)
			if form.is_valid():
				subject = form.cleaned_data['sms_subject']
				message = form.cleaned_data['sms_text']
				users = form.cleaned_data['select_users']
				obj = SendSMS()
				for user in users:
					result = obj.sendsms(message, user)
					obj_name = User.objects.get(username=user)
					if result:
						SmsHistory.objects.create(
							number=user,
							recipient=obj_name.get_full_name(),
							sms_subject=subject, 
							sms_text=message,
							sms_type = "Promotional SMS"
							)					
			else:
				return SendSMSForm
		return SendSMSForm	
		
class BulkSmsAdmin(ImportExportModelAdmin):
	change_form_template = "admin/sms/SmsMarketing/change_form.html"
	
	form = BulkSmsForm
	list_display = ['name','numbers','date']
	class Meta:
		model = BulkSms
	def get_form(self, request, obj=None, **kwargs):
		startdate = date.today()
		users = BulkSms.objects.filter(date=startdate)
		if request.method == 'POST':
			form = BulkSmsForm(request.POST)
			if form.is_valid():

				subject = form.cleaned_data['sms_subject']
				message = form.cleaned_data['sms_text']
				for user in users:
			 		print user.numbers
					obj = SendSMS()
					#obj.sendsms(message,user.numbers)
					BulkSmsHistory.objects.create(
						number=user.numbers,
						recipient=user.name,
						sms_subject=subject, 
						sms_text=message,
						sms_type = "Bulk SMS"
						)	
			else:
				return SmsMarketingForm
		return SmsMarketingForm

class BulkSmsHistoryAdmin(admin.ModelAdmin):
	list_display = ['number','recipient','sms_subject','sms_text','sms_type','date']
	list_filter = ('sms_subject',)
	def get_readonly_fields(self, request, obj=None):
		if obj:
			return self.readonly_fields + ('number', 'recipient','sms_subject','sms_text','date','sms_type')
		return self.readonly_fields

admin.site.register(SendSMS, SendSMSAdmin)
admin.site.register(SmsHistory, SmsHistoryAdmin)
admin.site.register(SmsSetting, SmsSettingAdmin)
admin.site.register(SmsMarketing, SmsMarketingAdmin)
admin.site.register(BulkSms, BulkSmsAdmin)
admin.site.register(BulkSmsHistory, BulkSmsHistoryAdmin)