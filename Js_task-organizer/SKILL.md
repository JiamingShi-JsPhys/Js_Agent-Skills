---

name: Js_task-organizer

description: "Task organizer. Use whenever the user works inside a task, project, research, or study folder - or names/attaches one - and is organizing, tidying, or producing or managing ANY file there. The trigger is the situation (a workspace folder plus any file activity), not a checklist of words: the example words below are illustrative, not exhaustive, because new phrasings will always surface and no keyword list can enumerate them all. Examples of file activity that fire it: organizing or cleaning the folder, setting up a task workspace, reading files in the folder and writing anything from them (a report, a study plan, notes, or ANY other deliverable), or producing ANY deliverable that lands in that folder. Trigger words (illustrative): organize, tidy, task folder, project folder, research folder, study folder, report, summary, notes, deliverable, init, broadcast index. The trigger is a workspace folder plus a deliverable, independent of how many steps the task has - even a single write inside a task folder fires the compound intent. HARD rule: producing a deliverable inside a task folder is a compound intent - it MUST be paired with the bookend loop (init at start, organize + broadcast before the final answer); the two are one action, never two; skipping it is a failure, not a shortcut. SESSION-START RULE: once a workspace folder is known, the first action is a read-only structure check (doctor) - if the standard structure is missing, run init before any content work, so every conversation starts from a tidy folder. Maintain a live _broadcast/ context-compression index: after every init, organize, and file change, rebuild it; it is a read-only digest so a later session reads the index first and open only the original files they need (token-saving); when a folder holds many or large files, build/read the index before opening originals. If a folder is referenced without an explicit organize request: PROPOSE one init first and run only after the user confirms; never reorganize a referenced folder uninvited. If a folder lacks the standard structure (material/ + process/ + results/ + _broadcast/) yet holds loose deliverable files, the missed-init signal fired - run init first. When triggered, RUN the tool via Bash and report the verified result - never reply with a description of this skill alone."


version: 1.0.0

author: Jiaming Shi

license: MIT

allowed-tools: Read, Write, Bash, Glob, Edit

---



# Js_task-organizer



A **task organizer** for task folders. It does two things:



- **Folder organization** — turns a messy task / project folder into a clean,

  standard three-tier structure (`material/initial` + `material/downloaded` +

  `process` + `results` + `_broadcast/`) with provenance-aware placement,

  mandatory before/after verification, and automatic rollback on failure.

- **Global coordination** — oversees the *whole* task lifecycle, not just a

  one-shot organize: it builds every structural folder the moment a task

  starts, tracks each file's provenance as work proceeds, keeps a read-only

  **broadcast index** of the entire folder so later sessions never re-read

  every original, and re-organizes + rebuilds that index right before final

  delivery. That keeps the folder coherent from start to finish and guards the

  context window on long tasks.



Use this Skill when a user asks to organize a task/project folder, set up a

task workspace, or prepare a research/legal/study task with a standard

structure.



## MANDATORY WORKFLOW - what you do when this skill triggers



**This skill is an instruction to ACT, not a document to summarize.** When

any trigger condition under "When to use" is met, you MUST run the tool and

report what it did. Answering with a description of this skill - its

features, its command list, its architecture - is a **failure mode**, not a

result. A summary is not an outcome; a created, verified folder is.



**Scope - workspace vs. direct chat.** This skill fires only when the user

has **chosen a workspace** (a task / project / research folder to work in).

For a workspace task you do the whole loop below - build the structure, keep

it tidy, and file the deliverable. If the user is just **chatting directly

with no chosen workspace folder**, this skill does NOT apply; do not organize.


**Before you finish any workspace task, run this 3-line self-check**
(answer yes to all three, or run the missing step first):

1. Did I run the session-start structure check - `doctor <root>` at the
   start, and `init <root>` when it reported the structure missing (so the
   folder has the full three-tier structure)?
2. After the deliverable was written, did I run `organize <root>`
   and then `broadcast <root>`?
3. Does the deliverable filename contain `final` / `report` / `review`
   / `summary` so that `organize` files it under `results/`?



Execute these steps in order:



