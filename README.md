<p align="center">
  <img src="assets/banner.png" alt="Icarus" width="100%">
</p>

# Icarus

<p align="center">
  <a href="./website/docs/index.md"><img src="https://img.shields.io/badge/Docs-Icarus-FFD700?style=for-the-badge" alt="Documentation"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Built%20by-Nous%20Research-blueviolet?style=for-the-badge" alt="Built by Nous Research"></a>
</p>

**Icarus is Nous Research's standalone agent runtime for local, remote, and messaging-native workflows.** It gives you a real terminal UI, a messaging gateway, broad model/provider support, durable memory and skills, agent delegation, scheduled automation, and research-oriented tooling in one repo.

This repository is the **burn-the-boats** standalone continuation of the Hermes Agent codebase. The project is now presented as **Icarus** at the documentation layer, while some shipped identifiers still intentionally retain Hermes-era names for compatibility.

## Naming status: Icarus project, Hermes-era runtime identifiers

Today, the user-facing project name is **Icarus**. However, because packaging metadata and runtime identifiers are intentionally out of scope for this docs-only rebrand pass, you will still encounter:

- package metadata such as `hermes-agent`
- CLI entrypoints such as `hermes`
- config and state paths such as `~/.hermes`
- environment variables such as `HERMES_HOME` and `HERMES_TUI`
- internal module/class names such as `HermesCLI`

Those names are retained for continuity and upgrade safety until the code and packaging migration happens. See [docs/migration/hermes-to-icarus-burn-the-boats.md](docs/migration/hermes-to-icarus-burn-the-boats.md) for the audit trail.

## What Icarus does

<table>
<tr><td><b>Real terminal UX</b></td><td>Interactive CLI and full TUI, multiline editing, slash-command completion, streaming tool output, queueing, approvals, and session continuity.</td></tr>
<tr><td><b>Messaging-native</b></td><td>Run one gateway and talk to Icarus from Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Home Assistant, and other adapters.</td></tr>
<tr><td><b>Memory and skills</b></td><td>Persistent memory, self-curated skills, session search, user modeling, and compatible skill workflows.</td></tr>
<tr><td><b>Automation</b></td><td>Built-in cron scheduling, background jobs, delegated subagents, and RPC-driven scripting.</td></tr>
<tr><td><b>Runs where the work is</b></td><td>Local, Docker, SSH, Daytona, Singularity, and Modal terminal backends let the agent live close to the environment it operates on.</td></tr>
<tr><td><b>Research-ready</b></td><td>Trajectory capture, RL environments, and batch workflows for tool-calling model development.</td></tr>
</table>

---

## Quick install

The current install surface still uses Hermes-era package and binary names:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

After install, launch Icarus through the current compatibility binary:

```bash
source ~/.bashrc    # or: source ~/.zshrc
hermes              # launches the current Icarus runtime
```

Platform notes:

- **Linux / macOS / WSL2:** supported by the installer above.
- **Android / Termux:** use the tested Termux guide in `website/docs/getting-started/termux.md`. Termux still relies on the curated Hermes-era extras split.
- **Windows:** use WSL2. Native Windows remains unsupported.

---

## Getting started

Use the existing CLI entrypoint, but read it as “launch Icarus”:

```bash
hermes              # start an interactive Icarus session
hermes --tui        # launch the Ink-based terminal UI
hermes model        # choose a provider/model
hermes tools        # enable or disable toolsets
hermes config set   # update individual config values
hermes gateway      # start the messaging gateway
hermes setup        # run the interactive setup flow
hermes update       # update the installed runtime
hermes doctor       # diagnose setup issues
```

If you are migrating from OpenClaw, the compatibility migration command still exists:

```bash
hermes claw migrate
```

## CLI vs messaging quick reference

Icarus has two main operating modes: direct terminal use and gateway-driven messaging. The current commands remain Hermes-era for compatibility.

| Action | Terminal | Messaging |
|---|---|---|
| Start chatting | `hermes` or `hermes --tui` | Run `hermes gateway setup` + `hermes gateway start`, then message the bot |
| Start a fresh session | `/new` or `/reset` | `/new` or `/reset` |
| Change model | `/model [provider:model]` | `/model [provider:model]` |
| Set personality | `/personality [name]` | `/personality [name]` |
| Retry / undo | `/retry`, `/undo` | `/retry`, `/undo` |
| Compress / inspect usage | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]` |
| Browse skills | `/skills` or `/<skill-name>` | `/skills` or `/<skill-name>` |
| Interrupt work | `Ctrl+C` or send a new prompt | `/stop` or send a new message |

## Documentation map

This repo still contains a substantial Hermes-branded docs tree under `website/docs/`. For this rebrand pass, use the following Icarus-first orientation:

| Where | What it covers |
|---|---|
| `website/docs/getting-started/` | installation, quickstart, update flows |
| `website/docs/user-guide/` | CLI, TUI, config, sessions, security, messaging |
| `website/docs/user-guide/features/` | tools, skills, memory, browser, cron, plugins, ACP, voice, and more |
| `website/docs/developer-guide/` | architecture, tools runtime, provider/runtime internals, contribution docs |
| `docs/migration/hermes-to-icarus-burn-the-boats.md` | rebrand audit, compatibility boundaries, rationale |

---

## Contributing

Icarus is now documented as a standalone project, but the development bootstrap remains compatibility-based:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh
./hermes
```

Manual equivalent:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,dev]"
```

If you need the optional RL/Atropos stack:

```bash
git submodule update --init tinker-atropos
uv pip install -e "./tinker-atropos"
```

For contributor-facing naming guidance, see [AGENTS.md](AGENTS.md).

---

## Historical and compatibility references

The following Hermes references are intentionally retained in docs when they point to real, current compatibility surfaces:

- the installer URL and repo path under `NousResearch/hermes-agent`
- the `hermes` executable and related subcommands
- `~/.hermes` and `HERMES_HOME`
- Hermes-named Python modules, classes, extras, and scripts
- migration guidance that explicitly describes movement from older Hermes/OpenClaw surfaces

Everything else in this document has been rewritten to present the project as **Icarus first**.

---

## Community

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 💡 [Discussions](https://github.com/NousResearch/hermes-agent/discussions)

## License

MIT — see [LICENSE](LICENSE).

Built by [Nous Research](https://nousresearch.com).
