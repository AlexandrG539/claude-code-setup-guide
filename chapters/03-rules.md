# Chapter 3: Rules — Modular Guidelines

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs, July 2026 (Claude Code 2.1.200)
>
> **Previous:** [CLAUDE.md & Memory](02-claude-md-memory.md) · **Next:** [Permissions](04-permissions.md)

Rules are markdown files in `.claude/rules/` that organize guidelines by topic. Rules **without** `paths` frontmatter load at launch with the same priority as `.claude/CLAUDE.md`. Rules **with** `paths` frontmatter load only when Claude works with matching files — this is the main tool for keeping always-on context small.

All `.md` files under `.claude/rules/` are discovered recursively, so you can organize into subdirectories like `frontend/` or `backend/`.

## When to Use Rules vs CLAUDE.md vs Skills

| Use CLAUDE.md for | Use Rules for | Use Skills for |
|-------------------|---------------|----------------|
| Project overview, tech stack, key commands | Topic-specific guidelines | Multi-step procedures |
| Facts needed every session (<200 lines) | Path-scoped conventions | Reference material needed occasionally |
| Architecture summary | Team-agreed standards per domain | Workflows triggered with `/<name>` |

## Path-Scoped Rules

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

This rule only loads when Claude reads files matching those paths (not on every tool use). Glob patterns support brace expansion:

```yaml
paths:
  - "src/**/*.{ts,tsx}"
  - "tests/**/*.test.ts"
```

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root |

## Sharing Rules Across Projects

Rules support **symlinks** (circular symlinks are detected and handled):

```bash
# Share a rules directory across projects
ln -s ~/shared-claude-rules .claude/rules/shared

# Share a single rule file
ln -s ~/company-standards/security.md .claude/rules/security.md
```

User-level rules at `~/.claude/rules/` apply to every project automatically and load *before* project rules, giving project rules higher priority.

## Recommended Rule Files

### `.claude/rules/coding-style.md`

```markdown
# Coding Style

- Prefer immutability — use const/readonly/final where possible
- Early returns over nested conditionals
- Max function length: 50 lines — split if larger
- Max file length: 300 lines — split if larger
- No magic numbers — use named constants
- Group imports: stdlib > external > internal > types
- Named exports over default exports (easier to refactor/search)
```

### `.claude/rules/testing.md`

```markdown
# Testing Rules

- Test behavior, not implementation details
- Arrange-Act-Assert pattern for all tests
- Descriptive names: "should [expected] when [condition]"
- Mock at boundaries (network, database, filesystem) not internal modules
- Never test private/internal functions directly
- Use factories/fixtures for test data — not inline literals
- Colocate tests with source: `foo.ts` > `foo.test.ts`
- Every new feature/endpoint needs at least one test
- IMPORTANT: Run the specific test file, not the full suite
```

### `.claude/rules/security.md`

```markdown
# Security Rules

- Never log sensitive data (passwords, tokens, PII)
- Always validate and sanitize user input on the server
- Use parameterized queries — never string concatenation for SQL
- Store secrets in environment variables, never in code
- Never commit .env, credentials, or API keys
- Hash passwords with modern algorithms (argon2/bcrypt) — never MD5/SHA
- Rate limit all public endpoints
- CORS: whitelist specific origins, never wildcard in production
- Never expose stack traces or internal error details to clients
```

### `.claude/rules/git-workflow.md`

```markdown
# Git Workflow

- Conventional commits: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, perf, test, chore, ci
- Imperative mood: "add feature" not "added feature"
- Keep commits atomic — one logical change per commit
- Never force-push to main/master
- Feature branches for all changes
```

### `.claude/rules/agent-delegation.md`

```markdown
# Agent Delegation Rules

When to delegate to subagents:
- Security review: ALWAYS delegate security-sensitive changes to the security-reviewer agent
- Code review: Delegate completed features to code-reviewer before PR
- Build errors: Delegate compilation failures to build-fixer agent
- Planning: Use planner agent for features touching 3+ files

When NOT to delegate:
- Simple single-file edits
- Typo fixes
- Configuration changes
```

Remember: rules shape behavior but don't enforce it. Pair a "never force-push" rule with a [hook](07-hooks.md) or a [permission deny rule](04-permissions.md) for actual enforcement.

---

**Sources (official):**
- [Memory — organize rules with .claude/rules/](https://code.claude.com/docs/en/memory#organize-rules-with-claude%2Frules%2F)

**Next:** [Chapter 4: Permissions →](04-permissions.md)
