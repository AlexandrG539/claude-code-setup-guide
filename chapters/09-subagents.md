# Chapter 9: Subagents — Isolated Workers

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs, 2026-07-04 (Claude Code 2.1.201)
>
> **Previous:** [Skills & Commands](08-skills.md) · **Next:** [Agent Teams & Networks](10-agent-teams-networks.md)

Subagents run in their own context window with a custom system prompt and their own tool/permission constraints. Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again — the subagent does that work in its own context and returns only the summary.

**As of v2.1.198, subagents run in the background by default** — your session stays responsive while they work, and Claude collects results when they finish. Stop all running background subagents with `Ctrl+X Ctrl+K`.

## Built-in Subagents

Claude Code ships built-in subagents it uses automatically — notably **Explore** (fast read-only codebase search) and **Plan** (research during plan mode). A user/project subagent with the same name overrides the built-in (e.g., define your own `Explore` with `model: haiku` to pin exploration to a cheaper model).

## Subagent File Format

Place in `.claude/agents/` (project) or `~/.claude/agents/` (user); both are scanned recursively. As of v2.1.198 the `/agents` wizard is removed — ask Claude to write the file or edit it directly.

```yaml
---
name: agent-name
description: |
  When to use this agent. Claude matches tasks to this description.
  Be specific so Claude delegates correctly.
model: sonnet            # sonnet | opus | haiku | fable | inherit, or a full model ID
tools: Read, Grep, Glob, Bash     # allowlist; inherits all tools if omitted
# disallowedTools: WebSearch      # denylist alternative
# skills:                # preload FULL skill content into the subagent at startup
#   - api-conventions
# memory: project        # persistent cross-session memory: user | project | local
# permissionMode: default  # default (alias: manual, v2.1.200+) | acceptEdits | auto | dontAsk | bypassPermissions | plan
# background: true       # always run in background (default: Claude decides; background since 2.1.198)
# isolation: worktree    # run in a temporary git worktree, auto-cleaned if unchanged
# maxTurns: 30           # cap the number of turns
# effort: low            # reasoning effort override
# mcpServers: [...]      # extra MCP servers for this subagent
# hooks: {...}           # subagent-scoped hooks
---

[System prompt for the subagent — it receives ONLY this plus basic env details,
not the full Claude Code system prompt.]

## Your Role
...

## Process
1. ...

## Output Format
...
```

Field notes (all verified against official docs):

- The field is **`permissionMode`** (camelCase). If the parent runs `bypassPermissions` or `acceptEdits`, the parent mode takes precedence; under parent `auto` mode the frontmatter is ignored too.
- `tools`/`disallowedTools` accept MCP patterns: `mcp__github`, `mcp__github__*`, and in `disallowedTools` also `mcp__*`.
- `skills:` injects full skill content at startup; the subagent can still invoke other skills via the Skill tool. You cannot preload skills that set `disable-model-invocation: true`.
- Plugin-provided subagents ignore `hooks`, `mcpServers`, and `permissionMode` for security.
- Some tools are never available inside subagents (they depend on session UI/state), e.g. `AskUserQuestion` mid-run and `ExitPlanMode` unless `permissionMode: plan`.

## Nested Subagents

A subagent whose `tools` includes `Agent` can spawn its own subagents (nesting up to 5 levels, since 2.1.172). For a main-thread agent launched with `claude --agent`, `Agent(worker, researcher)` syntax allowlists which types it may spawn; inside a subagent definition the type list is ignored — listing `Agent` simply enables nesting.

## Invocation Methods

| Method | Example |
|--------|---------|
| Natural language | "Use the security-reviewer agent to check this code" |
| @-mention | `@"code-reviewer (agent)"` |
| CLI (as main session agent) | `claude --agent code-reviewer` |
| Settings default | `"agent": "code-reviewer"` in settings.json |
| Inline JSON at launch | `claude --agents '{"reviewer": {...}}'` |
| Disable one | `"deny": ["Agent(Explore)"]` in permissions |

