import sys
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

from ccly.project.app_settings import contribute_settings


def _forget(*names: str) -> None:
    for loaded in list(sys.modules):
        if loaded in names or any(loaded.startswith(f"{name}.") for name in names):
            del sys.modules[loaded]


def _package(tmp_path, name, source):
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    if source is not None:
        (package / "ccly_settings.py").write_text(source, encoding="utf-8")
    return package


def test_new_settings_are_copied(tmp_path, monkeypatch):
    _forget("bulletin")
    _package(tmp_path, "bulletin", 'EXTERNAL_API_URL = "https://api.example.com"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    target.SECRET_KEY = "kept"
    contribute_settings(target, ["bulletin"])
    assert target.EXTERNAL_API_URL == "https://api.example.com"
    assert target.SECRET_KEY == "kept"


def test_missing_module_is_skipped(tmp_path, monkeypatch):
    _forget("bulletin")
    _package(tmp_path, "bulletin", None)
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    contribute_settings(target, ["bulletin"])
    assert not hasattr(target, "EXTERNAL_API_URL")


def test_existing_name_is_rejected(tmp_path, monkeypatch):
    _forget("bulletin")
    _package(tmp_path, "bulletin", 'SECRET_KEY = "nope"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    target.SECRET_KEY = "kept"
    with pytest.raises(ImproperlyConfigured, match="SECRET_KEY"):
        contribute_settings(target, ["bulletin"])
    assert target.SECRET_KEY == "kept"


def test_second_app_cannot_redefine_a_name(tmp_path, monkeypatch):
    _forget("bulletin", "kbdr")
    _package(tmp_path, "bulletin", 'EXTERNAL_API_URL = "https://one.example"\n')
    _package(tmp_path, "kbdr", 'EXTERNAL_API_URL = "https://two.example"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    with pytest.raises(ImproperlyConfigured, match="kbdr.ccly_settings.EXTERNAL_API_URL"):
        contribute_settings(target, ["bulletin", "kbdr"])
    assert target.EXTERNAL_API_URL == "https://one.example"
