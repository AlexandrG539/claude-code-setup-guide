---
name: verify-guide
description: |
  Re-verifies this guide against the latest official Claude Code sources and updates
  version stamps. Use when asked to update, re-verify, or check the guide for staleness,
  or when a Claude Code version newer than the one in chapter frontmatter has shipped.
allowed-tools: Read, Grep, WebFetch, Bash(python3 scripts/validate_guide.py), Bash(npm view *), Bash(curl -s https://raw.githubusercontent.com/*)
---

# Verify Guide Against Official Sources

1. Read the stamped version from any chapter's frontmatter (`claude_code_version`). Get the latest release: `npm view @anthropic-ai/claude-code version`.
2. Fetch the official changelog (`https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md`) and list every entry newer than the stamped version.
3. Map each entry to chapters using the README TOC. For each touched chapter, re-verify the affected claims against that chapter's Sources links and edit only what changed. Bug fixes without behavior changes need no edits.
4. Verify every claim you edit against the official docs page or live registry first. Drop third-party claims that no longer verify instead of keeping them.
5. Update frontmatter `verified` and `claude_code_version` on all 15 chapters (a pass covers the whole guide), update the README header stamp, and add What's-New rows for meaningful changes.
6. Run `python3 scripts/validate_guide.py` and fix anything it reports.
7. Report: version delta, chapters changed, claims corrected, claims dropped. Do not push without explicit user approval.
