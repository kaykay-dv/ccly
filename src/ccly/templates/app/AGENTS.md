# Developing __APP_NAME__

This repository is a Django app packaged for PyPI. It is loaded by [ccly](https://github.com/kaykay-dv/ccly), which owns the Django project. Do not add a project, a `manage.py`, or a second settings module for the site.

ccly serves the admin at `/m/`, the OpenAPI document at `/api/docs/`, and this app at `/__APP_NAME__/`.

## Run it

From this directory:

```bash
pip install -e .
```

From the site directory, where the `.env` file lives:

```bash
ccly init __APP_NAME__
ccly migrate
ccly runserver
```

Pass other Django commands through ccly as well: `ccly makemigrations`, `ccly shell`, `ccly check`, `ccly createsuperuser`.

## Where code goes

- Models belong in `src/__APP_NAME__/models.py`. After changing them, run `ccly makemigrations __APP_NAME__` and commit the migration files under `src/__APP_NAME__/migrations/`.
- Register models with the admin in `admin.py`.
- HTTP API code belongs in `views.py`, with serializers in `serializers.py` and routes in `urls.py`. ccly mounts `urls.py` at `/__APP_NAME__/`.
- `GET /__APP_NAME__/health/` must keep returning the JSON string `"OK"`.
- Tests belong in `tests/`.

Keep the src layout. The import name and the PyPI name are both `__APP_NAME__`.

## Settings

Values that are the same for every deployment belong in `src/__APP_NAME__/ccly_settings.py`. ccly copies uppercase names from that module into its own Django settings. A name that ccly, or an earlier app, already set is replaced. Use this for an external API URL and other constants shipped with the package:

```python
EXTERNAL_API_URL = "https://api.example.com"
INSTALLED_APPS = ["third.party.app"]
```

`INSTALLED_APPS` is not replaced. Those names are appended to the project's list, and a name that is already installed is skipped. Read the resulting values with `django.conf.settings`. Do not import Django settings from `ccly_settings.py`. Per-deployment values stay in the site's `.env` file, which ccly reads.

## Django practice

- Add a migration for every model change and keep it in the package.
- Give new routes a `name`, and include them in `urls.py` so they show up in the OpenAPI schema.
- Prefer `get_user_model()` over importing `User` directly.
- Validate external input in serializers or forms. Do not trust data from the external API described in `ccly_settings.py`.
- Keep privileged behavior behind the existing authentication. The healthcheck stays public (`AllowAny`).
- Run `ccly check` after changing settings, URLs, or installed models.
