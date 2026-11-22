import importlib
import importlib.metadata
import os
import re
import sys
from pathlib import Path

import pytest

from ccly.cli import run

APP_NAME = "cclysampleapp"


def _install_app(app_dir: Path, app_name: str) -> None:
    """Expose the generated package and its distribution metadata on sys.path.

    This is the same information ``pip install -e`` publishes: an importable
    package plus a dist-info directory whose Name is the PyPI name.
    """
    src = app_dir / "src"
    dist_info = src / f"{app_name}-0.1.0.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        "Metadata-Version: 2.1\n" f"Name: {app_name}\n" "Version: 0.1.0\n",
        encoding="utf-8",
    )
    (dist_info / "top_level.txt").write_text(f"{app_name}\n", encoding="utf-8")
    sys.path.insert(0, str(src))
    importlib.invalidate_caches()


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    work = tmp_path_factory.mktemp("ccly-site")
    app_parent = work / "package"
    app_parent.mkdir()
    site_dir = work / "site"
    site_dir.mkdir()
    previous = Path.cwd()
    previous_env = {
        key: os.environ[key]
        for key in os.environ
        if key.startswith("CCLY_") or key == "DJANGO_SETTINGS_MODULE"
    }
    for key in previous_env:
        del os.environ[key]
    try:
        os.chdir(app_parent)
        assert run(["create", APP_NAME]) == 0
        settings_module = (
            app_parent / APP_NAME / "src" / APP_NAME / "ccly_settings.py"
        )
        existing = settings_module.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        settings_module.write_text(
            existing + 'EXTERNAL_API_URL = "https://api.example.com"\n',
            encoding="utf-8",
        )
        _install_app(app_parent / APP_NAME, APP_NAME)
        os.chdir(site_dir)
        assert run(["init", APP_NAME]) == 0
        # The login copy below is the English admin string. Init may have
        # copied this machine's language, so the site under test stays en-us.
        env_file = site_dir / ".env"
        env_file.write_text(
            re.sub(
                r"^CCLY_LANGUAGE_CODE=.*$",
                "CCLY_LANGUAGE_CODE=en-us",
                env_file.read_text(encoding="utf-8"),
                count=1,
                flags=re.M,
            ),
            encoding="utf-8",
        )
        os.environ["DJANGO_SETTINGS_MODULE"] = "ccly.project.settings"
        import django
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        from django.test import Client

        django.setup()
        call_command("migrate", verbosity=0)
        call_command("check")
        user = get_user_model().objects.create_superuser(
            "admin",
            "admin@example.com",
            "s3cret-pass",
        )
        anonymous = Client()
        anonymous.defaults["HTTP_HOST"] = "localhost"
        staff = Client()
        staff.defaults["HTTP_HOST"] = "localhost"
        staff.force_login(user)
        yield {"app_name": APP_NAME, "anonymous": anonymous, "staff": staff}
    finally:
        os.chdir(previous)
        for key in list(os.environ):
            if key.startswith("CCLY_") or key == "DJANGO_SETTINGS_MODULE":
                del os.environ[key]
        os.environ.update(previous_env)


def test_app_settings_are_added_to_the_project(site):
    from django.conf import settings

    assert settings.EXTERNAL_API_URL == "https://api.example.com"


def test_installed_distribution_name_matches_the_package(site):
    mapping = importlib.metadata.packages_distributions()
    assert site["app_name"] in mapping.get(site["app_name"], [])
    from django.conf import settings
    from django.contrib import admin

    assert settings.CCLY_SITE_TITLE == site["app_name"]
    assert admin.site.site_header == site["app_name"]
    assert admin.site.site_title == site["app_name"]


def test_site_uses_its_own_cookies_and_local_production_defaults(site):
    from django.conf import settings

    name = settings.SESSION_COOKIE_NAME
    token = re.fullmatch(r"ccly_([0-9a-f]{8})_session", name)
    assert token
    site_id = token.group(1)
    assert settings.CSRF_COOKIE_NAME == f"ccly_{site_id}_csrf"
    assert settings.LANGUAGE_COOKIE_NAME == f"ccly_{site_id}_language"
    assert settings.CACHES["default"]["KEY_PREFIX"] == f"ccly_{site_id}"
    assert settings.SESSION_COOKIE_SECURE is False
    assert settings.CSRF_COOKIE_SECURE is False
    assert settings.SECURE_SSL_REDIRECT is False
    assert settings.SECURE_HSTS_SECONDS == 0
    assert settings.CSRF_TRUSTED_ORIGINS == []
    assert settings.DATABASES["default"]["CONN_MAX_AGE"] == 0
    assert settings.CCLY_ADMIN_IDLE_SECONDS == 1800
    assert settings.SESSION_COOKIE_AGE == 1800
    assert settings.SESSION_SAVE_EVERY_REQUEST is True

    response = site["anonymous"].get(f"/{site['app_name']}/m/login/")
    assert settings.CSRF_COOKIE_NAME in response.cookies


