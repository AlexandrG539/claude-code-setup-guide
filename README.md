# Claude Code: Complete Configuration Guide (July 2026)

> A comprehensive, tech-stack-agnostic guide for configuring Claude Code from scratch.
> Verified against official Anthropic documentation, the official changelog, and live package registries on **2026-07-03** (Claude Code **2.1.200**, default model **Claude Sonnet 5**).

The guide is split into chapters. Read them in order for a from-scratch setup, or jump to what you need.

## Table of Contents

**Phase 1: Foundation (Universal — Every Project)**

| # | Chapter | What it covers |
|---|---------|----------------|
| 1 | [Architecture Overview & File Layout](chapters/01-architecture.md) | Extension layers, context costs, directory structure, loading precedence |
| 2 | [CLAUDE.md & Memory](chapters/02-claude-md-memory.md) | Project memory, templates, imports, AGENTS.md, auto memory, `/init` |
| 3 | [Rules](chapters/03-rules.md) | Modular guidelines, path-scoped rules, symlink sharing, recommended rule files |
| 4 | [Permissions, Modes & Sandboxing](chapters/04-permissions.md) | Rule syntax, deny/ask/allow, **plan mode**, auto mode, sandbox |

**Phase 2: Core Tooling**

| # | Chapter | What it covers |
|---|---------|----------------|
| 5 | [Plugins](chapters/05-plugins.md) | Official marketplace, LSP plugins, service integrations, community marketplaces, budget |
| 6 | [MCP Servers](chapters/06-mcp.md) | Tool search (deferred loading), transports, scopes, verified server recommendations |
| 7 | [Hooks](chapters/07-hooks.md) | All 30 lifecycle events, 5 hook types, ready-to-use configuration |

**Phase 3: Project-Specific Configuration**

| # | Chapter | What it covers |
|---|---------|----------------|
| 8 | [Skills & Slash Commands](chapters/08-skills.md) | SKILL.md format, invocation control, arguments, bundled skills, community skills |
| 9 | [Subagents](chapters/09-subagents.md) | Frontmatter reference, nesting, memory, worktree isolation, recommended agents |
| 10 | [Agent Teams, Workflows & Multi-Agent Networks](chapters/10-agent-teams-networks.md) | Agent teams, dynamic workflows / ultracode, background agents, Agent SDK, MCP & A2A interconnect |

**Phase 4: Advanced Workflows**

| # | Chapter | What it covers |
|---|---------|----------------|
| 11 | [Context Management](chapters/11-context-management.md) | Budgets, `/compact`, `/btw`, `/branch`, checkpoints |
| 12 | [Monorepos & Parallel Workflows](chapters/12-monorepo-parallel.md) | Hierarchical CLAUDE.md, `claudeMdExcludes`, native worktrees (`claude -w`), background sessions |
| 13 | [Editors & CI/CD](chapters/13-editors-cicd.md) | IDE integrations, `claude-code-action@v1`, headless mode |
| 14 | [Vercel Integration](chapters/14-vercel.md) | Vercel agent skills, official MCP, deploy skill |

**Reference**

| # | Chapter | What it covers |
|---|---------|----------------|
| 15 | [Reference](chapters/15-reference.md) | Keyboard shortcuts, built-in commands, CLI flags, model configuration, troubleshooting |

---

## Why This Order?

1. **Foundation first** — CLAUDE.md, rules, and permissions define *what Claude always knows* and *what it can never do*. They cost nothing to set up, apply universally, and prevent mistakes from the start.
2. **Core tooling second** — plugins, MCP servers, and hooks are *infrastructure*. Install plugins before writing custom skills or agents, because plugins often bundle those. Hooks enforce automation that Claude cannot "forget."
3. **Project-specific third** — custom skills, subagents, and multi-agent setups fill gaps not covered by plugins.
4. **Advanced workflows last** — context management, parallel work, and CI/CD are refinements on a solid foundation.

## Quick-Start Checklist (15 minutes)

1. `claude` in your repo → `/init` (or `CLAUDE_CODE_NEW_INIT=1 claude` for the interactive flow) → [Ch. 2](chapters/02-claude-md-memory.md)
2. Set permissions in `.claude/settings.json`; run `/fewer-permission-prompts` after a few sessions → [Ch. 4](chapters/04-permissions.md)
3. Install your language's LSP plugin: `/plugin install typescript-lsp@claude-plugins-official` → [Ch. 5](chapters/05-plugins.md)
4. Add the auto-format + branch-protection hooks → [Ch. 7](chapters/07-hooks.md)
5. Learn three habits: **plan mode** (`Shift+Tab`) before non-trivial changes, `/code-review` before PRs, `/rewind` instead of fighting a broken state → [Ch. 4](chapters/04-permissions.md), [Ch. 8](chapters/08-skills.md), [Ch. 11](chapters/11-context-management.md)

## What's New Since the May 2026 Revision

