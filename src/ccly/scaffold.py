"""Scaffold an installable Django app."""

from __future__ import annotations

import keyword
import sys
from pathlib import Path

from ccly.extras import UnknownExtrasError, resolve_extras
from ccly.extras.base import Extra


def config_class_name(app_name: str) -> str:
    return "".join(part.capitalize() for part in app_name.split("_")) + "Config"


def validate_app_name(app_name: str) -> str | None:
    if app_name.isidentifier() and not keyword.iskeyword(app_name):
        return None
    return f"{app_name!r} is not a valid Python identifier."


def template_root() -> Path:
    return Path(__file__).resolve().parent / "templates" / "app"


def create_app(
    app_name: str,
    destination: Path | None = None,
    *,
    extras: list[str] | None = None,
) -> int:
    error = validate_app_name(app_name)
    if error:
        print(error, file=sys.stderr)
        return 2
    try:
        chosen = resolve_extras(extras or [])
    except UnknownExtrasError as exc:
        known = ", ".join(exc.known) or "(none)"
        print(
            f"Unknown extras: {', '.join(exc.names)}. Known: {known}.",
            file=sys.stderr,
        )
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
    _apply_extras(target, app_name, chosen)
    if _build_docs(target) != 0:
        return 1
    print(f"Created {target}")
    if chosen:
        print("Extras: " + ", ".join(extra.name for extra in chosen))
    print("Install it, then point a site at it:")
    print(f"  pip install -e {target}")
    print(f"  ccly init {app_name}")
    return 0


def _build_docs(destination: Path) -> int:
    from sphinx.cmd.build import build_main

    source = destination / "docs"
    output = source / "_build" / "html"
    status = build_main(["-q", "-b", "html", str(source), str(output)])
    if status != 0:
        print("Could not build the Sphinx documentation.", file=sys.stderr)
        return status
    print(f"Documentation: {output / 'index.html'}")
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


def _apply_extras(destination: Path, app_name: str, extras: list[Extra]) -> None:
    if not extras:
        return
    settings_path = destination / "src" / app_name / "ccly_settings.py"
    blocks = [
        extra.settings_block(app_name).rstrip()
        for extra in extras
        if extra.settings_block(app_name)
    ]
    if blocks:
        current = settings_path.read_text(encoding="utf-8").rstrip()
        settings_path.write_text(current + "\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")
    dependencies = [dep for extra in extras for dep in extra.dependencies()]
    if dependencies:
        project_path = destination / "pyproject.toml"
        project_path.write_text(
            _add_dependencies(project_path.read_text(encoding="utf-8"), dependencies),
            encoding="utf-8",
        )
    names = ", ".join(f'"{extra.name}"' for extra in extras)
    extras_path = destination / "src" / app_name / "ccly_extras.py"
    extras_path.write_text(
        '"""Extras selected with ``ccly create --extras``."""\n\n'
        f"EXTRAS = [{names}]\n",
        encoding="utf-8",
    )


def _add_dependencies(source: str, dependencies: list[str]) -> str:
    marker = "\n]\n\n[tool.hatch.build.targets.wheel]"
    if marker not in source:
        raise RuntimeError("pyproject.toml has no dependency list to extend.")
    added = "\n".join(f'    "{dependency}",' for dependency in dependencies)
    return source.replace(marker, "\n" + added + marker, 1)


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
