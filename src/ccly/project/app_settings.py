"""Merge settings contributed by the apps listed in CCLY_APPS."""

from __future__ import annotations

import importlib
import importlib.util
from types import ModuleType

from django.core.exceptions import ImproperlyConfigured


def is_setting_name(name: str) -> bool:
    return bool(name) and name[0].isalpha() and name.isupper()


def contribute_settings(target: ModuleType, app_names: list[str]) -> None:
    """Copy uppercase names from each app's ``ccly_settings`` module onto ``target``.

    These values belong to the app package, so they are the same for every
    deployment. A name ccly already defined, or that an earlier app defined,
    is left unchanged and reported as a conflict.
    """
    defined = {name for name in vars(target) if is_setting_name(name)}
    importlib.invalidate_caches()
    for app_name in app_names:
        module_name = f"{app_name}.ccly_settings"
        if importlib.util.find_spec(module_name) is None:
            continue
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not is_setting_name(name):
                continue
            if name in defined:
                raise ImproperlyConfigured(
                    f"{module_name}.{name} conflicts with a setting that is already defined."
                )
            setattr(target, name, value)
            defined.add(name)
