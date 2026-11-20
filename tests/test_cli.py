import re
from pathlib import Path

from ccly.cli import local_language_code, local_time_zone, run
from ccly.scaffold import config_class_name, template_root


def test_help():
    assert run([]) == 0
    assert run(["--help"]) == 0


def test_create_writes_a_package(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run(["create", "my_app"]) == 0
    package = tmp_path / "my_app"
    pyproject = (package / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "my_app"' in pyproject
    assert 'only-include = ["src/my_app"]' in pyproject
    apps = (package / "src" / "my_app" / "apps.py").read_text(encoding="utf-8")
    assert f"class {config_class_name('my_app')}(" in apps
    assert 'name = "my_app"' in apps
    views = (package / "src" / "my_app" / "views.py").read_text(encoding="utf-8")
    assert "class HealthView" in views
    assert 'return Response("OK")' in views
    urls = (package / "src" / "my_app" / "urls.py").read_text(encoding="utf-8")
    assert 'path("health/"' in urls
    assert (package / "src" / "my_app" / "migrations" / "__init__.py").is_file()
    contributed = (package / "src" / "my_app" / "ccly_settings.py").read_text(encoding="utf-8")
    assert "Uppercase names" in contributed
    assert 'CCLY_LOGO = "img/alaska.png"' in contributed
    logo = package / "src" / "my_app" / "static" / "img" / "alaska.png"
    source = template_root() / "static" / "img" / "alaska.png"
    assert logo.read_bytes() == source.read_bytes()


def test_create_rejects_a_bad_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run(["create", "not-an-app"]) == 2
    assert "not a valid Python identifier" in capsys.readouterr().err
    assert run(["create", "class"]) == 2


def test_create_refuses_to_overwrite(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run(["create", "bulletin"]) == 0
    assert run(["create", "bulletin"]) == 1
    assert Path("bulletin").is_dir()


def test_init_writes_env_without_a_fixed_site_name(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run(["ini", "bulletin", "kbdr"]) == 0
    env = Path(".env").read_text(encoding="utf-8")
    assert "CCLY_APPS=bulletin,kbdr" in env
    assert "CCLY_DATABASE_URL=sqlite:///db.sqlite3" in env
    assert "CCLY_SECRET_KEY=" in env
    assert "CCLY_SITE_NAME" not in env
    assert "CCLY_RATELIMIT_ENABLE=true" in env
    assert "CCLY_RATELIMIT_RATE=60/m" in env
    assert "CCLY_RATELIMIT_KEY=user_or_ip" in env
    assert "CCLY_RATELIMIT_FAIL_OPEN=false" in env
    token = re.search(r"CCLY_SESSION_COOKIE_NAME=ccly_([0-9a-f]{8})_session", env)
    assert token
    site = token.group(1)
    assert f"CCLY_CSRF_COOKIE_NAME=ccly_{site}_csrf" in env
    assert f"CCLY_LANGUAGE_COOKIE_NAME=ccly_{site}_language" in env
    assert f"CCLY_CACHE_PREFIX=ccly_{site}" in env
    assert "CCLY_COOKIE_SECURE=false" in env
    assert "CCLY_SECURE_SSL_REDIRECT=false" in env
    assert "CCLY_SECURE_HSTS_SECONDS=0" in env
    assert "CCLY_SECURE_PROXY_SSL_HEADER=" in env
    assert "CCLY_CSRF_TRUSTED_ORIGINS=" in env
    assert "CCLY_CONN_MAX_AGE=0" in env
    assert "CCLY_EMAIL_HOST=" in env
    assert "CCLY_EMAIL_PORT=587" in env
    captured = capsys.readouterr()
    assert "pip install -e /path/to/bulletin" in captured.err
    assert "pip install -e /path/to/kbdr" in captured.err


def test_init_uses_the_machine_locale_when_it_can(tmp_path, monkeypatch):
    monkeypatch.setenv("TZ", "Europe/Vienna")
    monkeypatch.setenv("LANG", "de_AT.UTF-8")
    monkeypatch.delenv("LC_ALL", raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    monkeypatch.chdir(tmp_path)
    assert run(["init", "bulletin"]) == 0
    env = Path(".env").read_text(encoding="utf-8")
    assert "CCLY_TIME_ZONE=Europe/Vienna" in env
    assert "CCLY_LANGUAGE_CODE=de-at" in env


def test_init_falls_back_when_the_machine_locale_cannot_be_read(tmp_path, monkeypatch):
    monkeypatch.setenv("TZ", "Not/AZone")
    for name in ("LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.setenv(name, "C")
    monkeypatch.setattr("ccly.cli._zone_from_localtime", lambda: None)
    monkeypatch.setattr("ccly.cli._macos_language", lambda: None)
    monkeypatch.setattr("ccly.cli._language_from_process_locale", lambda: None)
    assert local_time_zone() == "UTC"
    assert local_language_code() == "en-us"
    monkeypatch.chdir(tmp_path)
    assert run(["init", "bulletin"]) == 0
    env = Path(".env").read_text(encoding="utf-8")
    assert "CCLY_TIME_ZONE=UTC" in env
    assert "CCLY_LANGUAGE_CODE=en-us" in env


def test_init_does_not_replace_env_without_force(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run(["init", "bulletin"]) == 0
    original = Path(".env").read_text(encoding="utf-8")
    assert run(["init", "kbdr"]) == 1
    assert Path(".env").read_text(encoding="utf-8") == original
    assert run(["init", "kbdr", "--force"]) == 0
    replaced = Path(".env").read_text(encoding="utf-8")
    assert replaced != original
    assert "CCLY_APPS=kbdr" in replaced


def test_init_cookie_names_differ_between_sites(tmp_path, monkeypatch):
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()
    monkeypatch.chdir(first)
    assert run(["init", "bulletin"]) == 0
    monkeypatch.chdir(second)
    assert run(["init", "bulletin"]) == 0

    def cookie_name(directory: Path) -> str:
        for line in (directory / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("CCLY_SESSION_COOKIE_NAME="):
                return line
        raise AssertionError("session cookie name was not written")

    assert cookie_name(first) != cookie_name(second)


def test_init_rejects_a_bad_name(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert run(["init", "not-an-app"]) == 2
    assert not Path(".env").exists()


def test_django_command_requires_env(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run(["check"]) == 1
    assert "ccly init" in capsys.readouterr().err
