"""Django settings for digital_msharika project."""

import os
import re
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-z=-@k%e!ik^x+ql_o0ljswjv3e2wpis=v7vv*c*7amzs*ivm6j")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["kkktdmp.com", "www.kkktdmp.com", "localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["https://kkktdmp.com", "https://www.kkktdmp.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "tenants",
    "members",
    "fellowships",
    "pledges",
    "content_app",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "tenants.middleware.TenantMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "digital_msharika.urls"

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
                "django.template.context_processors.i18n",
                "tenants.context_processors.pending_applications",
            ],
        },
    },
]

WSGI_APPLICATION = "digital_msharika.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "kkkt_db"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", "English"),
    ("sw", "Kiswahili"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

AUTHENTICATION_BACKENDS = [
    "members.auth_backend.MemberBackend",
    "django.contrib.auth.backends.ModelBackend",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ),
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Briq OTP verification (used during signup)
def _briq_keys_from_spec_file():
    spec_file = BASE_DIR / "signup_auth_process_veification.txt"
    if not spec_file.exists():
        return "", ""
    raw = spec_file.read_text(encoding="utf-8", errors="ignore")
    api_key_match = re.search(r'X-API-Key:\s*([^\s"]+)', raw)
    app_key_match = re.search(r'\\"?app_key\\"?\s*:\s*\\"?([^"\\]+)', raw)
    return (
        api_key_match.group(1) if api_key_match else "",
        app_key_match.group(1) if app_key_match else "",
    )


_spec_api_key, _spec_app_key = _briq_keys_from_spec_file()
BRIQ_OTP_BASE_URL = os.getenv("BRIQ_OTP_BASE_URL", "https://karibu.briq.tz/v1/otp")
BRIQ_OTP_API_KEY = os.getenv("BRIQ_OTP_API_KEY", _spec_api_key)
BRIQ_OTP_APP_KEY = os.getenv("BRIQ_OTP_APP_KEY", _spec_app_key)
BRIQ_OTP_LENGTH = int(os.getenv("BRIQ_OTP_LENGTH", "6"))
BRIQ_OTP_EXPIRE_MINUTES = int(os.getenv("BRIQ_OTP_EXPIRE_MINUTES", "10"))
BRIQ_OTP_DELIVERY_METHOD = os.getenv("BRIQ_OTP_DELIVERY_METHOD", "sms")
BRIQ_OTP_MESSAGE_TEMPLATE = os.getenv(
    "BRIQ_OTP_MESSAGE_TEMPLATE",
    "Your verification code for KKKT-DMP is {code}",
)
BRIQ_WEBHOOK_SECRET = os.getenv("BRIQ_WEBHOOK_SECRET", "")

try:
    from . import briq_settings as _briq_settings

    BRIQ_OTP_BASE_URL = getattr(_briq_settings, "BRIQ_OTP_BASE_URL", BRIQ_OTP_BASE_URL) or BRIQ_OTP_BASE_URL
    BRIQ_OTP_API_KEY = getattr(_briq_settings, "BRIQ_OTP_API_KEY", BRIQ_OTP_API_KEY) or BRIQ_OTP_API_KEY
    BRIQ_OTP_APP_KEY = getattr(_briq_settings, "BRIQ_OTP_APP_KEY", BRIQ_OTP_APP_KEY) or BRIQ_OTP_APP_KEY
    BRIQ_OTP_LENGTH = getattr(_briq_settings, "BRIQ_OTP_LENGTH", BRIQ_OTP_LENGTH) or BRIQ_OTP_LENGTH
    BRIQ_OTP_EXPIRE_MINUTES = getattr(
        _briq_settings, "BRIQ_OTP_EXPIRE_MINUTES", BRIQ_OTP_EXPIRE_MINUTES
    ) or BRIQ_OTP_EXPIRE_MINUTES
    BRIQ_OTP_DELIVERY_METHOD = getattr(
        _briq_settings, "BRIQ_OTP_DELIVERY_METHOD", BRIQ_OTP_DELIVERY_METHOD
    ) or BRIQ_OTP_DELIVERY_METHOD
    BRIQ_OTP_MESSAGE_TEMPLATE = getattr(
        _briq_settings, "BRIQ_OTP_MESSAGE_TEMPLATE", BRIQ_OTP_MESSAGE_TEMPLATE
    ) or BRIQ_OTP_MESSAGE_TEMPLATE
    BRIQ_WEBHOOK_SECRET = getattr(
        _briq_settings, "BRIQ_WEBHOOK_SECRET", BRIQ_WEBHOOK_SECRET
    ) or BRIQ_WEBHOOK_SECRET
except ImportError:
    pass
