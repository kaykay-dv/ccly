# ccly

![Alaska](src/ccly/templates/app/static/img/alaska.png)

ccly (a nod to "Cicely" in [Northern Exposure](https://en.wikipedia.org/wiki/Northern_Exposure)) is a Django project you carry with you. It is particularly targeted at those who want to write Django-based microservices. ccly is opinionated in that it comes with a variety of pre-selected third-party apps.

The project lives in this package. A site is only a directory with a `.env` file. The apps you build are separate, publishable packages.

## Included

Admin is served at `/m/`. Django REST framework and an OpenAPI document (drf-spectacular) are included. django-axes watches login attempts, and django-ratelimit caps traffic at 60 requests a minute for each signed-in user, or for each IP when nobody is signed in.

## Install

ccly is not on PyPI. Install it from GitHub with git:

```bash
pip install git+https://github.com/kaykay-dv/ccly.git
```

Python 3.11 or newer.

## Create an app

```bash
ccly create bulletin
cd bulletin
pip install -e .
```

That writes a src-layout package, including `AGENTS.md` and a Sphinx project that uses the Read the Docs theme. The HTML is built into `docs/_build/html/`. It includes `GET /bulletin/health/`, which returns the JSON string `"OK"`.

## Start a site

From any other directory:

```bash
ccly init bulletin
ccly migrate
ccly createsuperuser
ccly runserver
```

`ccly ini` is an alias of `ccly init`. Pass `--force` to replace an existing `.env`.

### Addresses

- Admin: http://127.0.0.1:8000/m/
- OpenAPI docs: http://127.0.0.1:8000/api/docs/
- Schema: http://127.0.0.1:8000/api/schema/
- Health: http://127.0.0.1:8000/bulletin/health/

### Admin

The admin login heading, the browser title, and the admin header use the installed PyPI name of the apps in `CCLY_APPS`. Set `CCLY_SITE_NAME` to override that. `CCLY_SITE_NAME` is optional; when it is unset, the admin title is the PyPI name of each app in `CCLY_APPS`.

After you sign in, the upper-right corner of the admin has an OpenAPI link. The login form links to password reset, and the reset message is printed to the console unless you point `CCLY_EMAIL_BACKEND` at a real mailer. The account needs an email address.

### Django commands

Any other command is passed to Django:

```bash
ccly makemigrations
ccly check
ccly shell
```

## Configuration

`ccly init` writes a `.env` file. These are the variables and the defaults that are used.

### Core

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_SECRET_KEY` | Django secret key | Generated |
| `CCLY_DEBUG` | Debug mode | `true` |
| `CCLY_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CCLY_APPS` | Comma-separated import names to install and mount | App names passed to `ccly init` |
| `CCLY_DATABASE_URL` | Database URL | `sqlite:///db.sqlite3` |
| `CCLY_CONN_MAX_AGE` | Persistent database connections, in seconds | `0` |
| `CCLY_TIME_ZONE` | Time zone | Machine time zone, or `UTC` |
| `CCLY_LANGUAGE_CODE` | Language code | Machine language, or `en-us` |
| `CCLY_STATIC_URL` | Static URL | `static/` |

Set `CCLY_CONN_MAX_AGE` above `0` when the database is not SQLite.

### Cookies and cache

`ccly init` invents a new session cookie, CSRF cookie, language cookie, and cache prefix for each site. Two sites can then be served from the same domain without sharing logins or cache entries. Leave `CCLY_COOKIE_DOMAIN` empty so those cookies stay on that host.

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_SESSION_COOKIE_NAME` | Session cookie. Unique per site | `ccly_<id>_session` |
| `CCLY_CSRF_COOKIE_NAME` | CSRF cookie. Unique per site | `ccly_<id>_csrf` |
| `CCLY_LANGUAGE_COOKIE_NAME` | Language cookie. Unique per site | `ccly_<id>_language` |
| `CCLY_CACHE_PREFIX` | Cache key prefix. Unique per site | `ccly_<id>` |
| `CCLY_COOKIE_DOMAIN` | Cookie domain. Empty keeps cookies on this host | Empty |
| `CCLY_SESSION_COOKIE_PATH` | Session cookie path | `/` |
| `CCLY_CSRF_COOKIE_PATH` | CSRF cookie path | `/` |
| `CCLY_SESSION_COOKIE_SAMESITE` | `Lax`, `Strict`, or `None` | `Lax` |
| `CCLY_CSRF_COOKIE_SAMESITE` | `Lax`, `Strict`, or `None` | `Lax` |
| `CCLY_COOKIE_SECURE` | Secure flag for the session, CSRF, and language cookies | `false` |

The default cache is per process. Point Django at a shared cache when you run more than one process. The cache prefix keeps two sites apart when they share that cache.

### HTTPS

For a public HTTPS server, set `CCLY_DEBUG=false`, `CCLY_COOKIE_SECURE=true`, `CCLY_SECURE_SSL_REDIRECT=true`, and `CCLY_SECURE_HSTS_SECONDS=31536000`. Behind a reverse proxy, set `CCLY_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https` and list the public origins in `CCLY_CSRF_TRUSTED_ORIGINS` (for example `https://bulletin.example.com`).

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `false` |
| `CCLY_SECURE_HSTS_SECONDS` | HSTS lifetime. `0` disables it | `0` |
| `CCLY_SECURE_HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `false` |
| `CCLY_SECURE_HSTS_PRELOAD` | Allow HSTS preload | `false` |
| `CCLY_SECURE_PROXY_SSL_HEADER` | Proxy HTTPS header, for example `HTTP_X_FORWARDED_PROTO,https` | Empty |
| `CCLY_CSRF_TRUSTED_ORIGINS` | Comma-separated origins, including the scheme | Empty |
| `CCLY_USE_X_FORWARDED_HOST` | Trust `X-Forwarded-Host` from a proxy | `false` |

### Email

To send mail, set `CCLY_EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` and fill in `CCLY_EMAIL_HOST`.

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_EMAIL_BACKEND` | Email backend | `django.core.mail.backends.console.EmailBackend` |
| `CCLY_DEFAULT_FROM_EMAIL` | From address for password reset | `webmaster@localhost` |
| `CCLY_EMAIL_HOST` | SMTP host, used when the backend is SMTP | `localhost` |
| `CCLY_EMAIL_PORT` | SMTP port | `587` |
| `CCLY_EMAIL_HOST_USER` | SMTP username | Empty |
| `CCLY_EMAIL_HOST_PASSWORD` | SMTP password | Empty |
| `CCLY_EMAIL_USE_TLS` | STARTTLS. Do not enable this and SSL together | `true` |
| `CCLY_EMAIL_USE_SSL` | Implicit TLS. Do not enable this and TLS together | `false` |

### Login lockout

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_AXES_FAILURE_LIMIT` | Failed logins before lockout | `5` |
| `CCLY_AXES_COOLOFF_HOURS` | Lockout cooloff in hours | `1` |

### Rate limiting

Static files are not counted. A request past the rate gets HTTP 403.

`CCLY_RATELIMIT_IP_META_KEY` is optional. Set it to the request header your proxy uses, such as `HTTP_X_FORWARDED_FOR`, when `REMOTE_ADDR` is not the client.

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_RATELIMIT_ENABLE` | Rate limiting | `true` |
| `CCLY_RATELIMIT_RATE` | Allowed requests. Empty means no limit | `60/m` |
| `CCLY_RATELIMIT_KEY` | Who is counted: `user_or_ip`, `ip`, or `user` | `user_or_ip` |
| `CCLY_RATELIMIT_FAIL_OPEN` | Allow requests when the cache is down | `false` |

## Apps

Each app that provides a `urls` module is mounted at `/<app_name>/`.

### App settings

An app can also provide `ccly_settings.py`. Uppercase names in that module are added to the Django settings, for example an external API URL:

```python
EXTERNAL_API_URL = "https://api.example.com"
```

A later app replaces a value that ccly, or an earlier app, already set. `INSTALLED_APPS` is extended instead: names from the app are appended, and names already present stay where they are.

```python
INSTALLED_APPS = ["third.party.app"]
```

### Environment settings

A setting that belongs to the app, but must be configured per site, is read from `.env` with `env`. ccly records each call. Startup fails when a required variable is missing or blank:

```python
from ccly.env import env

CCLY_API_KEY = env("CCLY_API_KEY", required=True)
```

### Logo

`CCLY_LOGO` is the static path of the image shown to the left of the project name in the admin. A new app sets it to `img/alaska.png` and ships that file in `src/<app>/static/img`. Change the setting, and add the new file under `static/`, to use another logo.

## Extras

`--extras` takes one or more optional features. Each feature is a plugin.

`oauth_client` adds [mozilla-django-oidc](https://github.com/mozilla/mozilla-django-oidc):

```bash
ccly create bulletin --extras oauth_client
```

The app's `ccly_settings.py` wires the OpenID Connect client. After the app is installed, `ccly init` writes the provider's client id, secret, and endpoint URLs into `.env`. The callback URL is `http://127.0.0.1:8000/oidc/callback/`.

`oauth_provider` adds [django-oauth-toolkit](https://django-oauth-toolkit.readthedocs.io/en/latest/) so the site can issue tokens:

```bash
ccly create bulletin --extras oauth_provider
```

`ccly migrate` creates the provider tables. Register an application in the admin, then use the endpoints under `/o/`: `/o/authorize/`, `/o/token/`, `/o/revoke_token/`, and `/o/introspect/`. A browser that is not signed in is sent to `/m/login/`.

| Variable | Purpose | Default |
| --- | --- | --- |
| `OAUTHLIB_INSECURE_TRANSPORT` | Allow HTTP. Any value counts, including `false`; clear it to require HTTPS | `1` |
| `OAUTH2_ACCESS_TOKEN_EXPIRE_SECONDS` | Access token lifetime | `3600` |
| `OAUTH2_REFRESH_TOKEN_EXPIRE_SECONDS` | Idle refresh token lifetime. `0` means no expiry | `1209600` (14 days) |
| `OAUTH2_PKCE_REQUIRED` | Require PKCE on the authorization code grant | `true` |
| `OAUTH2_ROTATE_REFRESH_TOKEN` | Issue a new refresh token on each refresh | `true` |
| `OAUTH2_REFRESH_TOKEN_REUSE_PROTECTION` | Revoke the token family when a rotated refresh token is reused | `true` |
| `OAUTH2_ALLOWED_REDIRECT_URI_SCHEMES` | Comma-separated redirect schemes. Use `https` on a public site | `http,https` |
| `OAUTH2_SCOPES` | Comma-separated `name:description` scopes | `read:Read scope,write:Write scope` |
| `OIDC_RSA_PRIVATE_KEY` | PEM private key. Empty keeps OpenID Connect off | Empty |

Before a public deployment, clear `OAUTHLIB_INSECURE_TRANSPORT` and set `OAUTH2_ALLOWED_REDIRECT_URI_SCHEMES=https`. Paste a PEM key into `OIDC_RSA_PRIVATE_KEY` to enable OpenID Connect; `openid` is added to the scopes when that key is set.

To accept a token on one view without replacing the project's API settings:

```python
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope

class MyView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["read"]
```

Several extras can be selected together:

```bash
ccly create bulletin --extras oauth_client oauth_provider
```

