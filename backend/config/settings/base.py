"""
Base Django settings shared across all environments.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config
import sentry_sdk

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-this-in-production")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    # Jazzmin MUST come before django.contrib.admin
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "storages",
    # Project apps
    "accounts",
    "areas",
    "reports",
    "cleaners",
    "assignments",
    "stats",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ---------------------------------------------------------------------------
# SimpleJWT
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
).split(",")
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ---------------------------------------------------------------------------
# Email defaults (overridden per environment)
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@garbagems.local")

# ---------------------------------------------------------------------------
# Jazzmin admin UI  —  rich interactive configuration
# ---------------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    # Branding
    "site_title":        "GarbageMS Admin",
    "site_header":       "GarbageMS",
    "site_brand":        "🗑️ GarbageMS",
    "site_logo":         None,
    "site_logo_classes": "img-circle",
    "site_icon":         None,
    "welcome_sign":      "Welcome to the Garbage Management System",
    "copyright":         "GarbageMS",

    # Top bar search
    "search_model": ["reports.Report", "accounts.User", "areas.Area"],

    # User avatar in top-right
    "user_avatar": "avatar",

    # Top menu links
    "topmenu_links": [
        {"name": "Dashboard",    "url": "admin:index",              "permissions": ["auth.view_user"]},
        {"name": "Reports",      "url": "admin:reports_report_changelist"},
        {"name": "Areas",        "url": "admin:areas_area_changelist"},
        {"name": "Cleaners",     "url": "admin:cleaners_cleaner_changelist"},
        {"name": "🌐 Frontend",  "url": "http://localhost:3001",    "new_window": True},
        {"name": "📖 API Docs",  "url": "/api/health/",             "new_window": True},
    ],

    # User menu links (top-right dropdown)
    "usermenu_links": [
        {"name": "Frontend App",    "url": "http://localhost:3001", "new_window": True, "icon": "fas fa-external-link-alt"},
        {"name": "View my profile", "model": "accounts.user"},
    ],

    # Sidebar
    "show_sidebar":           True,
    "navigation_expanded":    True,
    "hide_apps":              ["token_blacklist"],
    "hide_models":            [],

    # Order sidebar menu
    "order_with_respect_to": [
        "auth",
        "accounts",
        "reports",
        "areas",
        "cleaners",
        "assignments",
        "stats",
    ],

    # Custom sidebar links
    "custom_links": {
        "reports": [
            {
                "name":        "Pending Reports",
                "url":         "admin:reports_report_changelist",
                "url_params":  "?status__exact=pending",
                "icon":        "fas fa-clock",
                "permissions": ["reports.view_report"],
            },
            {
                "name":        "Export All CSV",
                "url":         "admin:reports_report_changelist",
                "url_params":  "?all=1",
                "icon":        "fas fa-download",
            },
        ],
    },

    # Icons
    "icons": {
        "auth":                          "fas fa-shield-alt",
        "auth.Group":                    "fas fa-users-cog",
        "accounts.User":                 "fas fa-user-circle",
        "reports.Report":                "fas fa-trash-alt",
        "areas.Area":                    "fas fa-map-marked-alt",
        "cleaners.Cleaner":              "fas fa-hard-hat",
        "assignments.Assignment":        "fas fa-tasks",
        "token_blacklist.BlacklistedToken":  "fas fa-ban",
        "token_blacklist.OutstandingToken":  "fas fa-key",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    # Modals & UX
    "related_modal_active":       True,
    "custom_css":                 None,
    "custom_js":                  None,
    "use_google_fonts_cdn":       True,
    "show_ui_builder":            True,       # lets admin tweak theme live
    "changeform_format":          "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },

    # Language chooser
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":            False,
    "footer_small_text":            False,
    "body_small_text":              False,
    "brand_small_text":             False,
    "brand_colour":                 "navbar-success",
    "accent":                       "accent-teal",
    "navbar":                       "navbar-dark",
    "no_navbar_border":             False,
    "navbar_fixed":                 True,       # sticky top navbar
    "layout_boxed":                 False,
    "footer_fixed":                 False,
    "sidebar_fixed":                True,       # sticky sidebar
    "sidebar":                      "sidebar-dark-success",
    "sidebar_nav_small_text":       False,
    "sidebar_disable_expand":       False,
    "sidebar_nav_child_indent":     True,
    "sidebar_nav_compact_style":    True,
    "sidebar_nav_legacy_style":     False,
    "sidebar_nav_flat_style":       False,
    "theme":                        "default",
    "dark_mode_theme":              "darkly",  # toggle-able dark mode
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
    "actions_sticky_top": True,               # bulk-action bar stays visible while scrolling
}

# ---------------------------------------------------------------------------
# Sentry (optional — only initializes when DSN is set)
# ---------------------------------------------------------------------------
SENTRY_DSN = config("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.2,
        send_default_pii=False,
    )
