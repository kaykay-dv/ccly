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

| Variable | Purpose |
| --- | --- |
| `CCLY_SECRET_KEY` | Django secret key |
| `CCLY_DEBUG` | Debug mode |
| `CCLY_ALLOWED_HOSTS` | Comma-separated hosts |
| `CCLY_APPS` | Comma-separated import names to install and mount |
| `CCLY_DATABASE_URL` | Database URL, default `sqlite:///db.sqlite3` |
| `CCLY_TIME_ZONE` | Time zone |
| `CCLY_LANGUAGE_CODE` | Language code |
| `CCLY_EMAIL_BACKEND` | Email backend, default console |
| `CCLY_DEFAULT_FROM_EMAIL` | From address for password reset |
| `CCLY_AXES_FAILURE_LIMIT` | Failed logins before lockout |
| `CCLY_AXES_COOLOFF_HOURS` | Lockout cooloff in hours |
| `CCLY_RATELIMIT_ENABLE` | Rate limiting, default `true` |
| `CCLY_RATELIMIT_RATE` | Allowed requests, default `60/m`. Empty means no limit |
| `CCLY_RATELIMIT_KEY` | Who is counted: `user_or_ip` (default), `ip`, or `user` |
| `CCLY_RATELIMIT_FAIL_OPEN` | Allow requests when the cache is down, default `false` |

`CCLY_SITE_NAME` is optional. When it is unset, the admin title is the PyPI name of each app in `CCLY_APPS`.

`CCLY_RATELIMIT_IP_META_KEY` is optional. Set it to the request header your proxy uses, such as `HTTP_X_FORWARDED_FOR`, when `REMOTE_ADDR` is not the client. The default cache counts limits in each process; use a shared cache such as Redis or Memcached when you run more than one process. Static files are not counted. A request past the rate gets HTTP 403.

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
