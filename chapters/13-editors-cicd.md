---
description: "Editor and CI integration: VS Code/Cursor/JetBrains extensions, GitHub Actions via claude-code-action@v1, and headless claude -p with output formats. Read when the project has CI or when IDE integration is wanted."
read_when:
  - "the project has CI (GitHub Actions or similar)"
  - "setting up IDE integration (VS Code, Cursor, JetBrains)"
  - "scripting Claude Code non-interactively (claude -p)"
topics: [ide, vscode, jetbrains, github-actions, ci-cd, headless]
verified: 2026-07-28
claude_code_version: "2.1.220"
---

# Chapter 13: Editor Integration & CI/CD

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Monorepos & Parallel Workflows](12-monorepo-parallel.md) · **Next:** [Vercel Integration](14-vercel.md)

## Editor & Surface Integration

Claude Code runs as: a terminal CLI, a **desktop app** (macOS/Windows), a **web app** ([claude.ai/code](https://claude.ai/code)), and **IDE extensions**.

### VS Code / Cursor

- Install the official **Claude Code VS Code extension**, or run the CLI in the integrated terminal and connect with the `/ide` command.
- When connected, Claude sees your current selection and open files (the built-in IDE MCP server), and diffs can open in the editor.
- Multi-root workspaces are a known limitation: the extension uses the **first** workspace folder for cwd, configuration, and @-file autocomplete (open issues track full support). For multi-repo work, prefer one window per repo or `--add-dir`.

### JetBrains IDEs

Official plugin available; same `/ide` pairing model.

### Terminal + editor split (any editor)

**Left:** terminal with Claude Code. **Right:** editor showing files. Claude edits files, the editor auto-reloads, you review in real time. `Ctrl+G` opens your current *prompt* in your default text editor (useful for long prompts — not for opening project files).

### Web ↔ terminal

`/teleport` pulls a claude.ai/code web session into your terminal (fetches branch + conversation). `/remote-control` lets you continue a local session from another device. Both require a claude.ai subscription.

## CI/CD Integration

### GitHub Actions — the official path

Use the official **`anthropics/claude-code-action@v1`** (GA — do not use the old `@beta`). The fastest setup is interactive:

```
/install-github-app
```

This installs the Claude GitHub App on the repo and walks you through adding the workflow and the `ANTHROPIC_API_KEY` secret. (Requires repo admin. Bedrock/Vertex users: see the official docs for OIDC-based setup.)

**Basic workflow — responds to `@claude` mentions in issues/PRs:**

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Automated PR review on every PR (runs a bundled skill via a plugin):**

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          plugin_marketplaces: "https://github.com/anthropics/claude-code.git"
          plugins: "code-review@claude-code-plugins"
          prompt: "/code-review:code-review ${{ github.repository }}/pull/${{ github.event.pull_request.number }}"
```

**Scheduled automation:**

```yaml
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model opus"
```

Key action inputs: `prompt` (plain text or a `/skill` invocation), `claude_args` (any CLI flags: `--max-turns`, `--model`, `--allowedTools`, `--mcp-config`, …), `plugins` / `plugin_marketplaces`, `trigger_phrase` (default `@claude`), `use_bedrock` / `use_vertex`.

Best practices: never hardcode API keys (use repo secrets); keep CLAUDE.md concise — the action reads it; set `--max-turns` and workflow timeouts to bound cost.

### Headless mode (`claude -p`) for scripts and pipelines

```bash
# Simple lint-style usage
git diff origin/main...HEAD | claude -p "Review this diff for bugs and security issues. Be concise."

# Structured output for scripts
claude -p "..." --output-format json
claude -p "..." --output-format stream-json   # real-time processing

# Useful companions
claude -p "..." --max-turns 10 --max-budget-usd 2.50 --allowedTools "Read,Grep,Bash(npm test*)"
```

| Format | Flag | Use Case |
|--------|------|----------|
| Text | `--output-format text` | Simple pipe output (default) |
| JSON | `--output-format json` | Structured result (`result`, `session_id`, `total_cost_usd`, per-model cost breakdown) |
| Stream JSON | `--output-format stream-json` | Real-time event stream |

In `-p` mode there is no user to prompt, so tool calls follow your configured permission rules; combine with `--permission-mode`, allowlists, or a sandbox for unattended runs. For CI and scripted calls, official docs now recommend adding `--bare` (it will become the default for `-p` in a future release).

For deeper programmatic integration (custom agents, multi-agent systems), use the **Claude Agent SDK** — the same engine that powers the GitHub Action. See [Chapter 10](10-agent-teams-networks.md#the-claude-agent-sdk).

---

**Sources (official):**
- [GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [claude-code-action repository](https://github.com/anthropics/claude-code-action)
- [Headless / print mode](https://code.claude.com/docs/en/headless)
- [VS Code integration](https://code.claude.com/docs/en/vs-code)

**Next:** [Chapter 14: Vercel Integration →](14-vercel.md)
