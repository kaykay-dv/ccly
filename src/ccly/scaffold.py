"""Scaffold an installable Django app."""

from __future__ import annotations

import keyword
import sys
from pathlib import Path


def config_class_name(app_name: str) -> str:
    return "".join(part.capitalize() for part in app_name.split("_")) + "Config"


def validate_app_name(app_name: str) -> str | None:
    if app_name.isidentifier() and not keyword.iskeyword(app_name):
        return None
    return f"{app_name!r} is not a valid Python identifier."


def template_root() -> Path:
    return Path(__file__).resolve().parent / "templates" / "app"


def create_app(app_name: str, destination: Path | None = None) -> int:
    error = validate_app_name(app_name)
    if error:
        print(error, file=sys.stderr)
        return 2
    target = destination if destination is not None else Path.cwd() / app_name
    if target.exists():
        print(f"{target} already exists.", file=sys.stderr)
        return 1
    replacements = {
        "__APP_NAME__": app_name,
        "__APP_CLASS__": config_class_name(app_name),
    }
    _copy_tree(template_root(), target, replacements)
    print(f"Created {target}")
    print("Install it, then point a site at it:")
    print(f"  pip install -e {target}")
    print(f"  ccly init {app_name}")
    return 0


def _copy_tree(root: Path, destination: Path, replacements: dict[str, str]) -> None:
    app_name = replacements["__APP_NAME__"]
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = _package_static(path.relative_to(root), app_name)
        parts = [_replace(part, replacements) for part in relative.parts]
        target = destination.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        if _is_utf8(data):
            text = _replace(data.decode("utf-8"), replacements)
            target.write_text(text, encoding="utf-8")
        else:
            target.write_bytes(data)


def _package_static(relative: Path, app_name: str) -> Path:
    """Put template ``static/`` files inside the installable package.

    Django serves files from an installed app's ``static`` directory. A file
    left next to ``pyproject.toml`` would not be installed with the package.
    """
    if relative.parts and relative.parts[0] == "static":
        return Path("src", app_name, *relative.parts)
    return relative


def _is_utf8(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _replace(value: str, replacements: dict[str, str]) -> str:
    for key, replacement in replacements.items():
        value = value.replace(key, replacement)
    return value
