#!/usr/bin/env python3
"""Release guard: a plugin content change must ship with a version bump.

Installed plugins update only when the computed version changes — the
`version` field in plugins/6to9/.claude-plugin/plugin.json wins. If content
under plugins/6to9/ changes but that version doesn't move, users already on
the plugin never receive the change (auto-update is also off by default for
third-party marketplaces, so most users only get it on their next explicit
update anyway — but a stale version means even that does nothing).

    python3 scripts/check_version_bump.py <base-ref>

Compares <base-ref> against HEAD. plugins/6to9/evals/ is excluded: evals are
a dev-only harness and are never shipped to users.
"""
from __future__ import annotations

import json
import subprocess
import sys

PLUGIN_DIR = "plugins/6to9"
EVALS_DIR = f"{PLUGIN_DIR}/evals"
PLUGIN_JSON = f"{PLUGIN_DIR}/.claude-plugin/plugin.json"


def git(*args: str) -> str:
    """Run git in the current working directory (the repo root)."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    ).stdout


def changed_plugin_files(base: str, head: str = "HEAD") -> list[str]:
    out = git(
        "diff", "--name-only", base, head,
        "--", PLUGIN_DIR, f":(exclude){EVALS_DIR}",
    )
    return [line for line in out.splitlines() if line]


def read_version_at(ref: str) -> str | None:
    """plugin.json's `version` at `ref`, or None if the file doesn't exist there."""
    try:
        text = git("show", f"{ref}:{PLUGIN_JSON}")
    except subprocess.CalledProcessError:
        return None
    return json.loads(text)["version"]


def parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise SystemExit(f"plugin.json version {version!r} is not a strict X.Y.Z semver")
    a, b, c = (int(p) for p in parts)
    return a, b, c


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: check_version_bump.py <base-ref>", file=sys.stderr)
        return 2
    base = argv[0]

    changed = changed_plugin_files(base)
    if not changed:
        print("no changes under plugins/6to9/ (excluding evals) — no version bump required")
        return 0

    base_version = read_version_at(base)
    if base_version is None:
        print(f"plugin.json did not exist at {base} — no version bump required")
        return 0

    head_version = read_version_at("HEAD")
    if head_version is None:
        print("plugin.json is missing at HEAD", file=sys.stderr)
        return 1

    if head_version == base_version or parse_semver(head_version) <= parse_semver(base_version):
        print(
            f"plugins/6to9/ changed ({len(changed)} file(s): {', '.join(changed)}) but "
            f"`version` in {PLUGIN_JSON} went from {base_version} to {head_version} — not a "
            "bump. Installed plugins only update when this version increases; bump it "
            "(semver) so the change reaches users.",
            file=sys.stderr,
        )
        return 1

    print(f"plugins/6to9/ changed and version bumped {base_version} -> {head_version}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
