"""Icarus migration helper for importing an existing ~/.hermes home into ~/.icarus."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

from hermes_cli.setup import (
    Colors,
    color,
    print_error,
    print_header,
    print_info,
    print_success,
    prompt_yes_no,
)
from hermes_constants import ICARUS_HOME_DIRNAME, LEGACY_HERMES_HOME_DIRNAME


_DEF_EXCLUDES = {
    "__pycache__",
    ".DS_Store",
}


def default_legacy_home() -> Path:
    return Path.home() / LEGACY_HERMES_HOME_DIRNAME


def default_icarus_home() -> Path:
    return Path.home() / ICARUS_HOME_DIRNAME


def _iter_source_files(source_root: Path):
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _DEF_EXCLUDES for part in path.parts):
            continue
        yield path


def _new_report(source_root: Path, target_root: Path, overwrite: bool) -> dict[str, Any]:
    return {
        "source_root": str(source_root),
        "target_root": str(target_root),
        "overwrite": overwrite,
        "items": [],
        "summary": {"migrated": 0, "skipped": 0, "conflict": 0, "error": 0},
    }


def _record(report: dict[str, Any], *, kind: str, source: Path | None, destination: Path | None, status: str, reason: str = "") -> None:
    report["items"].append(
        {
            "kind": kind,
            "source": str(source) if source else None,
            "destination": str(destination) if destination else None,
            "status": status,
            "reason": reason,
        }
    )
    report["summary"][status] += 1


def plan_home_migration(source_root: Path, target_root: Path, overwrite: bool = False) -> dict[str, Any]:
    report = _new_report(source_root, target_root, overwrite)

    if not source_root.exists():
        _record(
            report,
            kind="source-root",
            source=source_root,
            destination=target_root,
            status="error",
            reason="Legacy Hermes home does not exist",
        )
        return report

    if not source_root.is_dir():
        _record(
            report,
            kind="source-root",
            source=source_root,
            destination=target_root,
            status="error",
            reason="Legacy Hermes home is not a directory",
        )
        return report

    if source_root.resolve() == target_root.resolve():
        _record(
            report,
            kind="source-root",
            source=source_root,
            destination=target_root,
            status="error",
            reason="Source and target are the same path",
        )
        return report

    files = list(_iter_source_files(source_root))
    if not files:
        _record(
            report,
            kind="source-root",
            source=source_root,
            destination=target_root,
            status="skipped",
            reason="No files found to migrate",
        )
        return report

    for source_path in files:
        rel = source_path.relative_to(source_root)
        dest_path = target_root / rel
        if dest_path.exists() and not overwrite:
            _record(
                report,
                kind=rel.as_posix(),
                source=source_path,
                destination=dest_path,
                status="conflict",
                reason="Destination already exists",
            )
        else:
            _record(
                report,
                kind=rel.as_posix(),
                source=source_path,
                destination=dest_path,
                status="migrated",
                reason="Would copy" if not overwrite else "Would copy/overwrite",
            )

    return report


def execute_home_migration(source_root: Path, target_root: Path, overwrite: bool = False) -> dict[str, Any]:
    report = plan_home_migration(source_root=source_root, target_root=target_root, overwrite=overwrite)
    if report["summary"]["error"]:
        return report

    executed_items: list[dict[str, Any]] = []
    summary = {"migrated": 0, "skipped": 0, "conflict": 0, "error": 0}

    for item in report["items"]:
        status = item["status"]
        if status != "migrated":
            executed_items.append(item)
            summary[status] += 1
            continue

        source = Path(item["source"])
        destination = Path(item["destination"])
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            executed_items.append({**item, "reason": "Copied" if not overwrite else "Copied/overwritten"})
            summary["migrated"] += 1
        except OSError as exc:
            executed_items.append({**item, "status": "error", "reason": str(exc)})
            summary["error"] += 1

    report["items"] = executed_items
    report["summary"] = summary
    return report


def _print_report(report: dict[str, Any], *, dry_run: bool) -> None:
    summary = report.get("summary", {})
    items = report.get("items", [])

    print()
    print_header("Dry Run Results" if dry_run else "Migration Results")
    if dry_run:
        print_info("No files were modified. This is a preview of what would happen.")

    migrated_items = [item for item in items if item.get("status") == "migrated"]
    conflict_items = [item for item in items if item.get("status") == "conflict"]
    skipped_items = [item for item in items if item.get("status") == "skipped"]
    error_items = [item for item in items if item.get("status") == "error"]

    if migrated_items:
        print()
        print(color("  ✓ Would migrate:" if dry_run else "  ✓ Migrated:", Colors.GREEN))
        for item in migrated_items:
            dest = (item.get("destination") or "").replace(str(Path.home()), "~")
            print(f"      {item.get('kind', 'unknown'):<24s} → {dest}")

    if conflict_items:
        print()
        print(color("  ⚠ Conflicts:", Colors.YELLOW))
        for item in conflict_items:
            print(f"      {item.get('kind', 'unknown'):<24s}  {item.get('reason', '')}")

    if skipped_items:
        print()
        print(color("  ─ Skipped:", Colors.DIM))
        for item in skipped_items:
            print(f"      {item.get('kind', 'unknown'):<24s}  {item.get('reason', '')}")

    if error_items:
        print()
        print(color("  ✗ Errors:", Colors.RED))
        for item in error_items:
            print(f"      {item.get('kind', 'unknown'):<24s}  {item.get('reason', '')}")

    parts = []
    if summary.get("migrated"):
        parts.append(f"{summary['migrated']} {'would migrate' if dry_run else 'migrated'}")
    if summary.get("conflict"):
        parts.append(f"{summary['conflict']} conflict(s)")
    if summary.get("skipped"):
        parts.append(f"{summary['skipped']} skipped")
    if summary.get("error"):
        parts.append(f"{summary['error']} error(s)")

    print()
    print_info(f"Summary: {', '.join(parts) if parts else 'Nothing to migrate.'}")
    if dry_run:
        print_info("To execute the migration, re-run without --dry-run or pass --yes in non-interactive mode.")


def migrate_from_hermes_command(args) -> None:
    source_root = Path(getattr(args, "source", None) or default_legacy_home()).expanduser()
    target_root = Path(getattr(args, "target", None) or default_icarus_home()).expanduser()
    dry_run = bool(getattr(args, "dry_run", False))
    overwrite = bool(getattr(args, "overwrite", False))
    auto_yes = bool(getattr(args, "yes", False))

    print()
    print(color("┌─────────────────────────────────────────────────────────┐", Colors.MAGENTA))
    print(color("│        ⚕ Icarus — Hermes Home Migration                │", Colors.MAGENTA))
    print(color("└─────────────────────────────────────────────────────────┘", Colors.MAGENTA))
    print()
    print_header("Migration Settings")
    print_info(f"Source:      {source_root}")
    print_info(f"Target:      {target_root}")
    print_info(f"Overwrite:   {'yes' if overwrite else 'no (skip conflicts)'}")

    preview_report = plan_home_migration(source_root=source_root, target_root=target_root, overwrite=overwrite)
    if preview_report["summary"]["error"]:
        print()
        for item in preview_report["items"]:
            print_error(item.get("reason", "Migration planning failed"))
        return

    print()
    print_header("Migration Preview")
    _print_report(preview_report, dry_run=True)

    if dry_run:
        return

    if not auto_yes:
        if not sys.stdin.isatty():
            print()
            print_info("Non-interactive session — preview only. Re-run with --yes to execute.")
            return
        if not prompt_yes_no("Proceed with migration?", default=True):
            print_info("Migration cancelled.")
            return

    report = execute_home_migration(source_root=source_root, target_root=target_root, overwrite=overwrite)
    _print_report(report, dry_run=False)
    if report["summary"].get("migrated"):
        print()
        print_success("Migration complete!")
        print_info("Your legacy ~/.hermes data is still untouched. Remove it manually after you verify ~/.icarus.")
