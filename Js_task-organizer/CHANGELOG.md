# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-10-14

Version counter restarted at 1.0.0 (2026-10-14). The full feature set of
the prior 1.1.x line is retained unchanged - this release only resets the
version number to a fresh baseline.

### Not claimed

The activation decision is made from a one-line description before SKILL.md
is read, so some wordings may still slip through; that is inherent and
accepted.

## Previous development history (archived, pre-1.0.0 restart)

## [1.1.1] - 2026-10-13

A directional fix to the trigger surface, prompted by two more live misses (a study plan written inside a learning-materials folder; a single read-then-write report job judged too small to need organizing).

### Changed

- **The trigger is now a general rule, not a growing keyword list.** The frontmatter description leads with the situation - a workspace folder plus any file activity - and labels the example words illustrative, not exhaustive. New phrasings keep appearing and no enumeration can cover them all, so the rule deliberately does not try; it states the situation instead. The same general rule is repeated in the When to use and Content-production scenarios sections: producing ANY deliverable inside a task folder triggers the bookend loop, regardless of the deliverable name.
- **The trigger no longer depends on task size.** A single write inside a task folder fires the compound intent just as a multi-step project does; the description and the Chinese guide now say so explicitly.

### Not claimed

This does not guarantee the skill loads for every possible phrasing. The activation decision is made from a one-line description before SKILL.md is read, and some wordings will still slip through - that is inherent and accepted. The change makes the rule general and situational rather than trying to enumerate cases.

## [1.1.0] - 2026-10-13

1.1.0 turns the bookend loop from **documentation into a mechanism**. The
previous line proved the rules were right but not self-enforcing: two live
tests showed agents skipping the loop entirely - once on a pure writing
request ("write an open-study report from these transcripts" inside a task
folder: the deliverable landed loose at the root, no `init` / `organize` /
`broadcast` ran), and once on a "read these files and write a report"
request where the skill was never even loaded. This release closes both
gaps, and pays for the always-on structure check with a
context-compression layer that costs nothing when nothing changed.

### Fixed

- **Content production is now a hard constraint, not a suggestion.**
  `SKILL.md` states explicitly that producing *any* deliverable inside a
  task folder (report, review, article, abstract, proposal, table) **MUST**
  be paired with the full bookend loop - `init` at task start and
  `organize` + `broadcast` before the final answer - with no separate
  "please organize" request required. Leaving the folder loose after a write
  is named a **failure mode**, not a valid shortcut. The "When to use"
  matched-trigger bullet repeats the same hard-constraint rule so the
  emphasis is not diluted to a single paragraph.

- **The trigger surface now covers the read-then-write shapes.** The
  activation decision is made from the one-line registry description
  *before* SKILL.md is ever read, so a description that only advertises the
  "organize a folder" shape lets a pure writing request pass by unloaded.
  The frontmatter description now explicitly covers "reading files in the
  folder and writing anything from them (report, feasibility study, review,
  summary, notes, article, proposal, thesis proposal, abstract, final
  draft)" and adds `feasibility`, `summary`, `notes`, `write-up` to the
  trigger words.

- **A SESSION-START rule sits on the trigger surface.** Once a workspace
  folder is known, the first action is the read-only structure check
  (`doctor <root>`) - cheap, idempotent, changes nothing - and `init` runs
  only when the check reports the structure missing. Every conversation now
  starts from a tidy folder without waiting for an organize request: it is
  step 1 of the MANDATORY WORKFLOW and the first always-on bullet in "When
  to use", with contract tests locking the wording. The read-only check
  runs before any user confirmation precisely because it moves nothing.

- **Chinese deliverable keywords extended.** A live audit showed `总结.md` /
  `终稿.docx` falling through to `process/` although both are finished
  deliverables. `总结`, `终稿`, `小结` now route to `results/` alongside the
  existing `定稿` / `最终版` / `综述` / `报告` (which already worked -
  `研究课题可行性报告.md` was verified to reach `results/`).

- **The user-level standing rule was actually written.** The deterministic
  per-session injection channel (user-level MEMORY.md) was empty - the rule
  that drives the bookend loop had never landed there, which is why the
  always-on behaviour never actually ran. It now carries the session-start
  structure check, the content-production hard constraint, the deliverable
  naming requirement, and the read-the-index-first rule.

