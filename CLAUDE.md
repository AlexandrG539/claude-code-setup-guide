# Project: Claude Code Configuration Guide

Agent-executable configuration guide for Claude Code. Humans and Claude agents read it to self-configure projects; verified accuracy is the product.

## Project Structure

- `README.md` — router: TOC with "Read when" triggers, agent self-configuration procedure, what's-new
- `chapters/01…15-*.md` — one topic per file, YAML frontmatter (`description`, `read_when`, `topics`, `verified`, `claude_code_version`)
- `llms.txt` — machine-readable index (llmstxt.org format, raw GitHub URLs)
- `scripts/validate_guide.py` — guide invariants check (also runs as a PostToolUse hook)

## Editing Rules

- Verify every claim against the chapter's Sources links before editing. Never state behavior not verified against official docs or live registries; drop unverifiable third-party claims rather than keep them.
- After changing chapter content, update that chapter's frontmatter `verified` date and `claude_code_version`, and keep the README header stamp on the same version.
- Chapter triggers live in three places that must stay in sync: frontmatter `read_when`, the README "Read when" column, and llms.txt annotations.
- Keep chapters under 500 lines and linked directly from README and llms.txt (one level deep). New chapters go into both indexes.
- Recommend one default per decision with an escape hatch. Text-only — no images or diagrams; agents are the primary readers.
- Use `/verify-guide` to re-verify the whole guide when a new Claude Code version ships.

## Git Conventions

- Conventional commits (`docs: …`)
- Pushing `main` publishes the guide — push only with explicit user approval
- Never force-push
