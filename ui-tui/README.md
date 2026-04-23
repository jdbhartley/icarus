# Icarus TUI

The Ink-based terminal UI for **Icarus**. TypeScript owns the screen; Python owns sessions, tools, model calls, and most slash-command logic.

## Compatibility note

This repo's TUI is now documented as part of **Icarus**, but the current launcher, env vars, paths, and some internal package names still retain Hermes-era identifiers:

- launch command: `hermes --tui`
- TUI gate env var: `HERMES_TUI=1`
- interpreter override: `HERMES_PYTHON`
- state/config base: `~/.hermes`, `HERMES_HOME`
- internal names like `HermesCLI`, `hermes-ink`, and `tui_gateway`

Those are real runtime surfaces today, so they stay in the examples below.

## Launching the TUI

From an installed environment:

```bash
hermes --tui
```

From the repo root, that launches the current Icarus TUI through the compatibility CLI.

## Process model

The client entrypoint is `src/entry.tsx`. It exits early if `stdin` is not a TTY, starts `GatewayClient`, then renders `App`.

`GatewayClient` spawns:

```text
python -m tui_gateway.entry
```

Interpreter resolution order:

```text
HERMES_PYTHON
→ PYTHON
→ $VIRTUAL_ENV/bin/python
→ ./.venv/bin/python
→ ./venv/bin/python
→ python3
→ python
```

Transport is newline-delimited JSON-RPC over stdio:

```text
ui-tui/src                  tui_gateway/
-----------                 -------------
entry.tsx                   entry.py
  -> GatewayClient            -> request loop
  -> App                      -> server.py RPC handlers

stdin/stdout: JSON-RPC requests, responses, events
stderr: captured into an in-memory log ring
```

Malformed stdout lines are treated as protocol noise and surfaced as `gateway.protocol_error`. Stderr becomes `gateway.stderr`. Neither writes directly into the terminal buffer.

## Running locally

Normal path from the repo root:

```bash
hermes --tui
```

The Python CLI expects `ui-tui/node_modules` to exist. If dependencies are missing:

```bash
cd ui-tui
npm install
```

Local package commands:

```bash
npm run dev
npm start
npm run build
npm run lint
npm run fmt
npm run fix
npm test
npm run test:watch
```

## App model

`src/app.tsx` is the center of the UI. Heavier logic lives under `src/app/`:

- `createGatewayEventHandler.ts` — event → state mapping
- `createSlashHandler.ts` — local slash dispatch
- `useComposerState.ts` — draft, multiline buffer, queue editing
- `useInputHandlers.ts` — keypress routing
- `useTurnState.ts` — assistant turn lifecycle
- `overlayStore.ts` / `uiStore.ts` — nanostores for overlays and UI flags
- `gatewayContext.tsx` — React context for the gateway client

The rendered Ink tree includes:

- static transcript output
- streaming assistant row
- prompt overlays
- queued message preview
- status rule
- input line
- completion list

The intro panel is driven by `session.info` and rendered through `components/branding.tsx`.

## Hotkeys and interaction model

### Main chat input

