"""Plugin interface for optional features of a generated app."""

from __future__ import annotations


class UnknownExtrasError(Exception):
    def __init__(self, names: list[str], known: list[str]) -> None:
        self.names = names
        self.known = known
        super().__init__(", ".join(names))


class Extra:
    """One optional feature that can be selected with ``ccly create --extras``."""

    name = ""

    def settings_block(self, app_name: str = "") -> str:
        """Python appended to the app's ``ccly_settings.py``."""
        return ""

    def dependencies(self) -> list[str]:
        """Requirements added to the app's ``pyproject.toml``."""
        return []

    def env_lines(self, app_names: list[str] | None = None) -> list[str]:
        """Lines appended to the site ``.env`` when the app is initialized."""
        return []

    def urlpatterns(self) -> list:
        """URL patterns mounted on the ccly project."""
        return []
