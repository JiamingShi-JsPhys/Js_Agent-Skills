"""Pre-publish audit: mechanical consistency checks across the release tree.

Covers: version agreement (SKILL.md / skill.json / CHANGELOG / zip name /
README table / notes title), artifact freshness vs sources, release-note
hygiene (zero-CJK, CRLF, correct skill name), stale-wording scan, one-liner
presence, CHANGELOG top entries, repo metadata files.

Run: python audit_pre_publish.py   (from the 本地仓库 directory)
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = [
    "Js_task-organizer",
    "Js_formula-validator",
    "Js_multi-dim-manager",
    "Js_longitudinal-analysis",
    "Js_conflict-detector",
    "Js_document-evolution-tracker",
]
NOTES = ROOT / "release" / "notes"

problems: list = []
warnings: list = []


def problem(msg: str) -> None:
    problems.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


# ---------------------------------------------------------------- versions
def fm_version(skill: str) -> str:
    t = read(ROOT / skill / "SKILL.md")
    m = re.search(r"^version:\s*(\S+)", t, re.M)
    return m.group(1).strip().strip('"') if m else ""


def json_version(skill: str) -> str:
    import json
    p = ROOT / skill / "skill.json"
    if not p.is_file():
        return ""
    try:
        return str(json.loads(read(p)).get("version", ""))
    except Exception:
        return "?"


def changelog_top(skill: str) -> str:
    t = read(ROOT / skill / "CHANGELOG.md")
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", t, re.M)
    return m.group(1) if m else ""


print("=" * 72)
print("1. VERSION AGREEMENT")
print("=" * 72)
root_readme = read(ROOT / "README.md")
for s in SKILLS:
    fm = fm_version(s)
    js = json_version(s)
    cl = changelog_top(s)
    zip_name = f"{s}-v{fm}.zip"
    zip_ok = (ROOT / "release" / zip_name).is_file()
    note_t = read(NOTES / f"{s}.md")
    note_v = re.search(r"^# .+ v(\d+\.\d+\.\d+)", note_t, re.M)
    note_v = note_v.group(1) if note_v else ""
    readme_v = ""
    for line in root_readme.splitlines():
        if f"`{s}`" in line and "](" in line:
            m = re.search(r"\]\([^)]*\)\s*v?(\d+\.\d+\.\d+)", line)
            if m:
                readme_v = m.group(1)
                break
    line = (f"  {s:<32} fm={fm or '-':<7} json={js or '-':<7} "
            f"changelog={cl or '-':<7} note={note_v or '-':<7} "
            f"readme={readme_v or '-':<7} zip={'OK' if zip_ok else 'MISSING'}")
    print(line)
    vals = {v for v in (fm, js, cl, note_v, readme_v) if v}
    if len(vals) > 1:
        problem(f"{s}: version mismatch across sources: {sorted(vals)}")
    if not zip_ok:
        problem(f"{s}: release zip {zip_name} missing")
    if js and js != fm:
        problem(f"{s}: skill.json {js} != SKILL.md {fm}")

# repo-level VERSION file
vfile = read(ROOT / "VERSION").strip()
print(f"  VERSION file: {vfile!r}")
if not re.fullmatch(r"\d+\.\d+\.\d+", vfile):
    problem(f"VERSION file not a semver: {vfile!r}")

# ---------------------------------------------------------------- freshness
print()
print("=" * 72)
print("2. ARTIFACT FRESHNESS (artifacts must be newer than sources)")
print("=" * 72)
for s in SKILLS:
    newest_src = max(
        (p.stat().st_mtime for p in (ROOT / s).rglob("*")
         if p.is_file() and ".pytest_cache" not in p.parts
         and "__pycache__" not in p.parts),
        default=0,
    )
    exe = ROOT / "release" / f"{s}-installer.exe"
    zp = ROOT / "release" / f"{s}-v{fm_version(s)}.zip"
    for art in (exe, zp):
        if not art.is_file():
            problem(f"{s}: artifact {art.name} missing")
            continue
        age = art.stat().st_mtime
        ok = age >= newest_src
        print(f"  {'OK ' if ok else 'STALE'} {art.name:<48} "
              f"art={age:.0f} src={newest_src:.0f}")
        if not ok:
            problem(f"{s}: {art.name} older than skill sources")
# installer_gui.py freshness vs exes
gui = ROOT / "installer" / "installer_gui.py"
newest_exe = max(
    (ROOT / "release" / f"{s}-installer.exe").stat().st_mtime for s in SKILLS
)
ok = newest_exe >= gui.stat().st_mtime
print(f"  {'OK ' if ok else 'STALE'} all exes vs installer_gui.py "
      f"exe={newest_exe:.0f} gui={gui.stat().st_mtime:.0f}")
if not ok:
    problem("installer_gui.py newer than every exe")

# ---------------------------------------------------------------- zip content
print()
print("=" * 72)
print("3. ZIP CONTENT (new SKILL.md + one-liner inside)")
print("=" * 72)
for s in SKILLS:
    zp = ROOT / "release" / f"{s}-v{fm_version(s)}.zip"
    if not zp.is_file():
        continue
    with zipfile.ZipFile(zp) as z:
        names = z.namelist()
        top = {n.split("/")[0] for n in names}
        # top-level docs only: nested READMEs (e.g. mcp_server/README.md) are
        # legitimate content, not duplicates.
        skill_md = [n for n in names
                    if n.count("/") == 1 and n.endswith("/SKILL.md")]
        readme = [n for n in names
                  if n.count("/") == 1 and n.endswith("/README.md")]
        if len(skill_md) != 1 or len(readme) != 1:
            problem(f"{s}: zip has {len(skill_md)} top-level SKILL.md / "
                    f"{len(readme)} top-level README.md")
            continue
        # byte comparison (text mode would mask CRLF/LF differences)
        src_skill = (ROOT / s / "SKILL.md").read_bytes()
        zip_skill = z.read(skill_md[0])
        same = zip_skill == src_skill
        zip_readme = z.read(readme[0]).decode("utf-8")
        oneliner = "install-web.ps1" in zip_readme
        fwlist = "Claude Code, DeepSeek Harness" in zip_readme
        print(f"  {'OK ' if (same and oneliner and fwlist) else 'BAD'} "
              f"{zp.name:<48} top={sorted(top)} skillmd={'=' if same else '!='} "
              f"oneliner={'Y' if oneliner else 'N'} fwlist={'Y' if fwlist else 'N'}")
        if not same:
            problem(f"{s}: zip SKILL.md bytes differ from repo")
        if not oneliner:
            problem(f"{s}: zip README lacks the one-line command")
        if not fwlist:
            problem(f"{s}: zip README lacks framework full-name list")

# ---------------------------------------------------------------- line endings
print()
print("=" * 72)
print("4b. LINE-ENDING CONVENTION (skill docs CRLF, root READMEs LF)")
print("=" * 72)


def ending(raw: bytes) -> str:
    crlf = raw.count(b"\r\n")
    bare = len(re.findall(rb"(?<!\r)\n", raw))
    if crlf and not bare:
        return "CRLF"
    if bare and not crlf:
        return "LF"
    return "MIXED" if (crlf or bare) else "EMPTY"


# skill-level docs must be CRLF
for s in SKILLS:
    for doc in ("SKILL.md", "README.md", "README_zh.md", "CHANGELOG.md"):
        p = ROOT / s / doc
        if not p.is_file():
            if doc == "CHANGELOG.md":
                warn(f"{s}: no CHANGELOG.md")
            continue
        k = ending(p.read_bytes())
        ok = k == "CRLF"
        print(f"  {'OK ' if ok else 'BAD'} {s}/{doc:<14} {k}")
        if not ok:
            problem(f"{s}/{doc}: {k}, expected CRLF")
# root READMEs must be LF
for doc in ("README.md", "README_zh.md"):
    p = ROOT / doc
    k = ending(p.read_bytes())
    ok = k == "LF"
    print(f"  {'OK ' if ok else 'BAD'} {doc:<20} {k}")
    if not ok:
        problem(f"{doc}: {k}, expected LF")
# release notes must be CRLF (checked in section 4 too, keep single source)
for p in sorted(NOTES.glob("*.md")):
    k = ending(p.read_bytes())
    if k != "CRLF":
        problem(f"notes/{p.name}: {k}, expected CRLF")

# ---------------------------------------------------------------- notes
print()
print("=" * 72)
print("4. RELEASE NOTES (zero-CJK, CRLF, skill name, one-liner)")
print("=" * 72)
for s in SKILLS:
    p = NOTES / f"{s}.md"
    raw = p.read_bytes()
    t = raw.decode("utf-8")
    cjk = re.findall(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", t)
    crlf = raw.count(b"\r\n")
    bare = len(re.findall(rb"(?<!\r)\n", raw))
    oneliner = "install-web.ps1" in t
    names_self = f"-Skill {s}" in t
    finish = "Finish" in t
    print(f"  {'OK ' if not (cjk or bare) else 'BAD'} {p.name:<44} "
          f"CJK={len(cjk)} bareLF={bare} CRLF={crlf} "
          f"oneliner={'Y' if oneliner else 'N'} skillname={'Y' if names_self else 'N'} "
          f"finish={'Y' if finish else 'N'}")
    if cjk:
        problem(f"{p.name}: contains CJK")
    if bare:
        problem(f"{p.name}: not pure CRLF")
    if not oneliner:
        problem(f"{p.name}: missing one-liner")
    if not names_self:
        problem(f"{p.name}: scriptblock example missing -Skill {s}")
    if not finish:
        warn(f"{p.name}: Finish button not mentioned")

# ---------------------------------------------------------------- stale wording
print()
print("=" * 72)
print("5. STALE-WORDING SCAN (docs must match the shipped UI)")
print("=" * 72)
stale_patterns = [
    ("按首字母排列", "old ZH UI wording"),
    ("shared", "removed shared platform option"),
    ("indeterminate", "old progress-bar mode"),
    ("Open folder\"", "check old button text usage"),
]
scan_files = [ROOT / "README.md", ROOT / "README_zh.md"]
for s in SKILLS:
    scan_files += [ROOT / s / "README.md", ROOT / s / "README_zh.md",
                   ROOT / s / "SKILL.md"]
hits = 0
for p in scan_files:
    t = read(p)
    for pat, why in stale_patterns:
        if pat in t:
            # "Open folder" is legitimate (it IS the current secondary button)
            if pat == 'Open folder"':
                continue
            print(f"  STALE {p.relative_to(ROOT)}: {pat!r} ({why})")
            hits += 1
if not hits:
    print("  OK   no stale wording in any doc")
else:
    problem(f"{hits} stale-wording hits")

# ---------------------------------------------------------------- one-liner
print()
print("=" * 72)
print("6. ONE-LINER PRESENCE")
print("=" * 72)
expect = {
    ROOT / "README.md": 1, ROOT / "README_zh.md": 1,
}
for s in SKILLS:
    expect[ROOT / s / "README.md"] = 1
    expect[ROOT / s / "README_zh.md"] = 1
for p, want in expect.items():
    n = read(p).count("install-web.ps1")
    ok = n >= want
    print(f"  {'OK ' if ok else 'MISS'} {str(p.relative_to(ROOT)):<56} x{n}")
    if not ok:
        problem(f"{p}: one-liner missing")
ps1 = ROOT / "install-web.ps1"
if not ps1.is_file():
    problem("install-web.ps1 missing from publish tree")
else:
    t = read(ps1)
    if "JiamingShi-JsPhys/Js_Agent-Skills" not in t:
        problem("install-web.ps1: repo slug wrong")
    print("  OK   install-web.ps1 present, repo slug correct")

# framework table parity: install-web.ps1 vs platform_paths.py
pp = read(ROOT / "installer" / "platform_paths.py")
for key in ("workbuddy", "claude", "codex", "dsh"):
    in_ps1 = f"{key} " in read(ps1) or f'"{key}"' in read(ps1)
    in_pp = f'"{key}"' in pp
    if not (in_ps1 and in_pp):
        problem(f"framework {key} missing from "
                f"{'ps1' if not in_ps1 else ''} {'platform_paths' if not in_pp else ''}")
print("  OK   framework table parity (workbuddy/claude/codex/dsh)")

# ---------------------------------------------------------------- changelogs
print()
print("=" * 72)
print("7. CHANGELOG TOP ENTRIES (must match shipped version)")
print("=" * 72)
for s in SKILLS:
    cl = changelog_top(s)
    fm = fm_version(s)
    ok = cl == fm
    print(f"  {'OK ' if ok else 'BAD'} {s:<32} changelog={cl or 'NONE':<8} "
          f"version={fm}")
    if not ok:
        problem(f"{s}: CHANGELOG top [{cl}] != version {fm}")

# ---------------------------------------------------------------- metadata
print()
print("=" * 72)
print("8. METADATA FILES")
print("=" * 72)
for f in ("LICENSE", "AUTHORS.md", "CITATION.cff", ".gitignore"):
    p = ROOT / f
    print(f"  {'OK ' if p.is_file() else 'MISS'} {f}")
    if not p.is_file():
        warn(f"{f} missing")
cit = read(ROOT / "CITATION.cff")
if cit and "Js_Agent-Skills" not in cit and "Js_Agent" not in cit:
    warn("CITATION.cff does not name the project")

# ---------------------------------------------------------------- summary
print()
print("=" * 72)
if problems:
    print(f"AUDIT FAILED — {len(problems)} problem(s):")
    for p in problems:
        print(f"  [PROBLEM] {p}")
else:
    print("AUDIT PASSED — no problems")
if warnings:
    print(f"{len(warnings)} warning(s):")
    for w in warnings:
        print(f"  [warn] {w}")
print("=" * 72)
sys.exit(1 if problems else 0)
