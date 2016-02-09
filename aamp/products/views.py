from django.contrib import messages
from django.db.models import Q
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

# Create your views here.

from .forms import VariationInventoryFormSet
from .mixins import StaffRequiredMixin
from .models import Product, Variation, Category
import random


def demo(request):
	return render(request, "demo.html", {})

class ProductColorView(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			color = request.GET.get('data')
			request.session['color'] = color
			return JsonResponse({"color":color})

class CategoryListView(ListView):
	model = Category
	queryset = Category.objects.all()
	template_name = "products/product_list.html"


class CategoryDetailView(DetailView):
	model = Category

	def get_context_data(self, *args, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
		obj = self.get_object()
		product_set = obj.product_set.all()
		default_products = obj.default_category.all()
		products = ( product_set | default_products ).distinct()
		context["products"]	= products
		return context


class VariationListView(StaffRequiredMixin, ListView):
	model = Variation
	queryset = Variation.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(VariationListView, self).get_context_data(*args, **kwargs)
		context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
		return context

	def get_queryset(self, *args, **kwargs):
		product_pk = self.kwargs.get("pk")
		if product_pk:
			product = get_object_or_404(Product, pk=product_pk)
			queryset = Variation.objects.filter(product=product_pk)
		return queryset

	def post(self, request, *args, **kwargs):
		formset = VariationInventoryFormSet(request.POST, request.FILES)
		print request.POST
		if formset.is_valid():
			formset.save(commit=False)
			for form in formset:
				new_item = form.save(commit=False)
				# if new_item.title:
				product_pk = self.kwargs.get("pk")
				product = get_object_or_404(Product, pk=product_pk)
				new_item.product = product
				new_item.save()

			messages.success(request, "Your inventory and pricing has been updated.")
			return redirect("products:product_list")
		raise Http404

class ProductListView(ListView):
	model = Product
	queryset = Product.objects.all()

	def get_context_data(self, *args, **kwargs):
		context = super(ProductListView, self).get_context_data(*args, **kwargs)
		context["query"] = self.request.GET.get("q")
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



