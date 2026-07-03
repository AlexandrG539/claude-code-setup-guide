# Chapter 6: MCP Servers — External Service Connections

> Part of the [Claude Code Configuration Guide](../README.md) · Verified against official docs and live npm/PyPI registries, July 2026 (Claude Code 2.1.200)
>
> **Previous:** [Plugins](05-plugins.md) · **Next:** [Hooks](07-hooks.md)

MCP (Model Context Protocol) connects Claude to external services — issue trackers, databases, deployment platforms, monitoring, documentation.

**Before adding MCP servers**, check whether an installed [plugin](05-plugins.md) already provides the connection (the official `github`, `linear`, `figma`, `vercel`, `supabase`, `sentry`, `slack`, … plugins bundle MCP servers).

## Tool Search — the new default

**This changed the economics of MCP.** Tool search is **enabled by default**: MCP tool definitions are *deferred* rather than loaded upfront — only tool names and server instructions load at session start, and Claude discovers full tool schemas on demand. Adding more servers now has minimal impact on your context window.

Older advice like "context shrinks from 200K to 70K with too many MCPs" or "keep under 80 tools" is **obsolete** for default setups. The practical limit is your overall context budget, which `/context` will show you.

Configuration (env var `ENABLE_TOOL_SEARCH` or settings `env`):

| Value | Behavior |
|-------|----------|
| (unset) | All MCP tools deferred, loaded on demand (default). Falls back to upfront loading on Vertex AI / non-first-party `ANTHROPIC_BASE_URL` |
| `auto` / `auto:N` | Load upfront if tools fit within 10% (or N%) of the context window; defer overflow |
| `false` | Load everything upfront (old behavior) |

Per-server exemption: set `"alwaysLoad": true` on a server whose tools Claude needs every turn. Note Haiku models don't support tool search.

## Adding Servers

```bash
# HTTP transport (recommended for remote/hosted servers; supports OAuth)
claude mcp add --transport http <name> <url>
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Local stdio server ( -- separates Claude's flags from the server command)
claude mcp add --transport stdio <name> -- npx -y <package>
claude mcp add --env API_KEY=your-key --transport stdio airtable -- npx -y airtable-mcp-server

# JSON form (for ws or copied configs; `streamable-http` is accepted as alias for `http`)
claude mcp add-json <name> '{"type":"http","url":"https://mcp.example.com/mcp"}'

# Manage
claude mcp list          # includes ⏸ Pending approval for unapproved project servers
claude mcp get <name>
claude mcp remove <name>
```

Inside a session: `/mcp` shows status, tool counts, and handles **OAuth authentication**; `/mcp enable|disable <server>|all` toggles connections; `/mcp reconnect <server>` fixes a dropped one. HTTP/SSE servers auto-reconnect with exponential backoff (5 attempts). SSE transport is deprecated — prefer HTTP.

### Scopes

| Scope | Available in | Stored in | Shared? |
|-------|--------------|-----------|---------|
| `local` (default) | Current project only | `~/.claude.json` | No |
| `project` | Current project | `.mcp.json` in repo root | Yes — committed; teammates are prompted to approve |
| `user` | All your projects | `~/.claude.json` | No |

```bash
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
claude mcp reset-project-choices    # re-prompt for .mcp.json approvals
```

## Which Servers to Add (verified July 2026)

### Tier 1: broadly useful

| Server | Purpose | Install |
|--------|---------|---------|
| **Context7** (Upstash) | Real-time, version-specific library documentation — solves knowledge cutoff for fast-moving frameworks. Add "use context7" to prompts needing current docs | `claude mcp add --transport stdio context7 -- npx -y @upstash/context7-mcp` |
| **Playwright** | Browser automation, E2E testing | `claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest` |

> ⚠️ **Correction vs. older guides:** the Playwright MCP package is **`@playwright/mcp`** (published by Microsoft, actively maintained). A package named `@anthropic/mcp-server-playwright` **does not exist** on npm (verified against the registry, 2026-07-03).

### Tier 2: add when needed

| Server | Notes |
|--------|-------|
| **GitHub** | Prefer the official `github` **plugin**, or skip entirely — Claude uses the `gh` CLI natively very well |
| **Fetch** | The reference fetch server is **Python-only**: PyPI `mcp-server-fetch`, run via `uvx` — `claude mcp add --transport stdio fetch -- uvx mcp-server-fetch`. (The npm package `@modelcontextprotocol/server-fetch` does not exist.) Usually unnecessary: Claude has a built-in WebFetch tool |
| **PostgreSQL** | ⚠️ The old reference server `@modelcontextprotocol/server-postgres` is **deprecated and archived** (last release Dec 2024; repo archived May 2025, no security updates). Don't use it. Use your database vendor's official MCP (e.g. Supabase/Neon/PlanetScale plugins or servers), or let Claude query via your ORM/CLI |
| **shadcn/ui, Magic UI, etc.** | Component-library servers — only if your project uses them; see each project's docs |

### Tier 3: platform servers

Most platforms now ship official remote MCPs with OAuth (Vercel — see [Chapter 14](14-vercel.md), Netlify, Cloudflare, Sentry, Stripe, PayPal, Notion, Linear, Asana, HubSpot, …). Prefer the vendor's official HTTP endpoint or its official Claude Code plugin over community stdio wrappers. Browse reviewed connectors in the [Anthropic Directory](https://claude.ai/directory).

## Context & Hygiene Rules (updated for tool search)

1. Tool search makes idle servers cheap, but **connected servers still cost something** (names + instructions) and add attack surface — remove servers you don't use: `claude mcp remove` or `/mcp disable`.
2. Reject unneeded `.mcp.json` servers from repos you clone: the settings keys are `enabledMcpjsonServers` / `disabledMcpjsonServers` (note: **not** `disabledMcpServers` — that's an internal `.claude.json` state key, not the documented setting).
3. Check real costs with `/mcp` (tool counts) and `/usage` (per-server token breakdown).
4. Prefer native tools (Glob, Grep, Read, `gh`, Explore subagent) when they cover the job — they're faster and cheaper than MCP round-trips.
5. Security: MCP servers act with *your* credentials. Only connect servers you trust; watch for prompt-injection via tool results (pair risky servers with permission `ask` rules or the sandbox).

## Enterprise

Admins can pin/allowlist servers via `managed-mcp.json`, `allowedMcpServers` / `deniedMcpServers`, and `allowManagedMcpServersOnly` in managed settings.

---

**Sources:**
- [MCP in Claude Code (official)](https://code.claude.com/docs/en/mcp) — incl. tool search
- [@playwright/mcp on npm](https://www.npmjs.com/package/@playwright/mcp) · [mcp-server-fetch on PyPI](https://pypi.org/project/mcp-server-fetch/) · [archived server-postgres](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/postgres)
- [Context7](https://github.com/upstash/context7)

**Next:** [Chapter 7: Hooks →](07-hooks.md)
