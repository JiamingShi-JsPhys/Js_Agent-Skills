# Naming and placement conventions (naming-conventions)

This file defines how Js_task-organizer decides, during the "organize"
stage, which tier each file should be placed in, plus the conflict
handling rules. It stays consistent with the placement table in
`SKILL.md`; if you change the keywords, update
`BUILTIN_PLACEMENT` in `scripts/rules.py` in sync.

## Three-tier structure semantics

| Tier | Directory | Meaning | Typical content |
|------|-----------|---------|-----------------|
| material | `material/` | input material | the user's own material, assistant downloads, indexes |
| process | `process/` | intermediate output | assistant output, drafts, intermediate results, snapshots, logs, verification report |
| results | `results/` | final deliverables | final versions, deliverables |

`material/` is subdivided into:

- `initial/` - **the user's own material**. Reserved: the tool never writes
  anything of its own here, so it can never collide with the user's files.
  Contents are preserved **verbatim** (never renamed, never modified).
- `downloaded/` - files the assistant fetched during the session.

## Placement priority (provenance first, then keywords)

**The destination is decided by who produced the file, never by guessing
from its name.** A file the user dropped in and a file the assistant
fetched may carry identical names, and a user file called
`download_notes.pdf` is still the user's own material.

| Priority | Condition | Target |
|----------|-----------|--------|
| 1 | registered as **downloaded** (the assistant fetched it this session) | `material/downloaded/` |
| 2 | registered as **user material** | `material/initial/` (verbatim) |
| 3 | filename contains final / deliverable | `results/` |
| 4 | filename contains draft / intermediate / temp / tmp / raw | `process/` |
| 5 | anything else - assistant output, undeclared | `process/` |

Provenance is recorded in `process/sources.json` (names only - no hashes,
no content reads, so maintaining it is free). It is written by:

- `init` - registers everything it lifts as user material;
- `mark-user` / `mark-downloaded` - explicit declarations;
- the organizer itself, self-healing: anything already sitting in
  `initial/` or `downloaded/` is registered automatically, so a user who
  drops material straight into `initial/` never has to declare anything.

Matching is on the **basename**, so a user file is recognised whether it is
at the root, inside a legacy sub-folder, or already in a tier.

> **The `download` / `reference` keyword rule was removed.**
> "downloaded" is something that *happened*, not something a filename can
> express. A keyword rule can never tell the difference between
> "the user's own file called download_notes.pdf" and "the file the
> assistant just fetched" - only provenance can.

## Keyword conflict conventions

- When one filename matches multiple keyword rules, take the **highest
  priority** in the table order above. For example `final_draft.md` contains
  both "final" (rule 3) and "draft" (rule 4) -> rule 4 wins -> it goes to
  `process/`. This is a deliberate design choice: **draft semantics take
  precedence over deliverable semantics**, because the organizer would
  rather put uncertain items into process than mis-deliver an intermediate
  draft as a final result.
- To change that priority, reorder the `placement` list in
  `scripts/rules.py` (or in your `.task-organizer.yml`) and note it in this
  file and `SKILL.md`.
- Keyword rules never override provenance. A user file named
  `final_report.md` that is registered as user material still goes to
  `initial/`, because it is the user's file and the user's word is final.

## Conflict and same-name handling

- **User material is never renamed.** If a file with the same name already
  exists in the destination, the incoming file is **left where it is and
  reported** as a conflict. Silently renaming a user's `report.pdf` to
  `report_1.pdf` would break the "put my initial material back exactly as
  it was" promise.
- **Files the tool owns may be suffixed.** Drafts, downloads and other
  assistant output get an automatic numeric suffix on collision:
  `a.txt` -> `a_1.txt` -> `a_2.txt` ... (for files with no extension, the
  suffix is inserted before the whole name).
- During rollback, when restoring in reverse, if the original path is now
  occupied, the `_r1`/`_r2` suffix is used to preserve it, and the
  discrepancy is recorded in `RollbackResult.conflicts`; files are never
  silently dropped.

## Nested content and sub-folders

- **Non-empty user sub-folders are relocated whole** into
  `material/initial/<dirname>/`, never flattened and never recursed into:
  `src/data/inner.txt` must still be `src/data/inner.txt` after the move,
  otherwise the verbatim promise is broken. Every nested file gets its own
  move record so the forced verification can track the new absolute paths.
- **Empty folders** are skipped, logged as "empty folder, not organized".
- Files already inside the standard three tiers are **not moved again**
  (the tool's own output directories are protected).

## Objects that are never moved

| Object | Behavior | Index remark |
|--------|----------|--------------|
| Hidden files (any path segment starting with `.`) | skipped | not included in the index |
| Symlinks | not moved | "symlink, not moved" |
| Read-only files | not moved | "read-only, not moved" |
| Empty folders | skipped | "empty folder, not organized" |
| Occupied files / over-long paths | exception caught and skipped | logged |
| User material whose name is already taken | left in place, reported | conflict |
