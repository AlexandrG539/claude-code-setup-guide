---
description: "Vercel integration: Vercel agent skills, the official MCP server, the CLI plugin, and a custom deploy skill template. Read only when the project deploys to Vercel."
read_when:
  - "the project deploys to Vercel"
topics: [vercel, deployment, nextjs, mcp]
verified: 2026-07-28
claude_code_version: "2.1.220"
---

# Chapter 14: Vercel Integration — Skills, MCP & Deployment

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Editors & CI/CD](13-editors-cicd.md) · **Next:** [Reference](15-reference.md)

Three complementary integrations, in order of usefulness:

## 14.1: Vercel Agent Skills

```bash
npx skills add vercel-labs/agent-skills
```

The repo (actively maintained, ~28k stars) currently ships 9 skills, including:

| Skill | What It Provides |
|-------|-----------------|
| **react-best-practices** | React/Next.js performance rules (waterfalls, bundle size, SSR, re-renders) |
| **web-design-guidelines** | Accessibility, performance, UX rules |
| **composition-patterns** | Compound components, API design, avoiding boolean props |
| **writing-guidelines** | Prose/documentation style |
| **vercel-deploy-claimable** | One-command deploy with a claimable preview URL |
| **vercel-optimize**, **react-native-guidelines**, **react-view-transitions**, … | See the repo |

Note the CLI is `npx skills add` (the older `npx add-skill` form is deprecated — use one consistently).

## 14.2: Vercel MCP Server (Official)

Vercel's official remote MCP with OAuth, at `https://mcp.vercel.com`:

```bash
claude mcp add --transport http vercel https://mcp.vercel.com
# then inside the session:
/mcp     # authenticate via OAuth
```

Capabilities (per Vercel docs, June 2026): search Vercel documentation, **manage teams/projects/deployments**, and analyze deployment logs. Public docs-search tools work without auth; management tools require the OAuth login. It grants the agent the same access as your Vercel user account, so keep human confirmation on for deploy/change operations.

Separately, there's an official Vercel plugin in the Claude Code marketplace — note it is **CLI-based, not MCP-based**: it requires the Vercel CLI (`npm i -g vercel` + `vercel login`) and ships the `/deploy`, `/vercel-logs`, and `/vercel-setup` commands:

```
/plugin install vercel@claude-plugins-official
```

The plugin (Vercel CLI) and the MCP server are different mechanisms and can coexist; for most setups pick one to avoid overlapping capabilities. Vercel also promotes a newer, larger plugin installed via its own skills CLI — `npx plugins add vercel/vercel-plugin` (28 skills, 3 agents, commands like `/vercel-plugin:deploy`) — see [vercel.com/docs/agent-resources/vercel-plugin](https://vercel.com/docs/agent-resources/vercel-plugin).

## 14.3: Custom Deploy Skill

`.claude/skills/deploy/SKILL.md`:

```yaml
---
name: deploy
description: Build, verify, and deploy to Vercel
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: true
---

Deploy the project to Vercel: $ARGUMENTS

1. Run the full build
2. Run type checker
3. Run linter
4. Run test suite
5. If ANY step fails, STOP. Do not deploy broken code.
6. Run `vercel --prod` for production or `vercel` for preview
7. Report deployment URL and status
```

`disable-model-invocation: true` matters here: you decide when to deploy, never Claude.

---

**Sources:**
- [Vercel MCP (official docs)](https://vercel.com/docs/agent-resources/vercel-mcp)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)

**Next:** [Chapter 15: Reference →](15-reference.md)
