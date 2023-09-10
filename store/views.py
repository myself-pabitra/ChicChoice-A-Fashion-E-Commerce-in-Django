from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q  # Import Q objects

# Create your views here.


def store(request, category_slug=None):


    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_avaliable=True)
        
        # paginator Implimentation to all Catagirized Products 
        paginator = Paginator(products,2)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)


        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_avaliable=True).order_by('id')

        # paginator Implimentation to all Products 
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)


        product_count = products.count()

    
    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e

    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
    }


    return render(request, 'store/Product_details.html',context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        products = []
        product_count = 0
        if keyword != '':
            # Perform the search using Q objects to search in both 'name' and 'description' fields.
            products = Product.objects.order_by('-created_date').filter(Q(product_name__icontains = keyword) | Q(description__icontains = keyword))
            product_count = products.count()

    context = {
        'products': products,
        'product_count':product_count,
    }

    

    return render(request, 'store/store.html',context)


