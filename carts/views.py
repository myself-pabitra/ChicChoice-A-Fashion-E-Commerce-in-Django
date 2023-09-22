from django.shortcuts import render, redirect,get_object_or_404
from store.models import Product,Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.http import HttpResponse



def _cart_id(request):

    cart = request.session.session_key
    if not cart:
        request.session.create()  # Create a new session if it doesn't exist
        cart = request.session.session_key  # Retrieve or create the session key
    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product

    #if user is Authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product,user = current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')


    #else user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            cart_item.save()
        return redirect('cart')







def remove_cart(request,product_id,cart_item_id):
    product = get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user = request.user,id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_item = CartItem.objects.get(product=product,cart = cart,id=cart_item_id)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id = cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, quantity=0, cart_item=None,shipment_cost=0):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user = request.user, is_active=True)
    else:
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

@login_required(login_url='login')
def checkout(request,total=0, quantity=0, cart_item=None,shipment_cost=0):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user = request.user, is_active=True)
    else:
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
    return render(request, 'store/checkout.html',context)