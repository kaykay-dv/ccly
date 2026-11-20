"""OAuth 2 authorization server backed by django-oauth-toolkit."""

from __future__ import annotations

from ccly.extras.base import Extra

_SETTINGS = """
from ccly.env import env

# OAuth 2 provider. https://django-oauth-toolkit.readthedocs.io/
INSTALLED_APPS = ["oauth2_provider"]


def _oauth2_flag(value):
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _oauth2_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def _oauth2_scopes(value):
    scopes = {}
    for item in _oauth2_csv(value):
        name, _, description = item.partition(":")
        name = name.strip()
        if name:
            scopes[name] = description.strip() or name
    return scopes


_oauth2_scopes_value = _oauth2_scopes(
    env("OAUTH2_SCOPES", default="read:Read scope,write:Write scope")
)
_oauth2_private_key = env("OIDC_RSA_PRIVATE_KEY", default="")
if _oauth2_private_key and "openid" not in _oauth2_scopes_value:
    _oauth2_scopes_value["openid"] = "OpenID Connect scope"

OAUTH2_PROVIDER = {
    "ACCESS_TOKEN_EXPIRE_SECONDS": int(
        env("OAUTH2_ACCESS_TOKEN_EXPIRE_SECONDS", default="3600")
    ),
    "REFRESH_TOKEN_EXPIRE_SECONDS": int(
        env("OAUTH2_REFRESH_TOKEN_EXPIRE_SECONDS", default="1209600")
    ),
    "PKCE_REQUIRED": _oauth2_flag(env("OAUTH2_PKCE_REQUIRED", default="true")),
    "ROTATE_REFRESH_TOKEN": _oauth2_flag(
        env("OAUTH2_ROTATE_REFRESH_TOKEN", default="true")
    ),
    "REFRESH_TOKEN_REUSE_PROTECTION": _oauth2_flag(
        env("OAUTH2_REFRESH_TOKEN_REUSE_PROTECTION", default="true")
    ),
    "ALLOWED_REDIRECT_URI_SCHEMES": _oauth2_csv(
        env("OAUTH2_ALLOWED_REDIRECT_URI_SCHEMES", default="http,https")
    ),
    "SCOPES": _oauth2_scopes_value,
}
if _oauth2_private_key:
    OAUTH2_PROVIDER["OIDC_ENABLED"] = True
    OAUTH2_PROVIDER["OIDC_RSA_PRIVATE_KEY"] = _oauth2_private_key
"""


class OAuthProvider(Extra):
    """Authorization server for OAuth 2, with optional OpenID Connect."""

    name = "oauth_provider"

    def settings_block(self) -> str:
        return _SETTINGS.strip() + "\n"

    def dependencies(self) -> list[str]:
        return ["django-oauth-toolkit>=3.0,<4"]

    def env_lines(self) -> list[str]:
        return [
            "",
            "# OAuth 2 provider (django-oauth-toolkit). Endpoints are under /o/.",
            "# Any value allows HTTP, including the word false. Clear it to require HTTPS.",
            "OAUTHLIB_INSECURE_TRANSPORT=1",
            "OAUTH2_ACCESS_TOKEN_EXPIRE_SECONDS=3600",
            "OAUTH2_REFRESH_TOKEN_EXPIRE_SECONDS=1209600",
            "OAUTH2_PKCE_REQUIRED=true",
            "OAUTH2_ROTATE_REFRESH_TOKEN=true",
            "OAUTH2_REFRESH_TOKEN_REUSE_PROTECTION=true",
            "OAUTH2_ALLOWED_REDIRECT_URI_SCHEMES=http,https",
            "OAUTH2_SCOPES=read:Read scope,write:Write scope",
            "# Paste a PEM private key to enable OpenID Connect. Leave empty for OAuth 2 only.",
            "OIDC_RSA_PRIVATE_KEY=",
        ]

    def urlpatterns(self) -> list:
        from django.urls import include, path

        return [path("o/", include("oauth2_provider.urls"))]