1. **Session-start structure check, then the folder-signal gate.**

   - **Run the structure check first - it is read-only and always safe.**
     As soon as the workspace folder is known, run `doctor <root>`. Doctor
     writes nothing, moves nothing and reads no content - one stat pass - so
     it runs **before** any confirmation; it is a check, not a layout
     change. It answers one question: does the folder already have the
     standard structure (`material/` + `process/` + `results/` +
     `_broadcast/`)? Healthy -> the folder is tidy; carry on with the task
     and skip the rest of this step. This is what makes every conversation
     start from a tidy folder without waiting for an organize request: one
     cheap, idempotent check that repairs nothing when nothing is broken.

   - **Doctor reported the structure missing -> apply the gate.**

     - The user **explicitly asked** to organize / set up a workspace, or
       the request is the compound "produce an artifact AND keep the folder
       tidy" (see "Content-production scenarios" below) -> that is already
       an explicit organize intent; run `init <root>` now (it builds the
       skeleton and lifts the loose files into `material/initial/`) and
       continue. No proposal needed.

     - A folder is **attached, referenced, or named** in the conversation
       and the user starts a task on it, but **did not explicitly ask** to
       organize / set up a workspace -> **PROPOSE one init** and stop there:

       *"I see you are working in `<folder>`; want me to set up the standard
       three-tier structure before we start?"* Do **not** run any command
       until the user confirms - `init` moves existing content into
       `material/initial/`, a layout change the user must agree to first.

       If the user declines, carry on with the task as asked and do not
       re-propose. Propose at most once per folder.

