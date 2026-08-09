from django.contrib import admin
from .models import Category, Product, Banner, ProductGallery, ProductColor

# Banners aur Category ko dashboard mein dikhane ke liye
admin.site.register(Category)
admin.site.register(Banner)

# ==========================================
# ADVANCED DASHBOARD FEATURES (MAGIC)
# ==========================================

# Product wale page ke andar hi Multiple Photos daalne ka option
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1  # Ek extra khali dabba dikhayega photo upload karne ke liye

# Product wale page ke andar hi Colors daalne ka option
class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

# Product Panel ko Sundar aur Fast banane ke liye
class ProductAdmin(admin.ModelAdmin):
    # Dashboard mein bahar hi yeh sab details dikhengi
    list_display = ['name', 'category', 'price', 'stock', 'is_available']
    # Bina product khole bahar se hi price, stock aur availability change karne ke liye
    list_editable = ['price', 'stock', 'is_available']
    # Multiple photos aur colors ko product page ke andar jodne ke liye
    inlines = [ProductGalleryInline, ProductColorInline]

# Naye advance features ke sath Product ko register karna
admin.site.register(Product, ProductAdmin)