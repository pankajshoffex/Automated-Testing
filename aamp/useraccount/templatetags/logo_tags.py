from django import template
from UI.models import UploadLogo

register = template.Library()

@register.assignment_tag
def set_logo():
	logo_data = UploadLogo.objects.all()
	logo = ""
	for i in logo_data:
		logo = i.logo.url
	return str(logo)


