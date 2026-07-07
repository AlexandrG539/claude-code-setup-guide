---
description: "Hooks: all ~30 lifecycle events, the five hook types, and a ready-to-use settings.json with auto-format, file protection, branch protection, and notifications. Read when a rule must be enforced every time — hooks are deterministic; CLAUDE.md prose is advisory."
read_when:
  - "always — core chapter, must-hold rules belong in hooks, not prose"
topics: [hooks, lifecycle-events, automation, enforcement, settings-json]
verified: 2026-07-07
claude_code_version: "2.1.202"
---

# Chapter 7: Hooks — Deterministic Automation

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [MCP Servers](06-mcp.md) · **Next:** [Skills & Commands](08-skills.md)

Hooks execute at specific lifecycle events. They are NOT AI — they run deterministically every time. This is what makes them powerful: formatting will always happen, not just when Claude "remembers" to do it.

**Rule of thumb:** if it's a suggestion, use CLAUDE.md. If it's a requirement, use a hook.

## Hook Types

Hooks support **five execution types**:

| Type | What It Does | Use Case |
|------|-------------|----------|
| `command` | Shell command (most common) | Formatting, linting, blocking, logging |
| `prompt` | Single-turn LLM evaluation | Judgment calls — "is this command safe?" |
| `agent` | Multi-turn subagent with tools (experimental) | Complex verification — "review this diff" |
| `http` | POST to HTTP endpoint | Webhooks — notify Slack, trigger CI |
| `mcp_tool` | Call an MCP server tool | Reuse existing MCP integrations as hook actions |

## Hook Events

The full official event list as of July 2026:

| Event | When It Fires |
|-------|--------------|
| `SessionStart` | Session begins or resumes (matchers: `startup`, `resume`, `clear`, `compact`) |
| `Setup` | On `--init` or `--maintenance` |
| `UserPromptSubmit` | When you press Enter — inject context, validate, log |
| `UserPromptExpansion` | When a prompt is expanded (commands/skills) |
| `PreToolUse` | Before a tool executes — block, validate, extend permissions |
| `PermissionRequest` | When a permission dialog would show — auto-allow/deny |
| `PermissionDenied` | After a permission is denied |
| `PostToolUse` | After a tool completes — format, typecheck |
| `PostToolUseFailure` | After a tool fails |
| `PostToolBatch` | After a batch of parallel tool calls |
| `Notification` | When Claude needs attention — desktop notifications |
| `MessageDisplay` | When a message is displayed |
| `SubagentStart` / `SubagentStop` | Subagent lifecycle |
| `TaskCreated` / `TaskCompleted` | Shared task list items (exit 2 blocks creation/completion) |
| `TeammateIdle` | Agent-team teammate about to go idle (exit 2 sends feedback, keeps it working) |
| `Stop` | When Claude finishes responding — final verification |
| `StopFailure` | When a stop handler fails |
| `InstructionsLoaded` | CLAUDE.md / rules load — debug which instruction files load and why |
| `ConfigChange` | Settings modified mid-session |
| `CwdChanged` | Working directory changed (`/cd`) |
| `FileChanged` | Watched file changed |
| `WorktreeCreate` / `WorktreeRemove` | Git worktree lifecycle |
| `PreCompact` / `PostCompact` | Around context compaction — preserve/re-inject state |
| `Elicitation` / `ElicitationResult` | Structured user-input requests |
| `SessionEnd` | Session terminates (matchers: `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`) |

## Configuration

