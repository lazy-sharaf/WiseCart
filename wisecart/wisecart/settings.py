from pathlib import Path


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-1c#&h1ps7=f5znz8hel191!_r%4_i72mscb&uy@g7bd)p((gay"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "products",
    "search",
    "shops",
    "comparison",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "wisecart.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "products.context_processors.featured_products",
                "shops.context_processors.featured_shops",
            ],
        },
    },
]

WSGI_APPLICATION = "wisecart.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "wisecart_db",
        "USER": "wisecart_team",
        "PASSWORD": "wise_people",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

AUTH_USER_MODEL = "users.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Dhaka"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication settings
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'users:profile'
LOGOUT_REDIRECT_URL = 'users:login'

# Custom authentication backends
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',  # Fallback to default backend
]

# Email settings
# Choose one of the following email backends based on your preference:

# Option 1: Gmail SMTP (requires app password)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail address
# EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Gmail app password
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Replace with your Gmail address

# Option 2: Outlook/Hotmail SMTP
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@outlook.com'  # Replace with your Outlook address
# EMAIL_HOST_PASSWORD = 'your-password'  # Replace with your Outlook password
# DEFAULT_FROM_EMAIL = 'your-email@outlook.com'  # Replace with your Outlook address

# Option 3: Yahoo SMTP
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mail.yahoo.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@yahoo.com'  # Replace with your Yahoo address
# EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with your Yahoo app password
# DEFAULT_FROM_EMAIL = 'your-email@yahoo.com'  # Replace with your Yahoo address

# Option 4: Custom SMTP Server
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'your-smtp-server.com'  # Replace with your SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@your-domain.com'  # Replace with your email
# EMAIL_HOST_PASSWORD = 'your-password'  # Replace with your password
# DEFAULT_FROM_EMAIL = 'your-email@your-domain.com'  # Replace with your email

# Option 5: SendGrid (recommended for production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'  # This should always be 'apikey'
# EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'  # Replace with your SendGrid API key
# DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'  # Replace with your verified sender

# Option 6: Mailgun (recommended for production)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-mailgun-username'  # Replace with your Mailgun username
# EMAIL_HOST_PASSWORD = 'your-mailgun-password'  # Replace with your Mailgun password
# DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'  # Replace with your verified sender

# For development/testing (currently active)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# DEFAULT_FROM_EMAIL = 'noreply@wisecart.com'

# Gmail SMTP Configuration (Active)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mahbuburrahmansoraf@gmail.com'
EMAIL_HOST_PASSWORD = 'lsou dmdu piku zhzp'
DEFAULT_FROM_EMAIL = 'mahbuburrahmansoraf@gmail.com'

# Email configuration
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 20  # Timeout in seconds for email operations
