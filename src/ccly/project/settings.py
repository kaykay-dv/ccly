"""Settings for the embedded project. Values come from the current directory's .env."""

from __future__ import annotations

import os
import sys
from datetime import timedelta
from pathlib import Path

import dj_database_url
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


_secret = os.environ.get("CCLY_SECRET_KEY", "").strip()
if not _secret:
    from django.core.exceptions import ImproperlyConfigured

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
        os.environ.get("CCLY_DATABASE_URL", "sqlite:///db.sqlite3")
    )
}

LANGUAGE_CODE = os.environ.get("CCLY_LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("CCLY_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = Path.cwd() / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/m/login/"

DEFAULT_FROM_EMAIL = os.environ.get("CCLY_DEFAULT_FROM_EMAIL", "webmaster@localhost")
MAILERS = {
    "default": {
        "BACKEND": os.environ.get(
            "CCLY_EMAIL_BACKEND",
            "django.core.mail.backends.console.EmailBackend",
        ),
    },
}

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

contribute_settings(sys.modules[__name__], CCLY_APPS)
