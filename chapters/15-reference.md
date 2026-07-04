# Chapter 15: Reference — Shortcuts, Commands, CLI Flags, Models, Troubleshooting

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs, 2026-07-04 (Claude Code 2.1.201)
>
> **Previous:** [Vercel Integration](14-vercel.md) · **Back to:** [README](../README.md)

## Keyboard Shortcuts

(Exact behavior verified against the official interactive-mode reference. macOS Option-key shortcuts require "Option as Meta" in your terminal.)

| Shortcut | Action |
|----------|--------|
| `Shift+Tab` | **Cycle permission modes** (default → acceptEdits → plan → …) — the fastest way into plan mode |
| `Esc` | Interrupt Claude mid-turn (work done so far is kept) |
| `Esc Esc` | Clear the input draft; on an **empty** prompt, opens the **rewind menu** (restore code/conversation) |
| `Ctrl+O` | Toggle the transcript viewer (detailed tool usage, expanded MCP calls) |
| `Ctrl+T` | Toggle Claude's task checklist |
| `Ctrl+B` | Move a running Bash command/agent to the background (twice under tmux) |
| `Ctrl+X Ctrl+K` | Stop all running background subagents (press twice to confirm) |
| `Ctrl+R` | Reverse-search prompt history (`Ctrl+S` cycles scope: session/project/all) |
| `Ctrl+G` | Open your current prompt in your default text editor |
| `Ctrl+L` | Redraw the screen |
| `Ctrl+U` / `Ctrl+K` / `Ctrl+W` / `Ctrl+Y` | Delete to line start / to line end / previous word / paste deleted text |
| `Option+T` / `Alt+T` | Toggle extended thinking (no effect on Fable 5, which always thinks) |
| `Option+P` / `Alt+P` | Switch model without clearing your prompt |
| `Option+O` / `Alt+O` | Toggle fast mode |
| `Shift+Enter` or `\`+`Enter` or `Ctrl+J` | Multiline input (run `/terminal-setup` for VS Code/Cursor/Zed bindings) |
| `!command` | Shell mode: run a command directly; output lands in context and Claude responds to it (disable via `respondToBashCommands: false`) |
| `@filepath` | File path autocomplete / reference |
| `/command` | Run a command or skill |
| Hold `Space` | Voice dictation (if enabled) |

## Useful Built-in Commands

| Command | What It Does |
|---------|-------------|
| `/help` | Show available commands |
| `/init` | Generate or refine CLAUDE.md (`CLAUDE_CODE_NEW_INIT=1` for the interactive flow) |
| `/memory` | Browse loaded CLAUDE.md / rules / auto-memory files; toggle auto memory |
| `/permissions` | Review and modify permission rules (shows source file per rule) |
| `/hooks` | Interactive hook configurator |
| `/mcp [reconnect\|enable\|disable]` | MCP server status, OAuth, per-server management |
| `/plugin [list\|install\|enable\|disable\|uninstall]` | Plugin manager (4 tabs: Discover, Installed, Marketplaces, Errors) |
| `/reload-plugins` / `/reload-skills` | Apply plugin / on-disk skill changes without restart |
| `/context [all]` | Context usage grid with optimization suggestions |
| `/compact [instructions]` | Summarize the conversation to free space |
| `/clear [name]` | New conversation (old one stays in `/resume`; aliases `/reset`, `/new`) |
| `/branch [name]` | Fork the conversation at this point (original preserved) |
| `/fork` | Hand a side task to a background subagent |
| `/rewind` | Restore code/conversation/both to a checkpoint (also `Esc Esc`) |
| `/resume` / `/rename` | Resume a session / name the current one |
| `/plan [description]` | Enter plan mode directly |
| `/model [alias\|id]` | Switch model (saves as default; press `s` in the picker for session-only) |
| `/effort [low\|medium\|high\|xhigh\|max\|ultracode\|auto]` | Set reasoning effort; `ultracode` = xhigh + automatic workflows |
| `/fast [on\|off]` | Toggle fast mode (Opus with faster output) |
| `/usage` | Session cost, plan limits, breakdown by skill/subagent/plugin/MCP (aliases `/cost`, `/stats`) |
| `/btw <question>` | Ephemeral side question — never enters context |
| `/recap` | One-line session summary on demand |
| `/tasks` | View running background shells and subagents |
| `/workflows` | Watch/manage dynamic workflow runs |
| `/agents` | Prints guidance for managing subagents (creation wizard removed in 2.1.198 — edit `.claude/agents/` or ask Claude) |
| `/cd <path>` | Change the session's working directory (2.1.169+) |
| `/add-dir <path>` | Add another directory to the workspace |
| `/sandbox` | Toggle OS-level filesystem/network sandboxing |
| `/statusline` / `/theme` / `/config` | UI & configuration (`/config key=value` works since 2.1.181) |
| `/doctor` / `/debug` | Diagnose install / session issues |
| `/install-github-app` | Set up GitHub Actions integration interactively |
| `/teleport` / `/remote-control` | Pull a web session into the terminal / control this session from another device |
| `/security-review` / `/review [PR]` / `/code-review` / `/simplify` / `/verify` | Review & verification skills — see [Chapter 8](08-skills.md#bundled-skills-built-into-claude-code) |
| `/loop` / `/deep-research` / `/batch` | Recurring prompts / bundled research workflow / parallel changes |

Removed/renamed since early 2026: the `/checkpoints` command is gone (use `/rewind`); conversation forking moved from `/fork` to `/branch`; `/simplify` became cleanup-only (bug hunting = `/code-review`).

## CLI Flags Worth Knowing

| Flag | Purpose |
|------|---------|
| `claude --continue` / `--resume [id\|name]` | Resume conversations (`--fork-session` to resume under a new session ID) |
| `claude --from-pr 123` | Resume sessions linked to a pull request |
| `claude -w <name>` / `--worktree` | Start in an isolated git worktree under `.claude/worktrees/` (add `--tmux` for panes) |
| `claude --permission-mode <mode>` | `default` (alias `manual`, v2.1.200+), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `claude -p "<prompt>"` | Non-interactive mode for CI/scripts |
| `--output-format text\|json\|stream-json` | Output format in `-p` mode |
| `--max-turns N` / `--max-budget-usd X` | Bound unattended runs |
| `--model <alias\|id>` / `--effort <level>` / `--fallback-model` | Model selection |
| `--agent <name>` / `--agents '<json>'` | Run a subagent definition as the main session agent |
| `--append-system-prompt "..."` | System-prompt-level instruction (stronger than CLAUDE.md; must be passed every invocation) |
| `--add-dir <path>` | Add a directory to the workspace at launch |
| `--allowedTools` / `--disallowedTools` | Session tool allow/deny lists |
| `--settings <file>` / `--mcp-config <file>` / `--plugin-dir <path>` | Sideload configuration |
| `--teammate-mode auto\|in-process\|tmux\|iterm2` | Agent-team display mode |
| `claude agents [--json]` | Dashboard of parallel background sessions |
| `claude mcp add/list/get/remove` | Manage MCP servers from the shell |
| `claude plugin install/uninstall [--scope]` | Manage plugins from the shell |

## Model Configuration

Current aliases (Anthropic API, July 2026): `sonnet` → **Sonnet 5** (native 1M-token context), `opus` → **Opus 4.8**, `haiku` → Haiku 4.5, `fable` → **Fable 5** (most capable; not the default — select with `/model fable`), `best` (Fable 5 where your org has access, otherwise latest Opus), plus `opus[1m]`, `sonnet[1m]` (no effect when `sonnet` already resolves to Sonnet 5), and **`opusplan`** (Opus during plan mode, Sonnet for execution).

**The default model depends on your account type:** Sonnet 5 for Pro, Team Standard, and Enterprise subscription seats; **Opus 4.8** for Max, Team Premium, Enterprise pay-as-you-go, and Anthropic API accounts; Sonnet 4.5 on Bedrock / Google Cloud's Agent Platform / Foundry.

- `/model` switches and saves as your default; press `s` in the picker for session-only.
- `/effort` adjusts reasoning depth (`ultracode` also enables automatic workflow orchestration — see [Chapter 10](10-agent-teams-networks.md)).
- `/fast` toggles fast mode (faster Opus output — same intelligence tier).
- Subagent cost control: `CLAUDE_CODE_SUBAGENT_MODEL` (see [Chapter 9](09-subagents.md)).
- Enterprise: `availableModels` + `enforceAvailableModels` restrict the picker; `fallbackModel` (chain of up to 3) covers overload.

## Troubleshooting

### Context filling up fast
- `/context` — see what's consuming space; follow its suggestions
- `/usage` — per-skill/plugin/MCP breakdown
- CLAUDE.md too large? Trim to <200 lines, move excess to skills/rules
- Uninstall unused plugins (`/plugin` → Installed → "Not used recently")
- Use subagents for exploration; `/compact` at logical boundaries

### Claude ignoring CLAUDE.md
- `/memory` — verify the file is actually loaded
- Too long (>200 lines) → trim; conflicting rules → make unambiguous; soft wording → imperative
- Must-happen actions belong in hooks, not CLAUDE.md

### Hooks not firing
- Event name is case-sensitive (`PreToolUse`, `PostToolUse`, `Stop`)
- `matcher` must match the **canonical** tool name (`Edit|Write`, `Bash`)
- `/hooks` shows registered hooks; check which settings file they came from
- Use the `InstructionsLoaded` hook or `claude --debug` to trace loading

### MCP server not working
- `/mcp` — connection status; `reconnect <server>` for one server
- HTTP/SSE servers auto-reconnect with backoff (5 attempts); stdio servers don't
- Check the package runs at all: `npx -y <package> --help`
- Tools not visible? They're deferred by tool search — that's normal; Claude finds them on demand ([Chapter 6](06-mcp.md))

### Subagents not being used
- Make the `description` field specific; add an agent-delegation rule; invoke explicitly by name

### Plugins not working
- Include the `@marketplace` suffix: `/plugin install name@marketplace-name`
- `/plugin` → Errors tab; `/reload-plugins` after changes
- LSP plugin errors usually mean the language-server binary is missing from `$PATH`
- Cache issues: `rm -rf ~/.claude/plugins/cache`, restart, reinstall

### Slow performance
- Uninstall unused plugins; keep CLAUDE.md lean
- Language servers (rust-analyzer, pyright) can eat memory on large projects — disable the plugin if needed
- `claude --debug` + `/doctor` for diagnostics

---

**Sources (official):**
- [Interactive mode (shortcuts)](https://code.claude.com/docs/en/interactive-mode)
- [Commands reference](https://code.claude.com/docs/en/commands)
- [CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Model configuration](https://code.claude.com/docs/en/model-config)
- [Troubleshooting](https://code.claude.com/docs/en/troubleshooting)

**Back to:** [README](../README.md)
