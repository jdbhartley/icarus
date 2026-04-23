from pathlib import Path
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_pyproject():
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _load_package_json():
    import json

    return json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))


def test_faster_whisper_is_not_a_base_dependency():
    data = _load_pyproject()
    deps = data["project"]["dependencies"]

    assert not any(dep.startswith("faster-whisper") for dep in deps)

    voice_extra = data["project"]["optional-dependencies"]["voice"]
    assert any(dep.startswith("faster-whisper") for dep in voice_extra)


def test_manifest_includes_bundled_skills():
    manifest = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")

    assert "graft skills" in manifest
    assert "graft optional-skills" in manifest


def test_pyproject_scripts_include_icarus_entrypoints():
    scripts = _load_pyproject()["project"]["scripts"]

    assert scripts["icarus"] == "hermes_cli.main:main"
    assert scripts["icarus-agent"] == "run_agent:main"
    assert scripts["icarus-acp"] == "acp_adapter.entry:main"
    assert scripts["hermes"] == "hermes_cli.main:main"
    assert scripts["hermes-agent"] == "run_agent:main"
    assert scripts["hermes-acp"] == "acp_adapter.entry:main"


def test_package_json_uses_icarus_branding_and_cli_hint():
    package_json = _load_package_json()

    assert package_json["name"] == "icarus-agent"
    assert "icarus --help" in package_json["scripts"]["postinstall"]


def test_acp_registry_uses_icarus_identity_and_command():
    import json

    agent = json.loads((REPO_ROOT / "acp_registry" / "agent.json").read_text(encoding="utf-8"))

    assert agent["name"] == "icarus-agent"
    assert agent["display_name"] == "Icarus"
    assert agent["distribution"]["command"] == "icarus"
