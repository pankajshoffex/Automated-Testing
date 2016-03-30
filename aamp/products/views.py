from django.contrib import messages
from django.db.models import Q
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.core.urlresolvers import reverse
# Create your views here.

from .mixins import StaffRequiredMixin
from orders.mixins import LoginRequiredMixin
from .models import Product, Variation, Category, ProductRating, Availability, Whishlist
from useraccount.models import SignUp
import random


@login_required(login_url="/accounts/login/")
def product_rating(request, pk):
	context = {}
	product = get_object_or_404(Product, pk=pk)

	if request.method == "POST":
		title = request.POST.get("title")
		name = request.POST.get("name")
		desc = request.POST.get("desc")
		star = request.POST.get("star")
		if desc and star:
			signup = request.user
			
			
			rating = ProductRating(product=product, user=signup)

			rating.title = title
			rating.name = name
			rating.desc = desc
			rating.rate = star
			rating.save()
			return redirect("products:product_detail", slug=product.slug )
		
		else:
			messages.error(request, "Please fill all information..!")
		
	context['product'] = product
	return render(request, 'products/product_rating.html', context)


def category_list(request, slug):
	context = {}
	cat = Category.objects.get(slug=slug)
	price_from = request.GET.get('from')
	price_to = request.GET.get('to')

	if price_from is not None and price_to is not None:
		print "yes"
		products = Product.objects.filter(categories__in=cat.get_descendants(include_self=True), sale_price__range=[Decimal(price_from), Decimal(price_to)])
	else:
		print "No"
		products = Product.objects.filter(categories__in=cat.get_descendants(include_self=True)).order_by("?")
	
	subcat = cat.get_children()
	category_image = str(cat.image)

	context['slug'] = slug
	context['image'] = category_image
	context['subcategory'] = subcat
	context['category'] = cat.name
	context['product_list'] = products
	return render(request, 'products/category_list.html', context)


class ProductColorView(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			color = request.GET.get('data')
			request.session['color'] = color
			return JsonResponse({"color":color})


class ProductListView(ListView):
	model = Product
	queryset = Product.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(ProductListView, self).get_context_data(*args, **kwargs)
		context["query"] = self.request.GET.get("q")
		context["recommended"] = Product.objects.all().order_by("?")[:6]
		return context

	def get_queryset(self, *args, **kwargs):
		qs = super(ProductListView, self).get_queryset(*args, **kwargs)
		query = self.request.GET.get("q")
		if query:
			qs = self.model.objects.filter(
					Q(title__icontains=query) |
					Q(long_description__icontains=query) |
					Q(short_description__icontains=query)
				)
			try:
				qs2 = self.model.objects.filter(
						Q(price__icontains=query)
					)

				qs = (qs | qs2).distinct()
			except:
				pass
		return qs

class ProductDetailView(DetailView):
	model = Product

	def get_context_data(self, *args, **kwargs):
		context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
		instance = self.get_object()
		context["related"] = sorted(Product.objects.get_related(instance)[:6], key= lambda x: random.random())
		return context

def availability(request):
	avail = request.GET.get('data')
	print avail
	if not avail:
		da = "please enter pincode"
	else:
		data = Availability.objects.filter(pin=avail)
		if not data:
			da = "Not Available"
		else:
			da = "Available"
	return HttpResponse(da)
	


@login_required(login_url="/accounts/login/")
def add_wishlist(request, pk):
	user = request.user
	product = Product.objects.get(pk=pk)

	wid, created = Whishlist.objects.get_or_create(user=user, product=product)

	if created:
		messages.success(request, "Successfully added to wishlist.")
	else:
		messages.error(request, "Already added to wishlist.")

	return HttpResponseRedirect(reverse('products:product_detail', kwargs={'slug': product.slug}))


class Wishlist(LoginRequiredMixin, ListView):
	model = Whishlist
	template_name = "products/wishlist.html"

	def get_queryset(self, *args, **kwargs):
		qs = super(Wishlist, self).get_queryset(*args, **kwargs)
		user = self.request.user
		qs = self.model.objects.filter(user=user)
		return qs

