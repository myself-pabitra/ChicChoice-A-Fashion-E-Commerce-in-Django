from django.shortcuts import render
from category.models import Category
from store.models import Product
# from carts.views import get_cart_data 


def home(request):

    category = Category.objects.all()
    products  = Product.objects.all().filter(is_avaliable=True)


    # cart_data = get_cart_data(request)


    # cart_items = cart_data['cart_items']
    # number_of_items = cart_data['number_of_items']





    context = {
        'category': category,
        'products': products,
        # 'cart_items':cart_items,
        # 'number_of_items':number_of_items
    }
    # print(context)
    return render(request, 'home.html',context)


