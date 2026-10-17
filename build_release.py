#!/usr/bin/env python3
"""Build per-skill release packages for Js_Agent-Skills.

Each skill is published independently: this script produces one .zip
per skill folder, excluding test artifacts and build noise.

Usage (from the repo root, i.e. the 本地仓库 directory):
    python build_release.py

Output: <repo_root>/release/<skill_name>-v<version>.zip

To build a single skill:
    python build_release.py --skill Js_task-organizer
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

# ------------------------------------------------------------------ config

_SKILLS = [
    "Js_task-organizer",
    "Js_formula-validator",
    "Js_multi-dim-manager",
    "Js_longitudinal-analysis",
    "Js_conflict-detector",
    "Js_document-evolution-tracker",
]

# Top-level entries to exclude from each skill zip.
_EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".venv",
    "_reports",            # formula-validator test output
    "release",            # output of this script
    ".workbuddy",
}

_EXCLUDE_FILES = {
    "RELEASE_NOTES.md",   # internal release body
    "_build",
}


def _zip_skill(skill_dir: Path, out_zip: Path) -> int:
    """Create a clean .zip for a single skill folder.

    The zip contains the skill folder itself (e.g. ``Js_task-organizer/``)
    so that extracting it into any directory yields a ready-to-use skill.
    """
    skill_name = skill_dir.name
    count = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # prune excluded dirs in-place
            dirs[:] = sorted(d for d in dirs if d not in _EXCLUDE_DIRS)
            rel_root = os.path.relpath(root, skill_dir.parent)
            for fname in sorted(files):
                if fname in _EXCLUDE_FILES:
                    continue
                abs_path = os.path.join(root, fname)
                arcname = os.path.join(rel_root, fname)
                zf.write(abs_path, arcname)
                count += 1
    return count


def _read_version(skill_dir: Path) -> str:
    """Read the version from skill.json, then SKILL.md frontmatter, else 1.0.0."""
    import json
    import re

    sj = skill_dir / "skill.json"
    if sj.is_file():
        try:
            v = json.loads(sj.read_text(encoding="utf-8")).get("version")
            if v:
                return str(v)
        except (json.JSONDecodeError, OSError):
            pass

    sm = skill_dir / "SKILL.md"
    if sm.is_file():
        m = re.search(r"^version:\s*(\S+)", sm.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip().strip('"')

    return "1.0.0"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build per-skill release packages for Js_Agent-Skills"
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Path to the repo root (default: auto-detect from script location)",
    )
    parser.add_argument("--out", default=None, help="Output directory (default: <repo>/release)")
    parser.add_argument("--skill", default=None, help="Build only this skill")
    args = parser.parse_args()

    repo_root = Path(args.repo) if args.repo else Path(__file__).parent
    if not repo_root.is_dir():
        print(f"ERROR: {repo_root} is not a directory", file=sys.stderr)
        return 1

    out_dir = Path(args.out) if args.out else repo_root / "release"
    out_dir.mkdir(parents=True, exist_ok=True)

    skills = [args.skill] if args.skill else _SKILLS

    print(f"Building per-skill release packages")
    print(f"  repo: {repo_root}")
    print(f"  out:  {out_dir}\n")

    all_ok = True
    for skill in skills:
        skill_dir = repo_root / skill
        if not skill_dir.is_dir():
            print(f"  SKIP  {skill} (directory not found)")
            all_ok = False
            continue
        version = _read_version(skill_dir)
        out_zip = out_dir / f"{skill}-v{version}.zip"
        n = _zip_skill(skill_dir, out_zip)
        size_kb = out_zip.stat().st_size / 1024
        print(f"  OK    {out_zip.name}  ({n} files, {size_kb:.1f} KB)")

    print(f"\nAll packages written to: {out_dir}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
