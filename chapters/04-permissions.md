# Chapter 4: Permissions, Permission Modes & Sandboxing

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs, July 2026 (Claude Code 2.1.200)
>
> **Previous:** [Rules](03-rules.md) · **Next:** [Plugins](05-plugins.md)

Permissions control what tools Claude can use without asking. Set these **early** — before installing plugins or running commands. Unlike CLAUDE.md, permission rules are **enforced by Claude Code itself**, regardless of what the model decides.

## Configuration

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
      "Bash(npx eslint *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git checkout *)",
      "Bash(git switch *)",
      "Bash(git stash*)",
      "Bash(git merge *)",
      "Bash(git rebase *)"
    ],
    "deny": [
      "Bash(git push --force*)",
      "Bash(git reset --hard*)",
      "Read(.env*)",
      "Read(**/*.pem)",
      "Read(**/*secret*)",
      "Read(**/*credential*)"
    ]
  }
}
```

Note: purely read-only commands (`ls`, `cat`, `grep`, `git status`, `git diff`, `git log`, `cd` within the project, etc.) are built-in read-only and never prompt — you don't need allow rules for them.

## Permission Rule Syntax

| Pattern | Meaning |
|---------|---------|
| `Bash` or `Bash(*)` | All Bash commands (as a **deny**, removes the tool from Claude's context entirely) |
| `Bash(npm run build)` | Exact command |
| `Bash(npm run *)` | Prefix wildcard (`:*` suffix is an equivalent trailing form: `Bash(npm run:*)`) |
| `Bash(git * main)` | Wildcards work at **any position** — matches `git checkout main`, `git merge main`, `git push origin main` |
| `Bash(* --version)` | Leading wildcard |
| `Read(.env*)` | gitignore-style path pattern — bare filenames match at any depth |
| `Edit(/src/**/*.ts)` | Leading `/` anchors at the **settings file's** directory (not filesystem root); `//path` is absolute; `~/path` is home |
| `WebFetch(domain:example.com)` | Domain-scoped web fetch |
| `mcp__server__tool` | A specific MCP tool; `mcp__server` or `mcp__server__*` = all tools of that server |
| `Agent(Explore)` | Controls which subagents can be spawned |
| `Tool(param:value)` | Deny/ask rules can match any scalar input parameter, e.g. `Agent(model:opus)`, `Bash(run_in_background:true)` |

**Evaluation order:** Deny → Ask → Allow. First match wins; specificity does not change the order, so a broad deny always beats a narrow allow.

Subtleties worth knowing (all official):

- The space before `*` enforces a word boundary: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- Claude Code splits compound commands on `&&`, `||`, `;`, `|`, `&`, newlines — a rule must match **each** subcommand independently, so `Bash(safe-cmd *)` doesn't approve `safe-cmd && rm -rf .`.
- Process wrappers `timeout`, `time`, `nice`, `nohup`, `stdbuf` (and bare `xargs`) are stripped before matching. Environment runners (`npx`, `docker exec`, `devbox run`, …) are **not** — `Bash(devbox run *)` would match `devbox run rm -rf .`, so write rules that include the inner command.
- Argument-constraining patterns like `Bash(curl http://github.com/ *)` are fragile (options, redirects, variables bypass them). Prefer: deny `curl`/`wget` and allow `WebFetch(domain:...)`, or use a PreToolUse hook.
- `Read`/`Edit` rules apply to Claude's file tools and recognized file commands (`cat`, `sed`, …), **not** to arbitrary subprocesses (a Python script opening a file). For OS-level enforcement use the [sandbox](#sandboxing).

## Permission Strategy

1. **Allow generously for development tools** — package managers, formatters, linters, test runners.
2. **Deny destructive operations** — force push, hard reset.
3. **Deny secret access** — env files, keys, credentials.
4. **Add project-specific allows** (`pnpm`, `turbo`, `cargo`, `pytest`, `go test`, …).
5. Run the built-in `/fewer-permission-prompts` skill: it scans your transcripts for read-only calls you keep approving and proposes an allowlist.

### User-Local vs Project Permissions

- **`.claude/settings.json`** (committed) — project-wide rules shared with the team.
- **`.claude/settings.local.json`** (gitignored) — personal approvals accumulated during sessions ("Yes, don't ask again").

Review both anytime with `/permissions` — the UI shows every rule and which file it came from.

## Permission Modes

Cycle modes with **Shift+Tab**, start with `claude --permission-mode <mode>`, or set `defaultMode` in settings.

| Mode | Behavior |
|------|----------|
| `default` | Prompts on first use of each tool |
| `acceptEdits` | Auto-accepts file edits and common filesystem commands in the working directory |
| `plan` | **Plan mode**: Claude reads files and runs read-only commands but doesn't edit anything |
| `auto` | Auto-approves with a background safety classifier; prompts only on risky actions (research preview) |
| `dontAsk` | Auto-denies anything not pre-approved via allow rules |
| `bypassPermissions` | Skips prompts (except explicit `ask` rules and the `rm -rf /` / `rm -rf ~` circuit breaker). Only for isolated containers/VMs |

### Plan mode — use it deliberately

Plan mode is one of the highest-leverage workflow habits: for any non-trivial change, let Claude explore and produce a plan first, review it, then approve execution.

- Enter with `Shift+Tab` (cycle) or the `/plan` command (`/plan fix the auth bug`).
- Start a session in it: `claude --permission-mode plan`.
- The `opusplan` model alias uses Opus for plan mode, then switches to Sonnet for execution (see [model configuration](15-reference.md#model-configuration)).

### Auto mode

`auto` mode uses a classifier to review each tool call and prompts only on risk (scope escalation, unknown infrastructure, suspicious content-driven actions). Org admins can disable it with `permissions.disableAutoMode`. Inspect the classifier's rules with `claude auto-mode defaults`.

## Sandboxing

Permissions and sandboxing are complementary: permissions control what Claude *may attempt*; the sandbox is OS-level enforcement of what Bash commands *can physically reach* (filesystem and network), even under prompt injection.

- Toggle per session with `/sandbox`; configure via the `sandbox` settings key.
- With `autoAllowBashIfSandboxed: true` (default when sandboxing is on), sandboxed Bash runs without prompting — the sandbox boundary replaces the prompt.
- Sandbox filesystem rules merge with your `Read`/`Edit` deny rules; network rules merge with `WebFetch(domain:...)` rules.

## Hooks as a permission layer

`PreToolUse` hooks run before the permission check and can deny, force a prompt, or allow. A hook exiting with code 2 blocks the call even when an allow rule matches; deny/ask rules still apply regardless of hook output. Pattern: allow all of `Bash`, then block specific commands with a hook. See [Chapter 7](07-hooks.md).

---

**Sources (official):**
- [Permissions](https://code.claude.com/docs/en/permissions)
- [Permission modes](https://code.claude.com/docs/en/permission-modes)
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)

**Next:** [Chapter 5: Plugins →](05-plugins.md)
