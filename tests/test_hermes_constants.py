"""Tests for hermes_constants module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

import hermes_constants
from hermes_constants import get_default_hermes_root, get_hermes_home, is_container


class TestGetHermesHome:
    """Tests for get_hermes_home() — Icarus branding with Hermes compatibility."""

    def test_no_home_env_returns_native_icarus(self, tmp_path, monkeypatch):
        """Fresh installs default to ~/.icarus when no home env vars are set."""
        monkeypatch.delenv("ICARUS_HOME", raising=False)
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert get_hermes_home() == tmp_path / ".icarus"

    def test_icarus_home_is_honored(self, tmp_path, monkeypatch):
        """ICARUS_HOME is the primary fork-specific home override."""
        icarus_home = tmp_path / "icarus-profile"
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.setenv("ICARUS_HOME", str(icarus_home))
        assert get_hermes_home() == icarus_home

    def test_hermes_home_compatibility_wins_when_explicitly_set(self, tmp_path, monkeypatch):
        """Legacy HERMES_HOME remains supported for existing installs."""
        hermes_home = tmp_path / "legacy-hermes-home"
        icarus_home = tmp_path / "icarus-home"
        monkeypatch.setenv("HERMES_HOME", str(hermes_home))
        monkeypatch.setenv("ICARUS_HOME", str(icarus_home))
        assert get_hermes_home() == hermes_home

    def test_explicit_legacy_native_home_is_still_honored(self, tmp_path, monkeypatch):
        """Existing installs can explicitly keep using ~/.hermes."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("ICARUS_HOME", raising=False)
        monkeypatch.setenv("HERMES_HOME", str(tmp_path / ".hermes"))
        assert get_hermes_home() == tmp_path / ".hermes"


class TestGetDefaultHermesRoot:
    """Tests for get_default_hermes_root() — Docker/custom deployment awareness."""

    def test_no_home_env_returns_native_icarus_root(self, tmp_path, monkeypatch):
        """Fresh installs default to ~/.icarus for profile-level operations too."""
        monkeypatch.delenv("ICARUS_HOME", raising=False)
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert get_default_hermes_root() == tmp_path / ".icarus"

    def test_icarus_home_is_native(self, tmp_path, monkeypatch):
        """When ICARUS_HOME = ~/.icarus, returns ~/.icarus."""
        native = tmp_path / ".icarus"
        native.mkdir()
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("ICARUS_HOME", str(native))
        assert get_default_hermes_root() == native

    def test_hermes_home_is_native(self, tmp_path, monkeypatch):
        """When HERMES_HOME = ~/.hermes, returns ~/.hermes."""
        native = tmp_path / ".hermes"
        native.mkdir()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(native))
        assert get_default_hermes_root() == native

    def test_icarus_home_profile_returns_icarus_root(self, tmp_path, monkeypatch):
        """When ICARUS_HOME is a profile under ~/.icarus, returns ~/.icarus."""
        native = tmp_path / ".icarus"
        profile = native / "profiles" / "builder"
        profile.mkdir(parents=True)
        monkeypatch.delenv("HERMES_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("ICARUS_HOME", str(profile))
        assert get_default_hermes_root() == native

    def test_hermes_home_is_profile(self, tmp_path, monkeypatch):
        """When HERMES_HOME is a profile under ~/.hermes, returns ~/.hermes."""
        native = tmp_path / ".hermes"
        profile = native / "profiles" / "coder"
        profile.mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(profile))
        assert get_default_hermes_root() == native

    def test_hermes_home_is_docker(self, tmp_path, monkeypatch):
        """When HERMES_HOME points outside ~/.hermes (Docker), returns HERMES_HOME."""
        docker_home = tmp_path / "opt" / "data"
        docker_home.mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(docker_home))
        assert get_default_hermes_root() == docker_home

    def test_hermes_home_is_custom_path(self, tmp_path, monkeypatch):
        """Any HERMES_HOME outside ~/.hermes is treated as the root."""
        custom = tmp_path / "my-hermes-data"
        custom.mkdir()
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(custom))
        assert get_default_hermes_root() == custom

    def test_docker_profile_active(self, tmp_path, monkeypatch):
        """When a Docker profile is active (HERMES_HOME=<root>/profiles/<name>),
        returns the Docker root, not the profile dir."""
        docker_root = tmp_path / "opt" / "data"
        profile = docker_root / "profiles" / "coder"
        profile.mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("HERMES_HOME", str(profile))
        assert get_default_hermes_root() == docker_root


class TestIsContainer:
    """Tests for is_container() — Docker/Podman detection."""

    def _reset_cache(self, monkeypatch):
        """Reset the cached detection result before each test."""
        monkeypatch.setattr(hermes_constants, "_container_detected", None)

    def test_detects_dockerenv(self, monkeypatch, tmp_path):
        """/.dockerenv triggers container detection."""
        self._reset_cache(monkeypatch)
        monkeypatch.setattr(os.path, "exists", lambda p: p == "/.dockerenv")
        assert is_container() is True

    def test_detects_containerenv(self, monkeypatch, tmp_path):
        """/run/.containerenv triggers container detection (Podman)."""
        self._reset_cache(monkeypatch)
        monkeypatch.setattr(os.path, "exists", lambda p: p == "/run/.containerenv")
        assert is_container() is True

    def test_detects_cgroup_docker(self, monkeypatch, tmp_path):
        """/proc/1/cgroup containing 'docker' triggers detection."""
        import builtins
        self._reset_cache(monkeypatch)
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        cgroup_file = tmp_path / "cgroup"
        cgroup_file.write_text("12:memory:/docker/abc123\n")
        _real_open = builtins.open
        monkeypatch.setattr("builtins.open", lambda p, *a, **kw: _real_open(str(cgroup_file), *a, **kw) if p == "/proc/1/cgroup" else _real_open(p, *a, **kw))
        assert is_container() is True

    def test_negative_case(self, monkeypatch, tmp_path):
        """Returns False on a regular Linux host."""
        import builtins
        self._reset_cache(monkeypatch)
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        cgroup_file = tmp_path / "cgroup"
        cgroup_file.write_text("12:memory:/\n")
        _real_open = builtins.open
        monkeypatch.setattr("builtins.open", lambda p, *a, **kw: _real_open(str(cgroup_file), *a, **kw) if p == "/proc/1/cgroup" else _real_open(p, *a, **kw))
        assert is_container() is False

    def test_caches_result(self, monkeypatch):
        """Second call uses cached value without re-probing."""
        monkeypatch.setattr(hermes_constants, "_container_detected", True)
        assert is_container() is True
        # Even if we make os.path.exists return False, cached value wins
        monkeypatch.setattr(os.path, "exists", lambda p: False)
        assert is_container() is True
