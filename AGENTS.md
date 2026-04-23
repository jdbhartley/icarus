# Icarus - Development Guide

Instructions for AI coding assistants and developers working on the **Icarus** codebase.

## Rebrand boundary for contributors

This repository is now documented as **Icarus**, the standalone continuation of Hermes Agent. This file uses **Icarus-first project language** while preserving Hermes-era names where they still describe real code, binaries, paths, env vars, or package metadata.

You will still see compatibility identifiers such as:

- package name: `hermes-agent`
- CLI entrypoint: `hermes`
- config/state home: `~/.hermes`
- env vars: `HERMES_HOME`, `HERMES_TUI`, `HERMES_PYTHON`
- internal classes/modules: `HermesCLI`, `hermes_cli`, `hermes_constants`

Do not rename those in code as part of docs work unless the task explicitly includes code or packaging migration.

## Development environment

```bash
source venv/bin/activate  # ALWAYS activate before running Python
```

## Project structure

```text
icarus/
├── run_agent.py          # AIAgent class — core conversation loop
├── model_tools.py        # Tool orchestration, discovery, dispatch
├── toolsets.py           # Toolset definitions and defaults
├── cli.py                # HermesCLI class — interactive CLI orchestrator
├── hermes_state.py       # SessionDB — SQLite session store (FTS5)
├── agent/                # Agent internals
├── hermes_cli/           # CLI subcommands and setup (`hermes ...` entrypoint)
├── tools/                # Tool implementations and backends
├── gateway/              # Messaging platform gateway
├── ui-tui/               # Ink terminal UI (`hermes --tui` today)
├── tui_gateway/          # Python JSON-RPC backend for the TUI
├── acp_adapter/          # ACP server for editor integration
├── cron/                 # Scheduler
├── environments/         # RL / Atropos environments
├── tests/                # Pytest suite
└── batch_runner.py       # Parallel batch processing
```

**Current compatibility home:** `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys)

## Naming guidance

Use these rules in docs, comments, and contributor-facing explanations:

- Say **Icarus** when referring to the project, product, or repo as a whole.
- Keep **Hermes** when referring to a concrete compatibility surface that still exists today.
- Keep exact code identifiers unchanged, even if they include `Hermes`.
- If a user needs to type something, document the real command or path that works now.
- If a historical name is retained, explain why briefly instead of pretending it is already migrated.

## Core dependency chain

```text
tools/registry.py
       ↑
