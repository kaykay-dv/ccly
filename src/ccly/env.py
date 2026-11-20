"""Settings an app reads from the site ``.env`` file."""

from __future__ import annotations

import inspect
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AdvertisedEnv:
    """One environment variable an app has asked ccly to configure."""

    name: str
    required: bool
    module: str


_registry: dict[str, AdvertisedEnv] = {}


def env(name: str, default: str | None = None, *, required: bool = False) -> str:
    """Read ``name`` from the environment and advertise it to ccly.

    ccly loads the site ``.env`` before importing an app's ``ccly_settings``.
    Assign the result to an uppercase name so it becomes a Django setting.
    A required variable that is missing or blank does not stop this import;
    the startup check reports it.
    """
    if not isinstance(name, str) or not name.strip():
        raise TypeError("env() name must be a non-empty string.")
    if required and default is not None:
        raise TypeError("env() with required=True does not take a default.")
    key = name.strip()
    _remember(key, required, _caller_module())
    raw = os.environ.get(key)
    if raw is None or raw.strip() == "":
        return "" if default is None else default
    return raw


def advertised() -> tuple[AdvertisedEnv, ...]:
    """Return the environment variables apps have advertised, in declaration order."""
    return tuple(_registry.values())


def clear() -> None:
    """Forget advertised variables. Tests use this between cases."""
    _registry.clear()


def _remember(name: str, required: bool, module: str) -> None:
    current = _registry.get(name)
    if current is None:
        _registry[name] = AdvertisedEnv(name, required, module)
        return
    modules = [part for part in current.module.split(", ") if part]
    if module and module not in modules:
        modules.append(module)
    _registry[name] = AdvertisedEnv(
        name,
        current.required or required,
        ", ".join(modules),
    )


def _caller_module() -> str:
    frame = inspect.currentframe()
    caller = frame.f_back.f_back if frame is not None and frame.f_back is not None else None
    if caller is None:
        return ""
    return str(caller.f_globals.get("__name__", ""))