2. **Resolve the target root path first.**

   - The user named a path, uploaded / referenced a folder, or the path is

     obvious from the conversation -> use it.

   - **The user gave no path** (e.g. "set up a task workspace", "organize

     my project folder") -> **ask for it**, and propose a concrete default

     so the user only has to say yes (e.g. `~/Desktop/<task-name>`).

     Never guess a location silently, and never abandon the task because

     the path is missing.

3. **Pick the entry point.**

   - Creating something new / the folder is empty / "set up a workspace"

     / "open a task" / the request is the compound "produce an artifact AND

     keep the folder tidy" -> `init` first. **`init` is the task-start

     command: it builds EVERY structural folder immediately** -

     `material/initial/`, `material/downloaded/`, `process/`, `results/`

     **and `_broadcast/`** - so no folder is missing when you start writing.

     It also lifts any pre-existing content into `material/initial/` as

     user material (cheap: no snapshot, no verify).

   - Existing folder with content / "organize this folder" -> `organize`

     (default `--mode full`).

   - Still ambiguous -> ask one short question; if the folder already

     exists, default to `organize`.

4. **Run it with Bash**, from this skill's own directory:

   ```bash

   cd <directory containing this SKILL.md>

   python -m scripts.run init     <root>

   python -m scripts.run organize <root>

   ```

   Python 3.10+ is required; only the standard library is needed

   (`openpyxl` merely adds the xlsx index).

5. **Verify the outcome before reporting.** Success looks like:

   ```

   organize: done

   verification: passed

   ```

   `verification: failed` means the tool has already rolled itself back to

   the before-state - report that fact, do not blindly re-run.

6. **Report concisely**: the three-tier tree that now exists, that the

   user's own material sits in `material/initial/` untouched, the

   verification verdict, and that the run can be reversed with `undo`

   (`process/history/`).

7. **For the rest of the session**: every time you download or fetch a

   file into the task folder, immediately declare it:

   ```bash

   python -m scripts.run mark-downloaded <root> <file> --url <source-url>

   ```

   This is what keeps `material/downloaded/` meaning "files the assistant

   fetched", instead of a guess from the filename.



8. **Final delivery - clean up, then build the broadcast index (mandatory).**

   Before you hand the final answer back to the user in a workspace task,

   run the pipeline **once more** so the deliverable you just produced is

   filed correctly (a file whose name contains `final`, `deliverable`,
   `report`, `review`, or `summary` lands in `results/`), and then rebuild

   ```bash

   python -m scripts.run organize <root>

   python -m scripts.run broadcast <root>

   ```

   The broadcast index (`_broadcast/INDEX.md`) is **mandatory for a workspace

   task**, not optional: it is a categorised, read-only digest that lets the

   next session (and you, if the conversation is long) jump to the right

   file instead of re-reading every original - which would waste a huge amount

   of tokens and can blow the context window. Never skip it on a workspace.



## Content-production scenarios (writing an article / review / report in a task folder)



This skill is also the right tool for a **compound** request: "write a review

of X" / "draft a report" / "summarise these transcripts" **when the work

happens inside a task folder**. The trigger is the *combination* of producing

an artifact **and** a task folder to keep tidy - either half alone may belong

to another tool.


**This is a hard constraint, not a suggestion.** If you produce ANY
deliverable (a report, review, article, abstract, proposal, table, or any
other finished document) **inside a task folder**, you MUST also run the
full bookend loop on that same folder - `init` at task start and
`organize` + `broadcast` before you hand the final answer back. These are
**not skippable, not deferrable, and not optional**: the act of writing the
file and the act of keeping the folder in the standard layout happen
together, every time, with no separate "please organize" request from the
user. Answering the writing request while leaving the folder loose - or
filing the deliverable by hand without running the tool - is a **failure
mode**, not a valid shortcut. Treat "write X into the task folder" as
always meaning "write X AND keep the folder organised"; the two are one
action, never two. This holds even for a one-shot writing task - the trigger
is a workspace folder plus a deliverable, not the number of steps, so a
single write still requires the bookend loop.


An earlier test exposed exactly this gap: a "write a review / proposal"
request was answered with a bare text file dropped into a loose folder,
because the agent read the request as a one-off writing job and never
recognised it as a compound "produce + keep tidy" intent. The bookend loop
below closes that gap - it is what you must run, in order, when the
trigger fires.


The standard action chain (run **in this order, no step may be skipped**):



1. **Set up first.** If the folder is new, or has no three-tier structure

   yet, run `init <root>` **before writing anything** - the compound request

   already carries an explicit "keep the folder tidy" intent, so this runs

   directly with no folder-signal proposal. `init` registers everything

   already in the folder as user material, so the source transcripts /

   notes the user dropped in are protected from the start - this is what

   keeps `initial/` and `results/` from ending up empty.

2. **Produce the artifact.** Write it into the task folder (any location;

   `organize` will file it).

3. **Declare provenance as you go.**

   - every file **you** fetched during the session -> `mark-downloaded`

     (with the source URL);

   - every file the **user** placed -> already registered by `init`, or

     declare it with `mark-user`.

4. **Name the deliverable so it is recognisable.** A file whose name

   contains `final` / `deliverable` / `report` / `review` / `summary`

   (the built-in recognition set) is filed under `results/`

   automatically. When in doubt, rename the finished artifact to

   `final_<name>` before the final `organize`.

5. **Run `organize <root>`** and report the verified result.

6. **Build the broadcast index.** Once the deliverable is filed, run

   `broadcast <root>` so `_broadcast/INDEX.md` + `_broadcast/index.json`

   summarise every file (the folder was already created by `init` at step

   1, so this only fills it). A later session then reads the index first

   and opens only the originals it needs.



**Re-filing rule.** If a blind first `organize` dumped files into

`process/` before anything was declared, declaring them afterwards

(`mark-user` / `mark-downloaded`) **and re-running `organize`** moves them

home - no `undo`/`redo` dance needed. Files with no declaration stay in

`process/` (the assistant-output fallback), which is what keeps re-runs

idempotent.



## Broadcast center (`_broadcast/`) - the context-compression index



A folder can hold more documents than a session can afford to read. The

broadcast center is the answer: a **read-only digest** of every supported

file, small enough to always read first, rich enough to know what to open

next. A later AI session reads `_broadcast/INDEX.md` and then opens only

the original long documents it actually needs - the index is the map, the

originals stay the territory.



Build it:



```bash

cd <directory containing this SKILL.md>

python -m scripts.run broadcast <root> [--ai] [--max-files N] [--keywords K]

```



What it writes - and all it writes - into `<root>/_broadcast/`:



| File | For |

|------|-----|

| `INDEX.md` | you and the next AI session: one line per file (path, type, size, date, one-sentence summary, keywords) |

| `index.json` | programmatic consumers: the same data, machine-readable |



Supported formats: `txt` / `md` / `csv` / `json` / `docx` / `pdf` / `pptx` /

`xlsx`. Everything else is listed under "Skipped", never touched. Text

extraction is standard-library first (`openpyxl` / `pdfminer` / `PyPDF2`

only upgrade the result) and encoding-tolerant: UTF-8 (BOM-aware), UTF-16,

GBK/GB18030 and Big5 notes all decode to real text instead of mojibake,

and a 500 MB log cannot exhaust memory (reads are bounded).



How summaries are made:



- **AI mode** - `TASK_ORG_AI=1` plus a key (the same opt-in as the index

  summaries), or `--ai`: the model writes the one-sentence summary and the

  keywords in one call. `--ai` forces the mode even without the env var;

  without a key it degrades to local and the index says `local`, never

  `ai`.

- **Local mode** (default) - the first 200 characters of the extracted

  text (cut at a sentence boundary when one is near), plus statistical

  keywords: English word frequency, and Chinese terms as repeated 2-4

  character n-grams extended to their full repeated phrase (a frequent

  fragment is superseded by the longer phrase it belongs to). Offline,

  deterministic, free.



Guarantees:



- **Read-only**: originals are opened for reading only - nothing is moved,

  renamed or modified. The only writes are the two files in `_broadcast/`.

- **Idempotent**: re-running regenerates both index files in place.

- **Bounded**: extraction is capped per file, `--max-files` caps the run,

  and an over-sized `INDEX.md` raises a warning, never a failure.

- **Protected**: `_broadcast` is tool-owned, so `init` / `organize` never

  relocate it.



Using the index in a later session: `INDEX.md` opens with a **Directory** -

every file is filed under its most salient keyword (the topics most common

across the corpus become the biggest headings). Scan that directory, jump

to the topic you need, and open only those originals - you **never have to

read every line** of the index. This is what keeps a folder of thousands of

files affordable: the next session reads the directory, not the originals.


### READ-ORDER protocol (mandatory for any later session)

When a session opens a folder that has a `_broadcast/` index, it follows this

exact read order. The point is to save tokens: the index is the cheap layer,

the originals are the expensive layer, and you open the expensive layer only
when a specific entry earns it.

1. **Read the directory first.** Open `_broadcast/INDEX.md` and read its
   **Directory** section (the keyword → file map). Do NOT read the per-file
   detail blocks yet. This one read tells you what exists and where, without
   touching a single original.
2. **Resolve the task to keywords.** From the user's request, pick the 1-3
   topics that matter. Look those up in the directory and note which file
   entries sit under them.
3. **Open only the matching originals.** Open *only* the original files the
   directory pointed at. Everything else stays unread. For files the index
   already summarizes well (a short summary line plus keywords), rely on the
   digest instead of opening the original at all.
4. **Skim the digest for the rest.** For files you did *not* open, the
   per-file summary + keywords in `INDEX.md` is your whole view of them -
   that is the intended token saving.
5. **If the index is missing or stale, build it first.** Run
   `doctor <root>`; if it says the broadcast index is absent or stale, run
   `broadcast <root>` before reading, so the cheap layer is current. Never
   fall back to re-reading every original just because the index lags.

If the folder has no `_broadcast/` at all, skip straight to step 5. The
protocol is what makes the index worth building: a later session that reads
`INDEX.md` and then opens only the files it names spends a small fraction of
the tokens a blind full-folder read would.


The broadcast center works on **any** folder, not just task folders; it is

a standalone command. For a **workspace task it is mandatory** (see step 8

of the workflow) - never skip it. When the user did not ask for it on a

non-workspace folder, propose it once and wait for confirmation.

Starting a **long-context task**, or any folder too large to read in one
session? Build the broadcast center first and read `INDEX.md` before
opening any original file.

## When to use

This skill has two layers, and that split is what keeps it reliable.

**Always-on (no separate trigger).** Two behaviours run on their own
whenever the user is working inside a task or project folder. They are part
of the normal task rhythm, not an optional feature, so they cannot be missed
by the match:

- **At session start (the structure check).** As soon as a workspace folder
  is known - named, attached, referenced, or visible as the working
  directory - run `doctor <root>` first. It is a **read-only, zero-cost**
  scan (no file is read, moved or written) that answers one question: is the
  standard structure (`material/` + `process/` + `results/` + `_broadcast/`)
  in place? If doctor reports `incomplete`, run `init` before any content
  work begins - that is the moment the skeleton gets built and the loose
  files are lifted into `material/initial/`. If doctor reports `healthy`,
  continue without touching anything. This is what makes every conversation
  start from a tidy folder instead of relying on the user to remember an
  organize request: one cheap check, structure repaired only when it is
  actually missing. The check is idempotent - on an already-tidy folder it
  costs one stat pass and changes nothing.
- **At task start**, `init` builds every structural folder up front
  (`material/initial`, `material/downloaded`, `process`, `results`, and
  `_broadcast/`). No folder is missing when the work begins.
- **At final delivery**, `organize` files the finished work into `results/`
  and `broadcast` rebuilds the read-only digest. This is mandatory for any
  task with a workspace folder - it is what lets the next session, and a
  long conversation, open only the originals it needs instead of re-reading
  everything.

**Matched triggers (these fire on their own signals).** On top of the two
always-on bookends, the skill also activates on two specific request shapes
that would otherwise be missed:

- **Content production.** The user reads files in a task folder and writes
  something from them - a report, a feasibility study, a review, a summary,
  notes, an article, an abstract - and the artifact lands in that folder. The trigger does not depend on the task being multi-step, nor on the deliverable's name: producing any deliverable inside a task folder fires it even when the writing is a single, one-shot job.
  This compound intent - "produce the artifact AND keep the folder in the
  standard layout" - triggers the skill even if the word "organize" is never
  spoken and even when the request looks like a pure writing task (see
  "Content-production scenarios"). **It is a hard constraint:** writing the
  artifact and maintaining the folder structure are one combined action -
  whenever you produce a deliverable in the folder you MUST also run the
  bookend loop (`init` at start, `organize` + `broadcast` before the final
  answer). Leaving the folder loose after a write is a failure, not a
  shortcut.
- **Folder signal.** A folder is attached, referenced, or named and the user
  starts a task on it without asking to organize. The skill PROPOSES one
  `init` first and runs only after confirmation (the folder-signal check in
  "MANDATORY WORKFLOW").

If the user is just chatting directly with no workspace folder, the skill
does not apply. The rest of the capabilities - the quick / incremental
tidy-up tiers, undo / redo, smart dedupe, custom placement rules, the
standalone `index` and `snapshot` commands - are available whenever they are
needed and are described in "Execution steps".

If the user only wants to "list folder contents" or "rename a single
file", do not trigger this Skill - that is out of scope.



## Directory structure spec



After running, the task folder must present the following three-tier

structure:



```

task_folder/

+---- _broadcast/        # read-only context-compression index (INDEX.md + index.json)

+---- material/

|   +---- initial/             # THE USER'S OWN MATERIAL - verbatim, never renamed

|   +---- downloaded/          # files the assistant fetched during the session

|   +---- duplicates/          # quarantined exact duplicates (move mode)

|   +---- Index.md             # auto-generated Markdown index

|   `---- Index.xlsx           # auto-generated Excel index (with "Statistics" sheet)

+---- process/                # assistant output + snapshots + logs + verification report

|   +---- YYYYMMDD_HHMMSS_before.json

|   +---- YYYYMMDD_HHMMSS_after.json

|   +---- YYYYMMDD_HHMMSS_OrganizeLog.md

|   +---- YYYYMMDD_HHMMSS_history.json

|   +---- .hash_cache.json             # incremental digest cache (hidden)

|   +---- sources.json                 # provenance manifest

|   +---- verification_report.md

|   +---- duplicate_report.md          # smart dedupe report

|   +---- history/                     # operation history + undo/redo

|   |   `---- YYYYMMDD_HHMMSS_history.json

|   `---- logs/                        # per-day activity log

|       `---- YYYYMMDD.log

`---- results/                # finished deliverables (name contains final / deliverable / report / review / summary)

```



## Placement model (provenance, not filename)



**The destination is decided by who produced the file, never by guessing

from its name.** A file the user dropped in and a file the assistant

fetched may carry identical names, and a user file called

`download_notes.pdf` is still the user's own material.



| Priority | Condition | Target |

|----------|-----------|--------|

| 1 | registered as **downloaded** (the assistant fetched it this session) | `material/downloaded/` |

| 2 | registered as **user material** | `material/initial/` (**verbatim**) |

| 3 | filename contains final / deliverable / report / review / summary | `results/` |

| 4 | filename contains draft / intermediate / temp / tmp / raw | `process/` |

| 5 | anything else - assistant output, undeclared | `process/` |



The old `download` / `reference` **keyword** rule was removed:

"downloaded" is something that *happened*, not something a filename can

express. Use `mark-downloaded` to record it.



**Re-filing.** Priority 1-2 beat the file's *current* location: a

file registered as user material that sits in `process/` (dumped there by a

blind first run) is moved to `material/initial/` on the next `organize`.

Priority 5 files are never re-filed - that is what keeps re-runs idempotent.



Two invariants the agent must never break:



1. **`material/initial/` is reserved for the user.** The tool never writes

   anything of its own there, so it can never collide with the user's

   files. The documented workflow is: the user creates the folder and drops

   material in, then runs `init`.

2. **User material is verbatim.** It is never renamed, never modified,

   never deleted. On a name clash the file is **left where it is and

   reported** instead of being silently suffixed `_1`. Only files the tool

   itself owns may be suffixed.



> **Customizable:** the keyword rows (3-4) are the built-in default. A user

> may override them with a `.task-organizer.yml` config file, optionally with

> several named `profiles.<name>` selected via `--profile`. The tool falls

> back to the built-ins when the config is absent or malformed, so it never

> crashes.



## Execution steps



There are **two entry points**, deliberately decoupled:



| Stage | `init` | `organize` |

|-------|--------|------------|

| Build the three-tier skeleton | yes | yes |

| Lift pre-existing loose content into `initial/` | yes | no |

| Write the `.task-organizer.yml` template | yes | no |

| SHA-256 snapshots | **no** | yes |

| C1-C8 forced verification | **no** | yes |

| Automatic rollback | **no** | yes |

| Operation history / undo | **no** | yes |



### `init` - the cheap entry point



Use it when the user is **creating** a task folder. It does the minimum

that makes the folder usable, and nothing that could fail expensively:



1. Build the three-tier skeleton (`mkdir -p` semantics, idempotent).

2. Write a fully commented-out `.task-organizer.yml` template, **never**

   overwriting an existing one.

3. Lift pre-existing content into `material/initial/`:

   - loose files keep their **exact name**;

   - sub-folders are moved **whole** (`src/data/inner.txt` stays

     `src/data/inner.txt`) - never flattened, never recursed into;

   - empty folders, hidden files and symlinks are skipped.

4. Register everything lifted as **user material** in

   `process/sources.json`, so the verbatim guarantee is recorded even for a

   folder the user never runs `organize` on.

5. Append an audit log under `process/` (Markdown, no snapshot).



`--classify` applies the keyword rules instead of "everything to initial",

so `final_report.pdf` lands in `results/` - but registration still marks

the file as the user's, so it is still never renamed.



### `organize` - the full pipeline (order is fixed)



1. **Scan** - recursive scan that identifies files/dirs/symlinks and

   filters hidden files and empty folders.

2. **Before snapshot** - `snapshot.make_snapshot(root, phase="before")`

   -> `process/YYYYMMDD_HHMMSS_before.json`, recording each file's

   path/size/mtime/SHA256/type. In `incremental` mode, files whose

   `size`+`mtime` are unchanged reuse the cached digest instead of being

   re-hashed.

3. **Organize** - `organize.organize_folder(root)`: build the structure,

   resolve each file's provenance, move files, write the

   `process/..._OrganizeLog.md` log, and log key moves/skips to

   `process/logs/YYYYMMDD.log`.

4. **Optional dedupe** - when `--dedupe-action` is `report` or

   `move`, `dedupe.run_dedupe` scans for exact + similar duplicates, writes

   `process/duplicate_report.md`, and (move mode) quarantines exact

   duplicates into `material/duplicates/` *before* the after-snapshot, so

   those moves are covered by the forced verification.

5. **After snapshot** - `snapshot.make_snapshot(root, phase="after")`.

6. **Mandatory verification** - `verify.verify(root, ...)`: run 8 checks
   (C1-C8) and write `verification_report.md`.

7. **Verification passed** -> generate `Index.md` + `Index.xlsx`, append a

   "Pipeline finished" section to the log, and write the operation

   history to `process/history/YYYYMMDD_HHMMSS_history.json` so the run can

   later be undone / redone.

8. **Artifact rotation** - keep only the newest `--keep` runs'

   timestamped artifacts. The newest before/after snapshot pair is always

   protected, and anything that is not a recognised timestamped artifact is

   never touched.

9. **Verification failed** -> **immediately trigger

   `rollback.rollback(root, session)`**: reverse the moves, delete created

   directories and indexes, rename the log to `..._Cancelled.md`, and

   restore the before-state.



### CLI usage



```bash

# --- create a task folder (cheap: no snapshot, no verify) ---

python -m scripts.run init <root>

python -m scripts.run init <root> --classify          # apply keyword rules too

python -m scripts.run init <root> --no-config         # skip the yml template



# --- main pipeline (organize + optional dedupe + verify + index + history) ---

python -m scripts.run organize <root>

python -m scripts.run organize <root> --mode quick        # move only, no verify

python -m scripts.run organize <root> --mode incremental  # reuse unchanged digests

python -m scripts.run organize <root> --keep 5            # artifact retention

python -m scripts.run organize <root> --dedupe-action report

python -m scripts.run organize <root> --dedupe-action move

python -m scripts.run organize <root> --config myrules.yml --profile pharma

python -m scripts.run organize <root> --no-index          # skip index generation

python -m scripts.run organize <root> -v    # verbose console log

python -m scripts.run organize <root> -q    # quiet console (warnings only)



# --- declare provenance (the agent calls this right after fetching a file) ---

python -m scripts.run mark-downloaded <root> <file> [--url <url>]

python -m scripts.run mark-user       <root> <file>



# --- standalone commands ---

python -m scripts.run index    <root>     # regenerate Index.md / Index.xlsx only

python -m scripts.run snapshot <root>     # safety airbag before a risky batch op



# Legacy positional form (equivalent to `organize <root>`)

python -m scripts.run <root>



# Undo / redo an already-verified run

python -m scripts.run undo <history_file> [--root <root>]

python -m scripts.run redo <history_file> [--root <root>]



# Standalone dedupe, outside the main pipeline

python -m scripts.run dedupe <root>                 # report only

python -m scripts.run dedupe <root> --action move    # + quarantine exact dups

```



`PipelineResult.ok` being True means organize + verification all passed

(`quick` mode has no verification stage, so "organized and nothing rolled

back" is its success condition); False means verification failed and was

auto-rolled back (or the pipeline terminated at an earlier stage).



### The steady-state file flow



```

user creates the folder and drops material in

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

   index     (whenever a hand-off report is needed)

   snapshot  (before anything risky)

```



The goal is that the folder stays tidy **continuously**, not only at the

end: build the skeleton once, then keep putting things where they belong.



## Provenance manifest (`process/sources.json`)



The manifest is the authoritative answer to "where does this file go", and

it is cheap to maintain - it stores **names only**, no hashes and no

content reads.



- `user` - files the user placed by hand. Recorded by `init`, by

  `mark-user`, and automatically for anything already sitting in

  `initial/`.

- `downloaded` - files the assistant fetched during the session. Recorded

  by `mark-downloaded`, and automatically for anything already sitting in

  `downloaded/`.



Matching is on the **basename**, so a user file is recognised whether it is

at the root, inside a legacy sub-folder, or already in a tier.



**Agent rule:** whenever you download or fetch a file into the task folder

during the conversation, call `mark-downloaded` (or `run.mark_downloaded`)

immediately, with the source URL. That is what makes `downloaded/` mean

"files the assistant downloaded" instead of "files whose name happens to

contain download".



## How it works (key points)



- **Two entry points.** `init` is the cheap door (skeleton + lift + config

  template, no snapshot / verify / rollback); `organize` is the full pipeline

  (snapshot + 8-check verification + auto-rollback + history + index).

  `--mode` adds `quick` (move-only) and `incremental` (reuse unchanged

  digests for the weekly cleanup).

- **Placement is by provenance, not filename.** Who produced the file decides

  its folder; declared sources (`mark-user` / `mark-downloaded`) are re-filed

  on re-run, undeclared files stay put so re-runs stay idempotent. Built-in

  keywords recognise `final` / `deliverable` / `report` / `review` /
  `summary` -> `results/` and `draft` / `temp` / `raw` -> `process/`;
  override via `.task-organizer.yml` (with named profiles).

- **Content production is a first-class trigger.** A request to write a

  review, report, or article *inside* a task folder carries an implicit
  "keep it

  tidy" intent - `init` first (so the user's inputs are registered), produce,

  declare provenance, name the deliverable, `organize`.

- **Safety net.** The 8 checks (C1-C8) roll back automatically on any

  error; `undo` / `redo` re-apply a verified state; `--keep N` rotates

  artifacts so `process/` never grows unbounded.



## Reference details

The lower-level mechanics - `init` vs `organize`, the `--mode` tiers
(`quick` / `incremental` / `full`), artifact rotation (`--keep N`),
standalone `index` / `snapshot`, undo / redo, smart dedupe, the YAML rule
config with domain profiles, and logging - are all covered in **Execution
steps** above and the `references/` files. They are kept out of this
action-first guide on purpose.


## Forced verification protocol (the 8 checks in verify.py)



| Code | Check | Severity | Meaning |

|------|-------|----------|---------|

| C1 | File count conservation | error | before user-file count == after user-file count (excluding new index/log) |

| C2 | Content integrity | error | every unmoved file's SHA256 is unchanged |

| C3 | Move traceability | error | every moved file has a log record and its target exists |

| C4 | No unauthorized deletion | error | before files must not vanish without reason |

| C5 | No unauthorized modification | error | unmoved files have matching sizes (pairs with C2 to catch truncation/rewrite) |

| C6 | No unauthorized addition | warning | after only permits new index/log/snapshot; other additions are warned |

| C7 | Directory structure compliance | error | the three-tier structure is fully present |

| C8 | Self-check (structure vs. loose files) | warning | a deliverable sits at the root with no standard structure - the missed-init signal; run `init` first |



Any error-level failure -> `VerifyResult.passed=False` -> rollback is

triggered. Only warnings (C6) do not block passing but are listed in the

report.



See `references/verification-protocol.md` for details.



## Edge cases (must be honored)



- **Empty folders**: skipped, logged as "empty folder, not organized".

- **Hidden files (start with `.`)**: skipped, never moved.

- **Symlinks**: not moved, marked "symlink, not moved" in the index.

- **Read-only files**: not moved, marked "read-only, not moved" in the

  index.

- **Occupied files / over-long paths**: exceptions are caught, the entry

  is skipped and logged so the whole batch does not fail.

- **User-material name clash**: the file is **left in place and reported**,

  never renamed.

- **Parent folder with multiple sub-tasks**: run `run()` per sub-task,

  each with its own snapshot/verify/rollback, then aggregate.



## Cost control



The tool is designed to stay cheap on big folders:



- the provenance manifest and the hash cache are the only things written

  outside a snapshot, and both are tiny JSON documents;

- `quick` mode does no hashing at all;

- `incremental` mode hashes only what changed;

- **AI summaries are strictly opt-in** - they run only when `TASK_ORG_AI`

  is set to a truthy value *and* an API key is present, so a pre-existing

  `OPENAI_API_KEY` in the environment can never silently spend tokens.

  Without both, the deterministic "filename + first 200 chars" placeholder

  is used.



## Output example



After organizing and passing verification, `material/Index.md` looks like:



```markdown

# Index



- generated under: `D:/work/my_task`

- entries: 5



| filename | type | size | source | summary | added at | remark |

|---|---|---|---|---|---|---|

| notes.txt | text | 11 B | process | notes.txt: hello notes | 1728... | normal |

| draft.txt | text | 13 B | process | draft.txt: draft content | 1728... | normal |

| final_report.md | document | 15 B | results | final_report.md: # final report | 1728... | normal |

| reference_paper.pdf | document | 12 B | downloaded | reference_paper.pdf (placeholder summary: not generated) | 1728... | normal |

| my_notes.txt | text | 9 B | initial | my_notes.txt: my notes | 1728... | verbatim |

```



The top of `process/verification_report.md` shows either

"Verdict: [PASS]" or "Verdict: [FAIL] (rollback needed)".



## Tech stack & dependencies



- Python 3.10+; standard library `pathlib` / `shutil` / `hashlib`.

- `openpyxl` (generates the xlsx index; gracefully degrades to md-only

  when missing).

- `pytest` + `pytest-cov` (tests and coverage, target >= 80%).



## Failure-handling principles



- No stage may crash the program in a "half-organized" state: `run()`

  catches and reports errors, and verification failure always rolls back.

- Rollback is "best effort": each failed step is recorded in

  `RollbackResult.conflicts`; files are never silently dropped.

- Users can retry manually: `rollback` is idempotent; re-running is safe.



## References



- Placement / naming details: `references/naming-conventions.md`

- Verification protocol details: `references/verification-protocol.md`

- Index / report templates: `assets/index-template.md`,

  `assets/verification-report-template.md`

- Example YAML placement config: `.task-organizer.yml.example`