### Added

- **Contract test `test_content_production_is_a_hard_constraint`.**
  Guards the hard-constraint wording ("hard constraint", "bookend loop",
  "skippable/deferrable", "failure ... loose") against future doc edits -
  if the phrasing is removed or softened, the test fails.

- **Self-check gate C8 (a warning, never a rollback).**
  `verify` now runs 8 checks instead of 7. C8 fires when the standard
  three-tier structure is missing while loose files still sit at the folder
  root - the signature of a task where the agent produced a deliverable but
  skipped `init`. It writes a `"run init first"` hint to the verification
  report and to the console so the missed bookend becomes visible instead of
  silent. C8 is warning-severity: it does not fail the run or trigger a
  rollback. Three new tests cover the pass / warn / tool-owned-file cases.

- **Complete folder tree in the README.**
  The top-of-README structure diagram now lists every sub-folder and
  generated file: `_broadcast/` (`INDEX.md`, `index.json`), `material/`
  (`initial/`, `downloaded/`, `duplicates/`, `Index.md`, `Index.xlsx`),
  `process/` (snapshots, `sources.json`, `verification_report.md`,
  `history/`, `logs/`), and `results/` (deliverables named with
  final / deliverable / report / review / summary).

- **E-tier: `init` builds the broadcast map on the spot.**
  `init_folder()` now runs a first `broadcast` pass the moment the three-tier
  skeleton is built, so `_broadcast/INDEX.md` + `index.json` exist before any
  content work begins. A later session always has the cheap layer to read
  from. `--no-broadcast` opts out; `InitResult` gains `broadcast_index_path`
  and `broadcast_error`.

- **F-tier: fingerprint-gated bookend refresh (token-saving by design).**
  Refreshing the index after `organize` is *gated*, not unconditional:
  `broadcast()` accepts `skip_if_unchanged`, first computes a pure `stat`
  fingerprint (path + size + mtime over the tree, never reads content or
  extracts text) and short-circuits to a zero-cost no-op when nothing
  changed. Only a real change rebuilds the index. `run.py` wires
  `refresh_broadcast` into the organize pipeline and exposes `--no-broadcast`
  on `organize`. The gate is what keeps repeated organize runs byte-stable
  (the incremental cache and `index.json` no longer churn on every run).

- **G-tier: mandatory READ-ORDER protocol for later sessions.**
  `SKILL.md` spells out the exact read order a later session must follow so
  the index actually saves tokens: read the Directory first, resolve the
  task to 1-3 keywords, open *only* the matching originals, skim the rest
  from the digest, and route any stale/absent index through `doctor` then
  `broadcast` rather than falling back to a blind full-folder read. When a
  folder holds many or large files, the index is built and read *before*
  any original is opened. A contract test guards every one of those phrases.

- **C-tier: read-only `doctor` diagnostics command.**
  A new `doctor` subcommand (`scripts/doctor.py`) inspects a folder and
  reports whether the structure is complete, which files are stranded at the
  root, which of those look like deliverables that should be in `results/`,
  and whether the broadcast index is fresh - then prints the single next step
  to run. It writes nothing, so it is always safe; six new tests cover the
  healthy / missed-init / stale / absent / nonexistent-root / no-mutation
  states.

