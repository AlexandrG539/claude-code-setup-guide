---
description: "Project documentation for AI agents: layered structure (CLAUDE.md → rules → skills → docs/ with a router index), on-demand navigation via read-when triggers, and an AI maintenance workflow that keeps docs in sync with code — content rules, freshness stamps, validation hooks, an /update-docs skill, and scheduled doc-sync agents. Read when project knowledge outgrows CLAUDE.md or docs drift from the code."
read_when:
  - "the project needs documentation that agents can find and load on demand"
  - "project knowledge outgrows CLAUDE.md (architecture, domain, status docs)"
  - "docs have drifted from the code or tech stack, or a doc-maintenance workflow is being set up"
topics: [documentation, docs-structure, progressive-disclosure, navigation, drift, doc-sync, freshness, maintenance]
verified: 2026-07-15
claude_code_version: "2.1.202"
---

# Chapter 16: Project Documentation for Agents

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Reference](15-reference.md)

Most projects need documentation beyond CLAUDE.md — architecture decisions, domain knowledge, development status — that agents must find on demand without loading it all into context. This chapter gives one default structure, one navigation pattern, and a maintenance workflow that keeps docs in sync with the code. The core failure mode it defends against is **drift**: a doc that contradicts the code is worse than no doc, because agents trust it.

Two principles drive everything below (both from official guidance):

1. **Split by relevance frequency, not by topic.** Always-relevant facts load every session; everything else loads on demand.
2. **Document only what the code can't say.** Anything Claude can re-derive from the codebase (directory layouts, dependency lists, code-level architecture) is a drift bomb — it duplicates a source of truth that will move without it.

## Where Each Kind of Knowledge Lives

| Knowledge | Home | Loaded | See |
|-----------|------|--------|-----|
| Facts every task needs (stack, commands, conventions) | Root `CLAUDE.md`, <200 lines | Every session | [Ch. 2](02-claude-md-memory.md) |
| Area-specific conventions | Subdirectory `CLAUDE.md` / path-scoped rules | When files in that area are read | [Ch. 3](03-rules.md), [Ch. 12](12-monorepo-parallel.md) |
| Procedures (deploy, release, review) | Skills | When invoked or matched | [Ch. 8](08-skills.md) |
| Long-form knowledge: architecture, domain, integrations, status | `docs/` with a router index | When the task matches a read-when trigger | This chapter |

**Default:** don't create `docs/` until you have knowledge that fails all three earlier homes — too long for CLAUDE.md, not tied to one directory, not a procedure. A small project is often fully served by CLAUDE.md plus one or two skills. **Escape hatch:** if the repo already has human-oriented docs, don't move them — add the router and frontmatter described below on top.

The official relocation signal for the CLAUDE.md → skill boundary: a CLAUDE.md section that has grown into a *procedure* rather than a *fact* (roughly 30+ lines of steps) becomes a skill. The CLAUDE.md → docs boundary: a *fact* that needs more than a few lines of explanation becomes a doc, with a one-line pointer left behind.

## What Belongs in Agent Docs — and What Never Does

Write down only what is **not derivable from the code**:

| Include | Exclude (agents re-derive these) |
|---------|----------------------------------|
| Why decisions were made (rationale, rejected alternatives) | Directory layouts, file listings |
| Pitfalls and non-obvious constraints ("X looks unused but the cron job needs it") | Dependency lists (manifests are the source of truth) |
| Domain knowledge not visible in code (business rules, external-system quirks) | Code-level architecture summaries readable from the code |
| Non-default conventions and their reasons | API signatures (generate or link instead) |
| Project stage, goals, roadmap — things only humans know | Anything that changes weekly without a maintenance mechanism |

Since v2.1.206, `/doctor` applies exactly this split to a checked-in CLAUDE.md: it proposes trimming content Claude can derive from the codebase while keeping pitfalls, rationale, and non-default conventions. Use it after `/init` and periodically.

**Time-sensitive content:** structure evolving topics as a `## Current method` section plus a collapsed `## Old patterns` section carrying deprecation dates (e.g. a `<details>` block labeled "Legacy v1 API (deprecated 2025-08)"). History survives without staling the main content, and an agent skimming the doc cannot mistake the old way for the current one.

## Structure: One Router, Flat Topic Files

```
docs/
├── README.md            # Router: what exists + read-when table (the only file agents read blind)
├── architecture.md      # One topic per file
├── domain-billing.md
├── integrations.md
└── status.md            # Project stage, current focus, known gaps
```

