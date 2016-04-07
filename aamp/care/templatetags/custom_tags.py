from django import template
from django.http import Http404
from care.models import CarePointUserProfile

register = template.Library()

@register.simple_tag
def get_care_user(request):
	user = request.user
	try:
		care_user = CarePointUserProfile.objects.get(user=user)
	except:
		raise Http404
	return care_user