- **Trigger-surface contract tests**:
  `test_description_covers_content_production_shape`,
  `test_workflow_opens_with_session_start_structure_check`,
  `test_session_start_check_is_always_on`, plus the Chinese-doc mirrors
  (re-pinned to the new "user confirms before running any folder-changing
  command" wording, doctor exempted as read-only) and the new keyword cases.

No tool-behavior regression: 1.1.0 is a documentation + contract + C8
self-check + E/F-tier refresh + G-tier read-protocol + C-tier doctor +
trigger-surface release. The 338-test suite (323 prior + 3 C8 + 6 doctor +
2 G-tier + 4 trigger-surface) passes; `__version__` and the SKILL
frontmatter read 1.1.0.

## [1.0.0] - 2026-10-13

The first release of the skill. It ships the complete, proven feature set:
the three-tier task-folder organizer with forced before/after verification,
the provenance model, and the **broadcast center** - a read-only
context-compression index that lets later AI sessions read a digest first and
open only the original documents they actually need.

### Added

- **Three-tier organizer with forced verification.** `organize` builds the
  `material` / `process` / `results` structure, takes before/after
  SHA-256 snapshots and enforces 7 consistency checks (C1-C7); any error
  triggers an automatic rollback to the before-state, so the folder is never
  left half-organized.

- **Provenance manifest** (`process/sources.json`). Placement is decided by
  *who produced the file*, never by its name: `user` material is lifted
  verbatim into `material/initial/` (never renamed, never modified, never
  deleted), assistant downloads go to `material/downloaded/`. The manifest
  stores names only - no hashes, no content reads. `mark-downloaded` /
  `mark-user` declare provenance explicitly.

- **Provenance re-filing.** `organize` moves files whose registered
  provenance contradicts their current location: user material stranded in
  `process/` (dumped there by a blind first run) goes to
  `material/initial/`, registered downloads go to `material/downloaded/`.
  Declaring with `mark-user` / `mark-downloaded` and re-running therefore
  just works - no `undo`/`redo` dance. Undeclared files are never touched
  (idempotent re-runs), and tool artifacts stay protected by the exact-path
  whitelist.

- **Broadcast center (`_broadcast/`) - the context-compression index.**
  `broadcast <root>` scans every supported document (`txt` / `md` / `csv`
  / `json` / `docx` / `pdf` / `pptx` / `xlsx` / `srt` / `vtt`), extracts
  text with the standard library (`openpyxl` / `pdfminer` / `PyPDF2` are
  optional upgrades, never requirements), and writes two lightweight files:
  `_broadcast/INDEX.md` - one line per file with path, type, size, date,
  a one-sentence summary and keywords - and `_broadcast/index.json`, the
  machine-readable twin. `INDEX.md` opens with a **categorized Directory**:
  every file is filed under its most salient keyword (the topics most
  common across the corpus become the biggest headings), so a reader scans
  the directory and opens only the originals they need without reading
  every line - the whole point when a folder holds thousands of files.
  Summaries are AI-generated when `TASK_ORG_AI=1` plus a key is configured
  (or `--ai` is passed); otherwise the local mode keeps the first 200
  characters and derives keywords statistically (English word frequency,
  Chinese character-bigram frequency). Subtitle files (`.srt` / `.vtt`)
  have their timing axis and index numbers stripped before summarization,
  so the digest summarizes the dialogue instead of a wall of metadata. The
  command is read-only with respect to the originals, idempotent, and
  bounded (per-file extraction cap, `--max-files`, soft size warning).
  `_broadcast` is a tool-owned prefix, so `init` / `organize` never
  relocate it. Works standalone on any folder, task folder or not.

- **Folder-signal trigger with propose-first semantics.** Referencing or
  attaching a folder and starting a task on it is a trigger class of its
  own: the mandatory workflow opens with a folder-signal check that PROPOSES
  one `init` ("I see you are working in `<folder>`; want me to set up the
  standard three-tier structure before we start?") and then stops - no
  command runs until the user confirms, because `init` moves existing
  content into `material/initial/` and reorganizing a referenced folder
  uninvited is a layout change the user must agree to first. An explicit
  organize / workspace request, or the compound content-production request,
  runs directly with no proposal. The proposal fires at most once per
  folder; a declined proposal is never repeated.

- **Content-production scenarios are first-class.** The frontmatter
  description claims the compound intent ("finishes producing an artifact -
  article / review / report / write-up - and wants the task folder kept in
  the standard three-tier layout"), and `SKILL.md` defines the action chain:
  `init` first (so the user's inputs are registered), produce, declare
  provenance, name the deliverable, `organize`.

- **Chinese deliverable keywords** in the built-in fallback table:
  `定稿` / `最终版` / `综述` / `报告` -> `results/` and `草稿` / `临时`
  -> `process/`. A finished `综述_xxx.txt` no longer falls through to
  `process/` because it lacks an English `final` in its name.

- **`init`** - the cheap entry point: skeleton + lift + config template,
  with no snapshot, no verification and no log file, so creating a task
  folder is instant.

- **Execution tiers** (`--mode quick|incremental|full`, default `full`):
  `incremental` reuses SHA-256 digests for files whose size and mtime are
  unchanged (hidden hash cache); `quick` is the no-frills tidy pass; `full`
  stays the guarantee tier.

- **Artifact rotation** (`--keep N`, default 5) keeps `process/` from
  growing without bound; the newest before/after snapshots are always
  protected.

- **Standalone `index` and `snapshot` sub-commands** - regenerate the
  hand-off indexes, or take the safety airbag before a risky batch
  operation.

- **Operation history & undo / redo** (`process/history/`):
  user-initiated reversal or re-application of a verified run, itself
  wrapped in the snapshot/verify/rollback protocol.

- **Smart deduplication** (`--dedupe-action report|move`): exact
  (SHA-256) and similar (first-1-KB prefix + `difflib` ratio >= 0.85)
  duplicates; `move` quarantines exact duplicates into
  `material/duplicates/` (originals are never deleted) and is covered by
  the forced verification.

- **YAML placement-rule config** (`.task-organizer.yml`) with named
  domain profiles (`--profile`), parsed by a dependency-free mini-reader
  that falls back to the built-ins on any error.

- **Per-day logging** (`process/logs/YYYYMMDD.log`) at INFO level, with
  `-v` / `-q` console control.

- **Agent-facing workflow**: `SKILL.md` opens with a mandatory workflow
  (resolve the path, pick the entry point, run via Bash, verify, report,
  declare provenance) so triggering the skill means *running* the tool,
  never answering with a description of it. Mirrored in `给中文用户.md`.

- **The skill is pure English.** `SKILL.md` and `README.md` carry no CJK;
  the dedicated Chinese user guide remains separate.

- Test suite: **323 passing cases** (0 skipped when the dependencies are
  absent), coverage >= 80%.

### Hardening

Hardening found by two adversarial debug rounds before the release (both
rounds plus regression tests are part of the shipped 1.0.0):

- **Legacy encodings decoded as mojibake.** `text_extract` sniffs the
  encoding (BOM, then UTF-8, GBK/GB18030, Big5, a NUL-density probe for
  BOM-less UTF-16, latin-1 last) and rejects decodes that land in the
  Unicode private-use area - GBK/Big5 bytes under the wrong codec do
  exactly that. Chinese notes saved in GBK/Big5/UTF-16 now summarize
  correctly.

- **Unbounded reads.** Plain-text files are read with a bounded character
  count after a 64 KB encoding probe, and the stdlib PDF path caps its
  byte read, so a 500 MB log cannot exhaust memory.

- **Symlink cycles and hidden trees.** The scan walks with
  `os.walk(followlinks=False)` and prunes hidden directories, `process/`
  and `_broadcast/` before descending, so a symlink loop or a `.git`
  tree can neither hang the scan nor waste time inside it. Index paths
  use forward slashes on every platform.

- **Unbounded skip list.** When `--max-files` bites, the skipped list
  stays aggregated (one line) while the count still reports every file.

- **Markdown-breaking names.** Filenames containing backticks no longer
  break the one-line-per-file bullet; summaries are whitespace-collapsed.

- **AI mode told the truth.** `--ai` without a key degraded to local
  summaries while the index still claimed `ai`; the mode label now
  reflects what was actually used. `--ai` also forces AI past the
  `TASK_ORG_AI` opt-in when a key is configured, and one call returns
  both the summary and the keywords (half the round trips).

- **Local keyword quality.** Chinese keywords are repeated 2-4 character
  n-grams extended to their full repeated phrase (a frequent fragment is
  superseded by the longer phrase), with overlapping fragments dropped;
  summaries cut at a sentence boundary when one is near. PDF page counts
  are only computed for the metadata fallback instead of re-reading every
  PDF.

- **Built-in keyword table restored for folders with a config.** A folder
  that has the comment-only `.task-organizer.yml` template (exactly what
  `init` writes) previously lost the built-in keyword rules, so deliverable
  names like `开题报告_*.md` fell through to `process/` instead of
  `results/`. An empty / comment-only config now silently uses the
  built-in placement table, so `报告` / `final` still route correctly.
