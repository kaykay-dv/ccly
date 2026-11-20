"""Admin and OpenAPI titles derived from installed app distributions."""

from __future__ import annotations

import importlib.metadata


def installed_distribution_names(import_name: str) -> list[str]:
    """Return PyPI distribution names that provide this import package."""
    try:
        mapping = importlib.metadata.packages_distributions()
    except Exception:
        return []
    return list(mapping.get(import_name) or [])


def site_title(app_names: list[str], override: str = "") -> str:
    """Title shown in the admin and the OpenAPI document.

    An explicit override wins. Otherwise each app contributes its installed
    distribution name, falling back to the import name. Several apps are
    joined with `` / ``. An empty project is titled Cicely.
    """
    custom = override.strip()
    if custom:
        return custom
    if not app_names:
        return "Cicely"
    labels: list[str] = []
    for app_name in app_names:
        found = installed_distribution_names(app_name)
        labels.append(found[0] if found else app_name)
    return " / ".join(labels)
