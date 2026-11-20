from ccly.branding import site_title


def test_override_replaces_app_names(monkeypatch):
    monkeypatch.setattr(
        "ccly.branding.installed_distribution_names",
        lambda import_name: ["distribution"],
    )
    assert site_title(["bulletin"], "Roslyn") == "Roslyn"


def test_distribution_names_are_joined(monkeypatch):
    names = {"bulletin": ["bulletin"], "kbdr": ["kbdr"]}
    monkeypatch.setattr(
        "ccly.branding.installed_distribution_names",
        lambda import_name: names.get(import_name, []),
    )
    assert site_title(["bulletin", "kbdr"]) == "bulletin / kbdr"


def test_missing_metadata_uses_the_import_name(monkeypatch):
    monkeypatch.setattr("ccly.branding.installed_distribution_names", lambda import_name: [])
    assert site_title(["bulletin"]) == "bulletin"


def test_empty_project_is_cicely():
    assert site_title([]) == "Cicely"
