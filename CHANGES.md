# Changes

## Documentation

- Show the Alaska logo at the top of `README.md`.
- `ccly create` adds a Sphinx project with the Read the Docs theme and builds the HTML docs.
- Generated `AGENTS.md` requires the documentation to be updated whenever the app changes.

## Extras

- `ccly create --extras` accepts plugin names. `oauth_client` adds mozilla-django-oidc to the app and writes its settings into `.env` on `ccly init`.

## App environment

- Apps can advertise `.env` settings from `ccly_settings.py` with `env`, including `env("CCLY_API_KEY", required=True)`.
- Startup checks fail when a required advertised variable is missing or blank.

## Packaging

- Marked ccly as alpha in `pyproject.toml` and added Django and Python classifiers.
- Added Karl (https://github.com/kaykay-dv/) as the package author.

## Site locale

- `ccly init` sets `CCLY_TIME_ZONE` and `CCLY_LANGUAGE_CODE` from the machine when it can read them, and otherwise uses `UTC` and `en-us`.

## Documentation

- Split `README.md` into shorter sections for install, the site, configuration, and apps.
- Noted in `README.md` that ccly is opinionated and ships with pre-selected third-party apps.
- Noted in `README.md` that ccly is particularly targeted at Django-based microservices.
- Noted in `README.md` that ccly is a nod to "Cicely" in Northern Exposure.
- Added `AGENTS.md` with a short description of ccly and a requirement to record file changes in this file.
- Added a Default column to the configuration table in `README.md`.
