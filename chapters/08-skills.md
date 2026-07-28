---
description: "Skills and slash commands: SKILL.md format, frontmatter reference, invocation control, arguments and dynamic context injection, bundled skills, and four ready-to-use skill templates. Read when a project has repeated procedures worth encoding as commands."
read_when:
  - "the same instructions or checklist keep being repeated in chat"
  - "a CLAUDE.md section has grown into a procedure rather than a fact"
  - "looking up bundled skills or SKILL.md frontmatter fields"
topics: [skills, slash-commands, skill-md, frontmatter, templates]
verified: 2026-07-28
claude_code_version: "2.1.220"
---

# Chapter 8: Skills & Slash Commands

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Hooks](07-hooks.md) · **Next:** [Subagents](09-subagents.md)

Skills extend what Claude can do: a `SKILL.md` file with instructions that loads on demand. Claude uses skills when relevant, or you invoke one directly with `/skill-name`.

**Custom commands are merged into skills.** `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Existing `.claude/commands/` files keep working and support the same frontmatter, but skills are the recommended form (supporting files, invocation control, subagent execution).

Claude Code skills follow the [Agent Skills open standard](https://agentskills.io), which works across multiple AI tools.

**Before creating skills**, check what your installed [plugins](05-plugins.md) already provide.

## When to create a skill

Create one when you keep pasting the same instructions/checklist/procedure into chat, or when a section of CLAUDE.md has grown into a *procedure* rather than a *fact*. Unlike CLAUDE.md content, a skill's body loads only when used.

## Skill File Structure

```
.claude/skills/
└── my-skill/
    ├── SKILL.md           # Main skill file (required)
    ├── PATTERNS.md        # Supporting reference (optional)
    ├── EXAMPLES.md        # Examples (optional)
    └── scripts/
        └── validate.sh    # Supporting scripts (optional)
```

## Frontmatter Reference (verified July 2026)

```yaml
---
name: skill-name                    # Display label; command name comes from the directory name
description: |
  One-paragraph description of when this skill should be used.
  Claude matches tasks to this description — write it as a trigger,
  not a summary.
allowed-tools: Read, Grep, Bash(git add *)   # PRE-APPROVES these tools while the skill is active
# disallowed-tools: AskUserQuestion  # REMOVES tools from the pool while the skill is active
# model: sonnet                      # Override model for this skill
# context: fork                      # Run in an isolated subagent context (in the background by default since 2.1.218)
# background: false                  # Opt a context: fork skill back into foreground execution (2.1.218+)
# agent: code-reviewer               # Which subagent type to use with context: fork
# disable-model-invocation: true     # Only YOU can invoke (manual /name); description stays out of context
# user-invocable: false              # Only CLAUDE can invoke; hidden from the / menu
# arguments: [issue, branch]         # Named arguments → $issue, $branch
---

# Skill Title

