from ccly.branding import header_parts, site_title


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
    assert header_parts([]) == []


def test_header_pairs_each_app_with_its_version(monkeypatch):
    names = {"bulletin": ["bulletin"], "kbdr": ["kbdr"]}
    versions = {"bulletin": "1.2.3", "kbdr": "4.5.6"}
    monkeypatch.setattr(
        "ccly.branding.installed_distribution_names",
        lambda import_name: names.get(import_name, []),
    )
    monkeypatch.setattr(
        "ccly.branding.distribution_version",
        lambda distribution_name: versions.get(distribution_name, ""),
    )
    assert header_parts(["bulletin", "kbdr"]) == [
        {"label": "bulletin", "version": "1.2.3"},
        {"label": "kbdr", "version": "4.5.6"},
    ]
    assert header_parts(["bulletin", "kbdr"], "Roslyn") == [
        {"label": "Roslyn", "version": "1.2.3"},
        {"label": "", "version": "4.5.6"},
    ]


def test_header_shows_a_repeated_version_once_beside_a_custom_title(monkeypatch):
    names = {"bulletin": ["bulletin"], "kbdr": ["kbdr"]}
    monkeypatch.setattr(
        "ccly.branding.installed_distribution_names",
        lambda import_name: names.get(import_name, []),
    )
    monkeypatch.setattr("ccly.branding.distribution_version", lambda distribution_name: "1.0.0")
    assert header_parts(["bulletin", "kbdr"], "Roslyn") == [
        {"label": "Roslyn", "version": "1.0.0"},
    ]


def test_header_omits_a_version_that_cannot_be_read(monkeypatch):
    monkeypatch.setattr("ccly.branding.installed_distribution_names", lambda import_name: [])
    monkeypatch.setattr("ccly.branding.distribution_version", lambda distribution_name: "")
    assert header_parts(["bulletin"]) == [{"label": "bulletin", "version": ""}]


def test_header_uses_the_import_name_when_the_package_map_misses_it(monkeypatch):
    monkeypatch.setattr("ccly.branding.installed_distribution_names", lambda import_name: [])
    monkeypatch.setattr(
        "ccly.branding.distribution_version",
        lambda distribution_name: "0.1.0" if distribution_name == "bulletin" else "",
    )
    assert header_parts(["bulletin"]) == [{"label": "bulletin", "version": "0.1.0"}]