Hooks go in `settings.json` (project or global), or use the interactive `/hooks` UI:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern",
        "hooks": [
          { "type": "command", "command": "shell command here" }
        ]
      }
    ]
  }
}
```

- `matcher`: tool name pattern (`"Edit|Write"`, `"Bash"`, `"*"` for all, `""` for no-tool events). Matchers use **canonical tool names**.
- Hook input arrives as **JSON on stdin** with fields like `tool_name`, `tool_input.file_path`, `tool_input.command`.
- Exit code 0 = success. Stdout is parsed for JSON output fields (`continue`, `decision: block`, `permissionDecision: allow|deny|ask|defer`, `updatedInput`, `additionalContext`, …); for most events plain stdout goes only to the debug log, but for `UserPromptSubmit`, `UserPromptExpansion`, and `SessionStart` it is **added to Claude's context**.
- Exit code 2 = block + feed stderr back to Claude as feedback (on blockable events; e.g. `SessionStart`, `Notification`, `PostToolUse` can't be blocked). Exit code 1 does **not** block — Claude Code treats it as a non-blocking error and proceeds.
- `${CLAUDE_PROJECT_DIR}` is officially documented: use it to reference hook scripts relative to the project root; it's also exported into the hook process environment.

## Recommended Hook Configuration

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
            "command": "fp=$(jq -r '.tool_input.file_path // empty'); blocked=false; for pattern in .env package-lock.json pnpm-lock.yaml yarn.lock .git/ node_modules/ dist/ .next/ build/; do case \"$fp\" in *\"$pattern\"*) blocked=true;; esac; done; if $blocked; then echo \"BLOCKED: Writing to $fp is not allowed.\" >&2; exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "cmd=$(jq -r '.tool_input.command // empty'); branch=$(cd \"$CLAUDE_PROJECT_DIR\" && git rev-parse --abbrev-ref HEAD 2>/dev/null); if echo \"$cmd\" | grep -qE '^git commit' && echo \"$branch\" | grep -qE '^(main|master|dev)$'; then echo \"BLOCKED: Never commit directly on $branch. Create a feature branch first.\" >&2; exit 2; fi; if echo \"$cmd\" | grep -qE 'git push.*(origin )?(main|master|dev)( |$)'; then echo \"BLOCKED: Never push directly to $branch. Merge via PR only.\" >&2; exit 2; fi"
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
| PostToolUse (prettier) | After any file edit | Auto-format (ts, tsx, js, jsx, mjs, css, json, md) |
| PreToolUse (file protection) | Before any write | Block writes to .env, lockfiles, .git, node_modules, build dirs |
| PreToolUse (branch protection) | Before git commit/push | Block commits on protected branches and direct pushes |
| Stop (console.log scanner) | When Claude finishes | Scan modified files for leftover debug statements |
| Notification | When Claude needs input | Desktop notification (Linux/macOS) |

**Blocking-hook shell pattern (important):** read stdin with command substitution (`fp=$(jq -r …)`) and call `exit 2` at the top level, as above. Do **not** pipe stdin into a group — `jq … | { read fp; …; exit 2; } || true` exits only the pipeline's subshell, and the trailing `|| true` rewrites the status to 0, so the hook prints `BLOCKED` but never actually blocks. (Verified 2026-07-07; earlier revisions of this guide shipped the broken form.)

## Advanced Hook Types

### LLM-Based Review (type: "prompt")

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

### Agent-Based Verification (type: "agent")

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

### Webhook Notifications (type: "http")

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          { "type": "http", "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" }
        ]
      }
    ]
  }
}
```

## Hooks and Permissions

- Deny/ask permission rules are evaluated regardless of hook output — a hook cannot un-deny.
- A hook exiting 2 blocks the call even when an allow rule matches.
- Pattern: allow `Bash` broadly, then a PreToolUse hook rejects the handful of commands you never want.

## Hook Design Best Practices

1. **Always end shell hooks with `|| true`** — prevents hook failures from blocking normal operation.
2. **Use exit code 2 to block** — stderr becomes feedback to Claude.
3. **Use `jq` for JSON parsing** of stdin.
4. **Keep `command` hooks fast** — they run synchronously.
5. **Use `prompt`/`agent` hooks sparingly** — they consume tokens and add latency.
6. **Test hooks manually first:**
   ```bash
   echo '{"tool_input":{"file_path":"src/index.ts"}}' | jq -r '.tool_input.file_path'
   ```
7. **Enterprise:** `allowManagedHooksOnly` in managed settings blocks all non-managed hooks.

---

**Sources (official):**
- [Hooks guide](https://code.claude.com/docs/en/hooks-guide)
- [Hooks reference (all events, payloads)](https://code.claude.com/docs/en/hooks)

**Next:** [Chapter 8: Skills & Commands →](08-skills.md)
