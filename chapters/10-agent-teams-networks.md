---
description: "Multi-agent options compared and configured: agent teams, dynamic workflows / ultracode, background agents, the Agent SDK, and MCP/A2A interconnect. Read when a task needs multiple coordinated agents or sessions, or when integrating Claude agents into services."
read_when:
  - "task needs more agents than one conversation can coordinate (audits, migrations, multi-angle review)"
  - "building programmatic agents or CI bots with the Agent SDK"
  - "connecting agents across tools or vendors (MCP, A2A)"
topics: [agent-teams, workflows, ultracode, background-agents, agent-sdk, a2a, orchestration]
verified: 2026-07-07
claude_code_version: "2.1.202"
---

# Chapter 10: Agent Teams, Workflows & Multi-Agent Networks

> Part of the [Claude Code Configuration Guide](../README.md) · **Previous:** [Subagents](09-subagents.md) · **Next:** [Context Management](11-context-management.md)

Claude Code now has four native ways to run multi-agent work, plus external interconnect options. Pick by **who holds the plan** and **whether workers must talk to each other**:

| | [Subagents](09-subagents.md) | Background agents | Agent teams | Dynamic workflows |
|---|---|---|---|---|
| What it is | Workers Claude spawns in-session | Independent parallel sessions | Peer sessions with a lead, shared tasks, messaging | A script the runtime executes |
| Who decides next step | Claude, turn by turn | You (dispatch) | The lead agent | The script |
| Workers talk to each other | No — report to caller only | No | **Yes** — mailbox + shared task list | No — results flow through script variables |
| Scale | A few per turn (nesting to 5 levels) | As many sessions as you dispatch | ~3–5 teammates typical | Dozens–hundreds of agents per run |
| Token cost | Low (summaries return) | Per-session | High (each teammate is a full session) | High but bounded (16 concurrent, 1,000/run caps) |

---

## Agent Teams (experimental)

Multiple Claude Code sessions coordinate: one **lead** assigns work, **teammates** work independently in their own context windows, communicate directly with each other, and share a task list with dependency tracking and file-locked claiming.

**Enable** (disabled by default; experimental):

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

**Use** — just describe the team in natural language:

