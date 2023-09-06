from django.shortcuts import render
from store.models import Product
# Create your views here.


def store(request):
    products = Product.objects.all().filter(is_avaliable=True)
    product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)