[Instructions for Claude when this skill activates]
```

Two commonly confused fields, exactly as documented:

- **`allowed-tools` grants permission, it does not restrict.** Listed tools run without prompting while the skill is active; every other tool remains callable under your normal permission rules. (For project skills it takes effect only after you trust the workspace.)
- **`disallowed-tools` restricts**: listed tools are removed from Claude's pool while the skill is active; the restriction clears on your next message.

Invocation control matrix:

| Setting | You can invoke | Claude can invoke | Context behavior |
|---------|----------------|-------------------|------------------|
| (default) | Yes | Yes | Description always in context; body loads when used |
| `disable-model-invocation: true` | Yes | No | Description NOT in context — saves tokens on every request |
| `user-invocable: false` | No | Yes | Description always in context |

Use `disable-model-invocation: true` for workflows with side effects you want to time yourself (`/deploy`, `/commit`). Use `user-invocable: false` for background knowledge that isn't a meaningful user action.

Boolean frontmatter fields accept `yes`/`no`/`on`/`off`/`1`/`0` (case-insensitive) alongside `true`/`false` since 2.1.218.

## Arguments & Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | Everything typed after the command. If absent from the body, arguments are appended as `ARGUMENTS: <value>` |
| `$ARGUMENTS[N]` / `$N` | Positional argument by 0-based index (`$0`, `$1`, …). Shell-style quoting: `/my-skill "hello world" second` |
| `$name` | Named argument declared in the `arguments` frontmatter list |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md — reference bundled scripts regardless of cwd |
| `${CLAUDE_PROJECT_DIR}` | Project root (v2.1.196+; also works inside `allowed-tools` rules) |
| `${CLAUDE_SESSION_ID}` | Current session ID |

### Dynamic context injection

A line like `` !`git diff HEAD` `` in the skill body is executed **before** Claude sees the content, and replaced with its output — the skill arrives with the current diff already inlined.

### Skill stacking (v2.1.199+)

`/code-review /fix-issue 123` loads both skills and passes `123` as `$ARGUMENTS` to each. Up to six skills can be chained at the start of one message.

## Bundled Skills & Commands (built into Claude Code)

| Command | Kind | What It Does |
|---------|------|-------------|
| `/code-review [target] [low\|medium\|high\|xhigh\|max\|ultra] [--fix] [--comment]` | Skill | Review the current diff (or a target) for correctness bugs and cleanups; `--fix` applies findings; `ultra` runs a multi-agent cloud review. Runs as a background subagent since 2.1.218, so the review doesn't fill your conversation |
| `/simplify` | Skill | Cleanup-only review (reuse, simplification, efficiency) that applies fixes — since 2.1.154 it does **not** hunt for bugs |
| `/review [PR]` | Built-in command | Review a GitHub pull request (same engine as `/code-review`) |
| `/security-review` | Built-in command | Deeper read-only security pass on pending changes |
| `/verify` | Skill | Exercise a change end-to-end to confirm it works |
| `/debug` | Skill | Enable debug logging and troubleshoot session issues |
| `/loop [interval] [prompt]` | Skill | Run a prompt repeatedly (self-paced if no interval) |
| `/deep-research <question>` | Bundled workflow | Multi-agent research workflow (see [Chapter 10](10-agent-teams-networks.md)) — manual invocation only since 2.1.218 |
| `/batch` | Skill | Large-scale parallel changes across worktrees |
| `/fewer-permission-prompts` | Skill | Analyze transcripts and propose a permission allowlist |
| `/init` | Built-in command | Generate or refine CLAUDE.md |

(Not exhaustive — other bundled skills include `/run`, `/dataviz`, and `/claude-api`, and availability depends on plan/platform. Type `/` to see what you have; the [commands reference](https://code.claude.com/docs/en/commands) is the authoritative list.)

Note: since 2.1.215 Claude no longer runs `/verify` or `/code-review` on its own — invoke them explicitly when you want them (same for `/deep-research` since 2.1.218).

## Installing Community Skills

The `skills.sh` ecosystem installs skills from GitHub repos:

```bash
# Install all skills from a repository
npx skills add <owner/repo>

# Install a specific skill
npx skills add "<owner/repo>" --skill "<skill-name>" --yes
```

Notes that keep tripping people up:

- Use the `--skill` flag to pick a single skill when installing with `skills add`.
- For Claude Code, the skills.sh CLI installs to `.claude/skills/` (project) or `~/.claude/skills/` (with `-g`), symlinked to a canonical copy; `.agents/skills/` is the install path for other agents (Cursor, Codex, Amp, "universal") — verify where files landed.
- Claude Code auto-discovers skills in `.claude/skills/`; check the repo's README for its intended install path.

Community skill sources worth knowing: [anthropics/skills](https://github.com/anthropics/skills) (official skill repo — `frontend-design`, `skill-creator`, `mcp-builder`, document skills like `pdf`/`docx`/`xlsx`), [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) (React/Next.js best practices, `web-design-guidelines`), [skills.sh](https://skills.sh/) directory.

## Essential Custom Skill Example: Verification Loop

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
Run the linter across all modified files.

## Phase 4: Test Suite
Run the test suite with coverage. Target: 80%+ coverage on changed files.

## Phase 5: Security Scan
Scan for hardcoded secrets, leftover debug statements, exposed error details.

## Phase 6: Diff Review
Run `git diff` — check for unintended changes, large files, merge conflict markers.

## Report Format

| Phase | Status | Details |
|-------|--------|---------|
| Build | PASS/FAIL | ... |
| Types | PASS/FAIL | ... |
| Lint  | PASS/FAIL | ... |
| Tests | PASS/FAIL | ... |
| Security | PASS/FAIL | ... |
| Diff  | PASS/FAIL | ... |

**Overall: READY / NOT READY for PR**
```

