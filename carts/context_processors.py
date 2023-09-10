from .models import Cart,CartItem
from .views import _cart_id

def cart_counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id = _cart_id(request))
            cart_items = CartItem.objects.all().filter(cart = cart[:1])
            for cart_item in cart_items:
                cart_count += cart_item.quantity

        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count = cart_count)



def nav_cart_items(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    except Cart.DoesNotExist:
        cart_items = []
    return dict(cart_items = cart_items)




