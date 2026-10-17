#!/usr/bin/env python3
"""Build a standalone per-skill installer executable for each skill.

Each skill gets its own double-clickable installer (e.g.
Js_task-organizer-installer.exe).  A skill is embedded into its exe as data;
when the exe runs it extracts that skill to a temp dir and shows a native
installer window (fixed title + description, multi-select harness framework
checklist, scope choice, install progress) that copies it into the matching
platform skill folder.  So 6 skills -> 6 installers.

Built with PyInstaller from a Python that has tkinter + PyInstaller.  On this
machine that is ``D:/mamba/python.exe`` (the repo venv's Python lacks tkinter,
so a GUI exe built there would crash with "No module named 'tkinter'").

**Windows + conda caveat (why this script exists):** in a conda env the
Tcl/Tk runtime DLLs (``tcl86t.dll`` / ``tk86t.dll``) live in
``<env>/Library/bin``, which is only on PATH when the env is *activated*.
PyInstaller resolves ``_tkinter.pyd``'s dependencies through PATH, so a
build launched by invoking the env's python directly silently drops those
DLLs and the frozen exe then dies with
``DLL load failed while importing _tkinter``.  We therefore put
``Library/bin`` on PATH for the PyInstaller subprocess (see
``_pyinstaller_env``), which makes PyInstaller's tcl/tk hook collect the
DLLs and the ``tcl8.6`` / ``tk8.6`` script libraries.

Usage (run from the repo root so the exes land in repo/dist):

    python build_installers.py [path-to-python-with-tkinter]
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
from installer.installer_core import INSTALL_MANIFEST  # noqa: E402

INSTALLER = REPO / "installer"
DIST = REPO / "dist"
# A Python that has BOTH tkinter and PyInstaller (see module docstring).
MAMBA_PY = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"D:/mamba/python.exe")

_SKILLS = [
    "Js_task-organizer",
    "Js_formula-validator",
    "Js_multi-dim-manager",
    "Js_longitudinal-analysis",
    "Js_conflict-detector",
    "Js_document-evolution-tracker",
]


def _stage_skill_dir(skill_dir: Path, staging: Path, keep: List[str]) -> Path:
    """Copy ONLY the manifest files of a skill to staging (lean bundle).

    The exe embeds this staged tree as its bundled skill.  Staging by
    manifest (instead of dropping a blacklist of artifacts) keeps the
    bundle -- and the temp extraction -- free of repo-only material
    (README, CHANGELOG, tests, packaging metadata, unused examples), and
    fails the build loudly when a manifest entry is missing on disk.
    """
    target = staging / skill_dir.name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    for rel in keep:
        src = skill_dir / rel
        if not src.exists():
            raise SystemExit(
                f"INSTALL_MANIFEST entry missing on disk: {skill_dir.name}/{rel}"
            )
        dst = target / rel
        if src.is_dir():
            shutil.copytree(
                src, dst,
                ignore=shutil.ignore_patterns(
                    "__pycache__", ".pytest_cache", ".mypy_cache"
                ),
            )
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return target


def _conda_env_root() -> Path:
    """Root directory of the conda env that ``MAMBA_PY`` belongs to.

    ``D:/mamba/python.exe`` sits directly in the env root, while a venv-style
    layout puts it in ``<root>/Scripts/python.exe`` -- handle both.
    """
    parent = MAMBA_PY.parent
    if parent.name.lower() == "scripts":
        return parent.parent
    return parent


def _pyinstaller_env() -> dict:
    """Environment for the PyInstaller subprocess.

    Puts the build Python's ``Library/bin`` on PATH so PyInstaller's tcl/tk
    hook can resolve ``_tkinter.pyd``'s dependent DLLs (``tcl86t.dll`` /
    ``tk86t.dll``) and bundle them into the exe.  Without this the frozen
    installer crashes at startup with
    ``DLL load failed while importing _tkinter``.
    """
    env = dict(os.environ)
    libbin = _conda_env_root() / "Library" / "bin"
    if libbin.is_dir():
        env["PATH"] = str(libbin) + os.pathsep + env.get("PATH", "")
    else:
        print(f"  WARNING: {libbin} not found; tcl/tk DLLs will NOT be bundled")
    return env


def _build_one_data(skill: str, staging: Path) -> Path:
    """Build with the skill bundled as data via --add-data (CLI form)."""
    keep = INSTALL_MANIFEST.get(skill)
    if not keep:
        raise SystemExit(
            f"{skill} has no INSTALL_MANIFEST entry; add one in "
            f"installer/installer_core.py before building its installer"
        )
    src = _stage_skill_dir(REPO / skill, staging, keep)
    name = f"{skill}-installer"
    out = DIST / name
    out_dir = DIST
    out_dir.mkdir(parents=True, exist_ok=True)
    if out.with_suffix("").exists() or out.exists():
        out.unlink()
    # CLI --add-data with SRC=DST; on Windows PyInstaller parses the first
    # '=' so this is safe.
    add_data = f"{src}:_BUNDLED_SKILL"
    cmd = [
        str(MAMBA_PY),
        "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--add-data={add_data}",
        f"--name={name}",
        f"--distpath={out_dir}",
        f"--workpath={staging / '_work' / name}",
        str(INSTALLER / "installer_gui.py"),
    ]
    print(f"  [{skill}] build: {name}.exe", flush=True)
    r = subprocess.run(cmd, cwd=str(REPO), env=_pyinstaller_env())
    if r.returncode != 0:
        raise SystemExit(f"PyInstaller failed for {skill} (exit {r.returncode})")
    exe = out_dir / name if (out_dir / name).exists() else out_dir / f"{name}.exe"
    if not exe.exists():
        raise SystemExit(f"expected {exe} but it does not exist")
    return exe


def main() -> None:
    if not MAMBA_PY.exists():
        raise SystemExit(f"mamba python not found at {MAMBA_PY}; pass its path as argv[1]")
    # The installer front-end is a native tkinter window, so the build Python
    # must have tkinter.  (The repo venv's Python lacks it; use the conda one.)
    r = subprocess.run(
        [str(MAMBA_PY), "-c", "import tkinter; print(tkinter.TkVersion)"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(
            f"python at {MAMBA_PY} lacks tkinter; pass a python that has it "
            f"(on this machine: D:/mamba/python.exe). Detail: {r.stderr.strip()[:160]}"
        )
    print(f"building 6 per-skill installers with {MAMBA_PY} "
          f"(tkinter {r.stdout.strip()})\n")

    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp)
        exes = [_build_one_data(s, staging) for s in _SKILLS]

    print("\n=== built installers ===")
    for exe in exes:
        print(f"  {exe.name}  ({exe.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
