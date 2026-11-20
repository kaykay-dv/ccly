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

    These values belong to the app package. A later app replaces a value
    defined by ccly or by an earlier app. ``INSTALLED_APPS`` is the exception:
    contributed app names are appended, and names already present are left in
    place. Values read with ``ccly.env.env`` come from the site environment.
    """
    importlib.invalidate_caches()
    for app_name in app_names:
        module_name = f"{app_name}.ccly_settings"
        if importlib.util.find_spec(module_name) is None:
            continue
        module = importlib.import_module(module_name)
        for name, value in vars(module).items():
            if not is_setting_name(name):
                continue
            if name == "INSTALLED_APPS":
                setattr(target, name, _extend_installed_apps(getattr(target, name, ()), value, module_name))
            else:
                setattr(target, name, value)


def _extend_installed_apps(existing, contributed, module_name: str) -> list[str]:
    if isinstance(contributed, str):
        contributed = [contributed]
    elif not isinstance(contributed, (list, tuple)):
        raise ImproperlyConfigured(
            f"{module_name}.INSTALLED_APPS must be a list of app names."
        )
    merged = list(existing)
    present = set(merged)
    for name in contributed:
        if name not in present:
            merged.append(name)
            present.add(name)
    return merged
