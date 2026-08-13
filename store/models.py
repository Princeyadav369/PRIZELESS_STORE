from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    name = models.CharField(max_length=255, help_text="Store ka naam (e.g., Prizeless Store)")
    domain = models.CharField(max_length=255, help_text="Website ka link (e.g., store1.com)", unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Is store ka malik kaun hai?")
    
    def __str__(self):
        return self.name

class Category(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    SECTION_CHOICES = [
        ('trending', '🔥 Trending New Arrivals'),
        ('combo', '🎁 Exclusive Combos & Sets'),
        ('bestseller', '⭐ Our Best Sellers'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0, help_text="Kitne items bache hain?")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    colors = models.CharField(max_length=255, blank=True, null=True, help_text="Colors yahan likhein comma laga kar (Jaise: Red, Blue, Black)")
    # section = models.CharField(max_length=20, choices=SECTION_CHOICES, default='trending', help_text="Yeh product website ke kis hisse mein dikhana hai?")
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.first_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

class Notification(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class StoreSetting(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    active_festival = models.CharField(max_length=50, default='normal')
    festival_music_url = models.URLField(max_length=500, blank=True, null=True, default="https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3", help_text="Yahan dashboard se koi bhi song URL paste karein")

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Banner(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, help_text="Banner ka naam (jaise: Diwali Sale)")
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_variations')
    color_name = models.CharField(max_length=50)

class VideoReview(models.Model):
    title = models.CharField(max_length=255, help_text="Video ka title")
    thumbnail_url = models.URLField(help_text="Thumbnail Image Link")
    video_url = models.URLField(help_text="Video streaming Source URL")
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title