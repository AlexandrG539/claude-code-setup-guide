#!/usr/bin/env python3
"""Validate guide invariants: chapter frontmatter, line limits, links, stamps.

Run from the repo root: python3 scripts/validate_guide.py
Exit 0 = all checks pass; exit 1 = violations printed to stdout.
"""
import glob
import os
import re
import sys

REQUIRED_FIELDS = ("description", "read_when", "topics", "verified", "claude_code_version")
MAX_LINES = 500          # official SKILL.md guidance, applied to chapters
MAX_DESCRIPTION = 1024   # official frontmatter description cap

errors = []
chapters = sorted(glob.glob("chapters/*.md"))
if not chapters:
    print("ERROR: no chapters/*.md found — run from the repo root")
    sys.exit(1)

versions = set()
for path in chapters:
    text = open(path, encoding="utf-8").read()
    lines = text.count("\n") + 1
    if lines > MAX_LINES:
        errors.append(f"{path}: {lines} lines exceeds the {MAX_LINES}-line target")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{path}: missing YAML frontmatter")
        continue
    fm = m.group(1)
    for field in REQUIRED_FIELDS:
        if not re.search(rf"^{field}:", fm, re.M):
            errors.append(f"{path}: frontmatter missing `{field}`")
    desc = re.search(r'^description:\s*"(.*?)"\s*$', fm, re.M)
    if desc and len(desc.group(1)) > MAX_DESCRIPTION:
        errors.append(f"{path}: description exceeds {MAX_DESCRIPTION} chars")
    ver = re.search(r'^claude_code_version:\s*"?([\d.]+)"?', fm, re.M)
    if ver:
        versions.add(ver.group(1))

if len(versions) > 1:
    errors.append(f"chapters disagree on claude_code_version: {sorted(versions)}")

# All relative markdown links must resolve.
for path in ["README.md"] + chapters:
    text = open(path, encoding="utf-8").read()
    base = os.path.dirname(path)
    for link in re.findall(r"\]\((?!https?://|#|mailto:)([^)#]+)(?:#[^)]*)?\)", text):
        target = os.path.normpath(os.path.join(base, link))
        if not os.path.exists(target):
            errors.append(f"{path}: broken relative link -> {link}")

# Every raw URL in llms.txt must map to a file in the repo.
if os.path.exists("llms.txt"):
    for url_path in re.findall(r"raw\.githubusercontent\.com/[^/]+/[^/]+/main/([^)\s]+)", open("llms.txt").read()):
        if not os.path.exists(url_path):
            errors.append(f"llms.txt: URL points to missing file -> {url_path}")
else:
    errors.append("llms.txt missing from repo root")

# README header stamp must match chapter frontmatter version.
readme = open("README.md", encoding="utf-8").read()
if versions:
    (only_version,) = versions or {""}
    if f"**{only_version}**" not in readme:
        errors.append(f"README.md: header does not mention Claude Code **{only_version}**")

if errors:
    print(f"GUIDE VALIDATION FAILED ({len(errors)} issue(s)):")
    for e in errors:
        print(f" - {e}")
    sys.exit(1)
print(f"guide validation passed: {len(chapters)} chapters, llms.txt, README consistent")
