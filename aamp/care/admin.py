from django.contrib import admin
from .models import	CarePointUserProfile, Taluka, CarePointPincode, CarePointBankDetail,CarePointDocuments, Faqs
		
# Register your models here.


class CarePointPincodeAdmin(admin.ModelAdmin):
	list_display = ['location', 'pincode']

	class Meta:
		model = CarePointPincode


class FAQAdmin(admin.ModelAdmin):
	list_display = ['question', 'answer', 'pub_date']

	class Meta:
		model = Faqs



admin.site.register(Faqs, FAQAdmin)
admin.site.register(CarePointUserProfile)
admin.site.register(Taluka)
admin.site.register(CarePointPincode, CarePointPincodeAdmin)
admin.site.register(CarePointDocuments)
admin.site.register(CarePointBankDetail)

