from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import pytest

from hermes_cli import migrate_from_hermes as migrate_mod


class TestPlanMigration:
    def test_reports_missing_source(self, tmp_path: Path):
        report = migrate_mod.plan_home_migration(
            source_root=tmp_path / ".hermes",
            target_root=tmp_path / ".icarus",
            overwrite=False,
        )

        assert report["summary"]["error"] == 1
        assert report["items"][0]["kind"] == "source-root"
        assert report["items"][0]["status"] == "error"

    def test_plans_files_to_copy(self, tmp_path: Path):
        source = tmp_path / ".hermes"
        target = tmp_path / ".icarus"
        (source / "memories").mkdir(parents=True)
        (source / "memories" / "MEMORY.md").write_text("hello", encoding="utf-8")

        report = migrate_mod.plan_home_migration(
            source_root=source,
            target_root=target,
            overwrite=False,
        )

        assert report["summary"]["migrated"] == 1
        assert report["items"][0]["destination"] == str(target / "memories" / "MEMORY.md")

    def test_marks_existing_target_as_conflict_without_overwrite(self, tmp_path: Path):
        source = tmp_path / ".hermes"
        target = tmp_path / ".icarus"
        source.mkdir()
        target.mkdir()
        (source / "config.yaml").write_text("old: true\n", encoding="utf-8")
        (target / "config.yaml").write_text("new: true\n", encoding="utf-8")

        report = migrate_mod.plan_home_migration(
            source_root=source,
            target_root=target,
            overwrite=False,
        )

        assert report["summary"]["conflict"] == 1
        assert report["items"][0]["status"] == "conflict"


class TestExecuteMigration:
    def test_copies_files_into_icarus_home(self, tmp_path: Path):
        source = tmp_path / ".hermes"
        target = tmp_path / ".icarus"
        (source / "logs").mkdir(parents=True)
        (source / "logs" / "gateway.log").write_text("ok", encoding="utf-8")

        report = migrate_mod.execute_home_migration(
            source_root=source,
            target_root=target,
            overwrite=False,
        )

        assert report["summary"]["migrated"] == 1
        assert (target / "logs" / "gateway.log").read_text(encoding="utf-8") == "ok"

    def test_skips_conflicts_without_overwrite(self, tmp_path: Path):
        source = tmp_path / ".hermes"
        target = tmp_path / ".icarus"
        source.mkdir()
        target.mkdir()
        (source / "config.yaml").write_text("from-source\n", encoding="utf-8")
        (target / "config.yaml").write_text("keep-me\n", encoding="utf-8")

        report = migrate_mod.execute_home_migration(
            source_root=source,
            target_root=target,
            overwrite=False,
        )

        assert report["summary"]["conflict"] == 1
        assert (target / "config.yaml").read_text(encoding="utf-8") == "keep-me\n"


class TestCommandHandler:
    def test_dry_run_prints_preview(self, tmp_path: Path, capsys):
        source = tmp_path / ".hermes"
        source.mkdir()
        (source / "SOUL.md").write_text("persona", encoding="utf-8")
        args = Namespace(source=str(source), target=str(tmp_path / ".icarus"), dry_run=True, overwrite=False, yes=False)

        migrate_mod.migrate_from_hermes_command(args)

        captured = capsys.readouterr()
        assert "Dry Run Results" in captured.out
        assert "SOUL.md" in captured.out

    def test_non_interactive_run_stops_after_preview_without_yes(self, tmp_path: Path, capsys):
        source = tmp_path / ".hermes"
        source.mkdir()
        (source / "config.yaml").write_text("a: 1\n", encoding="utf-8")
        args = Namespace(source=str(source), target=str(tmp_path / ".icarus"), dry_run=False, overwrite=False, yes=False)

        with patch.object(migrate_mod.sys.stdin, "isatty", return_value=False):
            migrate_mod.migrate_from_hermes_command(args)

        captured = capsys.readouterr()
        assert "preview only" in captured.out.lower()
        assert not (tmp_path / ".icarus" / "config.yaml").exists()

    def test_yes_executes_migration(self, tmp_path: Path, capsys):
        source = tmp_path / ".hermes"
        source.mkdir()
        (source / ".env").write_text("OPENAI_API_KEY=test\n", encoding="utf-8")
        target = tmp_path / ".icarus"
        args = Namespace(source=str(source), target=str(target), dry_run=False, overwrite=False, yes=True)

        migrate_mod.migrate_from_hermes_command(args)

        captured = capsys.readouterr()
        assert "Migration complete" in captured.out
        assert (target / ".env").read_text(encoding="utf-8") == "OPENAI_API_KEY=test\n"
