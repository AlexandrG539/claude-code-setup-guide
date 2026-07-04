# Chapter 11: Context Management Strategy

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs, 2026-07-04 (Claude Code 2.1.201)
>
> **Previous:** [Agent Teams & Networks](10-agent-teams-networks.md) · **Next:** [Monorepos & Parallel Workflows](12-monorepo-parallel.md)

Context window is your most precious resource. Manage it actively. (Note: Sonnet 5 — the default model on most subscription plans — has a native 1M-token context window, which relaxes but does not eliminate this discipline: a lean context is still faster, cheaper, and improves adherence.)

## Budget Awareness

| Feature | Context Cost |
|---------|-------------|
| CLAUDE.md (per 200 lines) | Loads in full every request |
| Rules without `paths` | Every request |
| Rules with `paths` | Only when matching files are touched |
| Auto memory | First 200 lines / 25KB of MEMORY.md every request |
| Each MCP server | **Low by default** — tool search defers tool definitions; only names + server instructions load upfront (see [Chapter 6](06-mcp.md)) |
| Each active plugin | Shown as "Context cost" in `/plugin` details before you install |
| Skill description | ~100 tokens per skill (zero if `disable-model-invocation: true`) |
| Skill full content (invoked) | One-time when used |
| Subagent | ~Zero in your window (isolated; returns a summary) |
| Dynamic workflow | ~Zero in your window (returns one report) |
| Hook (`command`/`http` type) | Zero **unless the hook returns output** — `additionalContext` JSON (and, for a few events, stdout) enters Claude's context each firing |
| Hook (`prompt`/`agent` type) | Tokens when triggered |

## Context Optimization Rules

1. **Monitor:** `/context` visualizes usage as a grid with optimization suggestions (pass `all` for the full per-item breakdown). `/usage` shows cost and a per-skill/subagent/plugin/MCP breakdown.
2. **Compact strategically:** run `/compact` at logical boundaries (after planning, after milestones, after a debugging session) — not mid-implementation. Optionally pass focus instructions.
3. **Know what survives compaction:** the project-root CLAUDE.md is re-injected after `/compact`; nested CLAUDE.md files and conversation-only instructions are not.
4. **Use subagents for exploration:** they burn their own context and return summaries.
5. **Use `/btw` for side questions:** the answer appears in an overlay and never enters conversation history; it reuses the prompt cache, so it's nearly free. Press `f` in the overlay to fork the thread into its own session if it grows.
6. **Clear between unrelated tasks:** `/clear [name]` starts fresh (the old conversation stays in `/resume`, labeled if you passed a name).
7. **Branch instead of polluting:** `/branch` forks the conversation at this point for a different direction, preserving the original.
8. **Prefer skills over a bloated CLAUDE.md** and path-scoped rules over global ones.
9. **Set `disable-model-invocation: true`** on manual-only skills — removes their descriptions from every request.
10. **Audit plugins:** `/plugin` → Installed surfaces plugins you haven't used recently (2.1.187+) — uninstall what you don't use.
11. **Name sessions:** `/rename` so you can `/resume` later without rebuilding context.

## Compaction Prompt Template

```
/compact Retain: [current task, key decisions made, files being modified].
Completed: [what's done]. Next: [immediate next step].
```

## Checkpoints & Rewind

`Esc Esc` (on an empty prompt) or `/rewind` opens the rewind menu: restore the **code**, the **conversation**, or **both** to a previous checkpoint. This makes aggressive experiments cheap — you can always roll back. Use it instead of nursing a polluted session.

---

**Sources (official):**
- [Context windows / how Claude Code uses context](https://code.claude.com/docs/en/context-window)
- [Costs & /usage](https://code.claude.com/docs/en/costs)
- [Checkpointing](https://code.claude.com/docs/en/checkpointing)

**Next:** [Chapter 12: Monorepos & Parallel Workflows →](12-monorepo-parallel.md)
