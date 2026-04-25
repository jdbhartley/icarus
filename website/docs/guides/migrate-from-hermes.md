---
sidebar_position: 11
title: "Migrate from Hermes"
description: "Move a legacy ~/.hermes home into Icarus's ~/.icarus layout with a preview-first migration command."
---

# Migrate from Hermes

`icarus migrate-from-hermes` copies an existing legacy `~/.hermes` home into the new default Icarus home at `~/.icarus`.

It is intentionally **preview-first**:
- first it shows exactly what would be copied
- then it asks for confirmation
- your original `~/.hermes` directory is left untouched

## Quick start

```bash
# Preview only
icarus migrate-from-hermes --dry-run

# Preview, then execute after confirmation
icarus migrate-from-hermes

# Execute non-interactively
icarus migrate-from-hermes --yes

# Overwrite files that already exist in ~/.icarus
icarus migrate-from-hermes --overwrite --yes
```

## What it does

The command walks your legacy Hermes home and copies files into the matching path under `~/.icarus`.

Examples:

| Legacy path | New path |
|---|---|
| `~/.hermes/config.yaml` | `~/.icarus/config.yaml` |
| `~/.hermes/.env` | `~/.icarus/.env` |
| `~/.hermes/SOUL.md` | `~/.icarus/SOUL.md` |
| `~/.hermes/memories/` | `~/.icarus/memories/` |
| `~/.hermes/skills/` | `~/.icarus/skills/` |
| `~/.hermes/logs/` | `~/.icarus/logs/` |

## Options

| Option | Description |
|---|---|
| `--source <path>` | Custom legacy Hermes home. Default: `~/.hermes` |
| `--target <path>` | Custom Icarus home. Default: `~/.icarus` |
| `--dry-run` | Show the preview only |
| `--overwrite` | Replace files already present in the target |
| `--yes`, `-y` | Skip the confirmation prompt |

## Conflict behavior

By default, existing files in `~/.icarus` are reported as conflicts and skipped.

Use `--overwrite` if you want the legacy Hermes file to replace the Icarus file.

## Safety notes

- The command **copies** data; it does not delete `~/.hermes`
- It is safe to run a dry run first to inspect the exact file list
- After migration, verify `~/.icarus` works the way you expect before deleting anything from `~/.hermes`
