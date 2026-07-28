# Claude Code: Complete Configuration Guide (July 2026)

> A comprehensive, tech-stack-agnostic guide for configuring Claude Code from scratch — written to be **executed by a Claude agent** as well as read by humans (see [For Agents](#for-agents-self-configuration-procedure)).
> Verified against official Anthropic documentation, the official changelog, and live package registries on **2026-07-28** (Claude Code **2.1.220**; default model is **Claude Sonnet 5** on Pro/Team Standard/Enterprise seats, **Opus 5** on Max/Team Premium/API accounts).

The guide is split into chapters. Each chapter's YAML frontmatter states what it covers, when to read it, and the version it was verified against. Machine-readable index: [`llms.txt`](llms.txt).

## Table of Contents

**Phase 1: Foundation (Universal — Every Project)**

| # | Chapter | What it covers | Read when |
|---|---------|----------------|-----------|
| 1 | [Architecture Overview & File Layout](chapters/01-architecture.md) | Extension layers, context costs, directory structure, loading precedence | **Always** — read first |
| 2 | [CLAUDE.md & Memory](chapters/02-claude-md-memory.md) | Project memory, templates, imports, AGENTS.md, auto memory, `/init` | **Always** |
| 3 | [Rules](chapters/03-rules.md) | Modular guidelines, path-scoped rules, symlink sharing, recommended rule files | Standards span several domains, or CLAUDE.md outgrows ~60 lines |
| 4 | [Permissions, Modes & Sandboxing](chapters/04-permissions.md) | Rule syntax, deny/ask/allow, **plan mode**, auto mode, sandbox | **Always** — before installing anything |

**Phase 2: Core Tooling**

| # | Chapter | What it covers | Read when |
|---|---------|----------------|-----------|
| 5 | [Plugins](chapters/05-plugins.md) | Official marketplace, LSP plugins, service integrations, community marketplaces, budget | Language has an LSP plugin, or team services have official plugins |
| 6 | [MCP Servers](chapters/06-mcp.md) | Tool search (deferred loading), transports, scopes, verified server recommendations | External services needed beyond plugins (DBs, browsers, trackers) |
| 7 | [Hooks](chapters/07-hooks.md) | All 30 lifecycle events, 5 hook types, ready-to-use configuration | **Always** — must-hold rules belong in hooks |

**Phase 3: Project-Specific Configuration**

| # | Chapter | What it covers | Read when |
|---|---------|----------------|-----------|
| 8 | [Skills & Slash Commands](chapters/08-skills.md) | SKILL.md format, invocation control, arguments, bundled skills, community skills | Repeated procedures exist worth encoding as commands |
| 9 | [Subagents](chapters/09-subagents.md) | Frontmatter reference, nesting, memory, worktree isolation, recommended agents | Delegatable roles fit (review, planning, build fixing) |
| 10 | [Agent Teams, Workflows & Multi-Agent Networks](chapters/10-agent-teams-networks.md) | Agent teams, dynamic workflows / ultracode, background agents, Agent SDK, MCP & A2A interconnect | Multi-agent coordination or Agent SDK integration needed |

**Phase 4: Advanced Workflows**

| # | Chapter | What it covers | Read when |
|---|---------|----------------|-----------|
| 11 | [Context Management](chapters/11-context-management.md) | Budgets, `/compact`, `/btw`, `/branch`, checkpoints | Long sessions, context pressure, or large codebases |
| 12 | [Monorepos & Parallel Workflows](chapters/12-monorepo-parallel.md) | Hierarchical CLAUDE.md, `claudeMdExcludes`, native worktrees (`claude -w`), background sessions | Repo is a monorepo, or parallel sessions are used |
| 13 | [Editors & CI/CD](chapters/13-editors-cicd.md) | IDE integrations, `claude-code-action@v1`, headless mode | Project has CI, or IDE integration is wanted |
| 14 | [Vercel Integration](chapters/14-vercel.md) | Vercel agent skills, official MCP, deploy skill | Project deploys to Vercel |
| 16 | [Project Documentation for Agents](chapters/16-project-documentation.md) | Layered docs structure, router index + read-when navigation, change→doc trigger map, maintenance automation (validator/drift/commit-gate hooks, `/update-docs` skill, scheduled doc-sync) | Project knowledge outgrows CLAUDE.md, or docs drift from the code |

**Reference**

| # | Chapter | What it covers | Read when |
|---|---------|----------------|-----------|
| 15 | [Reference](chapters/15-reference.md) | Keyboard shortcuts, built-in commands, CLI flags, model configuration, troubleshooting | Looking up a command/flag/shortcut/model, or troubleshooting |

---

## For Agents: Self-Configuration Procedure

This guide is written to be executed by a Claude agent configuring a project. Machine-readable index: [`llms.txt`](llms.txt). Each chapter's YAML frontmatter carries `description`, `read_when`, `verified`, and `claude_code_version`. Outside a clone, fetch raw files from `https://raw.githubusercontent.com/AlexandrG539/claude-code-setup-guide/main/<path>` (e.g. `chapters/04-permissions.md`).

**One-command setup:** install the [`self-configure` skill](templates/self-configure/SKILL.md) to `~/.claude/skills/self-configure/SKILL.md` once, and `/self-configure` runs this procedure in any project:

```bash
mkdir -p ~/.claude/skills/self-configure && curl -s https://raw.githubusercontent.com/AlexandrG539/claude-code-setup-guide/main/templates/self-configure/SKILL.md -o ~/.claude/skills/self-configure/SKILL.md
```

**Procedure** (standing instructions for the whole configuration task):

1. Inspect the project first: languages, package manager, frameworks, repo shape (single package or monorepo), existing `.claude/` and `CLAUDE.md`, CI provider, deploy target. Route by facts found, not by assumptions.
2. Read the core chapters in order: [1](chapters/01-architecture.md), [2](chapters/02-claude-md-memory.md), [4](chapters/04-permissions.md), [7](chapters/07-hooks.md). Read the others only when their **Read when** condition (TOC above, or chapter frontmatter) matches the project.
3. Apply configuration in chapter order: CLAUDE.md → permissions → plugins/MCP → hooks → skills/subagents. Use the chapter templates verbatim; adapt only project-specific values (commands, paths, branch names), and omit template sections that don't apply to the project type (a docs-only repo has no test or typecheck commands).
4. Rules that must always hold (formatting, protected files, protected branches) go into hooks, not CLAUDE.md prose — hooks are enforced, prose is advisory.
5. Verify what is checkable immediately: settings files parse as valid JSON, hook commands exit correctly when fed sample stdin (test both the pass and the block path), referenced scripts exist, templates landed where intended. Then ask the user to confirm in a **fresh session** — `/memory` (CLAUDE.md loaded), `/permissions` (rules registered, correct source file), `/hooks` (hooks registered), `/context` (nothing oversized) — because these commands reflect config loaded at session start, so the configuring session cannot observe its own output with them.
6. Expect harness guardrails: in auto or managed permission modes, writing settings files that grant `allow` rules, and pushing to protected branches, may be blocked by the permission classifier for user review. This is expected — present the proposed content to the user and continue after approval; do not retry the blocked call unchanged.

**Boundaries:**

| Always | Ask the user first | Never |
|--------|--------------------|-------|
| Compare each chapter's `claude_code_version` to the installed `claude --version`; if the CLI is newer, re-verify changed behavior against the [official docs](https://code.claude.com/docs) before applying | Overwriting an existing CLAUDE.md, settings file, or hook | Put secrets or credentials in CLAUDE.md, settings files, or committed MCP configs |
| Keep CLAUDE.md lean — only facts Claude can't infer from the code (Ch. 2 rubric) | Installing plugins or MCP servers | Enable `bypassPermissions` or weaken existing deny rules |
| Prefer each chapter's single recommended default; deviate only for a stated project-specific reason | Adding `allow` rules broader than the Ch. 4 template | Delete existing project configuration |

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

## What's New in the July 28, 2026 Update (2.1.203–2.1.220)

Re-verified against the official changelog and current docs on 2026-07-28. Meaningful changes:

| Area | Change | See |
|------|--------|-----|
| **Claude Opus 5** | `opus` now resolves to **Opus 5** (`claude-opus-5`, 2.1.219): 1M context, fast mode support. Default model for Max/Team Premium/API accounts and on Claude Platform on AWS / Bedrock / Google Agent Platform | [Ch. 15](chapters/15-reference.md#model-configuration) |
| **`/fork` → background session** | Since 2.1.212 `/fork` copies the conversation into an independent **background session**; the in-session subagent hand-off is now **`/subtask`**; `/branch` remains the in-session fork | [Ch. 15](chapters/15-reference.md), [Ch. 12](chapters/12-monorepo-parallel.md) |
| **Subagent limits** | Nesting defaults to **3 levels** (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, 2.1.217+; was a fixed 5 levels through 2.1.216); new caps: 200 spawns/session (2.1.212), 20 concurrent (2.1.217) | [Ch. 9](chapters/09-subagents.md) |
| **Workflow size default** | Dynamic workflow size guideline defaults to **`medium`** (<15 agents) since 2.1.219 (was `unrestricted`); settable via the `workflowSizeGuideline` settings key | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **Permissions (2.1.214)** | Single-segment `Edit(dir/**)` **allow** rules now match only `<cwd>/dir` (use `**/dir/**` for any depth; deny/ask keep any-depth match); commands >10,000 chars always prompt | [Ch. 4](chapters/04-permissions.md) |
| **Auto mode GA on all major providers** | No `CLAUDE_CODE_ENABLE_AUTO_MODE` opt-in needed since 2.1.207 (Bedrock, Agent Platform, Foundry); no longer a research preview; new `claude auto-mode reset` | [Ch. 4](chapters/04-permissions.md) |
| **Sandbox settings** | `sandbox.filesystem.disabled` (2.1.216), `sandbox.network.strictAllowlist` (2.1.219) | [Ch. 4](chapters/04-permissions.md) |
| **Skills** | `context: fork` skills run in the **background by default** (2.1.218, opt out with `background: false`); boolean frontmatter accepts `yes/no/on/off/1/0`; `/verify`, `/code-review`, `/deep-research` are no longer auto-invoked by Claude (2.1.215/2.1.218) | [Ch. 8](chapters/08-skills.md) |
| **Hooks** | `SessionStart` gained the `fork` matcher (2.1.214); new `DirectoryAdded` event after `/add-dir` (2.1.219) | [Ch. 7](chapters/07-hooks.md) |
| **MCP** | Tool calls >2 min auto-background (`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS`, 2.1.212); `/mcp` / `claude mcp list` show HTTP status on connection failures (2.1.219) | [Ch. 6](chapters/06-mcp.md) |
| **Worktree approvals** | "Always allow" grants save at the repository root and persist across worktrees (2.1.211) | [Ch. 4](chapters/04-permissions.md) |
| **`/doctor` = full checkup** | Diagnoses **and fixes** setup issues; alias `/checkup` (2.1.205); also new: screen-reader mode (`--ax-screen-reader`, 2.1.208) | [Ch. 15](chapters/15-reference.md) |

## What's New Since the May 2026 Revision

This revision was produced by re-verifying every claim against official sources (July 3–7, 2026). Meaningful changes:

| Area | Change | See |
|------|--------|-----|
| **Default model** | Claude Sonnet 5 became the default in 2.1.197 (native 1M-token context window); the default is account-dependent — now **Opus 5** on Max/Team Premium/API (2.1.219). Fable 5 available via `/model fable`; new `best` alias | [Ch. 15](chapters/15-reference.md#model-configuration) |
| **MCP tool search** | MCP tool definitions are deferred by default — old "keep 5–10 servers max / 80 tools" budget advice is obsolete | [Ch. 6](chapters/06-mcp.md) |
| **Subagents** | Run in **background by default** (2.1.198); nesting now defaults to 3 levels with new session caps — see the July 28 update below; `/agents` wizard removed; field is `permissionMode` (camelCase); many new frontmatter fields | [Ch. 9](chapters/09-subagents.md) |
| **Agent teams** | Simplified implicit-team model (2.1.178) — no TeamCreate/TeamDelete; still experimental behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **Dynamic workflows** | New in 2.1.154: `ultracode`, `/workflows`, `/deep-research`, saved workflows in `.claude/workflows/` | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **Commands renamed** | `/simplify` → `/code-review` for bug review (2.1.147; `/simplify` reintroduced as cleanup-only in 2.1.154); `/checkpoints` removed (use `/rewind`); `/fork` semantics changed again in 2.1.212 — see the July 28 update below | [Ch. 15](chapters/15-reference.md) |
| **New commands** | `/cd`, `/usage` (`/cost`,`/stats`), `/plan`, `/effort` (incl. `ultracode`), `/fast`, `/recap`, `/btw`, `/teleport`, `/reload-skills`, `/install-github-app` | [Ch. 15](chapters/15-reference.md) |
| **Permissions** | `Tool(param:value)` parameter-matching rules (2.1.178); tool-name glob deny rules (2.1.166); documented wrapper-stripping and compound-command semantics | [Ch. 4](chapters/04-permissions.md) |
| **Worktrees & background agents** | Native `claude -w` worktrees; `claude agents` dashboard; background agents auto-commit/push/draft-PR (2.1.198) | [Ch. 12](chapters/12-monorepo-parallel.md) |
| **Hooks** | Event list grew to ~30 (`UserPromptExpansion`, `PermissionDenied`, `PostToolBatch`, `TaskCreated`, `CwdChanged`, `FileChanged`, …); fifth hook type `mcp_tool`; `$CLAUDE_PROJECT_DIR` now officially documented | [Ch. 7](chapters/07-hooks.md) |
| **Skills** | Named arguments, `$ARGUMENTS[N]`, dynamic context injection (`` !`cmd` ``), skill stacking (2.1.199), `disallowed-tools`; clarified that `allowed-tools` *pre-approves* rather than restricts | [Ch. 8](chapters/08-skills.md) |
| **GitHub Actions** | Official path is `anthropics/claude-code-action@v1` + `/install-github-app` (raw `claude -p` piping demoted to simple cases) | [Ch. 13](chapters/13-editors-cicd.md) |
| **Workflow size (2.1.202)** | New **Dynamic workflow size** setting in `/config` — advisory agent-count guideline (`unrestricted`/`small`/`medium`/`large`) for the scripts Claude writes | [Ch. 10](chapters/10-agent-teams-networks.md) |
| **`/review` (2.1.202)** | `/review <pr>` is single-pass again; multi-agent PR review is `/code-review <level> <PR#>` | [Ch. 15](chapters/15-reference.md) |

### Corrections to the previous revision (verified against live registries)

- ❌ `@anthropic/mcp-server-playwright` does not exist → ✅ use **`@playwright/mcp`** (Microsoft).
- ❌ `@modelcontextprotocol/server-postgres` is deprecated & archived (May 2025) → ✅ use vendor MCPs/plugins.
- ❌ npm `@modelcontextprotocol/server-fetch` does not exist → ✅ the fetch server is Python: `uvx mcp-server-fetch`.
- ❌ settings key `disabledMcpServers` → ✅ documented key is **`disabledMcpjsonServers`** (plus `enabledMcpjsonServers`, managed `deniedMcpServers`).
- ❌ `\ide` → ✅ `/ide`. Several keyboard-shortcut fixes (`Shift+Tab` mode cycling, `Ctrl+O` transcript viewer, `Esc Esc` rewind semantics) — see [Ch. 15](chapters/15-reference.md).
- Repo renames: `affaan-m/everything-claude-code` → **`affaan-m/ECC`**; `ruvnet/claude-flow` → **`ruvnet/ruflo`**.
- Vercel MCP is no longer read-only: it manages teams/projects/deployments via OAuth at `https://mcp.vercel.com`.
- ❌ Earlier revisions' blocking-hook templates (Ch. 7) piped stdin into `{ …; exit 2; } || true`, which swallowed the exit code — the file/branch-protection hooks printed `BLOCKED` but never blocked → ✅ capture stdin via command substitution and `exit 2` at top level. Found 2026-07-07 by executing the guide's own self-configuration procedure.

## Sources

Every chapter ends with links to the official documentation pages it was verified against. Primary sources:

- [Claude Code documentation](https://code.claude.com/docs) (start at [best practices](https://code.claude.com/docs/en/best-practices) and the [features overview](https://code.claude.com/docs/en/features-overview))
- [Official changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [Official plugin catalog](https://claude.com/plugins) · [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) · [anthropics/skills](https://github.com/anthropics/skills)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) · [claude-code-action](https://github.com/anthropics/claude-code-action)

Third-party claims (packages, marketplaces, community repos) were checked against live npm/PyPI/GitHub state on 2026-07-04; each carries its source link in place. When this guide and the official docs disagree, trust the docs — and please file an issue here.
