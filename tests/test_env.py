import sys
from types import ModuleType

import pytest

from ccly.env import advertised, clear, env
from ccly.project.app_settings import contribute_settings
from ccly.project.checks import check_advertised_env


@pytest.fixture(autouse=True)
def _fresh_registry():
    clear()
    yield
    clear()


def test_env_reads_a_value_and_advertises_it(monkeypatch):
    monkeypatch.setenv("CCLY_API_KEY", "secret")
    assert env("CCLY_API_KEY", required=True) == "secret"
    recorded = advertised()
    assert len(recorded) == 1
    assert recorded[0].name == "CCLY_API_KEY"
    assert recorded[0].required is True
    assert check_advertised_env(None) == []


def test_required_env_fails_the_startup_check_when_missing(monkeypatch):
    monkeypatch.delenv("CCLY_API_KEY", raising=False)
    assert env("CCLY_API_KEY", required=True) == ""
    errors = check_advertised_env(None)
    assert len(errors) == 1
    assert errors[0].id == "ccly.E001"
    assert "CCLY_API_KEY" in errors[0].msg
    assert ".env" in errors[0].hint


def test_blank_required_env_fails_the_startup_check(monkeypatch):
    monkeypatch.setenv("CCLY_API_KEY", "  ")
    env("CCLY_API_KEY", required=True)
    assert check_advertised_env(None)


def test_optional_env_uses_its_default_and_does_not_fail(monkeypatch):
    monkeypatch.delenv("CCLY_API_KEY", raising=False)
    assert env("CCLY_API_KEY", default="") == ""
    assert check_advertised_env(None) == []


def test_required_env_rejects_a_default():
    with pytest.raises(TypeError):
        env("CCLY_API_KEY", default="x", required=True)
    assert advertised() == ()


def test_oauth_provider_uses_env_defaults(monkeypatch):
    for name in (
        "OAUTH2_SCOPES",
        "OAUTH2_ACCESS_TOKEN_EXPIRE_SECONDS",
        "OAUTH2_REFRESH_TOKEN_EXPIRE_SECONDS",
        "OAUTH2_PKCE_REQUIRED",
        "OAUTH2_ROTATE_REFRESH_TOKEN",
        "OAUTH2_REFRESH_TOKEN_REUSE_PROTECTION",
        "OAUTH2_ALLOWED_REDIRECT_URI_SCHEMES",
        "OIDC_RSA_PRIVATE_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    from ccly.extras.oauth_provider import OAuthProvider

    namespace: dict = {}
    exec(OAuthProvider().settings_block(), namespace)
    provider = namespace["OAUTH2_PROVIDER"]
    assert namespace["INSTALLED_APPS"] == ["oauth2_provider"]
    assert provider["ACCESS_TOKEN_EXPIRE_SECONDS"] == 3600
    assert provider["REFRESH_TOKEN_EXPIRE_SECONDS"] == 1209600
    assert provider["PKCE_REQUIRED"] is True
    assert provider["ROTATE_REFRESH_TOKEN"] is True
    assert provider["REFRESH_TOKEN_REUSE_PROTECTION"] is True
    assert provider["ALLOWED_REDIRECT_URI_SCHEMES"] == ["http", "https"]
    assert provider["SCOPES"] == {"read": "Read scope", "write": "Write scope"}
    assert "OIDC_ENABLED" not in provider


def test_oauth_provider_enables_oidc_when_a_private_key_is_set(monkeypatch):
    monkeypatch.setenv("OIDC_RSA_PRIVATE_KEY", "-----BEGIN PRIVATE KEY-----\\nabc")
    monkeypatch.setenv("OAUTH2_SCOPES", "read:Read")
    monkeypatch.setenv("OAUTH2_PKCE_REQUIRED", "false")
    from ccly.extras.oauth_provider import OAuthProvider

    namespace: dict = {}
    exec(OAuthProvider().settings_block(), namespace)
    provider = namespace["OAUTH2_PROVIDER"]
    assert provider["OIDC_ENABLED"] is True
    assert provider["OIDC_RSA_PRIVATE_KEY"].startswith("-----BEGIN")
    assert provider["SCOPES"]["openid"] == "OpenID Connect scope"
    assert provider["SCOPES"]["read"] == "Read"
    assert provider["PKCE_REQUIRED"] is False


def test_oauth_provider_is_mounted_at_o(monkeypatch):
    import django.urls

    monkeypatch.setattr(django.urls, "include", lambda name: name)
    monkeypatch.setattr(django.urls, "path", lambda route, view: (route, view))
    from ccly.extras.oauth_provider import OAuthProvider

    assert OAuthProvider().urlpatterns() == [("o/", "oauth2_provider.urls")]


def test_oauth_client_callback_is_mounted_at_oidc(monkeypatch):
    import django.urls

    monkeypatch.setattr(django.urls, "include", lambda name: name)
    monkeypatch.setattr(django.urls, "path", lambda route, view: (route, view))
    from ccly.extras.oauth_client import OAuthClient

    assert OAuthClient().urlpatterns() == [("oidc/", "mozilla_django_oidc.urls")]


def test_app_setting_from_env_is_copied_onto_the_project(tmp_path, monkeypatch):
    monkeypatch.setenv("CCLY_API_KEY", "secret")
    package = tmp_path / "bulletin"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "ccly_settings.py").write_text(
        "from ccly.env import env\n"
        'CCLY_API_KEY = env("CCLY_API_KEY", required=True)\n',
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    for loaded in list(sys.modules):
        if loaded == "bulletin" or loaded.startswith("bulletin."):
            del sys.modules[loaded]
    try:
        target = ModuleType("target")
        contribute_settings(target, ["bulletin"])
        assert target.CCLY_API_KEY == "secret"
        assert advertised()[0].module == "bulletin.ccly_settings"
        assert check_advertised_env(None) == []
    finally:
        for loaded in list(sys.modules):
            if loaded == "bulletin" or loaded.startswith("bulletin."):
                del sys.modules[loaded]
