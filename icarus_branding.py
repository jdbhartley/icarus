"""Central branding/constants for the Icarus fork.

Import-safe module with only stdlib dependencies. Runtime surfaces should use
these helpers instead of hardcoding product or command names.

Backward compatibility notes:
- Internal module/package names remain ``hermes_*``.
- Service/unit identifiers keep the legacy ``hermes`` base names so existing
  installs, scripts, and launchd/systemd units continue to work.
- User-facing command text should prefer :func:`display_cli_command`, which
  preserves the invoked alias when possible and otherwise falls back to the
  primary ``icarus`` command while still recognizing legacy aliases.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PRODUCT_NAME = os.getenv("ICARUS_PRODUCT_NAME", "Icarus")
LEGACY_PRODUCT_NAME = "Hermes Agent"

COMMAND_NAME = os.getenv("ICARUS_COMMAND_NAME", "icarus")
LEGACY_COMMAND_NAME = os.getenv("ICARUS_LEGACY_COMMAND_NAME", "hermes")

DISTRIBUTION_NAME = os.getenv("ICARUS_DISTRIBUTION_NAME", "icarus-agent")
LEGACY_DISTRIBUTION_NAME = "hermes-agent"

PACKAGE_NAME = os.getenv("ICARUS_PACKAGE_NAME", DISTRIBUTION_NAME)
LEGACY_PACKAGE_NAME = LEGACY_DISTRIBUTION_NAME

ACP_COMMAND_NAME = os.getenv("ICARUS_ACP_COMMAND_NAME", f"{COMMAND_NAME}-acp")
LEGACY_ACP_COMMAND_NAME = os.getenv("ICARUS_LEGACY_ACP_COMMAND_NAME", "hermes-acp")
ACP_IMPLEMENTATION_NAME = os.getenv("ICARUS_ACP_IMPLEMENTATION_NAME", DISTRIBUTION_NAME)

DOCS_URL = os.getenv(
    "ICARUS_DOCS_URL",
    "https://github.com/jdbhartley/icarus",
)

GATEWAY_SERVICE_NAME_BASE = os.getenv("ICARUS_GATEWAY_SERVICE_NAME_BASE", "hermes-gateway")
GATEWAY_LAUNCHD_LABEL_BASE = os.getenv("ICARUS_GATEWAY_LAUNCHD_LABEL_BASE", "ai.hermes.gateway")
GATEWAY_SERVICE_DESCRIPTION = os.getenv(
    "ICARUS_GATEWAY_SERVICE_DESCRIPTION",
    f"{PRODUCT_NAME} Gateway - Messaging Platform Integration",
)


def _basename(value: str | None) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    return Path(raw).name


def invoked_command_name(argv0: str | None = None) -> str | None:
    """Return the recognized CLI alias used to start this process, if any."""
    candidate = _basename(argv0 if argv0 is not None else (sys.argv[0] if sys.argv else ""))
    known = {
        COMMAND_NAME,
        LEGACY_COMMAND_NAME,
        ACP_COMMAND_NAME,
        LEGACY_ACP_COMMAND_NAME,
    }
    return candidate if candidate in known else None


def display_cli_command(*, prefer_primary: bool = False, argv0: str | None = None) -> str:
    """Return the best user-facing CLI command name.

    If the process was started via a known alias, preserve that alias in help
    text. Otherwise fall back to the primary ``icarus`` command.
    """
    invoked = invoked_command_name(argv0=argv0)
    if invoked in {COMMAND_NAME, LEGACY_COMMAND_NAME}:
        return invoked
    return COMMAND_NAME


def display_acp_command(*, prefer_primary: bool = False, argv0: str | None = None) -> str:
    """Return the best user-facing ACP command name."""
    invoked = invoked_command_name(argv0=argv0)
    if invoked in {ACP_COMMAND_NAME, LEGACY_ACP_COMMAND_NAME}:
        return invoked
    return ACP_COMMAND_NAME


def command_example(suffix: str = "", *, prefer_primary: bool = False, argv0: str | None = None) -> str:
    """Render a full CLI example like ``icarus setup`` or ``hermes setup``."""
    command = display_cli_command(prefer_primary=prefer_primary, argv0=argv0)
    suffix = str(suffix or "").strip()
    return f"{command} {suffix}".rstrip()


def repository_dir_candidates() -> tuple[str, ...]:
    """Return checkout directory names to probe under the runtime home dir."""
    ordered = [DISTRIBUTION_NAME, PACKAGE_NAME, LEGACY_DISTRIBUTION_NAME, LEGACY_PACKAGE_NAME]
    seen: set[str] = set()
    result: list[str] = []
    for item in ordered:
        value = str(item or "").strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)