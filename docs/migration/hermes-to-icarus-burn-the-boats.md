# Hermes to Icarus: burn-the-boats migration and docs audit

## Purpose

This document records the **docs-facing** portion of the rebrand from **Hermes Agent** to **Icarus** in the standalone repository. It explains what changed, what intentionally did **not** change, and why the remaining Hermes references are still present.

Scope of this pass:

- `README.md`
- `AGENTS.md`
- `ui-tui/README.md`
- this migration/audit document

Out of scope for this pass:

- Python module renames
- package metadata updates
- executable renames
- environment variable renames
- installer or publishing changes
- website-wide content sweep
- code behavior changes

## Executive summary

The repo is now documented as **Icarus**, a standalone project, rather than as a derivative or sub-brand presented primarily as Hermes Agent.

At the same time, the runtime still ships through Hermes-era compatibility surfaces such as:

- package name `hermes-agent`
- executable `hermes`
- config/state directory `~/.hermes`
- env vars like `HERMES_HOME`, `HERMES_TUI`, and `HERMES_PYTHON`
- internal code identifiers like `HermesCLI`, `hermes_cli`, and `hermes_constants`

The core rule of this migration is therefore:

> **Present the project as Icarus, but do not falsify live runtime facts.**

## Why a docs-only burn-the-boats pass exists

A full rename touches packaging, installer URLs, environment variables, config paths, entrypoints, module names, tests, release automation, and migration guarantees for existing users. That is a much riskier change than rebranding the docs layer.

A docs-only pass lets the standalone repo establish a clear project identity immediately while preserving:

- installability
- upgrade continuity
- profile/state compatibility
- existing scripts and user muscle memory
- references from release notes, issues, and external guides

In short: **brand now, break less, migrate the runtime later**.

## What changed in this pass

### 1. Top-level README now presents the project as Icarus

The old README centered Hermes Agent as the product identity. The new README now:

- names the project **Icarus** at the top
- describes it as the standalone continuation of the Hermes Agent codebase
- explains the compatibility boundary up front
- keeps only the Hermes references required for real commands, paths, and packaging facts
- points readers to this audit document for rationale

### 2. Contributor guidance now uses Icarus-first framing

`AGENTS.md` previously introduced the codebase as Hermes Agent throughout. It now:

- identifies the repo as **Icarus**
- teaches contributors when to use **Icarus** versus **Hermes** language
- preserves exact code identifiers where they remain Hermes-named
- explicitly warns against docs drift that invents nonfunctional Icarus commands or paths

### 3. TUI docs now describe the UI as the Icarus TUI

`ui-tui/README.md` now presents the terminal UI as part of Icarus while keeping runtime-accurate details such as:

- launch command `hermes --tui`
- `HERMES_TUI` and `HERMES_PYTHON`
- `~/.hermes` / `HERMES_HOME`
- internal names like `hermes-ink` and `HermesCLI`

### 4. A durable migration/audit trail now exists

This document exists so later runtime/package renames can distinguish between:

- **already rebranded docs surfaces**
- **deliberately retained Hermes compatibility surfaces**
- **future rename work that still remains**

## What still remains Hermes, and why

This section is the most important part of the audit.

### A. Package metadata remains Hermes

Observed current facts in `pyproject.toml`:

- project name: `hermes-agent`
- console scripts: `hermes`, `hermes-agent`, `hermes-acp`
- extras continue to reference `hermes-agent[...]`

Why retained:

- changing package metadata is a packaging migration, not a docs edit
- downstream install commands and dependency references would break
- release automation and existing installations may depend on the current names

Docs implication:

- documentation should identify the project as Icarus
- commands that users actually run must still show the current Hermes-era package/binary names

### B. Executable names remain Hermes

Current executable examples still use:

- `hermes`
- `hermes --tui`
- `hermes gateway`
- `hermes setup`
- `hermes claw migrate`

Why retained:

- these are the commands users can actually execute today
- changing docs to `icarus` would create immediate setup failures
- shell aliases and wrappers are out of scope for the current pass

Docs implication:

Use phrasing like:

- “launch Icarus with `hermes`”
- “current compatibility CLI binary: `hermes`”

That keeps the project identity current without lying about the executable name.

### C. Filesystem and env-var surfaces remain Hermes

Current state/config surfaces still include:

- `~/.hermes`
- `HERMES_HOME`
- `HERMES_TUI`
- `HERMES_PYTHON`

Why retained:

