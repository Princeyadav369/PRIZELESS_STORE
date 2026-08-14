import os
import django

# Django ka setup initialize karne ke liye
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_core.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # Seedha SQL command se database mein column add kar rahe hain
        cursor.execute("ALTER TABLE store_product ADD COLUMN section VARCHAR(20) DEFAULT 'trending';")
        print("✅ SUCCESS: 'section' column database mein directly add ho gaya!")
except Exception as e:
    print(f"⚠️ ALREADY EXISTS ya NOTE: {e}")