from django.urls import path, include
from store import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.register_view, name='register'),
    path('signin/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-new-password/', views.reset_new_password_view, name='reset_new_password'),
    
    # ==========================================
    # 🌍 GOOGLE LOGIN / ALLAUTH URLs
    # ==========================================
    path('accounts/', include('allauth.urls')),

    # ==========================================
    # 🛒 CUSTOMER VIEW (Shopping Website URLs)
    # ==========================================
    path('', views.store_home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    
    # Cart System
    path('cart/', views.cart_page, name='cart_page'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease-cart/<int:id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    
    # Wishlist System
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add-to-wishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Checkout & Payment
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_page_view, name='payment_page'),
    
    # Order Management
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-track/<int:order_id>/', views.order_track, name='order_track'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    
    # Customer Account & Notifications
    path('notifications/', views.notification_list, name='notifications'),
    path('profile/', views.account_profile_view, name='account_profile'),
    path('settings/', views.account_settings_view, name='account_settings'),

    # ==========================================
    # 🛑 SELLER PORTAL (Amazon Seller Style)
    # ==========================================
    path('seller-login/', views.seller_login_view, name='seller_login'),
    
    # Secure Dashboard URLs
    path('custom-dashboard/', views.custom_dashboard, name='custom_dashboard'),
    path('custom-dashboard/banners/', views.dashboard_banners, name='dashboard_banners'),
    path('custom-dashboard/delete-banner/<int:id>/', views.delete_banner, name='delete_banner'),
    path('custom-dashboard/add-product/', views.add_product_view, name='add_product'),
    path('custom-dashboard/add-category/', views.add_category_view, name='add_category'),
    path('custom-dashboard/edit-product/<int:id>/', views.edit_product_view, name='edit_product'),
    path('custom-dashboard/delete-product/<int:id>/', views.delete_product_view, name='delete_product'),
    path('dashboard/videos/', views.dashboard_videos, name='dashboard_videos'),
path('dashboard/videos/delete/<int:id>/', views.delete_video, name='delete_video'),
    
    # Login/Logout
    path('custom-login/', views.custom_login, name='custom_login'),
    path('custom-logout/', views.custom_logout, name='custom_logout'),
]

# Media files serving for development/production storage display fix
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)