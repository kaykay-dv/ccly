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


def distribution_version(distribution_name: str) -> str:
    """Installed version of a distribution, or empty when it cannot be read."""
    try:
        return importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return ""


def _version_for_app(import_name: str, distribution_names: list[str]) -> str:
    """Version of an app, trying the distribution name and then the import name.

    Editable installs often answer ``version(import_name)`` while leaving the
    import package out of ``packages_distributions()``.
    """
    candidates: list[str] = []
    for name in [*distribution_names, import_name]:
        if name and name not in candidates:
            candidates.append(name)
    for name in candidates:
        version = distribution_version(name)
        if version:
            return version
    return ""


def header_parts(app_names: list[str], override: str = "") -> list[dict[str, str]]:
    """Labels and versions for the admin header.

    Each app contributes its distribution name, or its import name when that
    distribution cannot be found, and the distribution version. A version that
    cannot be read is blank. An explicit title replaces the names and is shown
    once, followed by each distinct version.
    """
    custom = override.strip()
    parts: list[dict[str, str]] = []
    for app_name in app_names:
        found = installed_distribution_names(app_name)
        parts.append(
            {
                "label": found[0] if found else app_name,
                "version": _version_for_app(app_name, found),
            }
        )
    if not custom:
        return parts
    versions: list[str] = []
    for part in parts:
        version = part["version"]
        if version and version not in versions:
            versions.append(version)
    if not versions:
        return [{"label": custom, "version": ""}]
    branded = [{"label": custom, "version": versions[0]}]
    branded.extend({"label": "", "version": version} for version in versions[1:])
    return branded


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
