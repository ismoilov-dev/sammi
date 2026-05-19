# ─────────────────────────────────────────
#  EduCenter LMS — Django Settings
# ─────────────────────────────────────────
import os
from pathlib import Path
from datetime import timedelta
from decouple import config
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# ══════════════════════════════════════════
#  CORE
# ══════════════════════════════════════════
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost").split(",")

# ══════════════════════════════════════════
#  APPLICATIONS
# ══════════════════════════════════════════
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "storages",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.courses",
    "apps.projects",
    "apps.sources",
    "apps.core",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
SITE_ID = 1

# ══════════════════════════════════════════
#  MIDDLEWARE  ← TO'G'RILANDI
# ══════════════════════════════════════════
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",           # ✅ 1-CHI bo'lishi SHART
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # 'apps.accounts.middleware.UserActivityMiddleware',
]

ROOT_URLCONF      = "config.urls"
WSGI_APPLICATION  = "config.wsgi.application"

# ══════════════════════════════════════════
#  TEMPLATES
# ══════════════════════════════════════════
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
            ],
        },
    },
]

# ══════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════
DATABASES = {
    "default": {
        "ENGINE":   config("DB_ENGINE",   default="django.db.backends.postgresql"),
        "NAME":     config("DB_NAME",     default="educenter_db"),
        "USER":     config("DB_USER",     default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST":     config("DB_HOST",     default="localhost"),
        "PORT":     config("DB_PORT",     default="5432"),
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ══════════════════════════════════════════
#  INTERNATIONALIZATION
# ══════════════════════════════════════════
LANGUAGE_CODE = "en"
TIME_ZONE     = "Asia/Tashkent"
USE_I18N      = True
USE_TZ        = True

# ══════════════════════════════════════════
#  STATIC FILES
# ══════════════════════════════════════════
STATIC_URL  = config("STATIC_URL", default="/static/")
STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", default="staticfiles")

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 500
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 500
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ══════════════════════════════════════════
#  MINIO / S3  ← TO'G'RILANDI
# ══════════════════════════════════════════
DEFAULT_FILE_STORAGE    = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID       = os.getenv('MINIO_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY   = os.getenv('MINIO_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
AWS_S3_FILE_OVERWRITE   = False
AWS_DEFAULT_ACL         = 'public-read'
AWS_QUERYSTRING_AUTH    = False

# ✅ MINIO_ENDPOINT .env da faqat IP:PORT bo'lishi kerak
# Masalan: MINIO_ENDPOINT=16.170.235.75:9000  (127.0.0.1 EMAS!)
_minio_endpoint = os.getenv('MINIO_ENDPOINT', '')
AWS_S3_ENDPOINT_URL = f'http://{_minio_endpoint}' if _minio_endpoint else ''

# ══════════════════════════════════════════
#  DRF
# ══════════════════════════════════════════
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":    timedelta(minutes=config("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", default=60, cast=int)),
    "REFRESH_TOKEN_LIFETIME":   timedelta(days=config("JWT_REFRESH_TOKEN_LIFETIME_DAYS", default=7, cast=int)),
    "ROTATE_REFRESH_TOKENS":    True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN":        True,
    "ALGORITHM":                "HS256",
    "AUTH_HEADER_TYPES":        ("Bearer",),
    "AUTH_TOKEN_CLASSES":       ("rest_framework_simplejwt.tokens.AccessToken",),
    "SIGNING_KEY":              config("SECRET_KEY"),
}

# ══════════════════════════════════════════
#  CORS  ← TO'G'RILANDI
# ══════════════════════════════════════════
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="https://asilbekjon.uz"
).split(",")

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://asilbekjon.uz"
).split(",")

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-csrftoken",
    "x-requested-with",
]
# =========================================
# ALLAUTH
# =========================================


ACCOUNT_LOGIN_METHODS = {"email"}

ACCOUNT_SIGNUP_FIELDS = [
    "email*",
    "password1*",
    "password2*",
]

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False

REST_AUTH_SETTINGS = {
    "USE_JWT":                 True,
    "JWT_AUTH_COOKIE":         "access",
    "JWT_AUTH_REFRESH_COOKIE": "refresh",
    "JWT_AUTH_HTTPONLY":       True,
    "REGISTER_SERIALIZER":     "apps.accounts.serializers.CustomRegisterSerializer",
    "LOGIN_SERIALIZER":        "dj_rest_auth.serializers.LoginSerializer",
}

GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID",     default=""),
            "secret":    config("GOOGLE_CLIENT_SECRET", default=""),
            "key":       "",
        },
        "SCOPE":              ["profile", "email"],
        "AUTH_PARAMS":        {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "VERIFIED_EMAIL":     True,
    },
    "github": {
        "APP": {
            "client_id": config("GITHUB_CLIENT_ID",     default=""),
            "secret":    config("GITHUB_CLIENT_SECRET", default=""),
            "key":       "",
        },
        "SCOPE": ["user:email", "read:user"],
    },
}

SOCIALACCOUNT_EMAIL_AUTHENTICATION              = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

# ══════════════════════════════════════════
#  SWAGGER
# ══════════════════════════════════════════
SPECTACULAR_SETTINGS = {
    "TITLE":       "Sammi API",
    "VERSION":     "1.0.0",
    "DESCRIPTION": "Sammi clone LMS API",
    "SERVE_PERMISSIONS":    ["rest_framework.permissions.AllowAny"],
    "SERVE_AUTHENTICATION": [],
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_SETTINGS":  {"persistAuthorization": True},
    "SECURITY": [{"Bearer": []}],
    "COMPONENTS": {
        "securitySchemes": {
            "Bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        }
    },
    "EXTENSIONS": [],
    "DISABLE_ERRORS_AND_WARNINGS": True,  # Suppress schema generation warnings
}

# ══════════════════════════════════════════
#  SECURITY
# ══════════════════════════════════════════
SECURE_SSL_REDIRECT            = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE          = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE             = config("CSRF_COOKIE_SECURE", default=False, cast=bool)
SESSION_COOKIE_HTTPONLY        = True
CSRF_COOKIE_HTTPONLY           = False   # ✅ False — frontend JS cookie o'qishi uchun
SECURE_HSTS_SECONDS            = config("SECURE_HSTS_SECONDS", default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD            = True
X_FRAME_OPTIONS                = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF    = True
SECURE_BROWSER_XSS_FILTER      = True

# ══════════════════════════════════════════
#  CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
# ══════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 465
EMAIL_USE_SSL       = True
EMAIL_USE_TLS       = False
EMAIL_HOST_USER     = 'ismatbekismoilov2@gmail.com'
EMAIL_HOST_PASSWORD = 'hdiv hxlg etol ubgf'
EMAIL_TIMEOUT = 10