Rules, all from official skill-authoring guidance (skills are Anthropic's documented progressive-disclosure format; the same limits apply to any file an agent loads on demand):

- **One topic per file, under 500 lines.** Split before you exceed it.
- **One level deep.** Every doc is linked directly from the router. Agents may preview nested references with `head -100` and act on incomplete information — don't build chains of docs pointing at docs.
- **Table of contents at the top of any file over ~100 lines**, so a partial read still reveals the full scope.
- **Front-load triggers.** The first sentence of a description must say *when to read the doc*, not summarize it. (For skills this is enforced by budget: the listing truncates combined `description`/`when_to_use` text at 1,536 chars per skill and caps the whole listing at ~1% of the context window.)

### Template: `docs/README.md` router

```markdown
# Project Docs

Index for agents and humans. Read the matching doc before working in its area;
skip the rest. Keep this table in sync with the files (validated by hook).

| Doc | Covers | Read when |
|-----|--------|-----------|
| architecture.md | Service boundaries, data flow, why-not-X decisions | Changing cross-service behavior or adding a service |
| domain-billing.md | Billing rules, proration edge cases, tax quirks | Touching payments, invoices, or subscriptions |
| integrations.md | External APIs: auth, rate limits, sandbox gotchas | Calling or mocking a third-party service |
| status.md | Project stage, current focus, known gaps, non-goals | Planning work, or judging whether a gap is known |
```

### Template: doc frontmatter

```markdown
---
description: "Billing domain rules: proration, tax edge cases, refund constraints. Read when touching payments, invoices, or subscriptions."
read_when:
  - "touching payments, invoices, or subscriptions"
verified: 2026-07-15        # last date a human or agent checked this against the code
sources: [src/billing/, "Stripe API v2026-06"]   # what to verify against
---
```

The `verified` stamp is the freshness mechanism the maintenance workflow (below) reads and updates. The `sources` line tells the updating agent *what to check the doc against* — without it, re-verification degenerates into guessing.

## Navigation: Making Agents Use the Docs

Docs that agents don't load are dead weight; docs loaded wholesale are context bloat. The default wiring is two lines in CLAUDE.md plus the router:

```markdown
## Project Docs

Before working in an area, check the read-when table in `docs/README.md` and read
only the matching doc. Trust code over docs on conflict — and flag the mismatch.
```

That costs ~3 lines of always-loaded context; everything else is pay-per-use. The "trust code, flag mismatch" instruction turns every agent session into a passive drift detector.

**Escape hatch — path-scoped rule** instead of the CLAUDE.md section, when docs map cleanly to code areas ([Ch. 3](03-rules.md)):

```markdown
---
paths: ["src/billing/**"]
---
Read docs/domain-billing.md before modifying billing code.
```

Caveat: path-scoped rules trigger when Claude *reads* matching files; triggering on writes/new-file creation is not reliable as of this verification — keep the CLAUDE.md pointer as the primary wiring.

Do **not** use `@docs/...` imports in CLAUDE.md for this: imports load at session launch (recursively, up to 4 hops), so they cost full context every session — the opposite of on-demand.

## The Maintenance Workflow

Five mechanisms, from structural prevention to scheduled repair. The first two make most drift impossible; the last three catch what remains. Adopt them in order — a validator hook on top of derivable-content docs just automates the auditing of drift bombs.

### 1. Prevention: content rules (above)

Non-derivable content only; `Current method` / `Old patterns` for evolving topics; every doc carries `verified` + `sources` frontmatter.

### 2. Docs-as-code review

Official guidance, verbatim for CLAUDE.md and applicable to all agent docs: give the docs an owner, check them into git, and **review changes to them like code**. Test instruction changes empirically — observe whether agent behavior actually shifts. If Claude already does something correctly without an instruction, delete the instruction or convert it to a hook.

### 3. Deterministic checks: hooks

Prose rules are advisory; hooks are enforced ([Ch. 7](07-hooks.md)). Two hooks cover docs:

**Validator (PostToolUse)** — after any edit to a doc, check the invariants. Ask Claude to generate `scripts/validate_docs.py` for your repo enforcing: every `docs/*.md` has the frontmatter fields above, is linked from the router table, stays under 500 lines, and has no broken relative links. Then:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "fp=$(jq -r '.tool_input.file_path // empty'); case \"$fp\" in *docs/*.md|*CLAUDE.md) cd \"$CLAUDE_PROJECT_DIR\" && python3 scripts/validate_docs.py;; esac || true"
          }
        ]
      }
    ]
  }
}
```

(This guide's own repo runs exactly this pattern — `scripts/validate_guide.py` as a PostToolUse hook.)

**Drift reminder (Stop)** — when Claude finishes a turn that changed source files but no docs, surface it:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "cd \"$CLAUDE_PROJECT_DIR\" && changed=$(git diff --name-only HEAD 2>/dev/null); if echo \"$changed\" | grep -qE '^src/' && ! echo \"$changed\" | grep -qE '^(docs/|CLAUDE\\.md)'; then echo 'Docs check: source changed but no docs updated. If architecture, stack, domain rules, or status changed, run /update-docs.' >&2; fi || true"
          }
        ]
      }
    ]
  }
}
```

Adjust `^src/` to your source roots. **Escape hatch:** change the `fi` branch to `exit 2` to make it blocking — Claude must then update the docs (or explain) before stopping. Default to the reminder: most source changes legitimately need no doc update, and a blocking hook that cries wolf trains everyone to route around it.

