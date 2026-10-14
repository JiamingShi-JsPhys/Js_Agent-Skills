[English](README.md) · [中文说明](README_zh.md)

# Js_multi-dim-manager

> A self-contained state manager for multi-dimensional computational experiments.
> It iterates a parameter grid over many rounds, snapshots declared critical
> files each round, audits every round, and rolls back to any round
> non-destructively. Your compute plugin does the math; this skill manages the
> state around it.

---

## Workflow after triggering (see SKILL.md for details)

When a user asks to run, inspect, or recover a multi-dimensional experiment:

1. Load the config and confirm the parameter space, critical paths, and plugin
   command are present.
2. Expand the Cartesian product and report the total round count.
3. Prefer a dry run so the user sees the full plan before any side effect.
4. Execute the sweep: snapshot critical paths before, invoke the plugin, snapshot
   after, append one audit record per round.
5. On a failed round, record its status and (if `auto_rollback`) recover the last
   good baseline — audited. Do not abort the whole sweep.
6. Summarize: write `results_summary.csv/.md`, `report_draft.md`,
   `run_metadata.json`.
7. Recover on request with `rollback` (new directory by default; `--force` to
   overwrite).

### Common request shapes

- "Run this 2x2x2 grid, 200 rounds, and tell me which combinations passed."
- "Round 47 crashed — restore its state so I can inspect the inputs."
- "Roll everything back to round 150 and re-run from there with new params."
- "Show me the audit trail for the last 10 rounds."

## How the manager keeps state

The skill treats an experiment as a state machine over rounds. Three mechanisms
keep it honest.

### Snapshots (content-addressed, critical-path only)

Only the files you declare in `critical_paths` are snapshotted — never the whole
working directory. Each file's content is stored once, addressed by its SHA-256
hash, so a file that does not change between rounds costs no extra space. A
snapshot is just a manifest: `relative_path -> content_hash`.

### Audit

Every round appends one JSON line to `audit_log.jsonl` carrying the parameter
combination, input hash, output hash, timestamp, plugin exit code, and both
snapshots (pre/post). Rollback actions are recorded too, so the entire history
is reproducible after the fact.

### Rollback (non-destructive)

`rollback --round N` restores round N's post-state. By default it lands in a NEW
directory (`<workdir>.rollback_NNNN`); only `--force` overwrites the live
working directory. Either way the action is written to the audit log.

### Guarantees

- **Traceable**: every output is tied to a parameter combination and a snapshot.
- **Recoverable**: any recorded round can be restored, with the action logged.
- **Deterministic orchestration**: the same params always yield the same plan and
  the same recorded hashes. (The plugin's own determinism is the user's job — see
  Limitations.)

## Limitations

- **Determinism is orchestration-layer only.** The manager records hashes and
  replays the same plan for the same inputs, but it cannot make a non-
  deterministic plugin deterministic. If the plugin touches the network, uses
  random seeds, or reads the wall clock, identical inputs may diverge. Declare
  such behaviour in the plugin yourself.
- **Critical paths must be declared up front.** Files not listed in
  `critical_paths` are never snapshotted and therefore cannot be rolled back.
- **Golden-output verification is v0.2.** The current verifier only checks the
  plugin contract (exit 0 + a result file). Comparison against a known expected
  output is planned but not yet implemented.
- **YAML configs need PyYAML.** JSON configs work with the standard library
  alone.

## Core features

- Parameter-space definition from JSON/YAML (Cartesian expansion).
- Per-round snapshots of declared critical files (content-addressed store).
- Full append-only audit log with input/output hashes and timestamps.
- Non-destructive rollback to any round (or `--force` overwrite).
- Result aggregation to CSV / Markdown, plus a report draft.
- A unified plugin contract: one shell command, JSON in/out, exit 0/1/2.
- Pure standard library by default — no required third-party dependency.

## Download and install

**Option 1 — Download the release zip (recommended)**

Open the repository's Releases page, download the latest zip, unzip it, and run
`pip install -r requirements.txt` — no build step required.

**Option 2 — Let an Agent fetch it**

Copy the following instruction to your Agent, and it will locate and fetch the
skill automatically:

> Please visit https://github.com/JiamingShi-JsPhys/Js_Agent-Skills/tree/main/Js_multi-dim-manager, read the README.md in that folder, and download or install the skill according to its instructions.

You only need to tell the Agent the skill name; it handles the rest.

**Option 3 — Clone the repository**

```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_multi-dim-manager
pip install -r requirements.txt
```

Requirements: Python 3.10+. No third-party package is required for JSON configs.
YAML configs need `pyyaml` (`pip install pyyaml`). The skill uses only the
Python standard library otherwise.

## Quick start

```bash
cd Js_Agent-Skills/Js_multi-dim-manager

# 0. (optional) see the full plan without running anything
python scripts/run.py dryrun --config config.example.yaml

# 1. run the sweep (writes audit log, snapshots, summaries under ./output)
python scripts/run.py run --config config.example.yaml

# 2. restore a past round into a new directory
python scripts/run.py rollback --config config.example.yaml --round 12

# 3. regenerate the summaries from the audit log
python scripts/run.py summary --config config.example.yaml

# 4. check one round's plugin-contract outcome
python scripts/run.py verify --config config.example.yaml --round 12
```

### Output shape

```
output/
  audit_log.jsonl      # one JSON line per round (+ rollbacks)
  snapshots/store/     # content-addressed critical-file store
  results_summary.csv  # flat, filterable table
  results_summary.md   # same table in Markdown
  report_draft.md      # narrative draft
  run_metadata.json    # space, plugin, timing
```

## Tests & coverage

The suite currently covers 87 cases. Run it with:

```bash
python -m pytest -q
```

Target line coverage is >= 80%, matching the repository's quality baseline. Two
YAML-config tests skip automatically when PyYAML is not installed; JSON configs
always run.

## Project layout

```
Js_multi-dim-manager/
  SKILL.md                 # agent execution guide (MANDATORY WORKFLOW)
  README.md / README_zh.md # docs (this file + Chinese)
  config.example.yaml      # configuration template
  sample_plugin.py         # example compute plugin (contract demo)
  scripts/
    param_space.py         # space parsing + expansion
    config.py              # experiment config loading
    executor.py            # plugin invocation (shell + JSON + exit 0/1/2)
    snapshot.py            # content-addressed critical-path snapshots
    audit.py               # append-only JSONL audit log
    rollback.py            # non-destructive rollback
    aggregator.py          # result table aggregation
    report.py              # Markdown summaries / draft
    verify.py              # plugin-contract verification (golden: v0.2)
    run.py                 # CLI entry point
  tests/                   # unit + documentation-contract tests
```

## Using as an agent skill

Drop the folder into any Agent harness that supports the Skill specification.
When a request matches the scope (multi-round, multi-dimensional experiment with
state to track), the Agent reads `SKILL.md` and follows its MANDATORY WORKFLOW.
The skill is self-contained: it imports nothing from sibling skills.

## License

Released under the MIT License. See `LICENSE`.

## Report issues

Open an issue on the repository's Issues page, or email
`jiamingshi_phys@outlook.com` with subject prefix `agent-skill_report`.
