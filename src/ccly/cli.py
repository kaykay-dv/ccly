"""Command line for the Cicely Django project."""

from __future__ import annotations

import argparse
import importlib.util
import os
import secrets
import sys
from pathlib import Path

from ccly.scaffold import create_app, validate_app_name

HELP = """\
ccly — Cicely, a portable Django project.

The Django project lives in this package. A site is a directory with a .env
file. Apps you create are separate packages that the site loads by name.

Usage:
  ccly create <app_name>
  ccly init <app_name> [<app_name> ...] [--force]
  ccly ini <app_name> [<app_name> ...] [--force]
  ccly <django management command> [options]

Examples:
  ccly create bulletin
  pip install -e ./bulletin
  ccly init bulletin
  ccly migrate
  ccly createsuperuser
  ccly runserver
"""


def main(argv: list[str] | None = None) -> None:
    sys.exit(run(argv))


def run(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print(HELP)
        return 0
    command, rest = args[0], args[1:]
    if command == "create":
        return _command_create(rest)
    if command in {"init", "ini"}:
        return _command_init(rest)
    return _command_django(args)


def _command_create(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="ccly create",
        description="Create a Django app packaged for PyPI.",
    )
    parser.add_argument("app_name", help="Importable package name")
    parsed = _parse(parser, argv)
    if isinstance(parsed, int):
        return parsed
    return create_app(parsed.app_name)


def _command_init(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="ccly init",
        description="Write a .env that loads one or more installed apps.",
    )
    parser.add_argument("app_name", nargs="+", help="Importable app names")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing .env",
    )
    parsed = _parse(parser, argv)
    if isinstance(parsed, int):
        return parsed
    for app_name in parsed.app_name:
        error = validate_app_name(app_name)
        if error:
            print(error, file=sys.stderr)
            return 2
    env_path = Path.cwd() / ".env"
    if env_path.exists() and not parsed.force:
        print(f"{env_path} already exists. Pass --force to replace it.", file=sys.stderr)
        return 1
    env_path.write_text(_render_env(parsed.app_name), encoding="utf-8")
    print(f"Wrote {env_path}")
    missing = [name for name in parsed.app_name if importlib.util.find_spec(name) is None]
    if missing:
        print("These apps are not installed in this environment:", file=sys.stderr)
        for name in missing:
            print(f"  pip install -e /path/to/{name}", file=sys.stderr)
    return 0


def _command_django(argv: list[str]) -> int:
    if not (Path.cwd() / ".env").is_file():
        print("No .env in this directory. Run: ccly init <app_name>", file=sys.stderr)
        return 1
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ccly.project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(["ccly", *argv])
    return 0


def _render_env(app_names: list[str]) -> str:
    secret = secrets.token_urlsafe(50)
    site = secrets.token_hex(4)
    apps = ",".join(app_names)
    lines = [
        "# Local ccly site. Do not commit this file.",
        f"CCLY_SECRET_KEY={secret}",
        "CCLY_DEBUG=true",
        "CCLY_ALLOWED_HOSTS=localhost,127.0.0.1",
        f"CCLY_APPS={apps}",
        "CCLY_DATABASE_URL=sqlite:///db.sqlite3",
        "CCLY_CONN_MAX_AGE=0",
        "CCLY_TIME_ZONE=UTC",
        "CCLY_LANGUAGE_CODE=en-us",
        "CCLY_STATIC_URL=static/",
        "",
        "# Unique to this site, so another ccly instance can use the same domain.",
        f"CCLY_SESSION_COOKIE_NAME=ccly_{site}_session",
        f"CCLY_CSRF_COOKIE_NAME=ccly_{site}_csrf",
        f"CCLY_LANGUAGE_COOKIE_NAME=ccly_{site}_language",
        f"CCLY_CACHE_PREFIX=ccly_{site}",
        "CCLY_COOKIE_DOMAIN=",
        "CCLY_SESSION_COOKIE_PATH=/",
        "CCLY_CSRF_COOKIE_PATH=/",
        "CCLY_SESSION_COOKIE_SAMESITE=Lax",
        "CCLY_CSRF_COOKIE_SAMESITE=Lax",
        "",
        "# HTTPS deployment. Leave these off for a local http server.",
        "CCLY_COOKIE_SECURE=false",
        "CCLY_SECURE_SSL_REDIRECT=false",
        "CCLY_SECURE_HSTS_SECONDS=0",
        "CCLY_SECURE_HSTS_INCLUDE_SUBDOMAINS=false",
        "CCLY_SECURE_HSTS_PRELOAD=false",
        "CCLY_SECURE_PROXY_SSL_HEADER=",
        "CCLY_CSRF_TRUSTED_ORIGINS=",
        "CCLY_USE_X_FORWARDED_HOST=false",
        "",
        "CCLY_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend",
        "CCLY_DEFAULT_FROM_EMAIL=webmaster@localhost",
        "CCLY_EMAIL_HOST=",
        "CCLY_EMAIL_PORT=587",
        "CCLY_EMAIL_HOST_USER=",
        "CCLY_EMAIL_HOST_PASSWORD=",
        "CCLY_EMAIL_USE_TLS=true",
        "CCLY_EMAIL_USE_SSL=false",
        "",
        "CCLY_AXES_FAILURE_LIMIT=5",
        "CCLY_AXES_COOLOFF_HOURS=1",
        "CCLY_RATELIMIT_ENABLE=true",
        "CCLY_RATELIMIT_RATE=60/m",
        "CCLY_RATELIMIT_KEY=user_or_ip",
        "CCLY_RATELIMIT_FAIL_OPEN=false",
        "",
    ]
    return "\n".join(lines)


def _parse(parser: argparse.ArgumentParser, argv: list[str]):
    try:
        return parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return int(code)
