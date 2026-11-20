# ccly

ccly (Cicely) is a Django project you carry with you. The project lives in this package. A site is only a directory with a `.env` file. The apps you build are separate, publishable packages.

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

That writes a src-layout package, including `AGENTS.md`. It includes `GET /bulletin/health/`, which returns the JSON string `"OK"`.

## Start a site

From any other directory:

```bash
ccly init bulletin
ccly migrate
ccly createsuperuser
ccly runserver
```

`ccly ini` is an alias of `ccly init`. Pass `--force` to replace an existing `.env`.

- Admin: http://127.0.0.1:8000/m/
- OpenAPI docs: http://127.0.0.1:8000/api/docs/
- Schema: http://127.0.0.1:8000/api/schema/
- Health: http://127.0.0.1:8000/bulletin/health/

The admin login heading, the browser title, and the admin header use the installed PyPI name of the apps in `CCLY_APPS`. Set `CCLY_SITE_NAME` to override that. After you sign in, the upper-right corner of the admin has an OpenAPI link. The login form links to password reset, and the reset message is printed to the console unless you point `CCLY_EMAIL_BACKEND` at a real mailer. The account needs an email address.

Any other command is passed to Django:

```bash
ccly makemigrations
ccly check
ccly shell
```

## Configuration

`ccly init` writes:

| Variable | Purpose | Default |
| --- | --- | --- |
| `CCLY_SECRET_KEY` | Django secret key | Generated |
| `CCLY_DEBUG` | Debug mode | `true` |
| `CCLY_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CCLY_APPS` | Comma-separated import names to install and mount | App names passed to `ccly init` |
| `CCLY_DATABASE_URL` | Database URL | `sqlite:///db.sqlite3` |
| `CCLY_CONN_MAX_AGE` | Persistent database connections, in seconds | `0` |
| `CCLY_TIME_ZONE` | Time zone | `UTC` |
| `CCLY_LANGUAGE_CODE` | Language code | `en-us` |
| `CCLY_STATIC_URL` | Static URL | `static/` |
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
| `CCLY_SECURE_SSL_REDIRECT` | Redirect HTTP to HTTPS | `false` |
| `CCLY_SECURE_HSTS_SECONDS` | HSTS lifetime. `0` disables it | `0` |
| `CCLY_SECURE_HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `false` |
| `CCLY_SECURE_HSTS_PRELOAD` | Allow HSTS preload | `false` |
| `CCLY_SECURE_PROXY_SSL_HEADER` | Proxy HTTPS header, for example `HTTP_X_FORWARDED_PROTO,https` | Empty |
| `CCLY_CSRF_TRUSTED_ORIGINS` | Comma-separated origins, including the scheme | Empty |
| `CCLY_USE_X_FORWARDED_HOST` | Trust `X-Forwarded-Host` from a proxy | `false` |
| `CCLY_EMAIL_BACKEND` | Email backend | `django.core.mail.backends.console.EmailBackend` |
| `CCLY_DEFAULT_FROM_EMAIL` | From address for password reset | `webmaster@localhost` |
| `CCLY_EMAIL_HOST` | SMTP host, used when the backend is SMTP | `localhost` |
| `CCLY_EMAIL_PORT` | SMTP port | `587` |
| `CCLY_EMAIL_HOST_USER` | SMTP username | Empty |
| `CCLY_EMAIL_HOST_PASSWORD` | SMTP password | Empty |
| `CCLY_EMAIL_USE_TLS` | STARTTLS. Do not enable this and SSL together | `true` |
| `CCLY_EMAIL_USE_SSL` | Implicit TLS. Do not enable this and TLS together | `false` |
| `CCLY_AXES_FAILURE_LIMIT` | Failed logins before lockout | `5` |
| `CCLY_AXES_COOLOFF_HOURS` | Lockout cooloff in hours | `1` |
| `CCLY_RATELIMIT_ENABLE` | Rate limiting | `true` |
| `CCLY_RATELIMIT_RATE` | Allowed requests. Empty means no limit | `60/m` |
| `CCLY_RATELIMIT_KEY` | Who is counted: `user_or_ip`, `ip`, or `user` | `user_or_ip` |
| `CCLY_RATELIMIT_FAIL_OPEN` | Allow requests when the cache is down | `false` |

`ccly init` invents a new session cookie, CSRF cookie, language cookie, and cache prefix for each site. Two sites can then be served from the same domain without sharing logins or cache entries. Leave `CCLY_COOKIE_DOMAIN` empty so those cookies stay on that host.

For a public HTTPS server, set `CCLY_DEBUG=false`, `CCLY_COOKIE_SECURE=true`, `CCLY_SECURE_SSL_REDIRECT=true`, and `CCLY_SECURE_HSTS_SECONDS=31536000`. Behind a reverse proxy, set `CCLY_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https` and list the public origins in `CCLY_CSRF_TRUSTED_ORIGINS` (for example `https://bulletin.example.com`). To send mail, set `CCLY_EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend` and fill in `CCLY_EMAIL_HOST`. Set `CCLY_CONN_MAX_AGE` above `0` when the database is not SQLite.

`CCLY_SITE_NAME` is optional. When it is unset, the admin title is the PyPI name of each app in `CCLY_APPS`.

`CCLY_RATELIMIT_IP_META_KEY` is optional. Set it to the request header your proxy uses, such as `HTTP_X_FORWARDED_FOR`, when `REMOTE_ADDR` is not the client. Static files are not counted. A request past the rate gets HTTP 403. The default cache is per process; point Django at a shared cache when you run more than one process. The cache prefix above keeps two sites apart when they share that cache.

Each app that provides a `urls` module is mounted at `/<app_name>/`.

An app can also provide `ccly_settings.py`. Uppercase names in that module are added to the Django settings and are the same for every deployment, for example an external API URL:

```python
EXTERNAL_API_URL = "https://api.example.com"
```

`CCLY_LOGO` is the static path of the image shown to the left of the project name in the admin. A new app sets it to `img/alaska.png` and ships that file in `src/<app>/static/img`. Change the setting, and add the new file under `static/`, to use another logo.

A later app replaces a value that ccly, or an earlier app, already set. `INSTALLED_APPS` is extended instead: names from the app are appended, and names already present stay where they are.

```python
INSTALLED_APPS = ["third.party.app"]
```
