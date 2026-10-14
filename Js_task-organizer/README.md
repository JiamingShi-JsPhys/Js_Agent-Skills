>[English](README.md) · [中文说明](README_zh.md) 
# Js_task-organizer

> A task organizer skill by Jiaming Shi. Its core is two jobs: keeping the
> folder in a clean standard structure, and coordinating the whole task from
> start to finish.

Js_task-organizer turns a messy task or project folder into a tidy, standard
three-tier structure, and coordinates the whole file lifecycle of the task:
it builds every structural folder at the start, registers file provenance
throughout, gives you a read-only map of the folder via the broadcast center,
and re-organizes and rebuilds the index before final delivery. This keeps the
folder tidy throughout the task and protects the context window in long
sessions.

Before and after every organize pass it takes a full snapshot and runs eight
consistency checks (C1–C8). If any error-level check fails, the folder is
rolled back to its before-state — so you are not left with a half-organized
folder.

```
task_folder/
+---- _broadcast/            # read-only context-compression digest
|   +---- INDEX.md           #   one line per file: summary + keywords + category
|   `---- index.json         #   the same digest, machine-readable
+---- material/
|   +---- initial/           # YOUR material - kept verbatim, never renamed
|   +---- downloaded/        # files the assistant fetched this session
|   +---- duplicates/        # quarantined exact duplicates (dedupe move mode)
|   +---- Index.md           # auto-generated Markdown index (file + source)
|   `---- Index.xlsx         # auto-generated Excel index (with a "Statistics" sheet)
+---- process/               # assistant output + snapshots + logs + history
|   +---- YYYYMMDD_HHMMSS_before.json   # before snapshot
|   +---- YYYYMMDD_HHMMSS_after.json    # after snapshot
|   +---- YYYYMMDD_HHMMSS_OrganizeLog.md
|   +---- sources.json       # provenance manifest (user vs. downloaded)
|   +---- verification_report.md        # C1-C8 verdict
|   +---- history/           # operation history + undo / redo
|   `---- logs/              # per-day activity log
`---- results/               # finished deliverables (name contains
                             #   final / deliverable / report / review / summary)
```

One rule matters most: `material/initial/` is yours alone. The tool never
writes anything of its own into that folder, so it cannot collide with
your files. Create the folder, drop your material in, run `init` — and that
material is left untouched.

---

## Required workflow after triggering (see `SKILL.md` for details)

> This section mirrors the "Execution steps" in `SKILL.md`. The README only
> provides an entry-point overview; the Agent should follow `SKILL.md` when
> actually scheduling tasks.

This skill is an "act immediately" instruction, not a summary document. Once
a user request matches the skill's scope, the tool must be run and the result
must be reported — replying only with a description of "what this skill is,
what it does, what commands it has" counts as a task failure.

**Scope — workspace vs. direct conversation.** This skill triggers fully
only when the user has **selected a workspace** (a task / project / research
folder): build the structure, keep it tidy, archive deliverables. If the user
is only in direct conversation and has not selected any workspace folder,
this skill does not apply.

**Standard action chain (summary):**

1. **Session-start structure check — check first, then act.** As soon as a
   workspace folder is identified in the conversation (named / referenced as
   an attachment / given a path), the first step is a read-only check:

   ```bash
   python -m scripts.run doctor <root>
   ```

   `doctor` is read-only: no writes, no moves, no content reads — a pure
   `stat` scan, zero cost, so it can run before the user confirms (it is a
   check, not a change). Report `incomplete` → run `init <root>` to build the
   structure before starting work. Report `healthy` → change nothing,
   continue. This step is idempotent: an already tidy folder is checked once,
   with zero changes.

2. **Folder-signal detection — propose first, then act.** If `doctor`
   reports a missing structure and the user has not explicitly asked for
   organization → propose `init` once; do not run any command that changes
   the folder until the user confirms. If the user explicitly asks for
   organization, or the request is a composite "produce content + keep the
   folder tidy" request → skip the proposal and run `init` directly.

3. **Determine the target folder path.** If the user gave no path, offer a
   specific default and ask them to confirm.

4. **Choose the entry point.** New / empty folder → `init`. Existing messy
   folder → `organize`.

