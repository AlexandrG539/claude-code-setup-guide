---
description: "Writing CLAUDE.md project memory: content rules, copy-paste templates (root, global, local), imports, AGENTS.md compatibility, auto memory, and /init. Read when creating or revising a project's CLAUDE.md."
read_when:
  - "always — core chapter, needed for every project's initial setup"
topics: [claude-md, memory, agents-md, auto-memory, templates, init]
verified: 2026-07-28
claude_code_version: "2.1.220"
---

# Chapter 2: CLAUDE.md & Memory

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Architecture](01-architecture.md) · **Next:** [Rules](03-rules.md)

CLAUDE.md is loaded into every request. It defines what Claude always knows about your project. Alongside it, **auto memory** lets Claude accumulate its own notes per repository.

## Guidelines for CLAUDE.md

- **Target under 200 lines.** Official docs say "target under 200 lines per CLAUDE.md file" — longer files consume more context and reduce adherence. Shorter is better: for each line, keep only what earns its place.
- For each line, ask: *"Would removing this cause Claude to make mistakes?"* If not, cut it.
- Move procedures and reference material to [skills](08-skills.md) (on-demand loading) or [path-scoped rules](03-rules.md).
- Use imperative language: "Use X" and "Never do Y" — not "It would be nice if..."
- Write instructions concrete enough to verify: "Use 2-space indentation", not "Format code properly".
- State what NOT to do — prohibitions are more valuable than suggestions.
- **CLAUDE.md is context, not enforcement.** If something must happen at a specific point (format after every edit, block commits to main), use a [hook](07-hooks.md) — Claude cannot "forget" a hook.
- Use `@path/to/file` import syntax to reference other files without duplicating content. Note: imports still load at launch, so they organize content but don't save context.
- **HTML comments are stripped** before CLAUDE.md is injected. Use `<!-- maintainer notes -->` for human-only annotations that don't cost tokens. Comments inside code blocks are preserved.
- **Compaction behavior:** the project-root CLAUDE.md is re-injected after `/compact`. Nested CLAUDE.md files reload only when Claude next reads a file in that subdirectory. Conversation-only instructions do not survive compaction — promote important ones to CLAUDE.md.

### When to add to CLAUDE.md (official heuristics)

- Claude makes the same mistake a second time
- A code review catches something Claude should have known about this codebase
- You type the same correction you typed last session
- A new teammate would need the same context to be productive

## Template: Root CLAUDE.md

```markdown
# Project: [PROJECT NAME]

[One-line description of the project and its purpose.]

## Tech Stack

- [Language/Framework]: [version]
- [Database]: [type]
- [Testing]: [framework]
- [Package Manager]: [name]

## Project Structure

[directory tree showing key folders and their purposes]

## Commands

- `[command]` — [what it does]
- `[test command]` — [run specific test file]
- `[lint command]` — [run linter]
- `[typecheck command]` — [run type checker]

## Code Conventions

- [Rule about types/typing]
- [Rule about naming]
- [Rule about imports]
- [Rule about error handling pattern]

## Architecture Rules

- [Key architectural pattern]
- [Data flow direction]
- [API response format]

## Git Conventions

- [Commit format (e.g., conventional commits)]
- Never commit [secrets, env files, etc.]
- Never force-push to [protected branches]

## Security

- Never hardcode secrets — use environment variables
- Validate all user input server-side
- Never log PII or tokens
```

## Template: Global ~/.claude/CLAUDE.md

```markdown
# Personal Preferences

## Communication
- Be direct and concise
- If unsure, ask rather than guess
- Only add comments for "why", never for "what"

## Code Style
- Prefer early returns over deep nesting
- Don't add docstrings/comments to code you didn't change

## Safety
- Never run destructive commands without asking
- Never modify .env files without approval
- Show diffs before committing
```

## Template: CLAUDE.local.md (gitignored, personal)

```markdown
# Local Development Notes

## My Environment
- Database on localhost:[port]
- Staging URL: [url]

## Personal Reminders
- [Module X] is being refactored — check with [person] before changing
```