- these names are embedded in working code
- profile isolation and migration logic already depend on them
- renaming them would require data migration and careful backward compatibility handling

Docs implication:

- do not rewrite these to imaginary `~/.icarus` or `ICARUS_HOME` values yet
- do explain that they are compatibility-era identifiers

### D. Internal code identifiers remain Hermes

Examples:

- `HermesCLI`
- `hermes_cli`
- `hermes_constants`
- `display_hermes_home()`
- `get_hermes_home()`

Why retained:

- code identifier renames are out of scope
- broad internal renames would create unnecessary code churn in a docs-only pass
- developer docs must stay aligned with the code that contributors will actually edit

Docs implication:

- rename conceptual framing to Icarus
- keep exact symbol names untouched when referencing implementation details

### E. Historical references remain where they are materially true

Examples of acceptable retained Hermes mentions:

- “standalone continuation of Hermes Agent”
- links, issue trackers, or install surfaces still hosted under Hermes-era names
- migration content that explains how Hermes-era assets map into the standalone Icarus presentation

Why retained:

- removing all history would make the docs less accurate, not more
- users and contributors need continuity across prior releases, repos, and support discussions

## What was intentionally removed or rewritten

The following style changes guided this pass:

### Rewritten

- product-name headings that led with Hermes Agent
- intros that framed the repo primarily as Hermes rather than Icarus
- generic prose saying “Hermes” where no compatibility reason required it
- TUI and contributor docs that could safely say “Icarus” at the product level

### Not rewritten

- literal commands users must run now
- literal path/env-var examples that must work now
- literal code identifiers
- metadata-backed package names

## Language policy established by this audit

Going forward, docs in this repo should follow this rule set.

### Say “Icarus” for:

- project identity
- repo-level descriptions
- marketing/product summaries
- headings and document titles
- contributor introductions
- UI descriptions at the product layer

### Keep “Hermes” for:

- executable names that exist today
- package names that exist today
- filesystem/config/env-var names that exist today
- exact code identifiers
- legally or historically relevant references
- migration narratives where historical continuity matters

### Avoid:

- pretending the runtime rename is already done
- inventing `icarus` commands that do not exist
- inventing `~/.icarus` or `ICARUS_HOME` before code support exists
- deleting all Hermes mentions without regard for accuracy

## Suggested future work after this docs pass

A later runtime migration can use this document as the checklist boundary.

### Phase 1: compatibility-preserving runtime additions

Possible future steps:

- add an `icarus` console script alias alongside `hermes`
- add docs/build-site redirects from Hermes-era URLs
- introduce dual-recognized env vars where safe
- introduce user-facing messaging that prefers Icarus while honoring Hermes paths

### Phase 2: structured migration of state and packaging

Possible future steps:

- package rename from `hermes-agent` to an Icarus-native name
- data migration or dual-path support for `~/.hermes`
- env-var transition strategy from `HERMES_*` to `ICARUS_*`
- installer and release pipeline cutover
- documentation sweep across `website/docs/` and release materials

### Phase 3: internal code-symbol cleanup

Possible future steps:

- rename internal modules/classes only after compatibility layers are in place
- update tests, imports, scripts, and ecosystem references in one coordinated change
- retain migration notes long enough to support contributors through the transition

## Verification notes for this pass

This pass was designed to satisfy four constraints simultaneously:

1. **Icarus-first presentation** — the standalone repo now reads as Icarus in its key docs surfaces.
2. **Runtime accuracy** — commands and paths shown to users still work as documented.
3. **Historical continuity** — necessary Hermes references are preserved, not erased.
4. **Limited blast radius** — no code, packaging, or behavioral changes were required.

## File-by-file audit summary

| File | Result |
|---|---|
| `README.md` | Rewritten to present the project as Icarus, with explicit compatibility notes for Hermes-era commands and paths |
| `AGENTS.md` | Rewritten to guide contributors with Icarus-first language while preserving exact implementation identifiers |
| `ui-tui/README.md` | Rewritten to present the terminal UI as the Icarus TUI while retaining real launcher/env/path details |
| `docs/migration/hermes-to-icarus-burn-the-boats.md` | Added as the authoritative explanation of the docs rebrand boundary and remaining Hermes surfaces |

## Bottom line

The standalone repo now speaks with an **Icarus** voice at the docs layer.

What remains Hermes is not accidental residue; it is the set of **currently real compatibility surfaces** that still exist in code, packaging, and user environments. This document exists so those retained names are understood as deliberate, temporary, and auditable rather than as rebrand drift.
