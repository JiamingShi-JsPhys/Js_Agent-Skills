---
name: Js_document-evolution-tracker
description: Document evolution tracker. Use when the user has a family of document versions (timestamped or sequentially named files) and wants to see how the document changed over time -- which paragraphs / lines / sentences were added, removed, or modified between consecutive versions, and how a set of named concepts (or auto-detected headings) evolved (introduced / retained / modified / dropped). Triggers on "track document changes", "version history", "what changed between drafts", "concept lineage", "document evolution". Emits a Markdown + JSON timeline.
version: 1.0.0
author: Jiaming Shi
license: MIT
entry: src/cli.py
allowed-tools: Read, Write, Bash, Glob, Edit
dependencies:
  python: ">=3.9"
  pip:
    - PyYAML>=6.0
platforms:
  - workbuddy
  - claude
  - codex
  - dsh
---

# Js_document-evolution-tracker

A self-contained skill that tracks how a document **evolves across
versions**. Given a version family (a directory of `v1.md, v2.md, ...` or
timestamped files), it computes paragraph-level diffs between consecutive
versions and tracks a concept lineage (introduced / retained / modified /
dropped).

## MANDATORY WORKFLOW

1. Load the YAML config (`config/examples/family.yaml` as reference).
2. Verify `versions_dir` contains at least two versioned files.
3. `python -m src.cli run --config <path> [--concepts "A,B"]`.
4. Report the transition count and point the user at
   `./evolution/evolution_<tracking_id>.{md,json}`.

## When to use

- A family of document versions (timestamped or sequentially named) must
  be compared over time.
- The user asks "track document changes", "version history", "what
  changed between drafts", or "concept lineage".
- A named concept (a term, a heading, a definition) must be traced across
  drafts to see when it was introduced, modified, or dropped.
- The evolution of a draft must be reported as a timeline rather than a
  single end-to-end diff.

## Usage examples

```bash
# Validate a config and see the discovered version files.
python -m src.cli validate --config config/examples/family.yaml
python -m src.cli versions --config config/examples/family.yaml

# Run the tracker; optionally name the concepts to follow.
python -m src.cli run --config config/examples/family.yaml --concepts "entropy,partition function"
```

Reports are written to `./evolution/evolution_<tracking_id>.{md,json}`;
the Markdown timeline is for readers, the JSON for programmatic use.

## Failure handling

- **Config invalid** (`validate` exits non-zero) - fix the reported field
  and re-validate; the naming scheme and `versions_dir` are the usual
  culprits.
- **Fewer than two versions discovered** - the run aborts; check the
  `version_naming` rule against the actual filenames and retry.
- **A concept never appears** - it is reported as absent across all
  versions, which is a valid result, not an error.
- **Unexpected exit code** - report the message verbatim; do not fall back
  to diffing the files by hand.

## Diff granularity

| Granularity | Split rule |
| --- | --- |
| `line` | Non-empty lines |
| `paragraph` (default) | Blank-line separated blocks |
| `sentence` | Punctuation-delimited sentences |

## Limitations

- Diffing is **structural** (block alignment via `difflib`), not semantic.
  A concept is "present" only when its exact phrase (case-insensitive)
  appears in the version's text.
- Custom naming schemes beyond `sequential` / `timestamp` are not
  supported.