This revision was produced by re-verifying every claim against official sources (July 3, 2026). Meaningful changes:

| Area | Change | See |
|------|--------|-----|
| **Default model** | Claude Sonnet 5 is the default (2.1.197), with a native 1M-token context window. Fable 5 available via `/model fable`; Opus 4.8 current Opus | [Ch. 15](chapters/15-reference.md#model-configuration) |
| **MCP tool search** | MCP tool definitions are deferred by default — old "keep 5–10 servers max / 80 tools" budget advice is obsolete | [Ch. 6](chapters/06-mcp.md) |
| **Subagents** | Run in **background by default** (2.1.198); nested subagents up to 5 levels (2.1.172); `/agents` wizard removed; field is `permissionMode` (camelCase); many new frontmatter fields | [Ch. 9](chapters/09-subagents.md) |
| **Agent teams** | Simplified implicit-team model (2.1.178) — no TeamCreate/TeamDelete; still experimental behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **Dynamic workflows** | New in 2.1.154: `ultracode`, `/workflows`, `/deep-research`, saved workflows in `.claude/workflows/` | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **Commands renamed** | `/simplify` → `/code-review` for bug review (2.1.147; `/simplify` reintroduced as cleanup-only in 2.1.154); conversation forking is now `/branch` (`/fork` = hand-off to background subagent); `/checkpoints` removed (use `/rewind`) | [Ch. 15](chapters/15-reference.md) |
| **New commands** | `/cd`, `/usage` (`/cost`,`/stats`), `/plan`, `/effort` (incl. `ultracode`), `/fast`, `/recap`, `/btw`, `/teleport`, `/reload-skills`, `/install-github-app` | [Ch. 15](chapters/15-reference.md) |
| **Permissions** | `Tool(param:value)` parameter-matching rules (2.1.178); tool-name glob deny rules (2.1.166); documented wrapper-stripping and compound-command semantics | [Ch. 4](chapters/04-permissions.md) |
| **Worktrees & background agents** | Native `claude -w` worktrees; `claude agents` dashboard; background agents auto-commit/push/draft-PR (2.1.198) | [Ch. 12](chapters/12-monorepo-parallel.md) |
| **Hooks** | Event list grew to ~30 (`UserPromptExpansion`, `PermissionDenied`, `PostToolBatch`, `TaskCreated`, `CwdChanged`, `FileChanged`, …); fifth hook type `mcp_tool`; `$CLAUDE_PROJECT_DIR` now officially documented | [Ch. 7](chapters/07-hooks.md) |
| **Skills** | Named arguments, `$ARGUMENTS[N]`, dynamic context injection (`` !`cmd` ``), skill stacking (2.1.199), `disallowed-tools`; clarified that `allowed-tools` *pre-approves* rather than restricts | [Ch. 8](chapters/08-skills.md) |
| **GitHub Actions** | Official path is `anthropics/claude-code-action@v1` + `/install-github-app` (raw `claude -p` piping demoted to simple cases) | [Ch. 13](chapters/13-editors-cicd.md) |

### Corrections to the previous revision (verified against live registries)

- ❌ `@anthropic/mcp-server-playwright` does not exist → ✅ use **`@playwright/mcp`** (Microsoft).
- ❌ `@modelcontextprotocol/server-postgres` is deprecated & archived (May 2025) → ✅ use vendor MCPs/plugins.
- ❌ npm `@modelcontextprotocol/server-fetch` does not exist → ✅ the fetch server is Python: `uvx mcp-server-fetch`.
- ❌ settings key `disabledMcpServers` → ✅ documented key is **`disabledMcpjsonServers`** (plus `enabledMcpjsonServers`, managed `deniedMcpServers`).
- ❌ `\ide` → ✅ `/ide`. Several keyboard-shortcut fixes (`Shift+Tab` mode cycling, `Ctrl+O` transcript viewer, `Esc Esc` rewind semantics) — see [Ch. 15](chapters/15-reference.md).
- Repo renames: `affaan-m/everything-claude-code` → **`affaan-m/ECC`**; `ruvnet/claude-flow` → **`ruvnet/ruflo`**.
- Vercel MCP is no longer read-only: it manages teams/projects/deployments via OAuth at `https://mcp.vercel.com`.

## Sources

Every chapter ends with links to the official documentation pages it was verified against. Primary sources:

- [Claude Code documentation](https://code.claude.com/docs) (start at [best practices](https://code.claude.com/docs/en/best-practices) and the [features overview](https://code.claude.com/docs/en/features-overview))
- [Official changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [Official plugin catalog](https://claude.com/plugins) · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) · [anthropics/skills](https://github.com/anthropics/skills)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) · [claude-code-action](https://github.com/anthropics/claude-code-action)

Third-party claims (packages, marketplaces, community repos) were checked against live npm/PyPI/GitHub state on 2026-07-03; each carries its source link in place. When this guide and the official docs disagree, trust the docs — and please file an issue here.