tools/*.py
       ↑
model_tools.py
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

## Agent loop (`run_agent.py`)

`AIAgent` is the main runtime class. The conversation loop is synchronous and alternates between model calls and tool dispatch until the model returns a final answer or iteration budget is exhausted.

High-level pattern:

```python
while api_call_count < self.max_iterations and self.iteration_budget.remaining > 0:
    response = client.chat.completions.create(model=model, messages=messages, tools=tool_schemas)
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = handle_function_call(tool_call.name, tool_call.args, task_id)
            messages.append(tool_result_message(result))
        api_call_count += 1
    else:
        return response.content
```

Messages follow the OpenAI-style role format. Reasoning content is stored separately on assistant messages.

## CLI architecture

The classic interactive terminal interface still ships behind the `hermes` entrypoint.

Key pieces:

- **Rich** for banners, panels, and formatted output
- **prompt_toolkit** for input and autocomplete
- `HermesCLI` in `cli.py` for orchestration
- `load_cli_config()` for config merging
- `hermes_cli/commands.py` as the central slash-command registry
- `agent/skill_commands.py` for dynamic skill command loading

### Slash command registry

All slash commands are defined once in `hermes_cli/commands.py` using `CommandDef`. That single registry feeds:

- CLI dispatch
- gateway dispatch
- gateway help text
- Telegram bot command export
- Slack subcommand routing
- autocomplete
- CLI help groupings

### Adding a slash command

1. Add a `CommandDef` to `hermes_cli/commands.py`
2. Add a handler in `HermesCLI.process_command()` in `cli.py`
3. If gateway-visible, add a handler in `gateway/run.py`
4. For persistent settings, use the existing config save helpers

## TUI architecture (`ui-tui/` + `tui_gateway/`)

The TUI is the full-screen Ink interface for Icarus, currently launched via `hermes --tui` or `HERMES_TUI=1`.

Process model:

```text
hermes --tui
  └─ Node (Ink)  ──stdio JSON-RPC──  Python (tui_gateway)
       │                                  └─ AIAgent + tools + sessions
       └─ renders transcript, composer, prompts, activity
```

TypeScript owns rendering. Python owns sessions, tool execution, model calls, and most slash-command logic.

Important surfaces:

| Surface | Ink side | Gateway side |
|---|---|---|
| chat streaming | `app.tsx`, `messageLine.tsx` | `prompt.submit` → `message.delta/complete` |
| tool activity | `thinking.tsx` | `tool.start/progress/complete` |
| approvals | `prompts.tsx` | `approval.request` / `approval.respond` |
| clarify / sudo / secret | prompt components | `clarify.*`, `sudo.*`, `secret.*` |
| session picker | `sessionPicker.tsx` | `session.list/resume` |
| completions | `useCompletion` | `complete.slash`, `complete.path` |
| theming | `theme.ts`, `branding.tsx` | `gateway.ready` skin payload |

Useful dev commands:

```bash
cd ui-tui
npm install
npm run dev
npm start
npm run build
npm run type-check
npm run lint
npm run fmt
npm test
```

## Adding new tools

Required changes:

1. Create `tools/your_tool.py`
2. Register it with `tools.registry`
3. Add it to `toolsets.py` if needed

Rules:

- tool handlers must return JSON strings
- top-level `registry.register()` enables auto-discovery
- use `get_hermes_home()` for persistent state paths
- use `display_hermes_home()` for user-facing path text in schema descriptions
- do not hardcode `Path.home() / ".hermes"`

## Configuration surfaces

Two major config types:

### `config.yaml`

- defaults live in `hermes_cli/config.py`
- bump `_config_version` when migration is required

### `.env`

- optional environment variables are described in `OPTIONAL_ENV_VARS`
- include description, prompt text, source URL when relevant, and password/category metadata

### Config loaders

| Loader | Used by | Location |
|---|---|---|
| `load_cli_config()` | classic CLI mode | `cli.py` |
| `load_config()` | setup/tools/config helpers | `hermes_cli/config.py` |
| direct YAML load | gateway | `gateway/run.py` |

## Profiles and filesystem safety

Icarus still uses Hermes-era profile plumbing. Profiles are isolated by `HERMES_HOME`.

Contributor rules:

1. **Use `get_hermes_home()` for runtime state paths.**
2. **Never hardcode `~/.hermes` in code that reads or writes state.**
3. **Use display helpers for user-facing path strings.**
4. **Tests that depend on home paths must set `HERMES_HOME`.**
5. **Profile roots are HOME-anchored, not derived by appending to the current `HERMES_HOME`.**

Bad:

```python
path = Path.home() / ".hermes" / "config.yaml"
```

Good:

```python
from hermes_constants import get_hermes_home
path = get_hermes_home() / "config.yaml"
```

## Prompt caching policy

Prompt caching must not be broken by incidental changes.

Do **not** implement changes that:

- alter past context mid-conversation
- change toolsets mid-conversation
- rebuild system prompts mid-conversation
- reload memory unexpectedly during a live session

The intended context-changing escape hatch is context compression, not arbitrary mutation.

## Working directory behavior

- **CLI/TUI:** current working directory by default
- **Messaging:** `MESSAGING_CWD` env var, defaulting to the user's home directory

## Tests

Guardrails:

- tests must not write to the real `~/.hermes/`
- use temp directories plus `HERMES_HOME`
- preserve isolation provided by the test fixtures in `tests/conftest.py`

Typical pattern:

```python
home = tmp_path / ".hermes"
home.mkdir()
monkeypatch.setenv("HERMES_HOME", str(home))
```

## Docs-writing policy for this repo

For the docs-facing rebrand work in this standalone repo:

- prefer **Icarus** in headings, summaries, intros, and product descriptions
- preserve **Hermes** only for live compatibility facts, legal/history context, or exact code identifiers
- when in doubt, explain the boundary in one line rather than erasing history
- do not silently rewrite commands, env vars, or file paths to nonfunctional Icarus names

## Quick contributor summary

- Project name: **Icarus**
- Current working CLI binary: `hermes`
- Current config/state home: `~/.hermes`
- Current package metadata: `hermes-agent`
- Safe docs posture: Icarus-first presentation, Hermes-only where operationally necessary
