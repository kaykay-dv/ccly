"""Startup checks for settings advertised by apps."""

from __future__ import annotations

import os

from django.core.checks import Error, register

from ccly.env import advertised


@register
def check_advertised_env(app_configs, **kwargs):
    """Fail startup when a required app setting is missing from the environment."""
    errors = []
    for item in advertised():
        if not item.required:
            continue
        raw = os.environ.get(item.name)
        if raw is not None and raw.strip() != "":
            continue
        where = f" Declared in {item.module}." if item.module else ""
        errors.append(
            Error(
                f"{item.name} is required but is not set.{where}",
                hint=f"Add {item.name}=... to the site .env file.",
                id="ccly.E001",
            )
        )
    return errors
