# Forced before/after scan verification protocol (verification-protocol)

This file is the authoritative spec for Js_task-organizer's "forced before/
after scan verification" mechanism. The 8 checks in `verify.py`, the
trigger conditions in `rollback.py`, and the snapshot naming/storage rules
all follow this document.

## Design goal

Organizing is a **side-effecting** operation (it moves files, creates
directories, writes indexes). To keep the risk at an auditable, reversible
level, the tool takes a full scan snapshot before and after organizing, and
forces 7 comparison checks after organizing. **Any error-level check that
fails -> verification does not pass -> automatic rollback**; the user is
never left in a "half-organized and unprovable-lossless" state.

## Snapshots

- Location: the `process/` directory.
- Naming: `YYYYMMDD_HHMMSS_before.json` and `YYYYMMDD_HHMMSS_after.json`
  (the timestamp is produced by `utils.now_stamp()`, format
  `YYYYMMDD_HHMMSS`).
- Content (one record per regular file):

| Field | Meaning |
|-------|---------|
| `rel_path` | path relative to the task root |
| `abs_path` | absolute path |
| `size` | byte size |
| `mtime` | modification time (POSIX float) |
| `type` | `file` |
| `sha256` | file content SHA-256 (64 hex chars) |

Snapshots **exclude**: hidden files, symlinks, and the tool's own
generated artifacts (indexes / logs / snapshots / verification report). The
latter are checked separately via the C6 whitelist.

> Note: the two snapshots use different timestamped file names, so the
> after snapshot does not record the before JSON as a "user file" - this is
> exactly how "excluding one's own generated artifacts" is implemented.

## The 8 checks

| Code | Name | Level | Pass condition | On failure |
|------|------|-------|----------------|------------|
| C1 | File count conservation | error | before user-file count == after user-file count | rollback |
| C2 | Content integrity | error | every "unmoved" file's SHA256 is unchanged | rollback |
| C3 | Move traceability | error | every moved record's target file actually exists | rollback |
| C4 | No unauthorized deletion | error | a before file may only disappear if it was moved or is a deletable generated artifact | rollback |
| C5 | No unauthorized modification | error | every "unmoved" file's size is unchanged | rollback |
| C6 | No unauthorized addition | warning | after only allows whitelisted additions (index/log/snapshot/report) | warning only, not blocking |
| C7 | Directory structure compliance | error | all three standard tiers exist | rollback |
| C8 | Self-check (structure vs. loose files) | warning | the standard structure is present; if missing but loose files sit at the root, it warns "run `init` first" (the missed-init signal) | warning only, never blocks or rolls back |

- "Unmoved" = present in before, still present in after, and **not** in the
  move log.
- C2 and C5 are complementary: C2 catches content tampering via hash, C5
  catches truncation/appending (hash prefix unchanged but length changed)
  via size (defensive redundancy).
- C4 and C6 share the same whitelist: `utils.is_allowed_new_file`.
- C8 is a **self-check / reminder**, not a conservation rule: it never fails
  a run or triggers a rollback. It only fires when the three-tier structure
  is absent while loose files still sit at the root - the signature of a
  task where the agent produced files but skipped `init`. It tells you to
  run `init` first, then re-organize.

### The allowed-new-file whitelist

`utils.is_allowed_new_file` accepts a **relative path** (not a bare name)
and matches:

- the fixed-name artifacts (`Index.md`, `Index.xlsx`,
  `verification_report.md`, `duplicate_report.md`);
- any timestamped pipeline file
  (`YYYYMMDD_HHMMSS_<before|after>.json`,
  `YYYYMMDD_HHMMSS_<OrganizeLog|Cancelled>.md`,
  `YYYYMMDD_HHMMSS_history.json`) and the per-day `YYYYMMDD.log`;
- anything under `process/history/` or `process/logs/`;
- **`process/sources.json` by exact path** -- deliberately *not* by bare
  name, so a user file that merely happens to be called `sources.json` is
  still hashed and verified like any other user content.

`process/.hash_cache.json` is hidden (leading dot), so it never appears in
a snapshot at all and needs no whitelist entry.

## Verification report

- Output: `process/verification_report.md`.
- Top verdict line: `PASS` or `FAIL (rollback needed)`.
- Contains a table of the 8 checks + per-check details (at most 20 sample
  entries).

## Rollback trigger and behavior

When `verify.VerifyResult.passed == False`, `run()` immediately calls
`rollback.rollback(root, session)`:

1. **Reverse moves**: in log-reverse order, move each moved file back to its
   original path; if the original path is occupied, keep it with an `_rN`
   suffix.
2. **Purge generated artifacts**: delete indexes, logs, snapshots, and the
   verification report.
3. **Remove created directories**: the three-tier skeleton, its
   intermediate directories, and every directory created by relocating a
   user sub-folder, rmdir'd deepest-first once emptied (directories that
   still hold user files are never deleted).
4. **Seal the log**: rename `..._OrganizeLog.md` to
   `..._OrganizeLog_Cancelled.md`, preserving the audit trail.
5. Return `RollbackResult`; `success=True` means no conflicts.

Rollback itself is idempotent: re-running is safe.

## Degradation when a snapshot is missing

If the before or after snapshot does not exist (e.g. the pipeline was
interrupted mid-way), `verify` returns a `C0 snapshot missing` failure
(error level) directly, which also triggers rollback - "unable to prove
lossless" is treated as "not passed", a conservative but safe choice.

## Relationship to naming conventions

- Placement / keyword rules: see `naming-conventions.md`.
- Verification only judges "was the organize lossless", not "did the
  placement match the user's intent". If the user thinks a file was placed
  in the wrong tier, change the keyword table in `rules.py` (or your
  `.task-organizer.yml`), not the verification logic.

## Execution tiers

| Mode | Snapshots | Verification | History / index | Notes |
|------|-----------|--------------|-----------------|-------|
| `quick` | none | none | none | `dedupe move` is downgraded to `report`; no log file is opened |
| `incremental` | yes (cached digests) | yes | yes | unchanged files reuse `process/.hash_cache.json` |
| `full` (default) | yes (always re-hash) | yes | yes | the guarantee tier; never consults the cache |

`PipelineResult.ok` in `quick` mode means "organized and nothing rolled
back"; in every other tier it additionally requires `verified`.

`init` takes **no** snapshot and runs **no** verification by design -- it is
the cheap counterpart to `organize`, not a weaker version of it. Run
`organize` (any `--mode`) when you need the forced before/after guarantee.
