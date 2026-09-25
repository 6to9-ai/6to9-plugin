#!/usr/bin/env python3
"""Generate every client's guidance from ONE source: guide/agent-guide.md.

    python scripts/generate.py           # rewrite the generated files
    python scripts/generate.py --check   # exit 1 if any generated file is stale

Outputs (never edit these by hand; edit the source and re-run):
  plugins/6to9/skills/6to9/SKILL.md   Claude Code skill (frontmatter name + description)
  clients/cursor/6to9.mdc             Cursor rule, "Apply Intelligently" (description, no globs)
  clients/codex/AGENTS.snippet.md     block to paste into a repo's AGENTS.md
  generated/server_instructions.md    the MCP server `instructions` (the <!-- core --> part only);
                                      copied by hand into the 6to9 MCP service

Source format: YAML-style frontmatter with single-line `name:` and
`description:`, then Markdown. The text between `<!-- core -->` and
`<!-- /core -->` is the condensed guidance every MCP client receives, so its
first paragraph must stand alone within 512 characters (Codex weighs the
first 512 characters of server instructions most).

Stdlib only, so the repo needs no install step.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "guide" / "agent-guide.md"
REPO = "github.com/6to9-ai/6to9-plugin"
CORE_START, CORE_END = "<!-- core -->", "<!-- /core -->"
DESCRIPTION_MAX = 1024   # Claude Code truncates description + when_to_use at 1,536 in the listing
CORE_LEAD_MAX = 512


def provenance(target: str) -> str:
    return (f"<!-- GENERATED from guide/agent-guide.md in {REPO} by scripts/generate.py "
            f"({target}). Edit the source and re-run; never edit a copy. -->")


def parse(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit("agent-guide.md must start with a --- frontmatter block")
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if line.strip():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    for key in ("name", "description"):
        if not meta.get(key):
            raise SystemExit(f"frontmatter is missing `{key}`")
    if len(meta["description"]) > DESCRIPTION_MAX:
        raise SystemExit(f"description is {len(meta['description'])} chars; keep it <= {DESCRIPTION_MAX}")
    return meta, m.group(2).strip() + "\n"


def core_of(body: str) -> str:
    start, end = body.find(CORE_START), body.find(CORE_END)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(f"agent-guide.md needs one {CORE_START} ... {CORE_END} block")
    core = body[start + len(CORE_START):end].strip()
    lead = core.split("\n\n", 1)[0]
    if len(lead) > CORE_LEAD_MAX:
        raise SystemExit(f"the core's first paragraph is {len(lead)} chars; keep it <= {CORE_LEAD_MAX}")
    return core


def strip_markers(body: str) -> str:
    return re.sub(r"\n?<!-- /?core -->\n?", "\n", body).strip() + "\n"


def demote(body: str) -> str:
    """Drop the H1 and push every other heading down one level, so the
    block nests under the host AGENTS.md's own headings."""
    lines = [ln for ln in body.splitlines() if not ln.startswith("# ")]
    return "\n".join("#" + ln if ln.startswith("#") else ln for ln in lines).strip() + "\n"


def render(meta: dict[str, str], body: str) -> dict[Path, str]:
    full = strip_markers(body)
    return {
        ROOT / "plugins/6to9/skills/6to9/SKILL.md": (
            f"---\nname: {meta['name']}\ndescription: {meta['description']}\n---\n\n"
            f"{provenance('Claude Code skill')}\n\n{full}"),
        ROOT / "clients/cursor/6to9.mdc": (
            f"---\ndescription: {meta['description']}\nalwaysApply: false\n---\n\n"
            f"{provenance('Cursor rule')}\n\n{full}"),
        ROOT / "clients/codex/AGENTS.snippet.md": (
            f"<!-- 6to9:start -->\n{provenance('Codex AGENTS.md block')}\n\n"
            f"## 6to9: product and competitor intelligence\n\n{demote(full)}"
            f"<!-- 6to9:end -->\n"),
        ROOT / "generated/server_instructions.md": (
            f"{provenance('MCP server instructions')}\n\n{core_of(body)}\n"),
    }


def main(argv: list[str]) -> int:
    meta, body = parse(SOURCE.read_text(encoding="utf-8"))
    outputs = render(meta, body)
    if "--check" in argv:
        stale = [p for p, text in outputs.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != text]
        for p in stale:
            print(f"stale: {p.relative_to(ROOT)}")
        if stale:
            print("run: python scripts/generate.py")
        return 1 if stale else 0
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
