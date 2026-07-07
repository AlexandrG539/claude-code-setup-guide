---
description: "Monorepos and parallel work: hierarchical CLAUDE.md, claudeMdExcludes, native worktrees (claude -w), background sessions, branching strategy, and tmux. Read when the project is a monorepo or when running parallel Claude sessions."
read_when:
  - "the project is a monorepo (multiple packages/apps in one repo)"
  - "running several Claude sessions in parallel on one repo"
topics: [monorepo, worktrees, parallel-sessions, claude-md-hierarchy, tmux]
verified: 2026-07-07
claude_code_version: "2.1.202"
---

# Chapter 12: Monorepos & Parallel Workflows

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Context Management](11-context-management.md) · **Next:** [Editors & CI/CD](13-editors-cicd.md)

## Monorepo vs Separate Repos

### Recommendation: Monorepo

| Factor | Monorepo | Separate Repos |
|--------|----------|----------------|
| Claude context | Hierarchical CLAUDE.md — loads only relevant rules | Cross-repo duplication of instructions |
| Shared code | Single `packages/shared` — direct imports | Must publish packages or copy types |
| Integration | Claude sees both sides of your API | Must manually sync API contracts |
| Config | Auto-loads per directory | Needs `--add-dir` workaround |

### Monorepo Hierarchical CLAUDE.md

```
monorepo/
├── CLAUDE.md                 # Shared rules (always loaded, ~100 lines)
├── apps/
│   ├── web/CLAUDE.md         # Frontend rules (loads on demand in web/)
│   └── api/CLAUDE.md         # Backend rules (loads on demand in api/)
└── packages/
    └── shared/CLAUDE.md      # Shared package rules
```

### Monorepo tools (all verified)

- **`claudeMdExcludes`** — skip other teams' CLAUDE.md/rules by absolute-path glob. Put it in `.claude/settings.local.json` to keep the exclusion personal:

  ```json
  {
    "claudeMdExcludes": [
      "**/monorepo/CLAUDE.md",
      "/home/alex/monorepo/other-team/.claude/rules/**"
    ]
  }
  ```

  Arrays merge across settings layers; managed-policy CLAUDE.md files cannot be excluded (by design).
- **Nested `.claude/agents/`** — every `.claude/agents/` between cwd and the repo root is scanned; on a name collision the definition closest to cwd wins (2.1.178+).
- **Nested `.claude/workflows/`** — saved workflows load from every `.claude/workflows/` along the path; closest wins (2.1.178+).
- **`/cd <path>`** (2.1.169+) — relocate the session's primary working directory mid-session: the new directory's CLAUDE.md loads and `--resume` finds the session from there. `Cd` permission rules can restrict targets.
- **Path-scoped rules** (see [Chapter 3](03-rules.md)) — often better than per-directory CLAUDE.md for topic conventions.

### If You Must Use Separate Repos

```bash
# Option A: add the second repo to the workspace
cd ~/projects/frontend
claude --add-dir ~/projects/backend
```

Note: `--add-dir` grants *file access*; it does not load the other repo's CLAUDE.md by default. Set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to also load memory files from added directories. Skills and agents in an added directory's `.claude/` *are* loaded.

```bash
# Option B: parent directory with both clones
mkdir ~/projects/fullstack && cd ~/projects/fullstack
git clone <frontend> web
git clone <backend> api
claude
```

## Parallel Workflows

### Built-in worktree support (recommended)

Claude Code now manages git worktrees natively — no manual `git worktree add` needed:

```bash
# Start Claude in an isolated worktree at <repo>/.claude/worktrees/<name>
claude --worktree feature-auth     # short: claude -w feature-auth

# Auto-generated name
claude -w

# Branch the worktree from a PR (worktree created at .claude/worktrees/pr-123)
claude -w "#123"                   # also accepts a full PR URL
# Note: --from-pr is a *resume* flag (reopens sessions linked to a PR), not a worktree flag

# One tmux/iTerm2 pane per worktree session
claude -w feature-auth --tmux
```

Manual worktrees still work fine for full control:

```bash
git worktree add ../project-feature-a -b feature-a
cd ../project-feature-a && claude
# later
git worktree remove ../project-feature-a
```

All worktrees of one repo share the same auto-memory directory, so learnings carry across.

### Background agents (`claude agents`)

Run many independent sessions in parallel and monitor them from one dashboard:

```bash
claude agents            # open agent view (interactive terminal required)
claude agents --json     # script-friendly list of active sessions
```

From inside a session you can also background it and start something else; background sessions appear in `--resume` marked `bg`.

For **coordinated** parallelism (agents that talk to each other), see [Agent Teams in Chapter 10](10-agent-teams-networks.md).

### Conversation branching

```
/branch [name]     # fork the conversation at this point; original stays in /resume
/fork              # hand a side task to a background subagent instead
```

(Naming changed vs. older guides: `/fork` used to fork the conversation; that job now belongs to `/branch`.)

### Session persistence

```bash
claude --continue          # resume the most recent conversation
claude --resume            # interactive picker (or pass an ID/name)
claude --resume abc --fork-session   # resume as a NEW session id
claude --from-pr 123       # resume sessions linked to a PR
```

`/rename` names the current session for easier resumption; `/rewind` (or `Esc Esc`) restores code/conversation checkpoints.

### tmux for long sessions

```bash
tmux new -s claude-dev
# Detach: Ctrl+B, D — Reattach:
tmux attach -t claude-dev
```

---

**Sources (official):**
- [Monorepos & large codebases](https://code.claude.com/docs/en/large-codebases)
- [Worktrees](https://code.claude.com/docs/en/worktrees)
- [Agent view (background agents)](https://code.claude.com/docs/en/agent-view)
- [CLI reference](https://code.claude.com/docs/en/cli-reference)

**Next:** [Chapter 13: Editors & CI/CD →](13-editors-cicd.md)
