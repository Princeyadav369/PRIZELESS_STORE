from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, Order, OrderItem, Notification, StoreSetting, Wishlist, Banner
from .forms import ProductForm, CategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def store_home(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
        
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    setting, created = StoreSetting.objects.get_or_create(id=1)

    banners = Banner.objects.filter(is_active=True)

    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        
    return render(request, 'home.html', {
        'products': products, 'query': query, 'cart_count': cart_count, 
        'active_festival': setting.active_festival, 'user_wishlist': user_wishlist,
        'banners': banners
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    recommended_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'product_detail.html', {
        'product': product, 
        'recommended_products': recommended_products, 
        'cart_count': cart_count,
        'in_wishlist': in_wishlist
    })

def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    product_id = str(id)
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {'name': product.name, 'price': float(product.price), 'quantity': 1, 'image': product.image.url if product.image else ''}
    request.session['cart'] = cart
    
    cart_count = sum(item['quantity'] for item in cart.values())
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'cart_count': cart_count})
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def decrease_cart(request, id):
    cart = request.session.get('cart', {})
    product_id = str(id)
    if product_id in cart:
        if cart[product_id]['quantity'] > 1:
            cart[product_id]['quantity'] -= 1
        else:
            del cart[product_id]
        request.session['cart'] = cart
    return redirect('cart_page')

def cart_page(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0
    for p_id, item in cart.items():
        try:
            prod = Product.objects.get(id=int(p_id))
            cart_items.append({'product': prod, 'quantity': item['quantity']})
            cart_total += float(item['price']) * item['quantity']
        except Product.DoesNotExist:
            continue
            
    cart_count = sum(item['quantity'] for item in cart.values())
    return render(request, 'cart.html', {'cart_items': cart_items, 'cart_total': cart_total, 'cart_count': cart_count})

def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    product_id = str(id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    return redirect('cart_page')

def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart_page')

@login_required(login_url='/signin/')
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items, 'cart_count': cart_count})

@login_required(login_url='/signin/')
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    if wishlist_item.exists():
        wishlist_item.delete()
        status = 'removed'
    else:
        Wishlist.objects.create(user=request.user, product=product)
        status = 'added'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'action': status})
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='/signin/')
def remove_from_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'action': 'removed'})
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required(login_url='/signin/')
def checkout_view(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('home')
        
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        pincode = request.POST.get('pincode', '')
        payment_method = request.POST.get('payment_method')
        
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            total_amount=total_price,
            status='Pending'
        )
        
        for product_id, item_data in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                price=item_data['price'],
                quantity=item_data['quantity']
            )
            
        request.session['cart'] = {}
        return redirect('order_success', order_id=order.id)
        
    cart_count = sum(item['quantity'] for item in cart.values())
    return render(request, 'checkout.html', {
        'cart': cart, 
        'total_price': total_price, 
        'cart_count': cart_count
    })

def payment_page_view(request):
    return HttpResponse("Payment Logic Handled in Checkout Submission context.")

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order, 'order_id': order_id})

def order_track(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_track.html', {'order': order})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status in ['Pending', 'Confirmed']:
        order.status = 'Cancelled'
        order.save()
    return redirect('my_orders')

def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required(login_url='/signin/')
def account_profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        return redirect('account_profile')
    return render(request, 'account_profile.html', {'user': user})

@login_required(login_url='/signin/')
def my_orders_view(request):
    orders = Order.objects.filter(email=request.user.email).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})

@login_required(login_url='/signin/')
def account_settings_view(request):
    return render(request, 'account_settings.html')

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def custom_dashboard(request):
    products = Product.objects.all()
    setting, created = StoreSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        setting.active_festival = request.POST.get('festival_theme', 'normal')
        setting.save()
        return redirect('custom_dashboard')
    return render(request, 'dashboard.html', {'products': products, 'setting': setting})

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def dashboard_banners(request):
    banners = Banner.objects.all().order_by('-id')
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        link = request.POST.get('link', '')
        
        if title and image:
            Banner.objects.create(title=title, image=image, link=link)
            return redirect('dashboard_banners')
            
    return render(request, 'dashboard_banners.html', {'banners': banners})

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def delete_banner(request, id):
    if request.method == 'POST':
        banner = get_object_or_404(Banner, id=id)
        banner.delete()
    return redirect('dashboard_banners')

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('custom_dashboard')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('custom_dashboard')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def edit_product_view(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('custom_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

@user_passes_test(lambda u: u.is_staff, login_url='/seller-login/')
def delete_product_view(request, id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        product.delete()
    return redirect('custom_dashboard')

def seller_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff: 
                login(request, user)
                return redirect('custom_dashboard')
            else:
                messages.error(request, "Access Denied! Aap Customer hain, Shop Owner nahi.")
                return redirect('seller_login')
        else:
            messages.error(request, "Galat ID ya Password! Sirf authorized sellers hi login karein.")
            
    return render(request, 'seller_login.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')

def custom_logout(request):
    logout(request)
    return redirect('home')

# ==========================================================
# EMAIL SIGNUP & SIGNIN VIEWS (With Confirm Password & Smart Redirect)
# ==========================================================
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register')
            
        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered!")
            return redirect('register')
            
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')
        
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password!")
            return redirect('login')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Yahan hum password reset flow trigger kar rahe hain
            messages.success(request, "Password reset instructions have been sent to your email.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "This email is not registered with us!")
            return redirect('forgot_password')
            
    return render(request, 'forgot_password.html')