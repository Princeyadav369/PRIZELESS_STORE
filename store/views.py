from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from .models import Product, Category, Order, OrderItem, Notification, StoreSetting, Wishlist, Banner, StoreVideoReview
from .forms import ProductForm, CategoryForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db import connection
import random
import json
import urllib.request
import urllib.parse
import os
import traceback
import datetime

def store_home(request):
    # 🚀==== AUTO DATABASE FIX HACK ====🚀
    try:
        with connection.cursor() as cursor:
            cursor.execute('ALTER TABLE store_storesetting ADD COLUMN bg_music_link VARCHAR(500);')
            cursor.execute('ALTER TABLE store_product ADD COLUMN display_section VARCHAR(20) DEFAULT "trending";')
            cursor.execute('CREATE TABLE IF NOT EXISTS store_storevideoreview (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), thumbnail_url VARCHAR(200), video_url VARCHAR(200), is_active bool);')
    except:
        pass # Agar column pehle se bana hai toh error ignore karega
    # 🚀=================================🚀

    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
        
    categories = Category.objects.all()[:6] 
        
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    setting, created = StoreSetting.objects.get_or_create(id=1)

    auto_theme = setting.active_festival
    decoration_level = 'normal'

    if auto_theme == 'normal':
        today = datetime.date.today()
        m = today.month
        d = today.day
        
        if m == 8 and 10 <= d <= 15:
            auto_theme = 'independence'
            decoration_level = 'ultra' if d == 15 else 'high'
            
        elif m == 8 and 23 <= d <= 28:
            auto_theme = 'rakshabandhan'
            decoration_level = 'ultra' if d == 28 else 'high'
            
        elif (m == 10 and d >= 26) or (m == 11 and d <= 1):
            auto_theme = 'diwali'
            decoration_level = 'ultra' if (m == 11 and d == 1) else 'high'
            
        elif (m == 12 and d >= 27) or (m == 1 and d == 1):
            auto_theme = 'newyear'
            decoration_level = 'ultra' if (m == 1 and d == 1) else 'high'
            
        elif m == 3 and 20 <= d <= 25:
            auto_theme = 'holi'
            decoration_level = 'ultra' if d == 25 else 'high'
            
        elif m == 9 and 2 <= d <= 7:
            auto_theme = 'ganpati'
            decoration_level = 'ultra' if d == 7 else 'high'

    festival_titles = {
        'independence': "🇮🇳 Independence Day Special Picks",
        'rakshabandhan': "🎁 Raksha Bandhan Gifting Specials",
        'diwali': "🪔 Diwali Dhamaka Offers",
        'newyear': "❄️ Year-End Blockbuster Deals",
        'ganpati': "🔱 Ganpati Mahotsav Exclusive Deals",
        'holi': "🎨 Holi Rangotsav Special Collections",
        'normal': "🔥 Trending New Arrivals"
    }
    festival_title = festival_titles.get(auto_theme, "🔥 Trending New Arrivals")

    trending_products = products.filter(display_section='trending')
    combo_products = products.filter(display_section='combo')
    bestseller_products = products.filter(display_section='bestseller')

    banners = Banner.objects.filter(is_active=True)
    try:
        videos = StoreVideoReview.objects.filter(is_active=True)[:3]
    except:
        videos = []

    user_wishlist = []
    if request.user.is_authenticated:
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        
    return render(request, 'home.html', {
        'trending_products': trending_products,
        'combo_products': combo_products,
        'bestseller_products': bestseller_products,
        'categories': categories,
        'query': query, 
        'cart_count': cart_count, 
        'active_festival': auto_theme, 
        'decoration_level': decoration_level,
        'festival_title': festival_title,
        'user_wishlist': user_wishlist,
        'banners': banners,
        'videos': videos,
        'bg_music_link': setting.bg_music_link
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
        first_name = request.POST.get('first_name') or request.user.first_name or 'Customer'
        last_name = request.POST.get('last_name', '')
        email = request.user.email if request.user.is_authenticated else request.POST.get('email', '')
        phone = request.POST.get('phone', 'N/A')
        room_no = request.POST.get('room_no', '')
        street = request.POST.get('street', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '')
        full_address = f"{room_no}, {street}"
        order = Order.objects.create(
            first_name=first_name, last_name=last_name, email=email, phone=phone,
            address=full_address, city=city, pincode=pincode, total_amount=total_price, status='Pending'
        )
        for product_id, item_data in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(order=order, product=product, price=item_data['price'], quantity=item_data['quantity'])
        request.session['cart'] = {}
        request.session['pending_order_id'] = order.id
        return redirect('payment_page')
    cart_count = sum(item['quantity'] for item in cart.values())
    return render(request, 'checkout.html', {'cart': cart, 'total_price': total_price, 'cart_count': cart_count})

def payment_page_view(request):
    order_id = request.session.get('pending_order_id')
    if not order_id:
        return redirect('home')
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'select_method':
            method = request.POST.get('payment_method')
            if method == 'UPI':
                upi_string = f"upi://pay?pa=prizeless@ybl&pn=Prizeless%20Store&am={order.total_amount}&cu=INR"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_string)}"
                return render(request, 'payment.html', {'order': order, 'qr_url': qr_url, 'step': 'qr'})
            else:
                order.status = 'Confirmed'
                order.save()
                del request.session['pending_order_id']
                return redirect('order_success', order_id=order.id)
        elif action == 'confirm_upi':
            order.status = 'Confirmed'
            order.save()
            del request.session['pending_order_id']
            return redirect('order_success', order_id=order.id)
    return render(request, 'payment.html', {'order': order, 'step': 'selection'})

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
    categories = Category.objects.all()
    orders = Order.objects.all().order_by('-created_at')
    customers = User.objects.filter(is_staff=False)
    try:
        videos = StoreVideoReview.objects.all()
    except:
        videos = []
    
    total_orders = orders.count()
    total_revenue = sum(o.total_amount for o in orders if o.status == 'Confirmed')
    pending_orders = orders.filter(status='Pending').count()
    completed_orders = orders.filter(status='Confirmed').count()

    recent_notifications = orders[:5]
    setting, created = StoreSetting.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_festival':
            setting.active_festival = request.POST.get('festival_theme', 'normal')
            if request.POST.get('music_url'):
                setting.bg_music_link = request.POST.get('music_url')
            setting.save()
            messages.success(request, "Store Custom Dashboard Configurations Saved!")
        elif action == 'add_video':
            StoreVideoReview.objects.create(
                title=request.POST.get('v_title'),
                thumbnail_url=request.POST.get('v_thumb'),
                video_url=request.POST.get('v_url')
            )
            messages.success(request, "New Action Review Video Added!")
        return redirect('custom_dashboard')
        
    return render(request, 'dashboard.html', {
        'products': products, 'categories': categories, 'orders': orders, 'customers': customers, 'videos': videos,
        'total_orders': total_orders, 'total_revenue': total_revenue, 'pending_orders': pending_orders,
        'completed_orders': completed_orders, 'recent_notifications': recent_notifications, 'setting': setting
    })

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
        get_object_or_404(Banner, id=id).delete()
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
        get_object_or_404(Product, id=id).delete()
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

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            
            api_url = "https://api.brevo.com/v3/smtp/email"
            data = {
                "sender": {"name": "Prizeless Store", "email": "prizelessstore@gmail.com"},
                "to": [{"email": email, "name": user.username}],
                "subject": "Password Reset OTP - Prizeless Store",
                "htmlContent": f"<div style='font-family: Arial; padding: 20px;'><h2>Password Reset</h2><p>Hello {user.username},</p><p>Your 6-digit OTP for Prizeless Store is: <strong style='font-size: 24px; color: #ffca28;'>{otp}</strong></p><p>Do not share this OTP with anyone.</p></div>"
            }
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(api_url, data=json_data)
            req.add_header('accept', 'application/json')
            req.add_header('content-type', 'application/json')
            req.add_header('api-key', os.environ.get('BREVO_API_KEY'))
            
            try:
                response = urllib.request.urlopen(req)
                messages.success(request, "OTP has been sent to your email!")
                return redirect('verify_reset_otp')
            except Exception as api_error:
                messages.error(request, f"Brevo API Error: {str(api_error)}")
                return redirect('forgot_password')
        except User.DoesNotExist:
            messages.error(request, "This email is not registered with us!")
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')

def verify_reset_otp_view(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        real_otp = request.session.get('reset_otp')
        if user_otp == real_otp:
            messages.success(request, "OTP Verified! Enter your new password.")
            return redirect('reset_new_password')
        else:
            messages.error(request, "Invalid OTP! Please try again.")
            return redirect('verify_reset_otp')
    return render(request, 'verify_otp.html')

def reset_new_password_view(request):
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('forgot_password')
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_new_password')
        user = User.objects.get(email=reset_email)
        user.set_password(new_password)
        user.save()
        if 'reset_otp' in request.session:
            del request.session['reset_otp']
        if 'reset_email' in request.session:
            del request.session['reset_email']
        messages.success(request, "Password reset successful! Please login.")
        return redirect('login')
    return render(request, 'reset_password.html')