```text
Spawn three teammates to review PR #142:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

Since 2.1.178 there is no setup step: every session has one implicit team; teammates are spawned directly (the old `TeamCreate`/`TeamDelete` tools no longer exist — ignore pre-June-2026 tutorials that use them).

### What you can do

- **Talk to any teammate directly** — arrow keys in the agent panel → Enter opens its transcript; type to message it. In split-pane mode (`--teammate-mode tmux` / `iterm2`, or `teammateMode` setting) each teammate gets its own pane.
- **Require plan approval:** "Require plan approval before they make any changes" — the teammate works read-only until the lead approves its plan (give the lead approval criteria in your prompt).
- **Reuse subagent definitions as roles:** "Spawn a teammate using the security-reviewer agent type…" — the definition's `tools` and `model` apply; its body is appended to the teammate's system prompt.
- **Quality gates via hooks:** `TeammateIdle` (exit 2 = send feedback, keep it working), `TaskCreated` / `TaskCompleted` (exit 2 = block) — see [Chapter 7](07-hooks.md).
- **Shut down gracefully:** "Ask the researcher teammate to shut down."

### When teams beat subagents

Research/review from multiple angles, debugging with **competing hypotheses** ("spawn 5 teammates, have them try to disprove each other's theories"), cross-layer features where each teammate owns separate files. For sequential work or same-file edits, a single session or subagents win — teams add coordination overhead and each teammate burns its own tokens.

### Practical rules (official best practices)

- 3–5 teammates for most workflows; ~5–6 tasks per teammate.
- Teammates load CLAUDE.md/MCP/skills but **not** the lead's conversation — put task context in the spawn prompt.
- Prevent file conflicts: each teammate owns different files.
- Permissions: teammates inherit the lead's mode at spawn; their permission prompts bubble up to the lead. A teammate's message can't approve permissions or bypass denies.
- Known limits: no session resumption of in-process teammates, one team per session, no nested teams, lead is fixed.

---

## Dynamic Workflows (v2.1.154+)

A **workflow** is a JavaScript script that orchestrates subagents at scale — Claude writes it for the task you describe, the runtime executes it in the background, and your context receives only the final report. Use it for codebase-wide audits, 100+-file migrations, fix-until-green loops, and cross-checked research.

**Trigger:**

- Include the keyword `ultracode` in a prompt (or just say "use a workflow"):
  ```text
  ultracode: audit every API endpoint under src/routes/ for missing auth checks
  ```
- `/effort ultracode` — Claude plans a workflow for *every* substantive task in the session (xhigh reasoning + auto-orchestration; session-only).
- Run the bundled `/deep-research <question>` workflow — fan-out searches, source cross-checking with adversarial verification, cited report.

**Monitor:** `/workflows` — phases, per-agent token counts, pause/resume (`p`), stop (`x`), drill into any agent. Runs are resumable in-session: completed agents return cached results.

**Save & reuse:** press `s` in `/workflows` to save the run's script to `.claude/workflows/` (team, committed) or `~/.claude/workflows/` (personal). It becomes a `/<name>` command that can take `args`.

**Safety/cost:** workflow subagents always run in `acceptEdits` mode and inherit your tool allowlist; shell/web/MCP calls outside the allowlist still prompt. Caps: ~16 concurrent agents, 1,000 per run. Gauge spend on a small slice first. Disable org-wide with `disableWorkflows` if needed.

**Size guideline (v2.1.202+):** the **Dynamic workflow size** setting in `/config` caps the scale Claude aims for when writing workflow scripts: `unrestricted` (default), `small` (<5 agents), `medium` (<15), `large` (<50). It is sent to Claude as advice — an explicit prompt still overrides it, and the runtime caps above always apply. Changes take effect on the next prompt.

---

## Background Agents (`claude agents`)

A dashboard for many independent sessions: dispatch tasks, monitor progress, and collect results. Since 2.1.198, background agents that finish code work in a worktree **auto-commit, push, and open a draft PR**, and fire `Notification` hooks (`agent_needs_input` / `agent_completed`) you can route to Slack/desktop. Combine with `claude -w` worktrees ([Chapter 12](12-monorepo-parallel.md)) for conflict-free parallelism.

---

## The Claude Agent SDK

For programmatic multi-agent systems (services, CI bots, custom orchestrators), the **Claude Agent SDK** (TypeScript/Python) exposes the same engine Claude Code runs on: sessions, subagents (`agents` option), hooks, MCP connections, permission modes, and the Workflow tool. The GitHub Action ([Chapter 13](13-editors-cicd.md)) is built on it. Typical patterns:

- **Orchestrator-workers:** one SDK session spawns task-specific subagents with restricted tools (same frontmatter fields as file-based subagents, passed as JSON).
- **Pipelines:** chain `query()` calls, passing structured output between stages.
- **Custom harnesses:** define agents + hooks + MCP in code, deploy as a service.

Docs: [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview).

---

## Connecting agents across tools and vendors

What to use when the agents aren't all Claude Code sessions:

### MCP as the interconnect

MCP connects an agent to **tools** — and since any agent can be wrapped *as* an MCP server, it's also the pragmatic way to let one agent call another today. Patterns in production use:

- **Agent-as-MCP-server:** expose a specialized agent (e.g. an SDK-built reviewer) as an MCP tool that Claude Code calls like any other tool. The official `mcp-server-dev` plugin scaffolds servers.
- **Channels (2.1.x):** an MCP server can push events *into* a Claude Code session (Telegram/Discord/webhooks), so external systems — including other agents — can wake and message your session. Gated by `channelsEnabled` for orgs.
- **Shared external state:** multiple agents coordinating through an issue tracker, task queue, or database that all of them reach via the same MCP server — crude but robust, and the pattern behind most "agent swarm" products.

### A2A (Agent2Agent protocol)

For **cross-vendor** agent-to-agent communication, the Linux Foundation's **A2A protocol** (donated by Google in 2025) is the emerging standard: v1.0 stable landed March 2026 (v1.0.0 released 2026-03-12) with signed Agent Cards, 150+ member organizations, SDKs in Python/JS/Java/Go/.NET, and support in Microsoft Copilot Studio, Azure AI Foundry, and Amazon Bedrock AgentCore. The accepted framing: **MCP connects agents to tools; A2A connects agents to agents** — production stacks run both.

Anthropic has not (as of July 2026) shipped native A2A support in Claude Code; its native answer is agent teams + the Agent SDK. If you need Claude agents in an A2A mesh, wrap an Agent SDK service with an A2A server library.

### Community orchestrators

- **ruflo** (formerly `claude-flow`, repo renamed to [`ruvnet/ruflo`](https://github.com/ruvnet/ruflo); ~63k stars, active) — "agent meta-harness" for swarm-style orchestration across Claude Code, Codex, and others, with adaptive memory and RAG. Powerful, but a large third-party dependency — evaluate before adopting; prefer native teams/workflows when they suffice.
- **ECC** (formerly `everything-claude-code`, renamed to [`affaan-m/ECC`](https://github.com/affaan-m/ECC); ~225k stars, active) — harness optimization system (skills, instincts, memory, security) spanning Claude Code/Codex/Cursor. Cherry-pick components.

### Decision guide

1. All-Claude, one machine, needs discussion between workers → **agent teams**.
2. All-Claude, big fan-out with a repeatable plan → **dynamic workflow**.
3. All-Claude, independent tasks → **background agents + worktrees**.
4. Programmatic/service integration → **Agent SDK** (optionally exposed via MCP).
5. Cross-vendor mesh → **A2A** for agent↔agent, **MCP** for agent↔tools.

---

**Sources:**
- [Agent teams (official)](https://code.claude.com/docs/en/agent-teams)
- [Dynamic workflows (official)](https://code.claude.com/docs/en/workflows)
- [Agent view / background agents (official)](https://code.claude.com/docs/en/agent-view)
- [Claude Agent SDK (official)](https://code.claude.com/docs/en/agent-sdk/overview)
- [Claude Code changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) (2.1.154–2.1.202)
- [Linux Foundation: A2A surpasses 150 organizations](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year) · [A2A one-year report (AIwire, Apr 2026)](https://www.hpcwire.com/aiwire/2026/04/09/linux-foundation-a2a-protocol-marks-one-year-with-broad-enterprise-and-cloud-adoption/)

**Next:** [Chapter 11: Context Management →](11-context-management.md)
