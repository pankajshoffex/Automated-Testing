from django.template.defaulttags import register
import urllib
import base64

@register.filter(name='get_url')
def get_url(url):
	data = base64.urlsafe_b64encode(url)
	return data