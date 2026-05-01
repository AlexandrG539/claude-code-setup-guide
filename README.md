# Claude Code: Complete Configuration Guide (March 2026)

> A comprehensive, tech-stack-agnostic guide for configuring Claude Code from scratch.
> Compiled from official Anthropic documentation, community best practices, and verified against current sources (March 2026).

---

## Table of Contents

**Phase 1: Foundation (Universal — Every Project)**
1. [Architecture Overview](#1-architecture-overview)
2. [File System Layout](#2-file-system-layout)
3. [Step 1: CLAUDE.md — Project Memory](#step-1-claudemd--project-memory)
4. [Step 2: Rules — Modular Guidelines](#step-2-rules--modular-guidelines)
5. [Step 3: Permissions — Safety Boundaries](#step-3-permissions--safety-boundaries)

**Phase 2: Core Tooling (Common Plugins, MCP, Hooks)**
6. [Step 4: Plugins — Packaged Extensions](#step-4-plugins--packaged-extensions)
7. [Step 5: MCP Servers — External Service Connections](#step-5-mcp-servers--external-service-connections)
8. [Step 6: Hooks — Deterministic Automation](#step-6-hooks--deterministic-automation)

**Phase 3: Project-Specific Configuration**
9. [Step 7: Skills — On-Demand Knowledge](#step-7-skills--on-demand-knowledge)
10. [Step 8: Subagents — Isolated Workers](#step-8-subagents--isolated-workers)
11. [Step 9: Slash Commands — Workflow Shortcuts](#step-9-slash-commands--workflow-shortcuts)

**Phase 4: Advanced Workflows**
12. [Step 10: Context Management Strategy](#step-10-context-management-strategy)
13. [Step 11: Monorepo vs Separate Repos](#step-11-monorepo-vs-separate-repos)
14. [Step 12: Parallel Workflows](#step-12-parallel-workflows)
15. [Step 13: Editor Integration](#step-13-editor-integration)
16. [Step 14: Vercel Integration — Skills, MCP & Deployment](#step-14-vercel-integration--skills-mcp--deployment)
17. [Step 15: CI/CD Integration](#step-15-cicd-integration)

**Reference**
18. [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)
19. [Useful Built-in Commands Reference](#useful-built-in-commands-reference)
20. [Troubleshooting](#troubleshooting)
21. [Sources](#sources)

---

## Why This Order?

The guide is organized in four phases:

1. **Foundation first** — CLAUDE.md, rules, and permissions define *what Claude always knows* and *what it can never do*. These cost nothing to set up, apply universally, and prevent mistakes from the start.
2. **Core tooling second** — Plugins, MCP servers, and hooks are *infrastructure*. Install them before writing custom skills or agents, because plugins often bundle skills, agents, and MCP servers that would otherwise require manual creation. Hooks enforce deterministic automation that Claude cannot "forget."
3. **Project-specific third** — Custom skills, subagents, and commands fill gaps not covered by plugins. Creating them after plugin installation avoids duplication.
4. **Advanced workflows last** — Context management, parallel workflows, CI/CD, and deployment are refinements you add once the foundation is solid.

---

## 1. Architecture Overview

Claude Code has 8 extension layers that plug into different parts of the agentic loop:

| Layer | What It Does | When It Loads | Context Cost |
|-------|-------------|---------------|--------------|
| **CLAUDE.md** | Persistent project context and instructions | Session start (always) | Every request |
| **Rules** | Modular guidelines, optionally path-scoped | Session start (always) | Every request (path-scoped rules only when matched) |
| **Plugins** | Packaged bundles of skills, hooks, agents, and MCP servers | Session start | Varies |
| **Skills** | On-demand knowledge and invocable workflows | Description at start; full content when used | Low until invoked |
| **Subagents** | Isolated workers with separate context windows | When spawned | Zero (isolated) |
| **Commands** | Slash-command shortcuts for common tasks (merged with skills) | When invoked | One-time on invoke |
| **Hooks** | Deterministic shell scripts (or LLM/agent/HTTP) on lifecycle events | On trigger | Zero (external) |
| **MCP Servers** | Connections to external services and tools | Session start | Every request |

**Key principle:** CLAUDE.md and rules are *always-on* context. Skills, subagents, and commands are *on-demand*. Hooks run *outside* the AI loop entirely. Design your setup to minimize always-on context and maximize on-demand loading.

**Important:** As of 2026, commands (`.claude/commands/`) and skills (`.claude/skills/`) are **merged** — both create slash commands. A file at `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy`. Use whichever structure you prefer.

---

## 2. File System Layout

### Global Configuration (all projects)

```
~/.claude/
├── CLAUDE.md                 # Personal global preferences
├── settings.json             # Global hooks, permissions, MCP servers
├── commands/                 # Global slash commands
│   └── my-command.md
├── skills/                   # Global skills
│   └── my-skill/
│       └── SKILL.md
├── agents/                   # Global subagents
│   └── my-agent.md
└── rules/                    # Global rules (apply to all projects)
    └── my-rule.md
```

### Project Configuration

```
your-project/
├── CLAUDE.md                 # Project instructions (committed to git)
├── CLAUDE.local.md           # Personal local overrides (gitignored)
├── .claude/
│   ├── CLAUDE.md             # Alternative location for project instructions
│   ├── settings.json         # Project settings — hooks, permissions (committed)
│   ├── settings.local.json   # Local settings (gitignored)
│   ├── commands/             # Project slash commands
│   │   └── my-command.md
│   ├── agents/               # Subagent definitions
│   │   └── my-agent.md
│   ├── skills/               # Project skills
│   │   └── my-skill/
│   │       ├── SKILL.md
│   │       └── supporting-files...
│   └── rules/                # Project rules (path-scoped)
│       └── my-rule.md
├── .mcp.json                 # MCP server configuration (alternative to CLI)
```

### Monorepo Structure (hierarchical CLAUDE.md)

```
monorepo/
├── CLAUDE.md                 # Root: shared rules (always loaded)
├── .claude/                  # Shared config
├── apps/
│   ├── frontend/
│   │   └── CLAUDE.md         # Frontend-only rules (auto-loads in this dir)
│   └── backend/
│       └── CLAUDE.md         # Backend-only rules (auto-loads in this dir)
└── packages/
    └── shared/
        └── CLAUDE.md         # Shared package rules (auto-loads in this dir)
```

**How loading works:** Claude reads CLAUDE.md files from the working directory up to the root. Child directory files (e.g., `apps/frontend/CLAUDE.md`) load automatically when Claude accesses files in that directory. This means backend rules never pollute frontend context and vice versa.

### Loading Priority (highest to lowest)

| Level | Location | Purpose |
|-------|----------|---------|
| Managed policy | `/etc/claude-code/CLAUDE.md` (Linux) | Org-wide (admin) |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared (committed) |
| Project rules | `./.claude/rules/*.md` | Modular topic rules (committed) |
| Project local | `./CLAUDE.local.md` | Personal project overrides (gitignored) |
| User global | `~/.claude/CLAUDE.md` | Personal defaults (all projects) |
| User rules | `~/.claude/rules/*.md` | Personal rules (all projects) |

All levels are loaded and merged. When instructions conflict, more specific levels take precedence.

---

# Phase 1: Foundation

## Step 1: CLAUDE.md — Project Memory

CLAUDE.md is loaded into every request. It defines what Claude always knows about your project.

### Guidelines

- **Keep it under 200 lines** — bloated CLAUDE.md files cause Claude to ignore instructions. The previous recommendation of 500 lines was too generous; shorter files get better adherence.
- For each line, ask: *"Would removing this cause Claude to make mistakes?"* If not, cut it.
- Move reference material to skills (on-demand loading).
- Use imperative language: "Use X" and "Never do Y" — not "It would be nice if..."
- State what NOT to do — prohibitions are more valuable than suggestions.
- Use `@path/to/file` import syntax to reference other files without duplicating content.

### Template: Root CLAUDE.md

```markdown
# Project: [PROJECT NAME]

[One-line description of the project and its purpose.]

## Tech Stack

- [Language/Framework]: [version]
- [Database]: [type]
- [Testing]: [framework]
- [Package Manager]: [name]
- [Other key tools]

## Project Structure

[directory tree showing key folders and their purposes]

## Commands

- `[command]` — [what it does]
- `[command]` — [what it does]
- `[test command]` — [run specific test file]
- `[lint command]` — [run linter]
- `[typecheck command]` — [run type checker]

## Code Conventions

- [Rule about types/typing]
- [Rule about naming]
- [Rule about file organization]
- [Rule about imports]
- [Rule about error handling pattern]
- [Rule about exports (named vs default)]

## Architecture Rules

- [Key architectural pattern]
- [Data flow direction]
- [State management approach]
- [API response format]

## Git Conventions

- [Commit format (e.g., conventional commits)]
- [Branch naming]
- Never commit [secrets, env files, etc.]
- Never force-push to [protected branches]

## Security

- Never hardcode secrets — use environment variables
- Validate all user input server-side
- Never expose internal error details to client
- Never log PII or tokens
```

### Template: Global ~/.claude/CLAUDE.md

```markdown
# Personal Preferences

## Communication
- Be direct and concise
- Don't repeat back what I said
- If unsure, ask rather than guess
- Only add comments for "why", never for "what"

## Code Style
- Prefer early returns over deep nesting
- [Indentation preference]
- [Max line length]
- Don't add unnecessary type annotations to obvious types
- Don't add docstrings/comments to code you didn't change

## Safety
- Never run destructive commands without asking
- Never modify .env files without approval
- Never push to main/master directly
- Show diffs before committing
```

### Template: CLAUDE.local.md (gitignored, personal)

```markdown
# Local Development Notes

## My Environment
- Database on localhost:[port]
- [Service] on localhost:[port]
- Working on branch: [feature-branch]

## Personal Reminders
- [Module X] is being refactored — check with [person] before changing
- Staging URL: [url]
```

### Import Syntax

CLAUDE.md files can reference other files:

```markdown
See @README.md for project overview.
See @docs/api-spec.md for API documentation.
See @package.json for available commands.
```

---

## Step 2: Rules — Modular Guidelines

Rules are markdown files in `.claude/rules/` that organize guidelines by topic. They are always loaded (like CLAUDE.md) but can be **scoped to specific file paths** using YAML frontmatter, meaning they only consume context when Claude works on matching files.

### When to Use Rules vs CLAUDE.md

| Use CLAUDE.md for | Use Rules for |
|-------------------|---------------|
| Project overview, tech stack | Topic-specific guidelines |
| Key commands | Path-scoped conventions |
| Architecture summary | Detailed patterns per domain |
| Always-needed context (<200 lines) | Team-agreed standards |

### Path-Scoped Rules

Rules can target specific directories using `paths` frontmatter:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/routes/**/*.ts"
---

# API Development Rules

- All endpoints must validate input with schema validation
- Use consistent response format: { data, error, meta }
- Return proper HTTP status codes
```

This rule only loads when Claude is working on files matching those paths.

### Sharing Rules Across Projects

Rules support **symlinks** for reuse:

```bash
# Share personal rules across all projects
ln -s ~/shared-claude-rules .claude/rules/shared

# Share a single rule file
ln -s ~/company-standards/security.md .claude/rules/security.md
```

User-level rules at `~/.claude/rules/` apply to every project automatically.

### Recommended Rule Files

#### `.claude/rules/coding-style.md`

```markdown
# Coding Style

- Prefer immutability — use const/readonly/final where possible
- Early returns over nested conditionals
- Max function length: 50 lines — split if larger
- Max file length: 300 lines — split if larger
- Functions do one thing — if the name has "and", split it
- No magic numbers — use named constants
- Group imports: stdlib > external > internal > types
- Named exports over default exports (easier to refactor/search)
```

#### `.claude/rules/testing.md`

```markdown
# Testing Rules

- Test behavior, not implementation details
- Arrange-Act-Assert pattern for all tests
- Descriptive names: "should [expected] when [condition]"
- One logical assertion per test (related assertions are fine)
- Mock at boundaries (network, database, filesystem) not internal modules
- Never test private/internal functions directly
- Use factories/fixtures for test data — not inline literals
- Colocate tests with source: `foo.ts` > `foo.test.ts`
- Integration tests > unit tests for API endpoints
- Every new feature/endpoint needs at least one test
- IMPORTANT: Run the specific test file, not the full suite
```

#### `.claude/rules/security.md`

```markdown
# Security Rules

- Never log sensitive data (passwords, tokens, PII)
- Always validate and sanitize user input on the server
- Use parameterized queries — never string concatenation for SQL
- Store secrets in environment variables, never in code
- Never commit .env, credentials, or API keys
- Hash passwords with modern algorithms (argon2/bcrypt) — never MD5/SHA
- Set security headers (CSP, X-Frame-Options, HSTS)
- Rate limit all public endpoints
- CORS: whitelist specific origins, never wildcard in production
- File uploads: validate MIME type, limit size, use allowlist for extensions
- Never expose stack traces or internal error details to clients
```

#### `.claude/rules/git-workflow.md`

```markdown
# Git Workflow

- Conventional commits: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, perf, test, chore, ci
  - Scope: module or area affected
- Imperative mood: "add feature" not "added feature"
- Keep commits atomic — one logical change per commit
- Never commit commented-out code
- Never force-push to main/master
- Feature branches for all changes
- Squash WIP commits before merge
```

#### `.claude/rules/agent-delegation.md`

```markdown
# Agent Delegation Rules

When to delegate to subagents:
- Security review: ALWAYS delegate security-sensitive changes to the security-reviewer agent
- Code review: Delegate completed features to code-reviewer before PR
- Build errors: Delegate compilation failures to build-fixer agent
- Test writing: Delegate comprehensive test creation to test-writer agent
- Database changes: Delegate schema reviews to database-reviewer agent
- Planning: Use planner agent for features touching 3+ files

When NOT to delegate:
- Simple single-file edits
- Typo fixes
- Adding a single test
- Configuration changes
```

---

## Step 3: Permissions — Safety Boundaries

Permissions control what tools Claude can use without asking. Set these **early** — before installing plugins or running commands — to establish safety guardrails from the start.

### Configuration

In `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test*)",
      "Bash(npm install*)",
      "Bash(npx prettier *)",
      "Bash(npx tsc *)",
      "Bash(npx vitest *)",
      "Bash(npx jest *)",
      "Bash(npx playwright *)",
      "Bash(npx eslint *)",
      "Bash(git status*)",
      "Bash(git diff*)",
      "Bash(git log*)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git branch*)",
      "Bash(git checkout *)",
      "Bash(git switch *)",
      "Bash(git fetch*)",
      "Bash(git stash*)",
      "Bash(git merge *)",
      "Bash(git rebase *)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Bash(rm -rf /*)",
      "Read(.env*)",
      "Read(*.pem)",
      "Read(*secret*)",
      "Read(*credential*)"
    ]
  }
}
```

### Permission Syntax

| Pattern | Meaning |
|---------|---------|
| `Bash(npm run lint)` | Exact match |
| `Bash(npm run *)` | Prefix wildcard |
| `Bash(git * main)` | Glob pattern |
| `Read(.env*)` | Block reading env files |
| `Edit(src/**)` | Allow editing anywhere in src/ |

**Evaluation order:** Deny (highest) > Ask > Allow (lowest)

This means deny rules always win. Even if `Bash(git *)` is allowed, `Bash(git push --force*)` will still be blocked.

### Permission Strategy

1. **Allow generously for development tools** — npm, git read operations, formatters, linters, and test runners should all be pre-approved to avoid constant permission prompts
2. **Deny destructive operations** — force push, hard reset, recursive delete of root
3. **Deny secret access** — env files, credentials, PEM files should require explicit approval each time
4. **Add project-specific allows** — if you use pnpm, yarn, turbo, or other tools, add their patterns:

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm *)",
      "Bash(turbo *)",
      "Bash(yarn *)",
      "Bash(pytest *)",
      "Bash(cargo *)",
      "Bash(go test *)"
    ]
  }
}
```

### User-Local vs Project Permissions

- **`.claude/settings.json`** (committed) — project-wide rules shared by all team members
- **`.claude/settings.local.json`** (gitignored) — personal permissions accumulated during sessions

When Claude asks for permission and you approve, the approval goes to `settings.local.json`. Project-level permissions in `settings.json` apply to everyone.

---

# Phase 2: Core Tooling

## Step 4: Plugins — Packaged Extensions

Plugins bundle skills, hooks, agents, and MCP servers into installable packages. **Install plugins before creating custom skills, agents, or hooks** — plugins often provide these features out of the box.

### Installation

Plugins are installed interactively inside a Claude Code session using `/plugin` commands. They **cannot** be installed via Bash or external scripts.

```
/plugin marketplace add <marketplace-repo>     # Add a marketplace source
/plugin install <plugin-name>@<marketplace>    # Install from marketplace
/plugins                                        # List installed plugins
/plugin remove <plugin-name>                    # Remove a plugin
/reload-plugins                                 # Apply changes without restart
```

The `/plugin` command opens an interactive UI with four tabs: **Discover**, **Installed**, **Marketplaces**, and **Errors**.

**Important:** Always include the `@marketplace` suffix when installing. For example, `/plugin install superpowers@superpowers-marketplace`, NOT `/plugin install superpowers`.

### What Plugins Can Provide

A single plugin may bundle multiple extension types:

| Extension | Example |
|-----------|---------|
| **Skills** | TDD workflow, debugging methodology, design patterns |
| **Agents** | Code reviewer, security auditor, test writer |
| **Hooks** | Auto-format, branch protection, lint-on-save |
| **MCP Servers** | Database connections, service integrations |
| **Commands** | Custom slash commands |
| **LSP Servers** | Language server protocol for code intelligence |

### Official Anthropic Plugin Marketplace

Anthropic maintains `anthropics/claude-plugins-official` — a curated, high-quality plugin directory that is **automatically available** (no need to add the marketplace). Install official plugins directly:

```
/plugin install <plugin-name>@claude-plugins-official
```

### Tier 1: Must-Have Plugins

#### 1. Language Server (MUST HAVE)

Gives Claude real-time type errors, go-to-definition, and find-references — dramatically improves code quality. Navigation drops from ~45 seconds to ~50ms.

**Option A: Official Anthropic LSP** (try first)
```
/plugin install typescript-lsp@claude-plugins-official
```

**Option B: Community LSP** (if Option A has issues)
```
/plugin marketplace add boostvolt/claude-code-lsps

# Install for your language:
/plugin install vtsls@claude-code-lsps          # TypeScript/JavaScript
/plugin install pyright@claude-code-lsps        # Python
/plugin install rust-analyzer@claude-code-lsps  # Rust
/plugin install gopls@claude-code-lsps          # Go
```

The `boostvolt/claude-code-lsps` marketplace supports 22+ languages. If the official `typescript-lsp` works for your project, prefer it; if you encounter issues, fall back to `vtsls`.

#### 2. Frontend Design (HIGHLY RECOMMENDED for frontend projects)

Anthropic's official design skill with **277,000+ installs**. Generates production-grade UI with bold aesthetic choices, distinctive typography, purposeful color palettes, and intentional animations. Specifically designed to avoid generic "AI slop" aesthetics.

```
/plugin install frontend-design@claude-plugins-official
```

This plugin auto-invokes when Claude writes frontend code. It provides design direction before coding: picking an extreme tone, choosing distinctive fonts, and committing to a visual identity.

#### 3. Feature Development (RECOMMENDED)

Anthropic's official 7-phase workflow with **89,000+ installs**: requirements gathering, codebase exploration, architecture design, implementation, testing, review, and documentation.

```
/plugin install feature-dev@claude-plugins-official
```

#### 4. Superpowers (RECOMMENDED)

20+ battle-tested skills including brainstorm, write-plan, execute-plan, and TDD enforcement. Transforms Claude from "intelligent autocomplete" to a structured development workflow.

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Key behaviors: Socratic brainstorming before coding, micro-task planning, enforced RED-GREEN-REFACTOR cycle (Claude deletes code written before tests), and code review between tasks.

### Tier 2: Situational Plugins

| Plugin | Source | Purpose | Install |
|--------|--------|---------|---------|
| **commit-commands** | `claude-plugins-official` | Automated conventional commits and PR creation | `/plugin install commit-commands@claude-plugins-official` |
| **github** | `claude-plugins-official` | GitHub integration (issues, PRs, code review) | `/plugin install github@claude-plugins-official` |
| **pr-review-toolkit** | `claude-plugins-official` | Multi-agent code reviews with confidence scoring | `/plugin install pr-review-toolkit@claude-plugins-official` |
| **Context7** | `claude-plugins-official` | Live docs lookup (also available as MCP — see Step 5) | `/plugin install context7@claude-plugins-official` |

### Tier 3: Service-Specific Plugins

Install plugins for services your project uses:

```
/plugin install figma@claude-plugins-official       # Figma design integration
/plugin install vercel@claude-plugins-official       # Vercel deployment
/plugin install supabase@claude-plugins-official     # Supabase (DB, auth, storage)
/plugin install firebase@claude-plugins-official     # Firebase
/plugin install sentry@claude-plugins-official       # Error monitoring
/plugin install slack@claude-plugins-official        # Slack integration
```

**Important:** Service plugins often include MCP servers. After installing, check if the plugin already provides the MCP connection before adding a separate MCP server in Step 5.

### Community Plugin: everything-claude-code

The hackathon-winning configuration (50K+ GitHub stars) with 13 agents, 40+ skills, 32 commands, and comprehensive hooks.

```
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

**Caution:** As of March 2026, this plugin has active installation issues — the Claude plugin validator enforces strict constraints that can cause failures. If installation fails, cherry-pick individual skills via `npx skills add` instead (see Step 7).

### Plugin Budget

**Keep only 4-5 plugins active** — each consumes context window. Plugins load their skill descriptions and tool definitions at session start. Check context impact with `/context`.

### Post-Installation Checklist

After installing plugins, before proceeding to Steps 7-9:

1. Run `/plugins` to see all installed plugins and what they provide
2. Note which skills are already covered (TDD, debugging, review, etc.)
3. Note which MCP servers are already connected
4. Note which agents are already available
5. Only create custom skills/agents/commands for gaps not covered by plugins

---

## Step 5: MCP Servers — External Service Connections

MCP (Model Context Protocol) connects Claude to external services — databases, APIs, deployment platforms, documentation sources.

**Before adding MCP servers**, check if any installed plugins (Step 4) already provide the connection you need. For example, a Supabase plugin typically includes a Supabase MCP server.

### Configuration

MCP servers can be added via CLI or `.mcp.json` file:

```bash
# Standard MCP server (stdio transport)
claude mcp add <server-name> -- npx -y @package/server-name

# HTTP transport (for hosted MCP servers)
claude mcp add --transport http <server-name> https://mcp.example.com

# With environment variables
claude mcp add <server-name> -e API_KEY=your-key -- npx -y @package/server-name

# Scoped to user (all projects)
claude mcp add --scope user <server-name> -- npx -y @package/server-name

# List configured servers
claude mcp list

# Remove a server
claude mcp remove <server-name>
```

### Tier 1: Start Here (2-3 max)

| Server | Purpose | Install |
|--------|---------|---------|
| **Context7** | Real-time, version-specific documentation. Solves knowledge cutoff for rapidly-evolving frameworks (React, Next.js, Tailwind). Add "use context7" to any prompt needing current docs. | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| **Sequential Thinking** | Structured reasoning chains for complex problems | `claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking` |

**Note:** Context7 is also available as an official plugin (`/plugin install context7@claude-plugins-official`) which bundles skills, agents, and commands beyond the basic MCP connection. Choose one — don't install both.

### Tier 2: Add When Needed

| Server | Purpose | Install | Notes |
|--------|---------|---------|-------|
| **Playwright** | Browser automation, E2E testing | `claude mcp add playwright -- npx -y @anthropic/mcp-server-playwright` | Visible browser window for debugging |
| **GitHub** | PR/issue management | `claude mcp add github` | Often unnecessary — Claude has built-in `gh` CLI access |
| **PostgreSQL** | Direct database queries | `claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://..."` | Skip if using an ORM |
| **Fetch** | Read any URL/API docs | `claude mcp add fetch -- npx -y @modelcontextprotocol/server-fetch` | Claude has built-in `WebFetch` tool |
| **Magic UI** | Pre-built React+Tailwind component library with polished animations | See `magicui.design/docs/mcp` | Freemium — free tier has generation limits |
| **shadcn/ui** | Official shadcn component generation | See `ui.shadcn.com/docs/mcp` | Only if your project uses shadcn |

### Tier 3: Specialized

| Server | Purpose |
|--------|---------|
| **Vercel** | Deploy frontend, manage projects, search docs |
| **Netlify** | Site management, build hooks, env vars for JAMstack |
| **Railway** | Deploy backend |
| **Docker** | Container management |
| **Cloudflare** | Workers, DNS, CDN |
| **Sentry** | Error monitoring |

### Context Budget Rules

**Each active MCP server consumes context window on every request.**

- Context can shrink from 200K to ~70K with too many active MCPs
- Keep **5-10 active per project** maximum
- Stay under **80 active tools** total
- Use `/mcp` command to check token costs per server
- Disable unused servers at the project level:

```json
{
  "disabledMcpServers": ["playwright", "docker", "cloudflare"]
}
```

- Prefer native tools (Glob, Grep, Read, Explore subagent) for tasks under 1000 files — they cost zero context
- Check for overlap with plugins — a service plugin may already provide the MCP connection

---

## Step 6: Hooks — Deterministic Automation

Hooks execute at specific lifecycle events. They are NOT AI — they run deterministically every time. This is what makes them powerful: formatting will always happen, not just when Claude "remembers" to do it.

**Rule of thumb:** If it's a suggestion, use CLAUDE.md. If it's a requirement, use a hook.

### Hook Types

As of 2026, hooks support **four execution types**:

| Type | What It Does | Use Case |
|------|-------------|----------|
| `command` | Shell command (most common) | Formatting, linting, blocking, logging |
| `prompt` | Single-turn LLM evaluation | Judgment calls — "is this code safe to commit?" |
| `agent` | Multi-turn subagent with tools | Complex verification — "review this diff for security issues" |
| `http` | POST to HTTP endpoint | Webhooks — notify Slack, trigger CI, log to external service |

### Hook Events

| Event | When It Fires | Use Case |
|-------|--------------|----------|
| `PreToolUse` | Before a tool executes | Block dangerous operations, validate |
| `PostToolUse` | After a tool completes | Format code, run type checks |
| `PostToolUseFailure` | After a tool fails | Error logging, retry logic |
| `PermissionRequest` | When permission dialog shows | Auto-allow/deny |
| `UserPromptSubmit` | When you press Enter | Inject context, log prompts |
| `Stop` | When Claude finishes responding | Final verification, log summary |
| `StopFailure` | When stop handler fails | Error recovery |
| `SubagentStart` | When a subagent launches | Logging, resource allocation |
| `SubagentStop` | When a subagent completes | Post-process subagent work |
| `TeammateIdle` | When a teammate agent is idle | Task coordination |
| `TaskCompleted` | When a task finishes | Progress tracking |
| `Notification` | When Claude needs attention | Desktop notifications |
| `PreCompact` | Before context compression | Preserve critical state |
| `PostCompact` | After context compression | Restore context, re-inject state |
| `SessionStart` | Session begins or resumes | Restore context, detect environment |
| `SessionEnd` | Session ends | Save state, extract learnings |
| `ConfigChange` | Settings are modified | Audit, enforce constraints |
| `InstructionsLoaded` | CLAUDE.md or rules load | Dynamic rule injection |
| `WorktreeCreate` | Git worktree created | Setup parallel environments |
| `WorktreeRemove` | Git worktree removed | Cleanup |
| `Elicitation` | LLM requests user input | Custom input handling |
| `ElicitationResult` | User responds to elicitation | Process user responses |
| `Setup` | On `--init` or `--maintenance` | Project initialization |

`SessionStart` matchers: `startup`, `resume`, `clear`, `compact`
`SessionEnd` matchers: `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`

### Configuration Location

Hooks go in `settings.json` (project or global):

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          {
            "type": "command",
            "command": "shell command here"
          }
        ]
      }
    ]
  }
}
```

- `matcher`: tool name pattern to match (e.g., `"Edit|Write"`, `"Bash"`, `"*"` for all, `""` for no-tool events)
- `command`: shell command to run. Receives tool input as JSON on stdin.
- Exit code 0 = success (hook output suppressed). Exit code 2 = block tool + show output as feedback.

### Environment Variables Available in Hooks

| Variable | Description |
|----------|-------------|
| `$CLAUDE_PROJECT_DIR` | Root directory of the project |

Tool input is passed via **stdin as JSON** with fields like `tool_name`, `tool_input.file_path`, `tool_input.command`, etc.

### Recommended Hook Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | { read fp; if echo \"$fp\" | grep -qE '\\.(ts|tsx|js|jsx|mjs|css|json|md)$'; then npx prettier --write \"$fp\" 2>/dev/null; fi; } || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path // empty' | { read fp; blocked=false; for pattern in .env package-lock.json pnpm-lock.yaml yarn.lock .git/ node_modules/ dist/ .next/ build/; do case \"$fp\" in *\"$pattern\"*) blocked=true;; esac; done; if $blocked; then echo \"BLOCKED: Writing to $fp is not allowed.\" >&2; exit 2; fi; } || true"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // empty' | { read cmd; branch=$(cd \"$CLAUDE_PROJECT_DIR\" && git rev-parse --abbrev-ref HEAD 2>/dev/null); if echo \"$cmd\" | grep -qE '^git commit' && echo \"$branch\" | grep -qE '^(main|master|dev)$'; then echo \"BLOCKED: Never commit directly on $branch. Create a feature branch first.\" >&2; exit 2; fi; if echo \"$cmd\" | grep -qE 'git push.*(origin )?(main|master|dev)( |$)'; then echo \"BLOCKED: Never push directly to $branch. Merge via PR only.\" >&2; exit 2; fi; } || true"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command // empty' | { read cmd; if echo \"$cmd\" | grep -qiE '^git push'; then echo 'REMINDER: Review changes before pushing. Run /verify first.' >&2; fi; } || true"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && git diff --name-only 2>/dev/null | xargs grep -l 'console\\.log\\|console\\.debug' 2>/dev/null | head -10 | { files=$(cat); if [ -n \"$files\" ]; then echo \"WARNING: Debug statements found in modified files:\" >&2; echo \"$files\" >&2; fi; } || true"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Awaiting your input' 2>/dev/null || osascript -e 'display notification \"Awaiting your input\" with title \"Claude Code\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

**What each hook does:**

| Hook | Trigger | Action |
|------|---------|--------|
| PostToolUse (prettier) | After any file edit | Auto-format with Prettier (ts, tsx, js, jsx, mjs, css, json, md) |
| PreToolUse (file protection) | Before any write | Block writes to .env, lockfiles, .git, node_modules, dist, build |
| PreToolUse (branch protection) | Before git commit/push | Block commits on protected branches and direct pushes |
| PreToolUse (git push reminder) | Before git push | Remind to review changes and run /verify |
| Stop (console.log scanner) | When Claude finishes | Scan modified files for leftover debug statements |
| Notification | When Claude needs input | Desktop notification (Linux/macOS) |

### Advanced Hook Types

#### LLM-Based Review (type: "prompt")

Use for judgment calls that shell scripts can't handle:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review this bash command for safety. Is it destructive or dangerous? If yes, output BLOCK and explain why. If safe, output ALLOW."
          }
        ]
      }
    ]
  }
}
```

#### Agent-Based Verification (type: "agent")

Multi-turn verification with file and tool access:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "agent",
            "prompt": "Review the git diff for security vulnerabilities. Check for hardcoded secrets, SQL injection, XSS. Report findings."
          }
        ]
      }
    ]
  }
}
```

#### Webhook Notifications (type: "http")

POST to external services:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "http",
            "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
          }
        ]
      }
    ]
  }
}
```

### Hook Design Best Practices

1. **Always end shell hooks with `|| true`** — prevents hook failures from blocking normal operation
2. **Use exit code 2 to block** — outputs to stderr and blocks the tool
3. **Use `jq` for JSON parsing** — tool input arrives as JSON on stdin
4. **Keep `command` hooks fast** — hooks run synchronously. For heavy operations, use skills or commands instead
5. **Use `prompt`/`agent` hooks sparingly** — they consume tokens and add latency
6. **Test hooks manually first:**
   ```bash
   echo '{"tool_input":{"file_path":"src/index.ts"}}' | jq -r '.tool_input.file_path'
   ```

### Formatter Prerequisites

The auto-format hook requires a code formatter. If using Prettier:

```bash
npm install --save-dev prettier

cat > .prettierrc << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
EOF
```

The hook will silently skip formatting if Prettier is not installed (due to `2>/dev/null` and `|| true`).

### Interactive Hook Setup

Instead of editing JSON manually, use the built-in UI:

```
/hooks
```

---

# Phase 3: Project-Specific Configuration

## Step 7: Skills — On-Demand Knowledge

Skills are the most flexible extension. They load descriptions at session start (low cost) and full content only when invoked or auto-matched.

**Before creating skills**, check what your installed plugins (Step 4) already provide. Many plugins include skills for common workflows like TDD, debugging, and code review.

**Note:** Commands (`.claude/commands/`) and skills (`.claude/skills/`) are now **merged**. Both create slash commands. Use whichever structure you prefer. Skills support more advanced features (supporting files, `context: fork`, tool restrictions).

### Skill File Structure

```
.claude/skills/
└── my-skill/
    ├── SKILL.md           # Main skill file (required)
    ├── PATTERNS.md        # Supporting reference (optional)
    ├── EXAMPLES.md        # Examples (optional)
    └── scripts/           # Supporting scripts (optional)
        └── validate.sh
```

### SKILL.md Format

```yaml
---
name: skill-name
description: |
  One-paragraph description of when this skill should be used.
  Claude matches tasks to this description to decide relevance.
  Write this as a trigger, not a summary — focus on what pushes Claude
  out of its default behavior.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
# model: sonnet                      # Override model for this skill
# disable-model-invocation: true     # Hide from Claude (manual-only)
# context: fork                      # Run in isolated subagent context
# user-invocable: true               # Explicitly mark as user-invocable
---

# Skill Title

[Instructions for Claude when this skill activates]

## When to Use
[Conditions that trigger this skill]

## Process
1. [Step one]
2. [Step two]
3. [Step three]

## Gotchas
[Highest-signal content about Claude's failure points — what goes wrong without this skill]

## Patterns
[Code patterns, conventions, templates]

## Anti-Patterns
[What NOT to do]
```

### String Substitutions Available in Skills

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | Everything the user types after the command |
| `$N` | Nth positional argument |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md |

### Installing Community Skills

#### From skills.sh Marketplace

```bash
# Install all skills from a repository
npx skills add <owner/repo>

# Install a specific skill
npx skills add "<owner/repo>" --skill "<skill-name>" --yes

# Examples
npx skills add anthropics/skills --skill "web-interface-guidelines" --yes
npx skills add vercel-labs/agent-skills    # All Vercel React/Next.js skills
```

**Important syntax notes:**
- Use `--skill` flag for specific skills — do NOT use `@skill-name` suffix
- `--yes` skips confirmation prompts
- Skills install to `.agents/skills/`, not `.claude/skills/`
- Restart Claude Code after installing

#### Popular Pre-Built Skills

| Skill | Source | Installs | What It Does |
|-------|--------|----------|-------------|
| **frontend-design** | `anthropics/skills` | 110K/week | Production-grade UI with bold design (also available as plugin) |
| **web-interface-guidelines** | `anthropics/skills` | 133K/week | 100+ rules for accessibility, performance, UX, ARIA, focus states |
| **react-best-practices** | `vercel-labs/agent-skills` | — | 45 rules in 8 categories: waterfall elimination, bundle size, SSR, re-renders |
| **composition-patterns** | `vercel-labs/agent-skills` | — | Compound components, better API design, avoiding boolean props |
| **remotion-best-practices** | Community | 117K/week | Video generation with Remotion |
| **impeccable** | `impeccable.style` | — | Upgraded version of frontend-design with improved design quality |

### Built-in Skills

Claude Code includes these out of the box:

| Skill | Command | What It Does |
|-------|---------|-------------|
| Batch | `/batch` | Large-scale parallel code changes across worktrees |
| Claude API | `/claude-api` | Load Claude API reference material |
| Debug | `/debug` | Troubleshoot session issues |
| Loop | `/loop` | Run prompts/commands on recurring intervals |
| Simplify | `/simplify` | Review changed code for reuse, quality, efficiency |

### Essential Custom Skills to Create

#### Verification Loop (pre-PR quality gate)

```yaml
---
name: verification-loop
description: |
  Structured 6-phase verification for code changes. Use before creating
  PRs or after completing features. Runs build, typecheck, lint, tests,
  security scan, and diff review.
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

# Verification Loop

Run this 6-phase check before any PR or after major changes.

## Phase 1: Build
Run the project build command. Stop if it fails.

## Phase 2: Type Check
Run the type checker. Report all errors with file paths and line numbers.

## Phase 3: Lint
Run the linter across all modified files. Report violations.

## Phase 4: Test Suite
Run the test suite with coverage. Target: 80%+ coverage on changed files.
Report failing tests with full error output.

## Phase 5: Security Scan
Scan for:
- Hardcoded secrets, API keys, passwords
- Leftover console.log / print / debug statements
- TODO/FIXME/HACK comments in new code
- Exposed internal error messages

## Phase 6: Diff Review
Run `git diff` and check for:
- Unintended file changes
- Large files that shouldn't be committed
- Merge conflict markers
- Files that belong in .gitignore

## Report Format

| Phase | Status | Details |
|-------|--------|---------|
| Build | PASS/FAIL | [errors if any] |
| Types | PASS/FAIL | [error count] |
| Lint  | PASS/FAIL | [violation count] |
| Tests | PASS/FAIL | [pass/fail count, coverage %] |
| Security | PASS/FAIL | [findings] |
| Diff  | PASS/FAIL | [issues] |

**Overall: READY / NOT READY for PR**
```

### Skills vs Other Features

| If you need... | Use... |
|----------------|--------|
| "Always do X" rules | CLAUDE.md or `.claude/rules/` |
| Topic-specific guidelines | `.claude/rules/` |
| Reference material Claude needs sometimes | Skill |
| Workflow triggered with `/<name>` | Skill (commands merged with skills) |
| Isolated worker with limited tools | Subagent |
| External service connection | MCP Server |
| Deterministic automation | Hook |
| Bundled set of skills + agents + hooks | Plugin |

### Context Efficiency

- **Startup cost**: Only skill name + description loaded (~100 tokens per skill)
- **On-demand**: Full SKILL.md content loaded only when Claude decides to use it
- **Reference files**: Supporting files loaded only when needed
- **No penalty for unused skills**: Large skill libraries don't consume tokens until accessed
- Set `disable-model-invocation: true` on skills you only invoke manually — saves description tokens every request

---

## Step 8: Subagents — Isolated Workers

Subagents run in their own context window with limited tools. They explore, analyze, or work independently and return a summary — keeping your main context clean.

**Before creating these**, check if your installed plugins (Step 4) already provide equivalent agents.

### Subagent File Format

Place in `.claude/agents/`:

```yaml
---
name: agent-name
description: |
  When to use this agent. Claude matches tasks to this description.
  Be specific so Claude delegates correctly.
model: sonnet          # or: opus, haiku, inherit
tools: Read, Grep, Glob, Bash, Write, Edit    # limit to what's needed
# skills:             # optional: preload skills into subagent context
#   - skill-name
# memory: .claude/agent-memory/agent-name/  # persistent cross-session memory
# permission_mode: default  # default, acceptEdits, dontAsk, bypassPermissions, plan
---

[System prompt for the subagent]

## Your Role
[What this agent does]

## Process
1. [Step]
2. [Step]

## Output Format
[How to structure the response]
```

### New Invocation Methods

Subagents can be invoked in multiple ways:

| Method | Example |
|--------|---------|
| Natural language | "Use the security-reviewer agent to check this code" |
| @-mention | `@"code-reviewer (agent)"` |
| CLI flag | `claude --agent code-reviewer` |
| Settings default | `"agent": "code-reviewer"` in settings.json |

### Cost Optimization

Set `CLAUDE_CODE_SUBAGENT_MODEL` environment variable to run subagents on cheaper models while keeping your main session on Opus:

```bash
export CLAUDE_CODE_SUBAGENT_MODEL=sonnet
```

This is one of the most impactful cost optimizations — main session on Opus for complex reasoning, subagents on Sonnet/Haiku for focused tasks.

### Persistent Memory

The `memory` field gives a subagent a persistent directory that survives across conversations:

```yaml
---
name: code-reviewer
memory: .claude/agent-memory/code-reviewer/
---
```

The subagent can read/write to this directory to build up knowledge over time — codebase patterns, debugging insights, architectural decisions.

### Agent Teams

Beyond individual subagents, Claude Code supports **Agent Teams** where multiple agents coordinate:

- Agents share findings and challenge each other
- One agent's output feeds into another's input
- Coordinated parallel work on different aspects of a problem

Example: A code reviewer and security reviewer running in parallel, sharing findings, with a coordinator synthesizing their reports.

### Worktree Isolation

Run subagents in isolated git worktrees:

```yaml
---
name: experimental-refactor
isolation: worktree
---
```

The agent gets an isolated copy of the repository. If it makes no changes, the worktree is cleaned up. If it makes changes, the worktree path and branch are returned.

### Recommended Subagents

#### Planner

```yaml
---
name: planner
description: |
  Expert planning specialist. Use when implementing features that touch
  3+ files, require architecture decisions, or need refactoring strategy.
model: opus
tools: Read, Grep, Glob
memory: .claude/agent-memory/planner/
---

You are an expert planning specialist. Decompose complex requirements into
actionable implementation steps.

## Process
1. Analyze requirements thoroughly
2. Review existing codebase architecture
3. Identify all affected files and dependencies
4. Sequence implementation for incremental testing
5. Flag risks and edge cases

## Output
Produce a numbered plan with:
- Exact file paths for each change
- What to add/modify/remove
- Order of implementation
- Verification steps between phases
- Risks and mitigations

## Quality Standards
- Be specific: exact file paths and function names
- Minimize changes — don't refactor beyond scope
- Plans should enable incremental testing
```

#### Code Reviewer

```yaml
---
name: code-reviewer
description: |
  Senior code review specialist. Use after completing features or before
  PRs. Reviews for quality, security, performance, and best practices.
model: sonnet
tools: Read, Grep, Glob, Bash
---

You are a senior code reviewer. Review changes against a comprehensive checklist.

## Process
1. Run `git diff` to see all changes
2. Read each modified file in full
3. Check against all categories below
4. Produce structured report

## Review Categories

### Security (Critical)
- Hardcoded credentials or secrets
- SQL/NoSQL injection vulnerabilities
- XSS risks (unescaped user input in output)
- Missing input validation
- Authentication/authorization bypasses

### Code Quality (High)
- Functions longer than 50 lines
- Files longer than 300 lines
- Nesting deeper than 3 levels
- Missing error handling
- Leftover debug statements
- Missing test coverage for new code

### Performance (Medium)
- N+1 query patterns
- Unnecessary re-renders / recomputations
- Unbounded list operations (missing pagination)
- Missing memoization for expensive computations

## Verdict
- **Approve**: No critical or high issues
- **Warning**: Medium issues only — mergeable with notes
- **Block**: Critical or high issues — must fix
```

#### Build Error Resolver

```yaml
---
name: build-fixer
description: |
  Fix build failures, compilation errors, type errors, and lint violations.
  Use when the build breaks and needs systematic fixing.
model: haiku
tools: Read, Grep, Glob, Edit, Bash
---

You fix build errors efficiently.

## Process
1. Run the failing build/typecheck/lint command
2. Capture and parse all error output
3. Read the relevant source files
4. Fix the root cause (not symptoms)
5. Re-run to verify the fix
6. If new errors appear, fix those too (max 3 iterations)

## Rules
- Fix root causes, not symptoms
- Never suppress errors with @ts-ignore, type assertions, or // eslint-disable
- Never change public API signatures unless the error requires it
- Preserve existing behavior while fixing types/builds
```

### Pre-Built Agent Collections

The repository [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) has 100+ pre-built agents for various use cases.

---

## Step 9: Slash Commands — Workflow Shortcuts

Commands live in `.claude/commands/` as markdown files. Since commands and skills are now merged, you can use either location — commands are simpler (single file), skills support more features (supporting files, isolation).

### Command File Format

```yaml
---
description: Brief description shown in command picker
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
# disable-model-invocation: true   # Only manual invocation
---

[Instructions for Claude when this command is invoked]

$ARGUMENTS — this variable contains whatever the user types after the command
```

### Recommended Commands

#### `/verify`

```yaml
---
description: Run the full verification loop (build, types, lint, test, security, diff)
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

Run the verification loop skill. Execute all 6 phases and produce the report.
```

#### `/plan`

```yaml
---
description: Create a detailed implementation plan before coding
allowed-tools: Read, Grep, Glob
---

Create a detailed implementation plan for: $ARGUMENTS

1. Analyze the requirement
2. Explore the codebase to understand current architecture
3. Identify all files that need to change
4. List dependencies and risks
5. Produce a numbered step-by-step plan with exact file paths
6. Include verification steps between phases
7. Do NOT implement — only plan
```

#### `/create-component`

```yaml
---
description: Scaffold a new UI component with tests
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Create a new UI component for: $ARGUMENTS

1. Look at existing components for patterns, naming, and structure
2. Create the component file with proper types
3. Create the test file following existing test patterns
4. Export from the barrel file if one exists
5. Run the tests to verify
```

#### `/tdd`

```yaml
---
description: Implement a feature using test-driven development
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

Implement using TDD: $ARGUMENTS

Process:
1. Write a failing test first
2. Run it — confirm it fails for the right reason
3. Write the minimal code to make it pass
4. Run it — confirm it passes
5. Refactor if needed (keep tests green)
6. Repeat for the next behavior
7. Run full test suite at the end
```

#### `/code-review`

```yaml
---
description: Review current changes for quality, security, and best practices
allowed-tools: Read, Grep, Glob, Bash
---

Review all current uncommitted changes:

1. Run `git diff` to see all changes
2. Review each changed file against the code review checklist
3. Check for security issues, code quality, performance, and best practices
4. Produce a structured report with severity levels
5. Give a verdict: Approve / Warning / Block
```

#### `/build-fix`

```yaml
---
description: Fix all build, type, and lint errors
allowed-tools: Read, Edit, Grep, Glob, Bash
---

Fix all build errors:

1. Run the build command and capture errors
2. Run the type checker and capture errors
3. Run the linter and capture errors
4. Fix all errors starting with the most fundamental (types first)
5. Re-run after each fix to check for cascading issues
6. Repeat until clean build (max 5 iterations)
7. Run tests to ensure no regressions
```

#### `/new-feature`

```yaml
---
description: Create a feature branch and prepare for implementation
allowed-tools: Bash
---

Create a new feature branch for: $ARGUMENTS

1. Check that the working tree is clean — if dirty, stop and warn
2. Fetch latest from remote: `git fetch origin`
3. Checkout the development branch and pull latest changes
4. Create and switch to feature branch: `git checkout -b feature/<slugified-name>`
5. Confirm the branch was created and is ready for work
6. Do NOT start implementing — just set up the branch.
```

---

# Phase 4: Advanced Workflows

## Step 10: Context Management Strategy

Context window is your most precious resource. Manage it actively.

### Budget Awareness

| Feature | Context Cost |
|---------|-------------|
| CLAUDE.md (200 lines) | ~1-3% per request |
| Each MCP server | ~5-15% per request |
| Each active plugin | ~3-10% per request |
| Skill description (loaded) | ~0.1% per request |
| Skill full content (invoked) | ~2-5% one-time |
| Subagent | 0% (isolated) |
| Hook (command type) | 0% (external) |
| Hook (prompt/agent type) | Consumes tokens when triggered |

### Context Optimization Rules

1. **Monitor context**: Use `/context` command to see usage breakdown
2. **Compact strategically**: Run `/compact` after planning (before coding), after milestones, after debugging sessions — not mid-implementation
3. **Use subagents for exploration**: They explore in separate context, return only summaries
4. **Disable unused MCPs**: Each server costs tokens even if not actively used
5. **Use skills instead of bloated CLAUDE.md**: Skills load on-demand; CLAUDE.md loads every request
6. **Clear between unrelated tasks**: Use `/clear` to start fresh
7. **Name sessions**: Use `/rename` so you can resume later without rebuilding context
8. **Set `disable-model-invocation: true`** on manual-only skills

### Compaction Prompt Template

```
/compact Retain: [current task, key decisions made, files being modified].
Completed: [what's done]. Next: [immediate next step].
```

---

## Step 11: Monorepo vs Separate Repos

### Recommendation: Monorepo

| Factor | Monorepo | Separate Repos |
|--------|----------|----------------|
| Claude context | Hierarchical CLAUDE.md — loads only relevant rules | Burns 40-60% tokens on cross-repo duplication |
| Shared code | Single `packages/shared` — direct imports | Must publish npm packages or copy types |
| Build speed | Turborepo caching + parallel | Independent CI, no shared cache |
| Integration | Claude sees both sides of your API | Must manually sync API contracts |
| CLAUDE.md | Auto-loads per directory | Need `--add-dir` workaround |

### Monorepo Hierarchical CLAUDE.md

```
monorepo/
├── CLAUDE.md                 # Shared rules (always loaded, ~100 lines)
├── apps/
│   ├── web/CLAUDE.md         # Frontend rules (~100 lines, loads in web/)
│   └── api/CLAUDE.md         # Backend rules (~100 lines, loads in api/)
└── packages/
    └── shared/CLAUDE.md      # Shared package rules (~50 lines)
```

### If You Must Use Separate Repos

#### Option A: `--add-dir`

```bash
cd ~/projects/frontend
claude --add-dir ~/projects/backend
```

#### Option B: Parent Directory

```bash
mkdir ~/projects/fullstack
cd ~/projects/fullstack
git clone <frontend> web
git clone <backend> api
claude    # launches in parent, sees both
```

---

## Step 12: Parallel Workflows

### Git Worktrees (Multiple Claude Instances)

```bash
git worktree add ../project-feature-a -b feature-a
git worktree add ../project-bugfix bugfix-123

cd ../project-feature-a && claude
cd ../project-bugfix && claude

git worktree remove ../project-feature-a
```

### Conversation Forking

```
/fork
```

Creates an independent branch of the conversation.

### tmux for Long Sessions

```bash
tmux new -s claude-dev
# Detach: Ctrl+B, D
# Reattach:
tmux attach -t claude-dev
```

---

## Step 13: Editor Integration

### Zed (Recommended for Performance)

- Built-in Agent Panel for real-time file tracking
- `Cmd+Shift+R` — command palette
- `Ctrl+G` from Claude Code — opens current files in Zed
- Split-screen: terminal + editor side by side

### VS Code / Cursor

- Claude Code runs in the integrated terminal
- `\ide` command syncs file opens with the editor
- Extensions for deeper integration
- Multi-root workspaces for multi-repo setups

### General Setup

Split-screen: **Left** terminal with Claude Code, **Right** editor showing files. Claude edits files, editor auto-reloads, you review in real time.

---

## Step 14: Vercel Integration — Skills, MCP & Deployment

### 14.1: Vercel Agent Skills

```bash
npx add-skill vercel-labs/agent-skills
```

| Skill | What It Provides |
|-------|-----------------|
| **react-best-practices** | 45 rules in 8 categories (CRITICAL to LOW priority) |
| **web-design-guidelines** | 100+ rules: accessibility, performance, UX |
| **composition-patterns** | Compound components, API design |
| **vercel-deploy-claimable** | One-command deploy with preview URL |

### 14.2: Vercel MCP Server (Official)

```bash
# Project-specific (recommended)
claude mcp add --transport http vercel https://mcp.vercel.com/my-team/my-project
```

Read-only: project info, deployment status, logs, docs. Authenticate via `/mcp` (OAuth).

### 14.3: Community MCP (Write Access)

```bash
claude mcp add-json "vercel-write" '{"command":"npx","args":["-y","vercel-mcp"]}'
```

Trigger deployments, manage env vars, create/delete projects. Requires API token.

### 14.4: v0 MCP (UI Generation)

```bash
claude mcp add-json "v0" '{"command":"npx","args":["-y","v0-mcp"]}'
```

Generate React/Next.js components from text descriptions or design screenshots.

### 14.5: Custom Deploy Command

`.claude/commands/deploy.md`:

```yaml
---
description: Build, verify, and deploy to Vercel
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

Deploy the project to Vercel: $ARGUMENTS

1. Run the full build
2. Run type checker
3. Run linter
4. Run test suite
5. If ANY step fails, STOP. Do not deploy broken code.
6. Run `vercel --prod` for production or `vercel` for preview
7. Report deployment URL and status
```

---

## Step 15: CI/CD Integration

### Claude as a Linter

```json
{
  "scripts": {
    "lint:claude": "claude -p 'You are a linter. Look at changes vs main. Report issues: filename:line on one line, description on the next. No other text.'"
  }
}
```

### Claude for PR Review (GitHub Actions)

```yaml
name: Claude PR Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Claude Review
        run: |
          git diff origin/main...HEAD | claude -p "Review this diff for bugs, security issues, and best practices. Be concise." --output-format text
```

### Output Formats

| Format | Flag | Use Case |
|--------|------|----------|
| Text | `--output-format text` | Simple pipe output (default) |
| JSON | `--output-format json` | Structured data for scripts |
| Stream JSON | `--output-format stream-json` | Real-time processing |

---

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+U` | Delete entire input line |
| `Shift+Enter` | Multiline input |
| `Tab` | Toggle extended thinking display |
| `Ctrl+O` | Toggle verbose mode (see thinking) |
| `Option+T` / `Alt+T` | Toggle thinking on/off |
| `Esc Esc` | Interrupt current response or restore code |
| `Ctrl+G` | Open current files in editor (Zed) |
| `!command` | Run bash command directly |
| `@filepath` | Reference a file |
| `/command` | Run a slash command |

---

## Useful Built-in Commands Reference

| Command | What It Does |
|---------|-------------|
| `/help` | Show available commands |
| `/hooks` | Interactive hook configurator |
| `/mcp` | Show MCP server status and token costs |
| `/plugins` | List installed plugins |
| `/plugin` | Interactive plugin manager (4 tabs) |
| `/reload-plugins` | Apply plugin changes without restart |
| `/context` | Show context window usage breakdown |
| `/compact` | Manual context compression |
| `/clear` | Clear conversation (start fresh) |
| `/fork` | Fork conversation for parallel work |
| `/rewind` | Return to previous conversation state |
| `/resume` | Resume a previous session |
| `/rename` | Name current session for later resumption |
| `/checkpoints` | File-level rollback points |
| `/statusline` | Customize status bar display |
| `/config` | Edit global configuration |
| `/add-dir` | Add another directory to workspace |
| `/agents` | Manage subagents |
| `/permissions` | Review and modify permissions |
| `/batch` | Large-scale parallel changes across worktrees |
| `/simplify` | Review changes for quality and efficiency |
| `/debug` | Troubleshoot session issues |
| `/loop` | Run prompts on recurring intervals |

---

## Troubleshooting

### Context Window Filling Up Fast

- Run `/mcp` — check per-server token costs, disable unused servers
- Run `/context` — see what's consuming space
- CLAUDE.md too large? Trim to <200 lines, move excess to skills
- Use subagents for exploration (isolated context)
- Run `/compact` at logical boundaries

### Claude Ignoring CLAUDE.md Instructions

- File is too long (>200 lines) — Claude loses focus. Trim it.
- Instructions conflict with each other — make rules unambiguous
- Instructions are too soft ("consider doing X") — use imperative ("Always do X", "Never do Y")
- Run `/clear` — stale context may override rules

### Hooks Not Firing

- Check event name matches exactly (case-sensitive): `PreToolUse`, `PostToolUse`, `Stop`
- Check `matcher` pattern matches the tool name: `"Edit|Write"`, `"Bash"`, `"*"`
- Check script is executable: `chmod +x script.sh`
- Run `/hooks` to see registered hooks
- Check `settings.json` vs `settings.local.json` — local overrides project

### MCP Server Not Working

- Run `/mcp` to check connection status
- MCP connections can fail silently mid-session
- If a tool disappears, restart the session
- Check that `npx` can find the package: `npx -y @package/name --help`

### Subagents Not Being Used

- Check the `description` field is specific enough for Claude to match tasks
- Add an `agent-delegation.md` rule file telling Claude when to delegate
- Invoke manually: "Use the security-reviewer agent to check this code"
- Try @-mention: `@"security-reviewer (agent)"`

### Plugins Not Working

- Must be installed via `/plugin` commands inside Claude Code (not Bash)
- Include `@marketplace` suffix: `/plugin install name@marketplace-name`
- Run `/plugins` to see status
- Run `/reload-plugins` after configuration changes
- If a plugin provides MCP that needs authentication, run `/mcp` to authenticate

### TypeScript LSP Plugin Not Working

- Try the official plugin first: `/plugin install typescript-lsp@claude-plugins-official`
- If the official has issues, use community: `/plugin marketplace add boostvolt/claude-code-lsps` then `/plugin install vtsls@claude-code-lsps`
- Ensure `typescript-language-server` or `vtsls` binary is accessible

### skills.sh Installation Failing

- Use `--skill` flag for specific skills: `npx skills add "owner/repo" --skill "skill-name" --yes`
- Do NOT use `@skill-name` suffix — it's interpreted as a git tag
- Skills install to `.agents/skills/`, not `.claude/skills/`
- Restart Claude Code after installing marketplace skills

### Slow Performance

- Too many MCP servers active — disable unused ones
- Too many plugins — keep 4-5 max
- CLAUDE.md too large — trim to <200 lines
- Use the `CLAUDE_CODE_SUBAGENT_MODEL` env var to run subagents on cheaper models

---

## Sources

### Official Documentation
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Extend Claude Code (Features Overview)](https://code.claude.com/docs/en/features-overview)
- [CLAUDE.md / Memory](https://code.claude.com/docs/en/memory)
- [Skills](https://code.claude.com/docs/en/skills)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Hooks Reference](https://code.claude.com/docs/en/hooks)
- [MCP](https://code.claude.com/docs/en/mcp)
- [Plugins — Discover](https://code.claude.com/docs/en/discover-plugins)
- [Plugins — Create](https://code.claude.com/docs/en/plugins)
- [Settings](https://code.claude.com/docs/en/settings)

### Official Repositories
- [Anthropic Official Plugins Directory](https://github.com/anthropics/claude-plugins-official)
- [Anthropic Official Skills Repository](https://github.com/anthropics/skills)
- [Anthropic Claude Code (includes demo marketplace)](https://github.com/anthropics/claude-code)

### Community Guides
- [The Claude Code Setup That Won a Hackathon (Dev Genius)](https://blog.devgenius.io/the-claude-code-setup-that-won-a-hackathon-a75a161cd41c)
- [Everything Claude Code — Hackathon Config (GitHub)](https://github.com/affaan-m/everything-claude-code)
- [The Complete Guide to CLAUDE.md (Builder.io)](https://www.builder.io/blog/claude-md-guide)
- [Best Claude Code Plugins 2026 (Composio)](https://composio.dev/content/top-claude-code-plugins)
- [10 Must-Have Skills 2026 (Medium)](https://medium.com/@unicodeveloper/10-must-have-skills-for-claude-and-any-coding-agent-in-2026-b5451b013051)
- [Superpowers Complete Guide (pasqualepillitteri.it)](https://pasqualepillitteri.it/en/news/215/superpowers-claude-code-complete-guide)
- [A Mental Model for Claude Code (Level Up Coding)](https://levelup.gitconnected.com/a-mental-model-for-claude-code-skills-subagents-and-plugins-3dea9924bf05)
- [Claude Code Hooks: 20+ Examples (aiorg.dev)](https://aiorg.dev/blog/claude-code-hooks)

### Tools & Repositories
- [boostvolt/claude-code-lsps — LSP Plugins (22+ languages)](https://github.com/boostvolt/claude-code-lsps)
- [obra/superpowers-marketplace — Workflow Skills](https://github.com/obra/superpowers-marketplace)
- [VoltAgent/awesome-claude-code-subagents (100+ agents)](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins)
- [Claude Plugins Community Registry](https://claude-plugins.dev/)
- [Context7 MCP (Upstash)](https://github.com/upstash/context7)

### Vercel Integration
- [Vercel Agent Skills (GitHub)](https://github.com/vercel-labs/agent-skills)
- [Vercel Official MCP Documentation](https://vercel.com/docs/mcp/vercel-mcp)
- [Figma + Claude Code Bidirectional Workflow](https://www.figma.com/blog/introducing-claude-code-to-figma/)

### Component Libraries
- [Magic UI MCP Server](https://magicui.design/docs/mcp)
- [shadcn/ui MCP Server](https://ui.shadcn.com/docs/mcp)

### Skills Marketplaces
- [skills.sh — Agent Skills Directory](https://skills.sh/)
- [SkillsMP — Agent Skills Marketplace](https://skillsmp.com)
- [SkillHub — Claude Skills Marketplace](https://www.skillhub.club/)
- [Agent Skills Standard (agentskills.io)](https://agentskills.io/)