## Model Selection & Cost Optimization

Model resolution order for a subagent:

1. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable (highest)
2. Per-invocation model parameter (Claude's choice when delegating)
3. The definition's `model:` frontmatter
4. Otherwise inherits the main conversation's model

```bash
export CLAUDE_CODE_SUBAGENT_MODEL=haiku   # run all subagents on a cheaper model
```

This remains one of the most impactful cost optimizations: main session on a strong model for reasoning, subagents on Sonnet/Haiku for focused tasks.

## Persistent Memory

The `memory` field gives a subagent a directory that survives across conversations. Values are the keywords `user` | `project` | `local` — **not a path** (a directory path here is a common mistake from older guides):

| Value | Directory | Shared with |
|-------|-----------|-------------|
| `user` | `~/.claude/agent-memory/<name>/` | All projects on your machine |
| `project` | `.claude/agent-memory/<name>/` | Team (committed to git) |
| `local` | `.claude/agent-memory-local/<name>/` | Just you on this machine (gitignore it) |

When enabled: the subagent's prompt includes memory instructions plus the first 200 lines / 25KB of its `MEMORY.md`, and Read/Write/Edit are auto-enabled so it can manage its memory files.

## Worktree Isolation

```yaml
---
name: experimental-refactor
isolation: worktree
---
```

The agent gets an isolated copy of the repository in a temporary git worktree (branched from your default branch). No changes → worktree cleaned up automatically; worktrees kept because they contain changes are swept later per `cleanupPeriodDays`. Use for parallel file-mutating agents that would otherwise conflict.

## Recommended Subagents

### Planner

```yaml
---
name: planner
description: |
  Expert planning specialist. Use when implementing features that touch
  3+ files, require architecture decisions, or need refactoring strategy.
model: opus
tools: Read, Grep, Glob
memory: project
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
A numbered plan with exact file paths, what to change, order, verification
steps between phases, and risks.

## Quality Standards
- Be specific: exact file paths and function names
- Minimize changes — don't refactor beyond scope
```

### Code Reviewer

```yaml
---
name: code-reviewer
description: |
  Senior code review specialist. Use after completing features or before
  PRs. Reviews for quality, security, performance, and best practices.
model: sonnet
tools: Read, Grep, Glob, Bash
memory: project
---

You are a senior code reviewer.

## Process
1. Run `git diff` to see all changes
2. Read each modified file in full
3. Check against the categories below
4. Produce a structured report

## Review Categories
### Security (Critical)
- Hardcoded credentials, injection, XSS, missing validation, authz bypasses
### Code Quality (High)
- Long functions/files, deep nesting, missing error handling, debug statements, missing tests
### Performance (Medium)
- N+1 queries, unnecessary re-renders, unbounded lists, missing memoization

## Verdict
- **Approve** / **Warning** (medium only) / **Block** (critical or high)
```

Note: for diff review the bundled `/code-review` skill is often enough — create a custom reviewer when you need project-specific criteria or persistent memory.

### Build Error Resolver

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
2. Parse all error output
3. Fix the root cause (not symptoms)
4. Re-run to verify (max 3 iterations)

## Rules
- Never suppress errors with @ts-ignore or eslint-disable
- Never change public API signatures unless the error requires it
```

## Pre-Built Agent Collections

[VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) maintains 100+ pre-built agents. Review any third-party agent definition before adopting it — agents run with your permissions.

## Troubleshooting

- **Subagent not being used:** make the `description` more specific; add an [agent-delegation rule](03-rules.md); invoke explicitly by name.
- **Same name in multiple `.claude/agents/` dirs (monorepo):** the definition closest to the working directory wins (2.1.178+).
- **Need to watch/stop background subagents:** `/tasks` shows running work; `Ctrl+X Ctrl+K` stops all background subagents.

---

**Sources (official):**
- [Subagents](https://code.claude.com/docs/en/sub-agents)

**Next:** [Chapter 10: Agent Teams & Multi-Agent Networks →](10-agent-teams-networks.md)
