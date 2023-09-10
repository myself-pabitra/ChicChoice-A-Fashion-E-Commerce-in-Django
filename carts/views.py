from django.shortcuts import render, redirect,get_object_or_404
from store.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from django.http import HttpResponse


# def _cart_id(request):
#     cart = request.session.session_key
#     if not cart:
#         cart = request.session.create()
#     return cart


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        request.session.create()  # Create a new session if it doesn't exist
        cart = request.session.session_key  # Retrieve or create the session key
    return cart



def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cart')



def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product,id=product_id)
    cart_item = CartItem.objects.get(product=product,cart = cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    print(cart)
    product = get_object_or_404(Product,id=product_id)
    cart_item  = CartItem.objects.get(product=product,cart = cart)

    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_item=None,shipment_cost=0):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    number_of_items = cart_items.count()

    if cart_items:
        try:
            for cart_item in cart_items:
                total += (cart_item.product.price * cart_item.quantity)
                quantity += cart_item.quantity


            if total >= 999:
                shipment_cost = 0
            else:
                shipment_cost = 99
            
            grand_total = int(total + shipment_cost)


        except ObjectDoesNotExist:
            total = quantity = cart_items = None

        context = {
            'cart_items': cart_items,
            'total': total,
            'quantity': quantity,
            'shipment_cost':shipment_cost,
            'grand_total':grand_total,
            'number_of_items':number_of_items,
        }
        return render(request, 'store/cart.html', context)
    return render(request, 'store/EmptyCart.html')