5. **Run with Bash** (from the skill's directory):

   ```bash
   python -m scripts.run init     <root>
   python -m scripts.run organize <root>
   ```

   Requires Python 3.10+; no mandatory dependencies outside the standard
   library (`openpyxl` is only used for the Excel index).

6. **Verify before reporting.** When you see `verification: failed`, the
   tool has already rolled back — report honestly, do not blindly re-run.

7. **Concise report**: current three-tier structure, untouched material in
   `material/initial/`, verification verdict, and the option to `undo`.

8. **For the rest of the session**: every time a file is downloaded into the
   task folder, immediately declare its source with
   `mark-downloaded <root> <file> --url <URL>`.

9. **Before final delivery — organize once more and rebuild the broadcast
   index.** This is mandatory:

   ```bash
   python -m scripts.run organize  <root>
   python -m scripts.run broadcast <root>
   ```

   The broadcast index (`_broadcast/INDEX.md`) is mandatory in workspace
   tasks, not optional.

### Content-production scenarios (review / report / article / summary)

When "produce content" and "keep the task folder in the standard three-tier
structure" appear together, this skill triggers fully — **even if the word
"organize" is never mentioned**. Typical request shapes: read files in the
folder, then write a report / feasibility report / review / summary / notes
/ proposal. Note: triggering does not depend on how many steps the task has,
nor on the exact name of the deliverable — if any deliverable is produced
inside the workspace folder, even if it is written in one go, the full
organize-then-broadcast cycle must run. Standard action chain:

1. **Build the stage first.** If the folder is new or has no three-tier
   structure → run `init <root>` before writing.

2. **Produce content.** Write into the task folder (anywhere — `organize`
   will file it).

3. **Declare provenance as you go.** Your own downloads → `mark-downloaded`.
   User-provided files → already registered by `init`, or add a `mark-user`
   declaration.

4. **Give deliverables a recognizable name.** Filenames containing `final` /
   `deliverable` / `report` / `summary`are automatically filed into `results/`
   (Chinese word-tokens included).

5. **Run `organize <root>`** and report the verification verdict.

6. **Build the broadcast index.** `broadcast <root>` makes
   `_broadcast/INDEX.md` + `_broadcast/index.json` write a one-line summary
   and keywords for every file.

**Re-filing rule.** If a first blind `organize` dumped files into `process/`,
later declare their provenance (`mark-user` / `mark-downloaded`) and run
`organize` again — they will be moved back home. Files with no declaration
stay in `process/` (the assistant-output catch-all bucket), so re-runs stay
idempotent.

---

## Broadcast center (`_broadcast/`) — context-compression index

A folder may hold more documents than a single session can read. The
broadcast center is designed for this: it generates a read-only summary of
every supported file — small enough to read first in every session, detailed
enough to tell which original document to open next.

Build it:

```bash
python -m scripts.run broadcast <root> [--ai] [--max-files N] [--keywords K]
```

It writes only two files into `<root>/_broadcast/`:

| File | For whom |
|------|----------|
| `INDEX.md` | You and later AI sessions: one line per file (path, type, size, date, summary, keywords) |
| `index.json` | Program consumption: the same data, machine-readable |

Supported formats: `txt` / `md` / `csv` / `json` / `docx` / `pdf` / `pptx`
/ `xlsx`; other files are only registered in the "skipped" section. Text
extraction prioritizes the standard library (`openpyxl` / `pdfminer` /
`PyPDF2` are only enhancements), with tolerant encodings: UTF-8 (BOM
detection), UTF-16, GBK/GB18030, Big5; reads are bounded.

Two summary modes:

- **AI mode** — `TASK_ORG_AI=1` plus a key, or `--ai`: one call returns both
  a one-line summary and keywords. Without a key it falls back to local mode
  and marks the index `local` rather than falsely claiming `ai`.
- **Local mode** (default) — takes the first 200 characters of the extracted
  text (cut at a sentence boundary if possible), with statistical keywords:
  English by word frequency; Chinese expands repeated 2–4 character n-grams
  into full repeated phrases. Offline, deterministic, zero cost.

Guarantees:

- **Read-only**: original files are only opened and read — never moved,
  renamed, or modified. The only writes are the two files in `_broadcast/`.
- **Idempotent**: re-running rebuilds these two index files in place.
- **Bounded**: per-file extraction has an upper limit, `--max-files` caps the
  total, and an oversized `INDEX.md` warns rather than fails.
- **Protected**: `_broadcast` is a tool-owned directory; `init` / `organize`
  never move it.

How later sessions use it: `INDEX.md` starts with a table of contents — each
file is grouped under its most salient keyword. Scan the table of contents,
jump to the topic you need, and open only those originals. The next session
reads the table of contents, not the originals.

---

## Core features

Two main threads: **folder organization** and **whole-task coordination**.

- **Folder organization (standard three-tier)**: automatically builds the
  `material` / `process` / `results` structure and files documents by
  *provenance* (what you placed goes to `material/initial/`, AI downloads go
  to `material/downloaded/`, drafts/finals go to `results/`, working files
  go to `process/`), never by guessing at names. Your material is kept
  verbatim; on a name clash the file is left in place and reported.
- **Whole-task coordination (full lifecycle)**: `init` builds the entire
  structure at task start (including `_broadcast/`); `mark-downloaded` /
  `mark-user` register provenance as you go; the broadcast center provides a
  read-only map of the whole folder; and a final `organize` + broadcast
  rebuild happens before delivery.
- **Lossless and safe**: mandatory before/after SHA-256 snapshots + C1–C8
  eight-check verification, with automatic rollback on failure; `undo` /
  `redo`; `--mode` tiers (quick / incremental / full); `--keep N` artifact
  rotation.
- **Optional enhancements**: smart deduplication, YAML rules + domain
  profiles, standalone `index` / `snapshot`, dual-format indexes (Markdown +
  Excel), AI summaries (off by default), Chinese deliverable keywords,
  per-day logging.

---

## Download and install

**Option 1 — Download the release zip (recommended)**
Open the repository's Releases page, download the latest zip, and unzip it —
no install step required.

**Option 2 — Clone the repository**

```bash
git clone https://github.com/JiamingShi-phys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_task-organizer
```

Requirements: Python 3.10+. `openpyxl` is optional (only used for the Excel
index; without it the Markdown index is still produced). Everything except
`openpyxl` uses only the standard library.

---

## Quick start

```bash
cd Js_Agent-Skills/Js_task-organizer

# 0. (optional) read-only diagnostic: structure / stray files / broadcast freshness
python -m scripts.run doctor /path/to/task_folder

# 1. Create the task folder and put your material in it (by hand).
# 2. Cheap init: build the skeleton and lift your material into material/initial/.
python -m scripts.run init /path/to/task_folder

# 3. Full organize + verify (rolls back automatically on failure).
python -m scripts.run organize /path/to/task_folder

# 4. The assistant fetches a file -> declare it, then re-organize.
python -m scripts.run mark-downloaded /path/to/task_folder fetched.pdf --url https://...
python -m scripts.run organize /path/to/task_folder --mode quick
```

Other commands:

```bash
python -m scripts.run organize /path/to/task_folder --mode incremental --keep 5
python -m scripts.run organize /path/to/task_folder --profile pharma --config rules.yml
python -m scripts.run index     /path/to/task_folder        # regenerate the indexes only
python -m scripts.run snapshot  /path/to/task_folder        # safety airbag
python -m scripts.run undo      /path/to/task_folder/process/history/<file>.json
python -m scripts.run redo      /path/to/task_folder/process/history/<file>.json
python -m scripts.run dedupe    /path/to/task_folder --action report
python -m scripts.run doctor    /path/to/task_folder        # read-only diagnostic
python -m scripts.run broadcast /path/to/task_folder --ai   # AI-generated summaries
```

A successful run looks like:

```
Root: /path/to/task_folder
mode: full
organize: done
verification: passed
history: wrote 20261012_191444_history.json
```

When you see `verification: passed`, the structure is safe to use. When you
see `verification: failed`, the pipeline has already rolled back — fix the
problem and run it again.

### The steady-state file flow

```
you create the folder and drop material in
        |
        v
   +---------+      +-------------------------------------------+
   |  init   |----->| material/initial/<your files, untouched>  |
   +---------+      +-------------------------------------------+
        |
        v  (later, as work happens)
   organize --mode=quick|incremental|full
        |
        +--> assistant output ............ process/
        +--> final / deliverable ......... results/
        +--> mark-downloaded + organize .. material/downloaded/
        |
        v
   index    (whenever you need the hand-off report)
   snapshot (before anything risky)
```

The goal is to keep the folder tidy throughout the task, not just at the
end: build the skeleton once, then put things in the right place as you go.

### Step-by-step calls (library use)

```python
from pathlib import Path
from scripts import snapshot, organize, verify, index_md, index_xlsx, rollback, utils

root = Path("/path/to/task_folder").resolve()

before = snapshot.make_snapshot(root, phase="before")
session = utils.OrganizeSession(root=root)
organize.organize_folder(root, session=session)

after = snapshot.make_snapshot(root, phase="after")
vres = verify.verify(root, session=session, before=before, after=after)

if not vres.passed:
    rollback.rollback(root, session=session)   # verification failed -> rollback
else:
    index_md.write_index_md(root)
    index_xlsx.write_index_xlsx(root)
```

---

## Tests & coverage

```bash
pytest                                            # full suite
pytest --cov=scripts --cov-report=term-missing    # with coverage
```

The current test suite has 340 cases, with coverage around 88% (target >= 80%).

---

## Project layout

```
Js_task-organizer/
+---- SKILL.md              # Skill entry (YAML frontmatter + execution guide)
+---- README.md
+---- LICENSE               # MIT
+---- CHANGELOG.md
+---- CONTRIBUTING.md
+---- .gitignore
+---- .task-organizer.yml.example   # example YAML config with a pharma profile
+---- requirements.txt      # openpyxl, pytest, pytest-cov
+---- scripts/
|   +---- __init__.py
|   +---- run.py            # pipeline orchestration + CLI (init/material/index/snapshot/undo/redo/dedupe/mark-*)
|   +---- scan.py           # recursive scanning and entry classification
|   +---- snapshot.py       # before/after snapshots (+ optional digest cache)
|   +---- organize.py       # three-tier structure + provenance-aware placement
|   +---- verify.py         # mandatory 8-check verification (C1-C8)
|   +---- rollback.py       # log-driven rollback
|   +---- dedupe.py         # exact + similar duplicate detection
|   +---- history.py        # operation history + undo / redo
|   +---- rules.py          # YAML placement-rule config + profiles
|   +---- init.py           # cheap skeleton + content lift
|   +---- sources.py        # provenance manifest
|   +---- hashcache.py      # incremental hashing cache
|   +---- rotate.py         # artifact rotation
|   +---- text_extract.py   # text extraction: txt/md/csv/json/docx/pdf/pptx/xlsx/srt/vtt
|   +---- broadcast.py      # broadcast center: context-compression index (_broadcast/)
|   +---- doctor.py         # read-only diagnostics: structure / stray files / broadcast freshness
|   +---- index_md.py       # Markdown index
|   +---- index_xlsx.py     # Excel index (openpyxl)
|   `---- utils/            # shared utilities (paths/logs/snapshots/AI summary/structure)
|       +---- __init__.py
|       `---- logger.py     # standard-library logging
+---- references/
|   +---- naming-conventions.md
|   `---- verification-protocol.md
+---- assets/
|   +---- index-template.md
|   `---- verification-report-template.md
`---- tests/
    +---- __init__.py
    +---- conftest.py
    +---- fixtures/
    +---- test_scan.py
    +---- test_snapshot.py
    +---- test_organize.py
    +---- test_verify.py
    +---- test_rollback.py
    +---- test_index.py
    +---- test_run.py
    +---- test_dedupe.py
    +---- test_history.py
    +---- test_rules.py
    +---- test_logger.py
    +---- test_init.py
    +---- test_sources.py
    +---- test_hashcache.py
    +---- test_rotate.py
    +---- test_doctor.py        # read-only diagnostics
    +---- test_skill_docs.py    # documentation contract (workflow, triggers)
    `---- test_broadcast.py     # broadcast center: extraction, read-only, idempotence
```

---

## Using as an agent skill

This project is a self-contained agent Skill package. `SKILL.md` carries YAML
frontmatter (`name` / `description` / `version` / `author` / `license` /
`allowed-tools`) followed by an "Execution steps" guide. Point any agent at
this folder. When a user request matches this skill's scope, the agent reads
the execution steps in `SKILL.md` and shells out to the scripts. (Whether the
skill is loaded depends on the agent's recognition of its scope; it is not
guaranteed to trigger in every conversation.)

One important convention for the agent: whenever a file is downloaded or
fetched into the task folder during the conversation, immediately call
`mark-downloaded` (with the source URL). This is the only way for
`downloaded/` to truly mean "files downloaded by the AI" rather than "files
whose names happen to contain `download`".

You can also call the modules directly from Python:

```python
from pathlib import Path
from scripts import run
result = run.run(Path("/path/to/task_folder"))
print(result.summary_lines())
```

---

## License

MIT License, see [LICENSE](LICENSE).

---

## Report issues

Use the repo-wide entry point: see the **"Report issues"** section in the
repository's top-level `README.md` (email `jiaming_shi_phys@outlook.com`,
subject prefix `agent-skill_report`). Reporters who submit a clear,
reproducible issue (or a fix) are listed in the acknowledgement section of
the next release's notes.