Add `CLAUDE.local.md` to `.gitignore`. If you work across multiple git worktrees, note that a gitignored `CLAUDE.local.md` exists only in the worktree where you created it — import a home-directory file instead: `@~/.claude/my-project-instructions.md`.

## Import Syntax

```markdown
See @README.md for project overview.
See @package.json for available commands.
- git workflow: @docs/git-instructions.md
```

- Relative paths resolve relative to the file containing the import.
- Imports can nest up to 4 hops deep.
- Paths inside backticks or code blocks are **not** imported — wrap a path in backticks to mention it literally.
- The first time Claude Code sees imports pointing outside the project, it shows an approval dialog.

## AGENTS.md — Cross-Tool Compatibility

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repo uses `AGENTS.md` for other coding agents (Cursor, Aider, OpenCode, etc.), two official patterns:

**Import (lets you add Claude-specific content):**

```markdown
@AGENTS.md

## Claude Code

Claude-specific overrides go here.
```

**Symlink (when nothing Claude-specific is needed):**

```bash
ln -s AGENTS.md CLAUDE.md
```

On Windows, symlinks need Administrator/Developer Mode — use the import instead.

`/init` in a repo that already has `AGENTS.md` reads it and incorporates the relevant parts. It also reads `.cursorrules`, `.devin/rules/`, and `.windsurfrules`.

## `/init` — Project Setup

For a new or unfamiliar project, prefer `/init` over hand-writing CLAUDE.md. The interactive multi-phase flow (behind an env var) explores the codebase with a subagent, asks follow-up questions, and proposes CLAUDE.md, skills, and hooks for review:

```bash
CLAUDE_CODE_NEW_INIT=1 claude
> /init
```

If a `CLAUDE.md` already exists, `/init` suggests improvements rather than overwriting it.

## Auto Memory

Alongside the CLAUDE.md you write, Claude writes notes for itself across sessions (requires v2.1.59+, **on by default**).

- **Location:** machine-local at `~/.claude/projects/<project>/memory/`, where `<project>` is derived from the git repo — all worktrees and subdirectories of one repo share one memory directory. Outside a git repo, the project root is used instead.
- **What's loaded at session start:** the first 200 lines / 25KB of `MEMORY.md` (an index Claude maintains). Topic files (`debugging.md`, `api-conventions.md`, …) load on demand.
- **What Claude saves:** build commands it figured out, debugging insights, code-style preferences observed from your corrections, workflow habits. It decides what's worth keeping.
- **Audit:** run `/memory` to browse all loaded memory files, open them in your editor, or toggle the feature. Everything is plain markdown you can edit or delete (memory file frontmatter carries an ISO `modified` timestamp since 2.1.214).
- **Disable:** `"autoMemoryEnabled": false` in settings, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- **Custom location:** `autoMemoryDirectory` setting (absolute or `~/` path). When set in project settings, it's honored only after you accept the workspace trust dialog.

When you ask Claude to "remember" something mid-session, it saves to auto memory. To put it in CLAUDE.md instead, say "add this to CLAUDE.md".

CLAUDE.md is what *you* tell Claude. Auto memory is what *Claude tells itself*. Both load into every session.

**Subagent memory:** subagents can have their own persistent memory directories via the `memory:` frontmatter field — see [Chapter 9](09-subagents.md#persistent-memory).

## Managed / org-wide CLAUDE.md

Organizations can deploy a CLAUDE.md at the managed policy location (cannot be excluded by users), or inline it via the `claudeMd` key in `managed-settings.json`. Use managed *settings* for enforcement (deny rules, sandbox) and managed *CLAUDE.md* for behavioral guidance.

## Troubleshooting

- **Claude ignores instructions:** run `/memory` to confirm the file is actually loaded; make instructions more specific; remove conflicts between files (Claude may pick one arbitrarily); if it must always happen, make it a hook.
- **File too long (>200 lines):** move topic content to path-scoped rules or skills.
- **Instruction "lost" after `/compact`:** it was conversation-only or in a nested CLAUDE.md — see compaction note above.

---

**Sources (official):**
- [Memory (CLAUDE.md, rules, auto memory)](https://code.claude.com/docs/en/memory)

**Next:** [Chapter 3: Rules →](03-rules.md)
