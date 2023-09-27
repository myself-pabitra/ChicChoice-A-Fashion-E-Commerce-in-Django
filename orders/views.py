from django.shortcuts import render, redirect
from carts.models import CartItem
from .models import Order, Payment,OrderProduct
from .forms import OrderForm
import datetime
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import razorpay
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def Payments(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user = request.user, is_ordered = False, order_number = body['orderId'])

    # Verifying razorpay payment signature 
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))

    signature = client.utility.verify_payment_signature({
    'razorpay_order_id': body['razorpay_order_id'],
    'razorpay_payment_id': body['razorpay_payment_id'],
    'razorpay_signature': body['razorpay_signature'],})


    # Srring transaction details into Payment Model 
    payment = Payment(
        user = request.user,
        razorpay_order_id = body['razorpay_order_id'],
        razorpay_payment_id = body['razorpay_payment_id'],
        razorpay_payment_signature = body['razorpay_signature'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['payment_status'],
    )
    payment.save()
    order.payment = payment

    if signature:
        order.is_ordered = True
    else:
        order.is_ordered = False
    order.save()

    # Move the cart item to order  Product Table
    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()



        # Finally, reduce the quantity of the ordered items
        product = Product.objects.get(id = item.product_id)
        product.Stock -= item.quantity
        product.save()

    # Clear Cart
    CartItem.objects.filter(user=request.user).delete()

    # send order receive eamil to Customer

    orderproducts = OrderProduct.objects.filter(order_id = order.id)

    mail_subject = "Thank you for your order 😍"
    message = render_to_string('orders/order_received_email.html', {
        "user":request.user,
        'order':order,
        'orderproducts':orderproducts
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    # send order number and transaction id back to send data method to Shop

    data = {
        'order_number' : order.order_number,
        'transaction_id' : payment.razorpay_payment_id,

        
    }

    return JsonResponse(data)


def Place_Order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to the store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    grand_total = 0
    shipping_cost = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    if total >= 999:
        shipping_cost = 0
        print('executed 2')
    else:
        shipping_cost = 99
        print('executed 3')
    grand_total = int(total + shipping_cost)

    if request.method == 'POST':
        print('executed 4')
        form = OrderForm(request.POST)
        if form.is_valid():

            # Store all the billing information inside the Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.pin_code = form.cleaned_data['pin_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.shipping_cost = shipping_cost
            data.ip = request.META.get('REMOTE_ADDR')
            print(data)
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number)

# #################################### RazorPay Section ###########################################

            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
            razorpay_payment_details  = client.order.create({
                "amount": grand_total,
                "currency": "INR",
                'payment_capture': '1'
            })
            print(razorpay_payment_details)


            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                'shipping_cost': shipping_cost,
                'razorpay_payment_details':razorpay_payment_details,

            }

            return render(request, 'orders/payments.html', context)
        else:
            print('invalid form', form.errors)
            print(form.data)

    return redirect('checkout')



def Order_Complete(request):
    order_number = request.GET.get('order_number')
    transction_id = request.GET.get('transction_id')

    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        

        subtotal = 0
        for product in ordered_products:
            subtotal += product.product_price * product.quantity

        payment = Payment.objects.get(razorpay_payment_id=transction_id)

        context = {
            'order' : order,
            'ordered_products':ordered_products,
            'order_number' : order.order_number,
            'payment_id' : payment.razorpay_payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')