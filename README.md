> [English](README.md) · [中文说明](README_zh.md)

# Js_Agent-Skills: A Collection of Self-Contained Skills for AI Agents

`Js_Agent-Skills` is a repository of Agent Skills developed and maintained by **Jiaming Shi**. It provides standardized, auditable, and reliable local execution capabilities for various AI-agent harnesses.
Each skill in this repository is an independent, self-contained package. No complex installation or build step is required to run a skill — it can be dropped directly into any agent environment that supports the Skill specification.

- [Design Principles and Core Features](#design-principles-and-core-features)
- [Download and Install](#download-and-install)
- [Quick Start](#quick-start)
- [Release Scope](#release-scope)
- [Repository Layout](#repository-layout)
- [Development and Contribution](#development-and-contribution)
- [Reporting Issues](#reporting-issues)
- [License](#license)

## Design Principles and Core Features

1. **Agent-Native**: Each skill ships a `SKILL.md` with standard metadata. The agent reads that file on its own, understands the skill's scope and execution steps, and autonomously invokes the underlying scripts.
2. **Zero-Dependency Deployment**: Skills use only the Python standard library wherever possible, avoiding complex dependency chains and ensuring plug-and-play across platforms (Windows / macOS / Linux).
3. **Deterministic Safety**: To guard against execution hallucinations, each skill enforces verifiable, rollback-capable operations with complete audit logs.
4. **Trigger-to-Act**: Each skill's `SKILL.md` opens with a mandatory workflow, so a matching request makes the agent *run* the tool and report the result — never answer with a description of what the tool does.

### The six skills

The six installable skills are grouped by function. Each row links to that skill's `README.md` (the table is the single place you read all of them; the linked README is the per-skill deep-dive).

| | Category | Skill | One-line summary | Dependencies |
| :--- | :--- | :---: | :--- | :--- |
| | **File & Project Management** | [`Js_task-organizer`](Js_task-organizer/README.md) v1.1.0 | Reorganize a messy task folder into a verified three-tier structure, with a broadcast center as a context-compression index | Standard library |
| | | [`Js_document-evolution-tracker`](Js_document-evolution-tracker/README.md) v1.0.0 | Track version alignment and concept lineage across a document family; auto-discovers versions, block-level diffs, timeline report | Standard library |
| | **Experiment State & Scheduling** | [`Js_multi-dim-manager`](Js_multi-dim-manager/README.md) v1.1.0 | Cartesian-expand a parameter space into independent rounds for auto-running many same-type tasks | Standard library + PyYAML (optional, for YAML configs) |
| | **Data Analysis & Extraction** | [`Js_longitudinal-analysis`](Js_longitudinal-analysis/README.md) v1.0.0 | Longitudinal statistics pipeline: descriptive, manipulation check, LMM, lagged mediation, sensitivity | `pandas`, `numpy`, `scipy`, `statsmodels`, `openpyxl`; optional `Rscript` + `lme4`/`lavaan` |
| | **Verification & Detection** | [`Js_formula-validator`](Js_formula-validator/README.md) v1.0.1 | Deterministic physics / math formula checker; multi-layer independent checks with a report | Standard library |
| | | [`Js_conflict-detector`](Js_conflict-detector/README.md) v1.0.0 | Cross-document conflict detector; extracts numeric / boolean claims and classifies clauses | Standard library |

## Download and Install

There are **four** standard ways to get a skill:

### Option 1: The installer binary (recommended)
The **Releases** page publishes **one installer per skill** (six in total, one per skill in this release). Download the installer for the skill you want and run it — a native installer window opens (like a standard setup program): the skill's title and description are shown fixed at the top, then you tick one or more target harness frameworks (a checklist of full names: Claude Code, DeepSeek Harness, OpenAI Codex, WorkBuddy) and pick the scope (user or project), then click **Install**; a determinate progress bar tracks the copy file by file — like a standard downloader, it shows which file is being copied and how many remain. Nothing is preselected when the window opens. When you choose the project scope, the installer first scans your machine for task folders (detected via `.git`, `.workbuddy`, `.claude`, `.codex`, `.dsh`, `.agents`, `.task-organizer.yml` markers) and lets you choose one from a drop-down — no typing required:
- **Windows**: `Js_<skill>-installer.exe` (one per skill, e.g. `Js_task-organizer-installer.exe`). Each binary bundles its own skill; double-clicking it installs just that one skill.
- **macOS / Linux**: a double-click `.app` is **not yet available** (planned). Until then, macOS and Linux users should use the source-archive route below (Option 2) or run the CLI entry points from a repo checkout.

To drive the same logic from the CLI instead (from a repo checkout, or the binary):

```bash
# List what would be installed.
python install.py --list

# Install all discovered skills to your user-scoped WorkBuddy, Claude Code, OpenAI Codex, and DeepSeek Harness.
python install.py --platform all --scope user

# Install a single skill in project scope (relative to the current working directory).
python install.py --skill Js_task-organizer --scope project

# Force-overwrite an existing install.
python install.py --platform workbuddy --scope user --force
```

Equivalent CLI entry points: `uninstall.py` (remove an installed skill) and `verify.py` (check that an installed skill is intact). The shell forwarders `install.sh` / `install.ps1` exist for users who prefer to run the installer from the shell. The Windows installers are built from `installer/installer_gui.py` (a self-contained, pure-stdlib tkinter front-end) one per skill; to rebuild the six:

```bash
# Windows: build all six per-skill installers (needs PyInstaller)
python build_installers.py
```

A double-click `.app` for macOS (and a `.sh` for Linux) is **planned but not yet shipped** — those assets will appear on the Releases page once a macOS build environment is available.

#### One-line install — no download (Windows PowerShell)

Prefer not to download anything? Run this single command in PowerShell — it fetches the installer script straight from GitHub, installs, and cleans up after itself:

```powershell
irm https://raw.githubusercontent.com/JiamingShi-JsPhys/Js_Agent-Skills/main/install-web.ps1 | iex
```

That installs **all** skills into the user scope of **Codex** (the default framework). To choose skills, frameworks, or scope, pass parameters via a scriptblock (the `| iex` form cannot take arguments):

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/JiamingShi-JsPhys/Js_Agent-Skills/main/install-web.ps1))) -Skill Js_task-organizer -Frameworks workbuddy,claude -Scope user
```

Parameters: `-Skill` (a skill name, comma-separated names, or `*` for all), `-Frameworks` (`workbuddy`, `claude`, `codex`, `dsh`), `-Scope` (`user` or `project`), `-Dir` (task folder for project scope), `-Repo` / `-Branch` (defaults: this repository, `main`), `-Force` (overwrite existing installs). Windows PowerShell 5.1+; no Python required.

> **Why not "Open" straight from the browser?** A browser's download dialog ("Open / Save / Save as") can never run an `.exe` directly from the web — even "Open" first saves the file to a temporary folder and executes that copy. That is a browser security boundary and cannot be bypassed. The one-line command above is the standard equivalent: it runs online and leaves nothing on disk except the installed skills.

### Option 2: The source archive
From the **Releases** page (or "Generate ZIP / Generate Tarball"), download the source archive and unpack it — no installer required:
```bash
# from the .zip or .tar.gz on the Releases page
unzip js_agent_skills-<version>.zip        # or: tar xzf js_agent_skills-<version>.tar.gz
cd js_agent_skills   # each skill is its own top-level folder
```

### Option 3: Fetch via an Agent
Copy the instruction below to your agent; it will locate the matching skill and install it for you:

> Visit the repository https://github.com/JiamingShi-JsPhys/Js_Agent-Skills, find the skill folder you need (name the skill or describe its function), read the `README.md` inside that folder, and follow its instructions to download or install the skill.

You only need to tell the agent the skill name — it handles the rest.

### Option 4: Clone the repository
```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills   # each skill is its own top-level folder
```

## Quick Start

### 1. Mount via an Agent
Point the unzipped skill folder at your agent harness. When a user request matches the skill's scope, the agent reads the `SKILL.md` in that folder and follows its mandatory workflow to invoke the underlying scripts. Note: whether a skill is loaded depends on the agent's recognition of its scope; it is not guaranteed to trigger in every conversation.

### 2. Run via CLI Directly
Each skill provides a Python-based command-line interface. For `Js_task-organizer`:

```bash
cd Js_Agent-Skills/Js_task-organizer
python -m scripts.run /path/to/task_folder
```

For a skill such as `Js_conflict-detector`:

```bash
cd Js_Agent-Skills/Js_conflict-detector
python -m src.cli --help
```

### 3. Use as a Python Library (Example)
```python
from pathlib import Path
from scripts import run   # refer to the actual implementation inside the skill

result = run.organize(Path("/path/to/task_folder"))
print(result.summary_lines())
```
> Note: The above is an example. The actual interface is defined by the documentation inside each skill folder.

## Release Scope

This round's release includes the six installable skills:

- `Js_task-organizer`, `Js_formula-validator`, `Js_multi-dim-manager`, `Js_longitudinal-analysis`, `Js_conflict-detector`, `Js_document-evolution-tracker`.

In addition, **six per-skill installer binaries** (one double-click `.exe` per skill for Windows, built from `installer/` with PyInstaller) are published as release assets on the **Releases** page, so users can install a single skill without cloning the repository. The macOS `.app` and Linux `.sh` are planned and not yet available; on those platforms use the source-archive route above.

## Repository Layout

All released skills live at the **repository root** as independent top-level folders. The tree below is a 1:1 mapping of the on-disk layout: top-level directories first, then files, each group in **alphabetical order**. The internal layout of every skill is documented in that skill's own README.

```
Js_Agent-Skills/
├── Js_conflict-detector/                     # cross-document conflict detector
├── Js_document-evolution-tracker/            # version alignment + concept lineage
├── Js_formula-validator/                     # deterministic physics / math formula checker
├── Js_longitudinal-analysis/                 # longitudinal statistics pipeline
├── Js_multi-dim-manager/                     # multi-dimensional experiment state manager
├── Js_task-organizer/                        # task-folder organizer + broadcast center
├── installer/                                # cross-platform installer (native tkinter window + core)
│   ├── __init__.py
│   ├── assets/
│   │   └── README.md                         #   icon assets (place platform icons here)
│   ├── installer_core.py                     #   GUI-agnostic install / uninstall / verify
│   ├── installer_gui.py                      #   double-click target (packaged with PyInstaller)
│   ├── platform_paths.py                     #   (platform, scope) -> target directory
│   ├── requirements.txt
│   └── skill_loader.py                       #   auto-adaptive skill discovery
├── tests/                                    # installer unit tests
├── .gitignore
├── AUTHORS.md
├── audit_pre_publish.py                      # pre-release consistency audit
├── build_installers.py                       # per-skill .exe builder (PyInstaller)
├── build_release.py                          # per-skill source-archive builder
├── CITATION.cff
├── install-web.ps1                           # one-line web installer (PowerShell)
├── LICENSE
├── README.md
├── README_zh.md
├── VERSION
├── conftest.py
├── install.ps1
├── install.py
├── install.sh
├── uninstall.py
└── verify.py
```

A skill is a directory containing a `SKILL.md`; `skill.json` carries the richer metadata. Every released skill ships at least `SKILL.md`, bilingual READMEs, `LICENSE`, `CHANGELOG.md`, `skill.json`, `requirements.txt`, and a `tests/` suite; most also ship `pyproject.toml`, `CITATION.cff`, and `AUTHORS.md` (the formula validator is the exception), plus per-skill extras such as `CONTRIBUTING.md`, config examples, or `src/` / `scripts/` / `mcp_server/` code trees.

## Development and Contribution

This repository follows strict open-source engineering standards. If you wish to submit a new skill or fix an existing issue:

1. **Independence**: Each skill must live in its own folder and include a complete `LICENSE`, `README.md`, and a standard `SKILL.md` file.
2. **Quality Baseline**: Submitted Python code must include type hints and docstrings, and come with unit tests covering the core logic (target coverage >= 80%).
3. **Versioning**: Follow [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).
4. **Code Style**: Follow PEP 8 (suggested line width <= 88). Core flows must handle exceptions and degrade gracefully; avoid crashing on expected I/O errors.

## Reporting Issues

Preferred: Open an issue on the repository's **Issues** page. For security-vulnerability reports, use the alternative channel below.

Alternative (security-vulnerability reports only): Send an email to `jiamingshi_phys@outlook.com`.

- **Subject**: Must include the prefix `agent-skill_report`, the specific skill name, and a brief description.
  - Example: `agent-skill_report Js_task-organizer: path traversal allows reading outside the task folder`
- **Body**: Must include reproduction steps, expected behavior, actual behavior, and the runtime environment (OS, Python version, relevant dependencies installed).
- For severe reports like "file lost or corrupted", attach the before/after directory tree (`tree` output) and the generated `verification_report.md`.
- Contributors who submit clear, reproducible issues or pull requests will be listed in the acknowledgements of the next release notes.

## License

This repository is released under the [MIT License](LICENSE). See the `LICENSE` file in the root directory for details.

Each skill package carries its own `LICENSE` file; please refer to the declaration in that skill's folder.
