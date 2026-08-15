from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-m#3^!v#0(v9t@w#8%k-o&^%u_#9)w-1!$p(y@0#r^&8$!q_p@0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Cloudinary app integration
    'cloudinary_storage',
    'cloudinary',

    # Tera custom e-commerce app
    'store',

    # Allauth & Google Login
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Allauth specific middleware
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'shop_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'shop_core.wsgi.application'

# Database
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# ALLAUTH & GOOGLE LOGIN CONFIGURATION 
# ==========================================

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Normal Django login ke liye
    'django.contrib.auth.backends.ModelBackend',
    # Allauth / Google login ke liye
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Login hone ke baad customer kahan jayega? (Home page par)
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# YEH WOH CODE HAI JO PURANE BEKAR PAGE KO HATAYEGA AUR SEEDHA GOOGLE KHOL DEGA
SOCIALACCOUNT_LOGIN_ON_GET = True

# Google provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# ==========================================================
# REAL GMAIL SMTP SETTINGS (For Forgot Password & OTP)
# ==========================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465                 
EMAIL_USE_SSL = True             
EMAIL_USE_TLS = False            
EMAIL_HOST_USER = 'prizelessstore@gmail.com'
EMAIL_HOST_PASSWORD = 'prrhfktfttkpvddv'

# ==========================================
# CLOUDINARY PERMANENT IMAGE STORAGE CONFIG
# ==========================================
