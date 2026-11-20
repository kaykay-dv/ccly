"""OpenID Connect client backed by mozilla-django-oidc."""

from __future__ import annotations

from ccly.extras.base import Extra

_SETTINGS = """
from ccly.env import env

# OpenID Connect client. https://github.com/mozilla/mozilla-django-oidc
INSTALLED_APPS = ["mozilla_django_oidc"]
AUTHENTICATION_BACKENDS = [
    "mozilla_django_oidc.auth.OIDCAuthenticationBackend",
]
MIDDLEWARE = ["mozilla_django_oidc.middleware.SessionRefresh"]
OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID", required=True)
OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET", required=True)
OIDC_OP_AUTHORIZATION_ENDPOINT = env("OIDC_OP_AUTHORIZATION_ENDPOINT", required=True)
OIDC_OP_TOKEN_ENDPOINT = env("OIDC_OP_TOKEN_ENDPOINT", required=True)
OIDC_OP_USER_ENDPOINT = env("OIDC_OP_USER_ENDPOINT", required=True)
OIDC_RP_SIGN_ALGO = env("OIDC_RP_SIGN_ALGO", default="RS256")
OIDC_RP_SCOPES = env("OIDC_RP_SCOPES", default="openid email")
_oidc_jwks = env("OIDC_OP_JWKS_ENDPOINT", default="")
if _oidc_jwks:
    OIDC_OP_JWKS_ENDPOINT = _oidc_jwks
LOGIN_REDIRECT_URL = env("OIDC_LOGIN_REDIRECT_URL", default="/m/")
LOGOUT_REDIRECT_URL = env("OIDC_LOGOUT_REDIRECT_URL", default="/m/")
"""


class OAuthClient(Extra):
    """Relying party for an OpenID Connect provider."""

    name = "oauth_client"

    def settings_block(self) -> str:
        return _SETTINGS.strip() + "\n"

    def dependencies(self) -> list[str]:
        return ["mozilla-django-oidc>=4.0"]

    def env_lines(self) -> list[str]:
        return [
            "",
            "# OpenID Connect client (mozilla-django-oidc).",
            "OIDC_RP_CLIENT_ID=",
            "OIDC_RP_CLIENT_SECRET=",
            "OIDC_OP_AUTHORIZATION_ENDPOINT=",
            "OIDC_OP_TOKEN_ENDPOINT=",
            "OIDC_OP_USER_ENDPOINT=",
            "OIDC_OP_JWKS_ENDPOINT=",
            "OIDC_RP_SIGN_ALGO=RS256",
            "OIDC_RP_SCOPES=openid email",
            "OIDC_LOGIN_REDIRECT_URL=/m/",
            "OIDC_LOGOUT_REDIRECT_URL=/m/",
        ]

    def urlpatterns(self) -> list:
        from django.urls import include, path

        # The library's callback is /oidc/callback/.
        return [path("oidc/", include("mozilla_django_oidc.urls"))]
