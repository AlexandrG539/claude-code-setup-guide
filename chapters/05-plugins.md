---
description: "Installing plugins: the official marketplace, per-language LSP plugins, service-integration plugins, community marketplaces, and context budget. Read before writing custom skills or agents — plugins often bundle them."
read_when:
  - "the project's language has an LSP plugin (TypeScript, Python, Rust, Go, Java, ...)"
  - "the team uses services with official plugins (GitHub, Slack, Sentry, ...)"
topics: [plugins, lsp, marketplace, service-integrations]
verified: 2026-07-07
claude_code_version: "2.1.202"
---

# Chapter 5: Plugins — Packaged Extensions

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Permissions](04-permissions.md) · **Next:** [MCP Servers](06-mcp.md)

Plugins bundle skills, hooks, agents, MCP servers, and LSP servers into installable packages. **Install plugins before creating custom skills, agents, or hooks** — plugins often provide these out of the box.

## Installation

Plugins are managed with `/plugin` commands inside a session (interactive UI with **Discover / Installed / Marketplaces / Errors** tabs) or with `claude plugin ...` from the shell:

```
/plugin                                         # interactive manager
/plugin install <plugin-name>@<marketplace>     # install (always include @marketplace)
/plugin list [--enabled|--disabled]             # list installed
/plugin enable|disable <name>@<marketplace>     # toggle without uninstalling
/plugin uninstall <name>@<marketplace>          # remove
/plugin marketplace add <owner/repo|url|path>   # add a catalog
/plugin marketplace update <name>               # refresh a catalog
/reload-plugins                                 # apply changes without restart
```

When installing you choose a **scope**: user (all your projects — default), project (committed, shared with the team), or local (this repo, just you).

Before installing, the details pane shows the plugin's **Context cost** (tokens added per turn), **Last updated** date, and a **Will install** inventory of its commands/agents/skills/hooks/servers — review these; they're your budget controls.

## Official Anthropic Marketplace

`claude-plugins-official` is **automatically available** — no marketplace add needed:

```
/plugin install <plugin-name>@claude-plugins-official
```

Browse at [claude.com/plugins](https://claude.com/plugins) or `/plugin` → Discover. If a plugin reports "not found", run `/plugin marketplace update claude-plugins-official`.

### Code intelligence (LSP) — must-have

LSP plugins give Claude **automatic diagnostics after every edit** (it sees and fixes type errors in the same turn) and precise code navigation (go-to-definition, find-references). The official marketplace covers 12 languages; plugin names follow the `<lang>-lsp` pattern and require the language-server binary on your `$PATH`:

| Language | Plugin | Binary required |
|----------|--------|-----------------|
| TypeScript | `typescript-lsp` | `typescript-language-server` |
| Python | `pyright-lsp` | `pyright-langserver` |
| Rust | `rust-analyzer-lsp` | `rust-analyzer` |
| Go | `gopls-lsp` | `gopls` |
| C/C++ | `clangd-lsp` | `clangd` |
| Java | `jdtls-lsp` | `jdtls` |
| C# / Kotlin / Lua / PHP / Ruby / Swift | `csharp-lsp`, `kotlin-lsp`, `lua-lsp`, `php-lsp`, `ruby-lsp`, `swift-lsp` | see docs |

```
/plugin install typescript-lsp@claude-plugins-official
```

For languages not covered, the community marketplace [`boostvolt/claude-code-lsps`](https://github.com/boostvolt/claude-code-lsps) (third-party, active as of May 2026) fills gaps:

```
/plugin marketplace add boostvolt/claude-code-lsps
/plugin install <lsp-name>@claude-code-lsps
```

### Highly recommended official plugins

All names below verified against the live official repo (July 2026):

| Plugin | Purpose |
|--------|---------|
| **frontend-design** | Anthropic's design skill — production-grade UI, avoids generic "AI slop" aesthetics. Auto-invokes on frontend work |
| **feature-dev** | Structured multi-phase feature workflow: requirements → exploration → architecture → implementation → testing → review |
| **security-guidance** | Reviews each change Claude makes for common vulnerabilities and fixes findings in-session |
| **commit-commands** | Git workflows: commit, push, PR creation (`/commit-commands:commit`) |
| **pr-review-toolkit** | Specialized agents for reviewing pull requests |
| **code-review** / **code-simplifier** | Review workflows (much of this is also bundled in Claude Code as `/code-review` / `/simplify`) |
| **mcp-server-dev** / **plugin-dev** / **agent-sdk-dev** / **skill-creator** / **hookify** | Toolkits for building your own MCP servers, plugins, SDK agents, skills, and hooks |
| **explanatory-output-style** / **learning-output-style** | Alternative response styles |
| **claude-md-management**, **code-modernization**, **ralph-loop**, **session-report** | Situational utilities — browse `/plugin` → Discover |

### Service integrations

The official marketplace also carries integration plugins that bundle pre-configured MCP servers — install these instead of hand-configuring MCP for these services:

- **Source control:** `github`, `gitlab`
- **Project management:** `atlassian` (Jira/Confluence), `asana`, `linear`, `notion`
- **Design:** `figma` · **Infra:** `vercel`, `firebase`, `supabase` · **Comms:** `slack` · **Monitoring:** `sentry`

**Important:** after installing a service plugin, check `/mcp` before adding a separate MCP server for the same service — the plugin usually already provides it.

## Community Marketplaces

- **`anthropics/claude-plugins-community`** — third-party plugins that passed Anthropic's automated validation and safety screening, each pinned to a commit SHA. Add manually: `/plugin marketplace add anthropics/claude-plugins-community`, then `install <name>@claude-community`.
- **`obra/superpowers-marketplace`** — the popular Superpowers workflow suite (20+ skills, including brainstorm, write-plan, execute-plan). Active as of 2026: `/plugin marketplace add obra/superpowers-marketplace` then `/plugin install superpowers@superpowers-marketplace`.
- **`affaan-m/ECC`** (formerly `everything-claude-code` — the repo was renamed; ~225k stars, actively developed as of July 2026) — a large "agent harness optimization" config: skills, instincts, memory, security. Powerful but heavyweight; cherry-pick rather than installing everything.

**Security note (official):** plugins execute arbitrary code with your user privileges. Only install from sources you trust; check the "Will install" inventory first. Orgs can restrict sources via `strictKnownMarketplaces` / `blockedMarketplaces`.

## Plugin Budget

- Every enabled plugin's skills/instructions cost context each turn — the **Context cost** figure in `/plugin` makes this visible per plugin. Keep only what you use.
- Since 2.1.187, `/plugin` → Installed shows a **"Not used recently"** group (no invocation in 2+ weeks across 10+ sessions) — audit it periodically.
- Plugin MCP servers are cheap by default thanks to [tool search](06-mcp.md#tool-search--the-new-default); reloading plugins mid-session may invalidate the prompt cache (Claude Code warns and requires `--force` when it would).

## Post-Installation Checklist

1. `/plugin list` — see what's installed and enabled
2. Note which skills are already covered (TDD, review, commits, …)
3. `/mcp` — note which MCP servers plugins already provide
4. Only create custom skills/agents ([Chapters 8](08-skills.md)–[9](09-subagents.md)) for the gaps

---

**Sources:**
- [Discover plugins (official)](https://code.claude.com/docs/en/discover-plugins)
- [Official plugin catalog](https://claude.com/plugins) · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace) · [boostvolt/claude-code-lsps](https://github.com/boostvolt/claude-code-lsps) · [affaan-m/ECC](https://github.com/affaan-m/ECC)

**Next:** [Chapter 6: MCP Servers →](06-mcp.md)