### 4. On-demand repair: the `/update-docs` skill

The workhorse. Install as `.claude/skills/update-docs/SKILL.md`; run it after merging significant changes, when the Stop hook flags drift, or when a doc's `verified` stamp looks old.

```yaml
---
name: update-docs
description: |
  Sync project docs with the current code and tech stack. Use after changes
  that touch architecture, public behavior, dependencies, or project status,
  or when a doc's verified stamp predates significant changes in its sources.
  Pass a doc name or changed area as an argument to narrow scope.
allowed-tools: Read, Grep, Glob, Bash(git diff *), Bash(git log *)
---

# Update Project Docs

Sync docs with reality. Scope: $ARGUMENTS (if empty, determine scope from git).

1. **Find what changed.** If no argument given: for each doc, run
   `git log --oneline --since=<its verified date> -- <its sources paths>`.
   Docs whose sources changed since their stamp are the work list.
2. **Map changes to docs** using the read-when table in docs/README.md.
   Changes matching no doc's scope may need a NEW doc — propose, don't
   auto-create, unless the router has a place for it.
3. **Verify each affected doc claim-by-claim** against the current code and
   manifests (package.json, pyproject.toml, lockfiles — the stack's source of
   truth). Fix what drifted. Delete claims that are now derivable from code.
4. **Supersede, don't overwrite**, behavior that changed: move the old way to
   an "Old patterns" section with a deprecation date; describe the new way
   under "Current method".
5. **Bump `verified:`** (today's date) only on docs actually re-verified.
6. **Run the validator** (scripts/validate_docs.py) and fix violations.
7. **Report** a table: doc → status (current / updated / needs human decision),
   with one line per change made. Never invent facts to fill gaps — mark
   unknowns as "needs human input".
```

The `verified`-stamp-vs-git-log comparison in step 1 is what makes this cheap: an unchanged area costs one `git log`, not a re-read of the whole codebase.

For **creating** docs, no separate skill is needed — the rules are structural: new file under `docs/`, frontmatter filled in, row added to the router table, under 500 lines, one level deep. Put those five lines in the router's header comment (as in the template) and the validator enforces the rest.

### 5. Scheduled repair: doc-sync agents

Official docs name **"syncing docs after PRs merge"** as a scheduled-automation use case. Default: a weekly cloud Routine (`/schedule`, [Ch. 10](10-agent-teams-networks.md)):

```
/schedule weekly: run /update-docs across the repo; open a PR with the doc
changes and a table of what drifted; do not push to main.
```

**Escape hatches:** `/loop` for a session-local cadence; or a CI job via `claude-code-action` ([Ch. 13](13-editors-cicd.md)) triggered on merge to main, running `/update-docs` headless — prefer this when doc updates must go through the same PR gate as code.

## Which Mechanism When

| Situation | Mechanism |
|-----------|-----------|
| Doc describes something the code already states | Delete it (prevention beats sync) |
| Doc invariants (frontmatter, router links, size) | Validator hook — deterministic |
| Source changed, docs didn't | Stop-hook reminder → `/update-docs` |
| Big merge / stack upgrade landed | `/update-docs` immediately |
| Nobody remembers to do any of this | Scheduled Routine opening doc-sync PRs |
| Agent reports doc-vs-code mismatch mid-task | Fix the doc in the same PR as the code |

## Troubleshooting

- **Agents ignore the docs:** the router pointer is missing from CLAUDE.md, or read-when triggers describe topics instead of situations. Rewrite triggers as "touching X / changing Y".
- **Agents load too many docs:** topics overlap. Merge or re-split so any task matches at most one or two rows.
- **`/update-docs` rewrites too much:** its scope is the diff since the `verified` stamps — commit doc updates regularly so the window stays small, and keep `sources` paths narrow.
- **Docs keep drifting anyway:** they contain derivable content. Apply the include/exclude table and let `/doctor` (v2.1.206+) demonstrate the technique on CLAUDE.md.

---

**Sources (official):**
- [Memory — CLAUDE.md content rules, subdirectory loading, imports, /doctor trim](https://code.claude.com/docs/en/memory)
- [Best practices — include/exclude table, docs-as-code, hooks vs prose](https://code.claude.com/docs/en/best-practices)
- [Skills — progressive disclosure, 500-line tip, listing budgets](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices — one-level references, TOCs, time-sensitive content](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Hooks reference — events, exit codes](https://code.claude.com/docs/en/hooks)
- [Overview — scheduled automation, "syncing docs after PRs merge"](https://code.claude.com/docs/en/overview)
- [Steering Claude Code (Anthropic blog, June 2026) — CLAUDE.md ownership, skills/hooks/rules split](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)

All claims verified against these live sources on 2026-07-15. Numeric limits (200/500 lines, 1,536 chars, 1% listing budget, 4 import hops) are official recommendations or configurable defaults, not standards.
