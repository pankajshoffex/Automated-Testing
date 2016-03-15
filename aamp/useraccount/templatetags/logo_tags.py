from django import template
from UI.models import UploadLogo
from products.models import Category, ProductRating, Product

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

@register.assignment_tag
def five_star():
	five = range(1,6)
	return five


def rate_average(value, arg):
	"Subtracts the arg from the value"
	product = Product.objects.get(pk=arg)
	rate = ProductRating.objects.filter(product=product)
	count = ProductRating.objects.filter(product=product).count()
	if count != 0:

		addition = 0
		for i in rate:
			addition = int(addition) + int(i.rate)
		return int(addition) / int(count)
	else:
		return 0

    

register.filter('rate', rate_average)






