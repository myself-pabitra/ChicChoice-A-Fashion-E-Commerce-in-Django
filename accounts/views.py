from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests


# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage





from django.http import HttpResponse
def Register_User(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # confirm_password = form.cleaned_data['confirm_password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name = first_name,last_name = last_name,email=email,username = username,password = password)
            user.phone_number = phone_number
            user.save()



            #User Activation 
            current_site = get_current_site(request)
            mail_subject = "Please Activate your account"
            message = render_to_string('accounts/account_verification_email.html', {
                "user":user,
                "domain":current_site,
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                "token":default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            return redirect('/accounts/login_user/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form' : form,
    }
    return render(request,'accounts/register.html',context)



def activate(request,uidb64,token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,"Congratulations! Your account has been verified successfully")
        return redirect ('login')
    else:
        messages.info(request,"Invalid action Link")
        return redirect('register')





def Login_User(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variation by cart Id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))

                    # Getting the cart Items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pv in product_variation:
                        if pv in ex_var_list:
                            index = ex_var_list.index(pv)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                #next=/cart/checkout/
                params = dict(x.split('=')for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.warning(request,'username or password not correct')
            return redirect('login')

    return render(request,'accounts/login.html')



@login_required(login_url='login')
def Logout_User(request):
    auth.logout(request)
    messages.warning(request,'you are logged out')
    return redirect('login')





@login_required(login_url='login')
def dashboard(request):
    return render(request,'accounts/dashboard.html')


def Forgot_Password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #Password Reset
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string('accounts/password_reset_email.html', {
                "user":user,
                "domain":current_site,
                "uid":urlsafe_base64_encode(force_bytes(user.pk)),
                "token":default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,"Password reset mail has been send to your mail"+ " (" + email +") " + " Please Reset your Password")
            return redirect('login')

        else:
            messages.warning(request,"Account with this email does not exist") 
            return redirect('forgot_password')

    return render(request,'accounts/forgot_password.html')



def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,"Please reset your password")
        return redirect('resetPassword')
    else:
        messages.warning(request,"your token has been expired. Please try again")
        return redirect('login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset is Successful")
            return redirect('login')
        else:
            messages.warning(request,"Passwords do not match")
            return redirect('resetPassword')
    else: 
        return render(request,'accounts/resetpassword.html')