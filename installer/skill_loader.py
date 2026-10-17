"""Skill discovery and metadata loading for the Js_Agent-Skills installer.

The installer is *auto-adaptive*: it looks for skill directories both at the
repository root (the original layout) and under a top-level ``skills/``
directory (the 方案 C target layout). A directory is treated as a skill when
it contains a ``SKILL.md``. Metadata is read from ``skill.json`` when
present; when absent, a minimal record is synthesised from the directory
name so the installer still works for skills that only carry ``SKILL.md``.

Pure standard library.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

__all__ = [
    "SkillMeta",
    "discover_skills",
    "load_skill_meta",
]

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


@dataclass
class SkillMeta:
    """Metadata for a single installable skill."""

    name: str
    directory: Path
    version: str = "0.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    entry: str = ""
    dependencies: Dict = field(default_factory=dict)
    platforms: List[str] = field(default_factory=lambda: ["workbuddy", "claude", "codex", "dsh"])

    @property
    def has_skill_md(self) -> bool:
        return (self.directory / "SKILL.md").exists()

    @property
    def has_skill_json(self) -> bool:
        return (self.directory / "skill.json").exists()

    def summary_line(self) -> str:
        desc = self.description.split(".")[0] + "." if self.description else ""
        return f"{self.name} v{self.version} -- {desc}"


def _read_frontmatter_version(skill_md: Path) -> Optional[str]:
    """Pull the ``version:`` scalar out of a SKILL.md frontmatter block."""
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"^version:\s*(\S+)", text, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else None


def _synthesize_meta(skill_dir: Path) -> SkillMeta:
    """Build a minimal meta from a directory that lacks skill.json."""
    skill_md = skill_dir / "SKILL.md"
    version = _read_frontmatter_version(skill_md) or "0.0.0"
    return SkillMeta(
        name=skill_dir.name,
        directory=skill_dir,
        version=version,
        description="",
        author="Jiaming Shi",
        license="MIT",
        entry="",
        dependencies={},
    )


def load_skill_meta(skill_dir: Path) -> SkillMeta:
    """Load a skill's metadata from ``skill.json`` (falling back to synthesis).

    Raises ``FileNotFoundError`` if the directory does not contain a
    ``SKILL.md`` (i.e. it is not a skill at all).
    """
    skill_dir = Path(skill_dir)
    if not (skill_dir / "SKILL.md").exists():
        raise FileNotFoundError(f"not a skill directory (no SKILL.md): {skill_dir}")

    skill_json = skill_dir / "skill.json"
    if skill_json.exists():
        raw = json.loads(skill_json.read_text(encoding="utf-8"))
        return SkillMeta(
            name=str(raw.get("name", skill_dir.name)),
            directory=skill_dir,
            version=str(raw.get("version", "0.0.0")),
            description=str(raw.get("description", "")),
            author=str(raw.get("author", "Jiaming Shi")),
            license=str(raw.get("license", "MIT")),
            entry=str(raw.get("entry", "")),
            dependencies=dict(raw.get("dependencies", {}) or {}),
            platforms=list(raw.get("platforms", ["workbuddy", "claude", "codex", "dsh"])),
        )

    return _synthesize_meta(skill_dir)


def _is_skill_dir(entry: Path) -> bool:
    """A directory is a skill iff it directly contains a SKILL.md."""
    return entry.is_dir() and (entry / "SKILL.md").exists()


def discover_skills(repo_root: Path) -> List[SkillMeta]:
    """Discover installable skills across both repo layouts.

    Scans the two candidate locations:

    - ``repo_root/*``  -- skills that live at the repository root.
    - ``repo_root/skills/*``  -- skills under the 方案 C ``skills/`` dir.

    Results are de-duplicated by skill name (root wins if a name appears in
    both) and returned sorted by name for deterministic installer UI.
    """
    repo_root = Path(repo_root)
    found: Dict[str, SkillMeta] = {}

    # 1) Root-level skills.
    for entry in sorted(repo_root.iterdir()):
        if _is_skill_dir(entry):
            meta = load_skill_meta(entry)
            found.setdefault(meta.name, meta)

    # 2) skills/ subdirectory.
    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if _is_skill_dir(entry):
                meta = load_skill_meta(entry)
                # Root layout takes precedence when both define the same name.
                if meta.name not in found:
                    found[meta.name] = meta

    return sorted(found.values(), key=lambda m: m.name)
