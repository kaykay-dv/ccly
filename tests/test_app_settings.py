import sys
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

from ccly.project.app_settings import contribute_settings


def _forget(*names: str) -> None:
    for loaded in list(sys.modules):
        if loaded in names or any(loaded.startswith(f"{name}.") for name in names):
            del sys.modules[loaded]


@pytest.fixture(autouse=True)
def _drop_fake_apps():
    # Later tests ask importlib whether these names are installed. A leftover
    # module still counts as found after its temporary path is gone.
    names = ("bulletin", "kbdr")
    _forget(*names)
    yield
    _forget(*names)


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


def test_existing_name_is_overridden(tmp_path, monkeypatch):
    _forget("bulletin")
    _package(tmp_path, "bulletin", 'EXTERNAL_API_URL = "https://api.example.com"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    target.EXTERNAL_API_URL = "https://old.example"
    contribute_settings(target, ["bulletin"])
    assert target.EXTERNAL_API_URL == "https://api.example.com"


def test_later_app_overrides_an_earlier_one(tmp_path, monkeypatch):
    _forget("bulletin", "kbdr")
    _package(tmp_path, "bulletin", 'EXTERNAL_API_URL = "https://one.example"\n')
    _package(tmp_path, "kbdr", 'EXTERNAL_API_URL = "https://two.example"\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    contribute_settings(target, ["bulletin", "kbdr"])
    assert target.EXTERNAL_API_URL == "https://two.example"


def test_installed_apps_are_appended(tmp_path, monkeypatch):
    _forget("bulletin", "kbdr")
    _package(tmp_path, "bulletin", 'INSTALLED_APPS = ["news", "django.contrib.gis"]\n')
    _package(tmp_path, "kbdr", 'INSTALLED_APPS = ["news", "archive"]\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    target.INSTALLED_APPS = ["django.contrib.auth", "bulletin"]
    contribute_settings(target, ["bulletin", "kbdr"])
    assert target.INSTALLED_APPS == [
        "django.contrib.auth",
        "bulletin",
        "news",
        "django.contrib.gis",
        "archive",
    ]


def test_installed_apps_must_be_a_list(tmp_path, monkeypatch):
    _forget("bulletin")
    _package(tmp_path, "bulletin", "INSTALLED_APPS = 3\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    target = ModuleType("target")
    target.INSTALLED_APPS = ["django.contrib.auth"]
    with pytest.raises(ImproperlyConfigured, match="INSTALLED_APPS"):
        contribute_settings(target, ["bulletin"])
    assert target.INSTALLED_APPS == ["django.contrib.auth"]