| Key | Behavior |
|---|---|
| `Enter` | Submit the current draft |
| empty `Enter` twice | Interrupt the current run or send the next queued message, depending on state |
| `Shift+Enter` / `Alt+Enter` | Insert newline |
| `\` + `Enter` | Append line to multiline buffer |
| `Ctrl+C` | Interrupt active work, clear draft, or exit |
| `Ctrl+D` | Exit |
| `Ctrl+G` | Open `$EDITOR` with the current draft |
| `Ctrl+L` | New session (`/clear`) |
| `Ctrl+V` / `Alt+V` | Paste clipboard image |
| `Tab` | Apply active completion |
| `Up/Down` | Cycle completions, edit queued drafts, or navigate history |
| `!cmd` | Run a shell command through the gateway |
| `{!cmd}` | Inline shell interpolation before send |

### Prompt and picker modes

| Context | Keys | Behavior |
|---|---|---|
| approval prompt | `Up/Down`, `Enter` | move and confirm approval choice |
| approval prompt | `o`, `s`, `a`, `d` | quick-pick once / session / always / deny |
| clarify prompt | `Up/Down`, `Enter` | select a choice |
| clarify prompt | digit key | quick-pick a numbered choice |
| sudo / secret prompt | `Enter` | submit typed value |
| sudo / secret prompt | `Ctrl+C` | cancel with empty response |
| resume picker | `Up/Down`, `Enter` | select session |
| resume picker | `1-9` | quick-pick visible session |

### Interaction rules

- Plain text entered while the assistant is busy is queued.
- Slash commands and `!cmd` execute immediately and do not queue.
- Queue auto-drains after each assistant response unless a queued item is being edited.
- Completion requests are debounced by 60 ms.
- `Ctrl+G` writes the full draft to a temp file, swaps buffers, opens `$EDITOR`, restores the TUI, and submits the edited text if the editor exits cleanly.
- Input history is currently stored under `~/.hermes/.hermes_history` or the directory pointed to by `HERMES_HOME`.

## Prompt flows

The Python gateway can pause the main loop and request structured input:

- `approval.request`
- `clarify.request`
- `sudo.request`
- `secret.request`
- `session.list`

These are stateful UI branches inside `app.tsx`, not separate screens.

## Slash commands

The local TUI slash handler owns built-ins that require direct client behavior:

- `/help`
- `/quit`, `/exit`, `/q`
- `/clear`
- `/new`
- `/compact`
- `/resume`
- `/copy`
- `/paste`
- `/details`
- `/logs`
- `/statusbar`, `/sb`
- `/queue`
- `/undo`
- `/retry`

Everything else falls through to:

1. `slash.exec`
2. `command.dispatch`

That keeps aliases, skills, plugins, and registry-backed command logic on the Python side.

## Event surface

Primary client events:

| Event | Payload |
|---|---|
| `gateway.ready` | `{ skin? }` |
| `session.info` | session metadata for banner and tool/skill panels |
| `message.start` | begin assistant streaming |
| `message.delta` | `{ text, rendered? }` |
| `message.complete` | `{ text, rendered?, usage, status }` |
| `thinking.delta` / `reasoning.delta` | incremental reasoning text |
| `status.update` | `{ kind, text }` |
| `tool.start` / `tool.progress` / `tool.complete` | live tool activity |
| `clarify.request` | `{ question, choices?, request_id }` |
| `approval.request` | `{ command, description }` |
| `sudo.request` / `secret.request` | masked prompt requests |
| `background.complete` | `{ task_id, text }` |
| `btw.complete` | `{ text }` |
| `error` | `{ message }` |
| `gateway.stderr` | synthesized child stderr |
| `gateway.protocol_error` | synthesized malformed stdout |

## Theme model

The client starts with `DEFAULT_THEME` from `theme.ts`, then merges skin data delivered in `gateway.ready`.

Current branding overrides include:

- agent name
- prompt symbol
- welcome text
- goodbye text

Current color overrides include:

- banner title, accent, border, body, dim
- label, ok, error, warn

`components/branding.tsx` uses these values for the logo, session panel, and update notice.

## File map

```text
ui-tui/
  packages/hermes-ink/   forked Ink renderer (legacy internal name)
  src/
    entry.tsx            TTY gate + render()
    app.tsx              top-level Ink tree, composes src/app/*
    gatewayClient.ts     child process + JSON-RPC bridge
    theme.ts             default palette + skin merge
    constants.ts         display constants, hotkeys, tool labels
    types.ts             shared client-side types
    banner.ts            ASCII art data

    app/
      createGatewayEventHandler.ts  event → state mapping
      createSlashHandler.ts         local slash dispatch
      useComposerState.ts           draft + multiline + queue editing
      useInputHandlers.ts           keypress routing
      useTurnState.ts               assistant turn lifecycle
      overlayStore.ts               nanostores for overlays
      uiStore.ts                    nanostores for UI flags
      gatewayContext.tsx            React context for gateway client
      constants.ts                  app-level constants
      helpers.ts                    pure helpers
      interfaces.ts                 internal interfaces

    components/
      appChrome.tsx      status bar, input row, completions
      appLayout.tsx      top-level layout composition
      appOverlays.tsx    overlay routing
      branding.tsx       banner + session summary
      markdown.tsx       Markdown-to-Ink renderer
      maskedPrompt.tsx   masked input for sudo / secrets
      messageLine.tsx    transcript rows
      modelPicker.tsx    model switch picker
      prompts.tsx        approval + clarify flows
      queuedMessages.tsx queued input preview
      sessionPicker.tsx  session resume picker
      textInput.tsx      custom line editor
      thinking.tsx       spinner, reasoning, tool activity

    hooks/
      useCompletion.ts   slash + path completion
      useInputHistory.ts persistent history navigation
      useQueue.ts        queued message management
      useVirtualHistory.ts in-memory history for pickers

    lib/
      history.ts         persistent input history
      messages.ts        message formatting helpers
      osc52.ts           OSC 52 clipboard copy
      rpc.ts             JSON-RPC type helpers
      text.ts            ANSI detection and text helpers

    types/
      hermes-ink.d.ts    declarations for @hermes/ink
```

Related Python side:

```text
tui_gateway/
  entry.py               stdio entrypoint
  server.py              RPC handlers and session logic
  render.py              optional rich/ANSI bridge
  slash_worker.py        persistent HermesCLI subprocess for slash commands
```

## Rebrand boundary for this document

This README now presents the TUI as part of **Icarus**. Hermes references remain only where they point at current compatibility-critical runtime facts: command names, env vars, filesystem locations, package names, and code identifiers that have not yet been renamed.
