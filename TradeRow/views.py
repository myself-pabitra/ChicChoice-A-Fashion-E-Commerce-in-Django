from django.shortcuts import render
from category.models import Category
from store.models import Product





def home(request):
    category = Category.objects.all()
    products  = Product.objects.all().filter(is_avaliable=True)
    context = {
        'category': category,
        'products': products,
    }

    return render(request, 'home.html',context)