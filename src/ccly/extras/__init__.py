"""Optional features selected with ``ccly create --extras``."""

from __future__ import annotations

import importlib
import importlib.util

from ccly.extras.base import Extra, UnknownExtrasError
from ccly.extras.oauth_client import OAuthClient

__all__ = [
    "Extra",
    "UnknownExtrasError",
    "env_lines_for_apps",
    "resolve_extras",
    "urlpatterns_for_apps",
]


class ExtraRegistry:
    def __init__(self) -> None:
        self._extras: dict[str, Extra] = {}

    def register(self, extra: Extra) -> None:
        self._extras[extra.name] = extra

    def known(self) -> list[str]:
        return sorted(self._extras)

    def resolve(self, names: list[str]) -> list[Extra]:
        chosen: list[Extra] = []
        seen: set[str] = set()
        unknown: list[str] = []
        for name in names:
            if name in seen:
                continue
            seen.add(name)
            extra = self._extras.get(name)
            if extra is None:
                unknown.append(name)
            else:
                chosen.append(extra)
        if unknown:
            raise UnknownExtrasError(unknown, self.known())
        return chosen

    def for_apps(self, app_names: list[str]) -> list[Extra]:
        importlib.invalidate_caches()
        chosen: list[Extra] = []
        seen: set[str] = set()
        for app_name in app_names:
            module_name = f"{app_name}.ccly_extras"
            try:
                spec = importlib.util.find_spec(module_name)
            except ModuleNotFoundError:
                spec = None
            if spec is None:
                continue
            module = importlib.import_module(module_name)
            for name in getattr(module, "EXTRAS", []):
                if name in seen or name not in self._extras:
                    continue
                seen.add(name)
                chosen.append(self._extras[name])
        return chosen


REGISTRY = ExtraRegistry()
REGISTRY.register(OAuthClient())


def resolve_extras(names: list[str]) -> list[Extra]:
    return REGISTRY.resolve(names)


def env_lines_for_apps(app_names: list[str]) -> list[str]:
    lines: list[str] = []
    for extra in REGISTRY.for_apps(app_names):
        lines.extend(extra.env_lines())
    return lines


def urlpatterns_for_apps(app_names: list[str]) -> list:
    patterns: list = []
    for extra in REGISTRY.for_apps(app_names):
        patterns.extend(extra.urlpatterns())
    return patterns
