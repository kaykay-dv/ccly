"""Settings for the embedded project. Values come from the current directory's .env."""

from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from ccly.branding import site_title
from ccly.project.app_settings import contribute_settings

load_dotenv(Path.cwd() / ".env")

PACKAGE_DIR = Path(__file__).resolve().parent


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str) -> list[str]:
    raw = os.environ.get(name, default)
    return [part.strip() for part in raw.split(",") if part.strip()]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _env_text(name: str, default: str) -> str:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip()


def _env_optional(name: str) -> str | None:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return None
    return raw.strip()


def _env_samesite(name: str) -> str:
    value = _env_text(name, "Lax")
    if value not in {"Lax", "Strict", "None"}:
        raise ImproperlyConfigured(f"{name} must be Lax, Strict, or None.")
    return value


def _env_proxy_ssl_header(name: str) -> tuple[str, str] | None:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    header, separator, value = raw.partition(",")
    header, value = header.strip(), value.strip()
    if not separator or not header or not value:
        raise ImproperlyConfigured(
            f"{name} must look like HTTP_X_FORWARDED_PROTO,https."
        )
    return header, value


def _env_rate(name: str, default: str) -> str | None:
    """A django-ratelimit rate (``60/m``), or None when the variable is empty."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip()
    if value == "":
        return None
    if re.fullmatch(r"\d+/\d*[smhd]", value) is None:
        raise ImproperlyConfigured(
            f"{name} must look like 60/m, or be empty to disable the limit."
        )
    return value


_secret = os.environ.get("CCLY_SECRET_KEY", "").strip()
if not _secret:
    raise ImproperlyConfigured(
        "CCLY_SECRET_KEY is missing. Run ccly init <app_name> in this directory."
    )

SECRET_KEY = _secret
DEBUG = _env_bool("CCLY_DEBUG", False)
ALLOWED_HOSTS = _env_list("CCLY_ALLOWED_HOSTS", "localhost,127.0.0.1")
CCLY_APPS = _env_list("CCLY_APPS", "")
CCLY_SITE_TITLE = site_title(CCLY_APPS, os.environ.get("CCLY_SITE_NAME", ""))
# An app replaces this by setting CCLY_LOGO in its ccly_settings module.
CCLY_LOGO = "img/alaska.png"

INSTALLED_APPS = [
    "ccly.project.apps.CclyProjectConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "axes",
    *CCLY_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "ccly.project.ratelimit.RatelimitMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "ccly.project.urls"
WSGI_APPLICATION = "ccly.project.wsgi.application"
ASGI_APPLICATION = "ccly.project.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PACKAGE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ccly.project.context_processors.admin_brand",
            ],
        },
    },
]

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("CCLY_DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=_env_int("CCLY_CONN_MAX_AGE", 0),
    )
}

LANGUAGE_CODE = os.environ.get("CCLY_LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("CCLY_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = _env_text("CCLY_STATIC_URL", "static/")
STATIC_ROOT = Path.cwd() / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# The admin lives under each installed app. Login links use the first app.
LOGIN_URL = f"/{CCLY_APPS[0]}/m/login/" if CCLY_APPS else "/accounts/login/"

# One token per site. Cookie names and the cache prefix keep two ccly
# processes on the same domain from reading each other's sessions.
_cache_prefix = _env_text(
    "CCLY_CACHE_PREFIX",
    "ccly_" + hashlib.sha256(SECRET_KEY.encode()).hexdigest()[:8],
)
_cookie_domain = _env_optional("CCLY_COOKIE_DOMAIN")
_cookie_secure = _env_bool("CCLY_COOKIE_SECURE", False)
_session_path = _env_text("CCLY_SESSION_COOKIE_PATH", "/")
_session_samesite = _env_samesite("CCLY_SESSION_COOKIE_SAMESITE")

SESSION_COOKIE_NAME = _env_text("CCLY_SESSION_COOKIE_NAME", f"{_cache_prefix}_session")
SESSION_COOKIE_DOMAIN = _cookie_domain
SESSION_COOKIE_PATH = _session_path
SESSION_COOKIE_SECURE = _cookie_secure
SESSION_COOKIE_SAMESITE = _session_samesite

CSRF_COOKIE_NAME = _env_text("CCLY_CSRF_COOKIE_NAME", f"{_cache_prefix}_csrf")
CSRF_COOKIE_DOMAIN = _cookie_domain
CSRF_COOKIE_PATH = _env_text("CCLY_CSRF_COOKIE_PATH", "/")
CSRF_COOKIE_SECURE = _cookie_secure
CSRF_COOKIE_SAMESITE = _env_samesite("CCLY_CSRF_COOKIE_SAMESITE")
CSRF_TRUSTED_ORIGINS = _env_list("CCLY_CSRF_TRUSTED_ORIGINS", "")

LANGUAGE_COOKIE_NAME = _env_text(
    "CCLY_LANGUAGE_COOKIE_NAME", f"{_cache_prefix}_language"
)
LANGUAGE_COOKIE_DOMAIN = _cookie_domain
LANGUAGE_COOKIE_PATH = _session_path
LANGUAGE_COOKIE_SECURE = _cookie_secure
LANGUAGE_COOKIE_SAMESITE = _session_samesite

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": _cache_prefix,
        "KEY_PREFIX": _cache_prefix,
    }
}

SECURE_SSL_REDIRECT = _env_bool("CCLY_SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = _env_int("CCLY_SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("CCLY_SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = _env_bool("CCLY_SECURE_HSTS_PRELOAD", False)
SECURE_PROXY_SSL_HEADER = _env_proxy_ssl_header("CCLY_SECURE_PROXY_SSL_HEADER")
USE_X_FORWARDED_HOST = _env_bool("CCLY_USE_X_FORWARDED_HOST", False)

DEFAULT_FROM_EMAIL = os.environ.get("CCLY_DEFAULT_FROM_EMAIL", "webmaster@localhost")
_email_backend = _env_text(
    "CCLY_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
_email_mailer: dict = {"BACKEND": _email_backend}
if _email_backend == "django.core.mail.backends.smtp.EmailBackend":
    _email_mailer["OPTIONS"] = {
        "host": _env_text("CCLY_EMAIL_HOST", "localhost"),
        "port": _env_int("CCLY_EMAIL_PORT", 587),
        "username": os.environ.get("CCLY_EMAIL_HOST_USER", ""),
        "password": os.environ.get("CCLY_EMAIL_HOST_PASSWORD", ""),
        "use_tls": _env_bool("CCLY_EMAIL_USE_TLS", True),
        "use_ssl": _env_bool("CCLY_EMAIL_USE_SSL", False),
    }
MAILERS = {"default": _email_mailer}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": CCLY_SITE_TITLE,
    "VERSION": "1.0.0",
}

AXES_FAILURE_LIMIT = _env_int("CCLY_AXES_FAILURE_LIMIT", 5)
AXES_COOLOFF_TIME = timedelta(hours=_env_float("CCLY_AXES_COOLOFF_HOURS", 1))

# django-ratelimit. An empty CCLY_RATELIMIT_RATE means no limit.
RATELIMIT_ENABLE = _env_bool("CCLY_RATELIMIT_ENABLE", True)
RATELIMIT_FAIL_OPEN = _env_bool("CCLY_RATELIMIT_FAIL_OPEN", False)
CCLY_RATELIMIT_RATE = _env_rate("CCLY_RATELIMIT_RATE", "60/m")
CCLY_RATELIMIT_KEY = _env_text("CCLY_RATELIMIT_KEY", "user_or_ip")
RATELIMIT_CACHE_PREFIX = f"{_cache_prefix}:"
_ip_meta = os.environ.get("CCLY_RATELIMIT_IP_META_KEY", "").strip()
if _ip_meta:
    RATELIMIT_IP_META_KEY = _ip_meta

contribute_settings(sys.modules[__name__], CCLY_APPS)
