>[English](README.md) · [中文说明](README_zh.md) 
# Js_Agent-Skills: A Collection of Self-Contained Skills for AI Agents

`Js_Agent-Skills` is a repository of Agent Skills developed and maintained by Jiaming Shi. It aims to provide standardized, auditable, and reliable local execution capabilities for various AI Agent harnesses.

Each subfolder in this repository is an independent, self-contained Skill package. No complex installation or build steps are required — it can be dropped directly into any AI Agent environment that supports the Skill specification.

## Design Principles

1. **Agent-Native**: Each Skill package contains a `SKILL.md` file with standard metadata. The Agent can read this file on its own, understand the skill's scope and execution steps, and autonomously invoke the underlying scripts.
2. **Zero-Dependency Deployment**: Skill packages use only the Python standard library wherever possible, avoiding complex dependency chains and ensuring plug-and-play across platforms (Windows / macOS / Linux).
3. **Deterministic Safety**: To guard against execution hallucinations from AI, each skill enforces verifiable, rollback-capable operations with complete audit logs.

## Skill Directory Structure

This repository is a growing skill library. Each skill is independent and does not interfere with others.

| Folder | Skill Name | Core Functionality |
| :--- | :--- | :--- |
| `Js_task-organizer/` | Js_task-organizer | Reorganizes a messy task folder into a standardized three-tier structure (`material` / `process` / `results`, plus the tool's own `_broadcast/` index directory). It includes mandatory before/after snapshots, 8-check verification (C1–C8), and automatic rollback on failure. It also provides a broadcast center (a read-only context-compression index in `_broadcast/` so later sessions read the digest first and open only the original documents they need) and a startup read-only diagnostic (`doctor`). Other features: provenance-based filing, operation history, smart deduplication, YAML placement rules, and per-day logging. |
| *(planned)* | *TBD* | *The author will continue to contribute independent skill packages for research, data processing, and AI workflows.* |

## How to Obtain and Install

There are two standard ways to get a skill:

### Option 1: Download a Release Package (Recommended)
1. Go to the repository's **Releases** page (right sidebar or tag list).
2. Download the latest Release zip for the skill you want (e.g., `Js_task-organizer-v1.2.1.zip`).
3. Unzip it to any directory. No installation step required.

### Option 2: Clone the Repository
```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_task-organizer   # or another skill folder
```

## How to Run a Skill

### 1. Mount via an Agent
Point the unzipped skill folder at your Agent harness. When a user request matches the skill's scope, the Agent reads the `SKILL.md` in that folder and follows its "Execution steps" to invoke the underlying scripts. Note: whether a skill is loaded depends on the Agent's recognition of its scope; it is not guaranteed to trigger in every conversation.

### 2. Run via CLI Directly
Each skill provides a Python-based command-line interface. For `Js_task-organizer`:
```bash
cd Js_Agent-Skills/Js_task-organizer
python -m scripts.run /path/to/task_folder
```

### 3. Use as a Python Library (Example)
```python
from pathlib import Path
from scripts import run   # refer to the actual implementation inside the skill

result = run.organize(Path("/path/to/task_folder"))
print(result.summary_lines())
```
> Note: The above is an example. The actual interface is defined by the documentation inside each skill folder.

## Development and Contribution Guidelines

This repository follows strict open-source engineering standards. If you wish to submit a new skill or fix an existing issue:

1. **Independence**: Each skill must live in its own folder and include a complete `LICENSE`, `README.md`, and a standard `SKILL.md` file.
2. **Quality Baseline**: Submitted Python code must include type hints and docstrings, and come with unit tests covering the core logic (target coverage >= 80%).
3. **Versioning**: Follow [Semantic Versioning](https://semver.org/) and [Keep a Changelog](https://keepachangelog.com/).
4. **Code Style**: Follow PEP 8 (suggested line width <= 88). Core flows must handle exceptions and degrade gracefully; avoid crashing on expected I/O errors.

## Reporting Issues and Feedback

Preferred: Open an issue on the repository's **Issues** page.

Alternative: Send an email to `jiamingshi_phys@outlook.com`.

- **Subject**: Must include the prefix `agent-skill_report`, the specific skill name, and a brief description.
  - Example: `agent-skill_report Js_task-organizer: dedupe move fails on read-only file`
- **Body**: Must include reproduction steps, expected behavior, actual behavior, and the runtime environment (OS, Python version, relevant dependencies installed).
- For severe reports like "file lost or corrupted", attach the before/after directory tree (`tree` output) and the generated `verification_report.md`.
- Contributors who submit clear, reproducible issues or pull requests will be listed in the acknowledgements of the next release notes.

## License

This repository is released under the [MIT License](LICENSE). See the `LICENSE` file in the root directory for details.

Each skill package carries its own `LICENSE` file; please refer to the declaration in that skill's folder.
