from django import template
from UI.models import SitePage

register = template.Library()

@register.assignment_tag
def footer_tag():
	pages = SitePage.objects.active()
	return pages