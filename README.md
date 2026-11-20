# ccly

ccly (Cicely) is a Django project you carry with you. The project lives in this package. A site is only a directory with a `.env` file. The apps you build are separate, publishable packages.

Admin is served at `/m/`. Django REST framework and an OpenAPI document (drf-spectacular) are included, and django-axes watches login attempts.

## Install

```bash
pip install ccly
```

Python 3.11 or newer.

## Create an app

```bash
ccly create bulletin
cd bulletin
pip install -e .
```

That writes a src-layout package. It includes `GET /bulletin/health/`, which returns the JSON string `"OK"`.

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

`CCLY_SITE_NAME` is optional. When it is unset, the admin title is the PyPI name of each app in `CCLY_APPS`.

Each app that provides a `urls` module is mounted at `/<app_name>/`.
