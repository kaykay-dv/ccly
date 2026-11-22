# Changes

## Admin

- The admin and its password reset are served at `/<app_name>/m/` instead of `/m/`.

## Documentation

- Removed the command walkthrough from the `README.md` introduction and added a Quick start for the first steps.
- Replaced the `README.md` "Included" paragraph with a short list of supported features.
- Rewrote the `README.md` introduction so it states what ccly does: one shared Django project, publishable apps, and a site that is only a `.env` file.
- Split the extras documentation into "OAuth client" and "Identity provider".
- Moved the OAuth extras section to the bottom of `README.md`.
- Show the Alaska logo at the top of `README.md`.
- `ccly create` adds a Sphinx project with the Read the Docs theme and builds the HTML docs.
- Generated `AGENTS.md` requires the documentation to be updated whenever the app changes.

## Extras

- `ccly create --extras` accepts plugin names. `oauth_client` adds mozilla-django-oidc to the app and writes its settings into `.env` on `ccly init`.
- `oauth_provider` adds django-oauth-toolkit. The site serves OAuth 2 at `/o/`, and OpenID Connect turns on when `OIDC_RSA_PRIVATE_KEY` is set.
- The project test site pins `CCLY_LANGUAGE_CODE` to `en-us` so the admin login check does not follow the machine language.

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