def test_login_uses_the_package_name_and_password_reset(site):
    from django.conf import settings

    admin = f"/{site['app_name']}/m/"
    assert settings.LOGIN_URL == f"{admin}login/"
    assert site["anonymous"].get("/m/login/").status_code == 404
    response = site["anonymous"].get(f"{admin}login/")
    body = response.content.decode()
    assert response.status_code == 200
    assert site["app_name"] in body
    assert f"{admin}password_reset/" in body
    assert "Forgotten your login credentials?" in body


def test_admin_navbar_shows_the_logo_beside_the_project_name(site):
    from django.conf import settings
    from django.contrib.staticfiles.finders import find

    assert settings.CCLY_LOGO == "img/alaska.png"
    found = find("img/alaska.png")
    assert found is not None
    assert Path(found).read_bytes().startswith(b"\x89PNG")

    response = site["staff"].get(f"/{site['app_name']}/m/")
    body = response.content.decode()
    assert response.status_code == 200
    start = body.index('id="site-name"')
    brand = body[start : body.index("</div>", start)]
    # The app name also appears in the admin URL, so check the visible label.
    assert f'class="ccly-logo">{site["app_name"]}' in brand
    assert 'src="/static/img/alaska.png"' in brand


def _signed_in_client():
    from django.contrib.auth import get_user_model
    from django.test import Client

    client = Client()
    client.defaults["HTTP_HOST"] = "localhost"
    client.force_login(get_user_model().objects.get(username="admin"))
    return client


def test_admin_idle_script_is_only_on_signed_in_pages(site):
    from django.conf import settings

    admin = f"/{site['app_name']}/m/"
    signed_in = site["staff"].get(admin)
    body = signed_in.content.decode()
    assert signed_in.status_code == 200
    assert 'id="ccly-admin-idle"' in body
    assert 'data-idle-seconds="1800"' in body
    assert f'data-idle-url="{admin}idle/"' in body
    assert f'data-idle-key="ccly-admin-idle:{settings.SESSION_COOKIE_NAME}"' in body
    assert "localStorage" in body
    assert 'getElementById("logout-form")' in body

    login = site["anonymous"].get(f"{admin}login/")
    assert login.status_code == 200
    assert 'id="ccly-admin-idle"' not in login.content.decode()


def test_admin_idle_keepalive(site):
    from django.conf import settings

    idle = f"/{site['app_name']}/m/idle/"
    anonymous = site["anonymous"].get(idle)
    assert anonymous.status_code == 401

    response = site["staff"].get(idle)
    assert response.status_code == 204
    assert response.content == b""
    cookie = response.cookies[settings.SESSION_COOKIE_NAME]
    assert int(cookie["max-age"]) == settings.SESSION_COOKIE_AGE


def test_expired_admin_session_returns_to_login(site):
    from datetime import timedelta

    from django.contrib.sessions.models import Session
    from django.utils import timezone

    client = _signed_in_client()
    stored = Session.objects.get(session_key=client.session.session_key)
    stored.expire_date = timezone.now() - timedelta(seconds=1)
    stored.save()
    response = client.get(f"/{site['app_name']}/m/")
    assert response.status_code == 302
    assert "/login/" in response.url


def test_admin_logout_ends_the_session(site):
    client = _signed_in_client()
    admin = f"/{site['app_name']}/m/"
    response = client.post(f"{admin}logout/")
    assert response.status_code == 200
    assert "Logged out" in response.content.decode()
    assert "_auth_user_id" not in client.session
    follow = client.get(admin)
    assert follow.status_code == 302
    assert "/login/" in follow.url


def test_admin_header_links_to_openapi(site):
    response = site["staff"].get(f"/{site['app_name']}/m/")
    body = response.content.decode()
    assert response.status_code == 200
    assert site["app_name"] in body
    assert 'class="ccly-openapi"' in body
    assert 'href="/api/docs/"' in body
    assert ">OpenAPI<" in body

    password_change = site["staff"].get(f"/{site['app_name']}/m/password_change/")
    assert password_change.status_code == 200
    assert ">OpenAPI<" in password_change.content.decode()


def test_ratelimit_uses_env_defaults_and_blocks_past_the_rate(site):
    from django.conf import settings
    from django.core.cache import cache
    from django.test import override_settings

    assert settings.RATELIMIT_ENABLE is True
    assert settings.RATELIMIT_FAIL_OPEN is False
    assert settings.CCLY_RATELIMIT_RATE == "60/m"
    assert settings.CCLY_RATELIMIT_KEY == "user_or_ip"

    health = f"/{site['app_name']}/health/"
    cache.clear()
    try:
        with override_settings(CCLY_RATELIMIT_RATE="1/m"):
            first = site["anonymous"].get(health)
            second = site["anonymous"].get(health)
            static = site["anonymous"].get("/static/img/alaska.png")
        assert first.status_code == 200
        assert second.status_code == 403
        assert static.status_code != 403
    finally:
        cache.clear()


def test_healthcheck_returns_ok_json(site):
    response = site["anonymous"].get(f"/{site['app_name']}/health/")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    assert response.json() == "OK"


def test_schema_and_docs(site):
    schema = site["anonymous"].get("/api/schema/")
    assert schema.status_code == 200
    assert f"/{site['app_name']}/health/" in schema.content.decode()
    docs = site["anonymous"].get("/api/docs/")
    assert docs.status_code == 200
    assert site["app_name"] in docs.content.decode()
