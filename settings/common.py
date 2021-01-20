import os
import sys
from datetime import timedelta
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = bool(int(os.environ.get("DEBUG",0)))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

INSTALLED_APPS = [
    "djoser",
    "rest_framework.authtoken",
    "django_cleanup",  # When deleting object it will also delete image file
    "django_filters",
    "django_mailjet",
    "img_upload_api",
    "corsheaders",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "wsgi.application"

DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_DATABASE", "image"),
            "USER": os.environ.get("DB_USER", "image"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "image"),
            "HOST": os.environ.get("DB_HOST", "db"),
            "PORT": os.environ.get("DB_PORT", 5432),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
]
AUTH_USER_MODEL = "img_upload_api.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ['rest_framework.permissions.AllowAny'],
}



DJOSER = {
    # Change login field to Email
    "LOGIN_FIELD": "email",
    # Generate link to change new password
    "PASSWORD_RESET_CONFIRM_URL": "api/auth/users/confirm/reset-password/{uid}/{token}/",
    'ACTIVATION_URL': 'users/confirm/activation/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    "SET_PASSWORD_RETYPE": False,
    "PASSWORD_RESET_CONFIRM_RETYPE": False,
    "SERIALIZERS": {
        "user_create": "img_upload_api.serializers.UserRegisterSerializer",
        "user": "img_upload_api.serializers.UserRegisterSerializer",
    },
    # Creating new users is allowed only for admin user
    "PERMISSIONS": {"user_create": ["rest_framework.permissions.AllowAny"],
                    'user_list': ['rest_framework.permissions.AllowAny'],
                    'user': ['rest_framework.permissions.IsAuthenticated'],
                    },
}



SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=10),
}

EMAIL_BACKEND = "django_mailjet.backends.MailjetBackend"
MAILJET_API_KEY = os.environ.get("MAILJET_KEY", "")
MAILJET_API_SECRET = os.environ.get("MAILJET_SECRET", "")
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_FROM", "")

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

CORS_ORIGIN_WHITELIST = os.environ.get("CORS_ALLOWED_HOSTS").split(',')

STATIC_URL = '/bstatic/'
MEDIA_URL = '/media/'

STATIC_ROOT = '/static/'
MEDIA_ROOT = '/media/'

TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"
