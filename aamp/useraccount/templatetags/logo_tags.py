from django import template
from UI.models import UploadLogo
from products.models import Category

register = template.Library()

@register.assignment_tag
def set_logo():
	logo_data = UploadLogo.objects.all()
	logo = ""
	for i in logo_data:
		logo = i.logo.url
	return str(logo)

@register.assignment_tag
def set_node():
	nodes = Category.objects.all()
	return nodes

def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)

register.filter('sub', sub)