Note: Claude Code now bundles `/verify` and `/code-review`, which cover much of this — create custom variants only when you need project-specific phases.

## More Recommended Custom Skills

### `/plan-feature` (planning without implementing)

```yaml
---
description: Create a detailed implementation plan before coding
allowed-tools: Read, Grep, Glob
disable-model-invocation: true
---

Create a detailed implementation plan for: $ARGUMENTS

1. Explore the codebase to understand current architecture
2. Identify all files that need to change
3. List dependencies and risks
4. Produce a numbered step-by-step plan with exact file paths
5. Do NOT implement — only plan
```

(Also consider built-in **plan mode** — `Shift+Tab` or `/plan` — which enforces read-only exploration at the permission level. See [Chapter 4](04-permissions.md#plan-mode--use-it-deliberately).)

### `/tdd`

```yaml
---
description: Implement a feature using test-driven development
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
disable-model-invocation: true
---

Implement using TDD: $ARGUMENTS

1. Write a failing test first
2. Run it — confirm it fails for the right reason
3. Write the minimal code to make it pass
4. Run it — confirm it passes
5. Refactor if needed (keep tests green)
6. Repeat for the next behavior
7. Run full test suite at the end
```

### `/new-feature`

```yaml
---
description: Create a feature branch and prepare for implementation
allowed-tools: Bash(git fetch*), Bash(git checkout *), Bash(git switch *), Bash(git pull*)
disable-model-invocation: true
---

Create a new feature branch for: $ARGUMENTS

1. Check that the working tree is clean — if dirty, stop and warn
2. Fetch latest from remote
3. Checkout the development branch and pull latest changes
4. Create and switch to feature branch: feature/<slugified-name>
5. Do NOT start implementing — just set up the branch.
```

## Skills vs Other Features

| If you need... | Use... |
|----------------|--------|
| "Always do X" rules | CLAUDE.md or [rules](03-rules.md) |
| Reference material Claude needs sometimes | Skill |
| Workflow triggered with `/<name>` | Skill |
| Isolated worker with limited tools | [Subagent](09-subagents.md) |
| Orchestrating many agents from a script | [Dynamic workflow](10-agent-teams-networks.md) |
| External service connection | [MCP server](06-mcp.md) |
| Deterministic automation | [Hook](07-hooks.md) |
| Bundled set of skills + agents + hooks | [Plugin](05-plugins.md) |

## Context Efficiency

- **Startup cost:** only name + description (~100 tokens per skill).
- **On-demand:** full SKILL.md loads only when invoked or matched.
- **Supporting files:** loaded only when needed.
- Set `disable-model-invocation: true` on manual-only skills — removes even the description from context.
- Changes to skills on disk (in `~/.claude/skills/`, project `.claude/skills/`, and `--add-dir` directories) are picked up **automatically within the session** (live change detection). `/reload-skills` (v2.1.152+) still exists; a restart is only needed when you create a top-level skills directory that didn't exist at session start.

---

**Sources (official):**
- [Skills](https://code.claude.com/docs/en/skills)
- [Commands reference (bundled skills)](https://code.claude.com/docs/en/commands)

**Next:** [Chapter 9: Subagents →](09-subagents.md)
