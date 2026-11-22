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
LOGIN_REDIRECT_URL = env("OIDC_LOGIN_REDIRECT_URL", default="__CCLY_ADMIN_URL__")
LOGOUT_REDIRECT_URL = env("OIDC_LOGOUT_REDIRECT_URL", default="__CCLY_ADMIN_URL__")
"""


def _admin_url(app_name: str) -> str:
    if not app_name:
        return "/m/"
    return f"/{app_name}/m/"


class OAuthClient(Extra):
    """Relying party for an OpenID Connect provider."""

    name = "oauth_client"

    def settings_block(self, app_name: str = "") -> str:
        block = _SETTINGS.replace("__CCLY_ADMIN_URL__", _admin_url(app_name))
        return block.strip() + "\n"

    def dependencies(self) -> list[str]:
        return ["mozilla-django-oidc>=4.0"]

    def env_lines(self, app_names: list[str] | None = None) -> list[str]:
        admin_url = _admin_url(app_names[0] if app_names else "")
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
            f"OIDC_LOGIN_REDIRECT_URL={admin_url}",
            f"OIDC_LOGOUT_REDIRECT_URL={admin_url}",
        ]

    def urlpatterns(self) -> list:
        from django.urls import include, path

        # The library's callback is /oidc/callback/.
        return [path("oidc/", include("mozilla_django_oidc.urls"))]
