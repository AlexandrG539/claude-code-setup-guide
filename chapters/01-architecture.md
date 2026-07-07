---
description: "Claude Code extension layers, global vs project directory layout, loading order, and settings precedence. Read first — every other chapter builds on this file map."
read_when:
  - "always — core chapter, read before configuring anything"
topics: [architecture, file-layout, extension-layers, settings-precedence, context-costs]
verified: 2026-07-07
claude_code_version: "2.1.202"
---

# Chapter 1: Architecture Overview & File Layout

> Part of the [Claude Code Configuration Guide](../README.md) · **Next:** [Chapter 2: CLAUDE.md & Memory](02-claude-md-memory.md)

Claude Code has these extension layers that plug into different parts of the agentic loop:

| Layer | What It Does | When It Loads | Context Cost |
|-------|-------------|---------------|--------------|
| **CLAUDE.md** | Persistent project context and instructions | Session start (always) | Every request |
| **Rules** | Modular guidelines, optionally path-scoped | Session start (always) | Every request (path-scoped rules only when matched) |
| **Auto memory** | Notes Claude writes for itself per repository | Session start (first 200 lines / 25KB of MEMORY.md) | Every request |
| **Plugins** | Packaged bundles of skills, hooks, agents, MCP and LSP servers | Session start | Varies (visible as "Context cost" in `/plugin`) |
| **Skills** (merged with commands) | On-demand knowledge and invocable `/workflows` | Description at start; full content when used | Low until invoked |
| **Subagents** | Isolated workers with separate context windows | When spawned (background by default since 2.1.198) | Zero (isolated) |
| **Agent teams** | Multiple coordinating Claude Code sessions (experimental) | When teammates are spawned | Zero in lead context, but each teammate is a full session |
| **Dynamic workflows** | Scripts that orchestrate dozens–hundreds of subagents | When triggered (`ultracode`, saved workflow) | Zero (results return as one report) |
| **Hooks** | Deterministic shell scripts (or prompt/agent/http/mcp_tool) on lifecycle events | On trigger | Zero (external) |
| **MCP Servers** | Connections to external services and tools | Session start, but tool definitions are **deferred by default** (tool search) | Low by default; higher with `alwaysLoad` or `ENABLE_TOOL_SEARCH=false` |

**Key principle:** CLAUDE.md and rules are *always-on* context. Skills, subagents, and workflows are *on-demand*. Hooks run *outside* the AI loop entirely. Design your setup to minimize always-on context and maximize on-demand loading.

**Commands and skills are merged.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Skills support more features (supporting files, invocation control, subagent execution), so prefer skills for new work. See [Chapter 8](08-skills.md).

---

## File System Layout

### Global Configuration (all projects)

```
~/.claude/
├── CLAUDE.md                 # Personal global preferences
├── settings.json             # Global hooks, permissions, env, model
├── commands/                 # Global slash commands (legacy location, still works)
├── skills/                   # Global skills
│   └── my-skill/
│       └── SKILL.md
├── agents/                   # Global subagents (scanned recursively)
├── rules/                    # Global rules (apply to all projects)
├── workflows/                # Saved dynamic workflows (personal)
├── agent-memory/<agent>/     # Subagent memory with `memory: user`
├── projects/<project>/memory/  # Auto memory (per repository, machine-local)
└── teams/ , tasks/           # Agent-team runtime state (auto-managed)
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
│   ├── commands/             # Project slash commands (legacy location, still works)
│   ├── agents/               # Subagent definitions (scanned recursively)
│   ├── skills/               # Project skills
│   │   └── my-skill/
│   │       ├── SKILL.md
│   │       └── supporting-files...
│   ├── rules/                # Project rules, optionally path-scoped
│   ├── workflows/            # Saved dynamic workflows (shared with team)
│   ├── agent-memory/<agent>/       # Subagent memory `memory: project` (committed)
│   └── agent-memory-local/<agent>/ # Subagent memory `memory: local` (gitignore it)
├── .mcp.json                 # Project-scoped MCP servers (committed)
```

### Monorepo Structure (hierarchical CLAUDE.md)

```
monorepo/
├── CLAUDE.md                 # Root: shared rules (always loaded)
├── .claude/                  # Shared config
├── apps/
│   ├── frontend/
│   │   └── CLAUDE.md         # Frontend-only rules (loads on demand in this dir)
│   └── backend/
│       └── CLAUDE.md         # Backend-only rules (loads on demand in this dir)
└── packages/
    └── shared/
        └── CLAUDE.md         # Shared package rules (loads on demand in this dir)
```

**How loading works:** Claude reads CLAUDE.md files by walking up the directory tree from the working directory (those load in full at launch, ordered root → cwd, so closer files are read last). CLAUDE.md files in *subdirectories below* the working directory load on demand, when Claude reads files in those directories. This means backend rules never pollute frontend context and vice versa. See [Chapter 12](12-monorepo-parallel.md) for `claudeMdExcludes` and other monorepo tools.

### Loading Order and Precedence

Memory files are concatenated (broadest scope first, most specific last), not overridden:

| Scope | Location | Purpose |
|-------|----------|---------|
| Managed policy | `/etc/claude-code/CLAUDE.md` (Linux/WSL), `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | Org-wide (admin; cannot be excluded) |
| User global | `~/.claude/CLAUDE.md` + `~/.claude/rules/*.md` | Personal defaults (all projects) |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` + `./.claude/rules/*.md` | Team-shared (committed) |
| Project local | `./CLAUDE.local.md` | Personal project overrides (gitignored) |

For **settings** (permissions, hooks, env), precedence is: managed settings → CLI arguments → `.claude/settings.local.json` → `.claude/settings.json` → `~/.claude/settings.json`. A deny rule at any level cannot be overridden by an allow at another level.

---

**Sources (official):**
- [Features overview](https://code.claude.com/docs/en/features-overview)
- [Memory](https://code.claude.com/docs/en/memory)
- [Settings](https://code.claude.com/docs/en/settings)

**Next:** [Chapter 2: CLAUDE.md & Memory →](02-claude-md-memory.md)
