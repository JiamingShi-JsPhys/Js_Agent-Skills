[English](README.md) · [中文说明](README_zh.md)

# Js_formula-validator

> A formula verifier skill by Jiaming Shi. It runs five deterministic computer-algebra checks on a physics or maths formula and returns a compact verdict, so an AI can check a derivation it does not fully trust without redoing the algebra itself.

Js_formula-validator turns a formula you are not sure about into a pass / fail / unknown verdict. It parses the input, propagates SI dimensions, enumerates limit cases, compares the two sides at ten thousand sampled points, and tries to prove the identity symbolically - every step runs through SymPy, NumPy and mpmath, never through generation.

The model extracts the formula and reads the report; it does not compute the algebra. The tool prints one compact JSON line and writes the highlighted failures to a Markdown report, so verification does not flood the conversation.

```
input: "E = m*c**2"  +  units
        |
        v
   +---------+   D1 parse         D2 dimension
   | validate|--> D3 limit-case   D4 numeric (10k Monte-Carlo)
   |  /check |--> D5 symbolic identity
   +---------+
        |
        v
   compact JSON summary  +  _reports/latest.md (highlighted)
```

---

## Workflow after triggering (see `SKILL.md` for details)

> This section mirrors the "Execution steps" in `SKILL.md`. The README only provides an entry-point overview; the Agent should follow `SKILL.md` when actually verifying a formula.

This skill is an "act immediately" instruction, not a summary document. Once a user request matches the skill's scope, the tool must be run and the result must be reported - replying only with a description of "what this skill is, what it does, what commands it has" counts as a task failure.

**Scope - formula in hand vs. derivation in hand.** This skill triggers whenever a formula, derivation, or matrix enters the conversation and the user is checking, validating, debugging, or about to rely on it - independent of how the formula arrived (typed, pasted, or attached) and independent of how many lines it spans. If the user is only chatting about physics with no concrete symbolic claim to check, this skill does not apply.

**Standard action chain (summary):**

1. **Extract the formula - read, do not compute.** As soon as a formula appears in the conversation, pull the expression (and any units) and hand it to the tool; do not re-derive it yourself.

   ```bash
   python scripts/cli.py validate --expr "1/(x*(1+x)) = 1/x - 1/(1+x)"
   ```

   Every check runs through SymPy / NumPy / mpmath; the model only interprets the report.

2. **Choose the entry point.** One equation to verify -> `validate`. A single result to inspect -> `check`. A multi-step derivation -> `derive`. A representation matrix -> `matrix`.

3. **Run with Bash** (from the skill's directory):

   ```bash
   python scripts/cli.py validate --expr "E = m*c**2" --units E=J --units m=kg --units c=m/s
   python scripts/cli.py check    --expr "hbar**2*k**2/(2*m)" --units hbar=J*s --units k=1/m
   python scripts/cli.py derive  --steps "1/(1-x**2)" --steps "1/((1-x)*(1+x))" --steps "1/(1-x)"
   python scripts/cli.py matrix  --matrix "Matrix([[0, -I], [I, 0]])"
   ```

   Requires Python 3.10+; `sympy`, `numpy`, `scipy`, `mpmath` (scipy only for the functions NumPy lacks, imported on demand).

4. **Report the verdict, not the algebra.** The tool prints one compact JSON line (pass / fail / unknown / conflict) and writes the highlighted failures to `_reports/latest.md`. Surface the failing point and the dominant error class; do not recompute the expression.

5. **For the rest of the session**: whenever a new formula appears, run the relevant subcommand again - verification is cheap and deterministic.

### Common request shapes

When "check a formula" and "keep the reasoning trustworthy" appear together, this skill triggers fully - **even if the word "verify" is never mentioned**. Typical request shapes: "is this right?", "this looks off", "check the dimensions", "which step breaks?", "is this matrix unitary?". Note: triggering does not depend on how many steps the task has, nor on the exact wording - any symbolic claim whose correctness matters fires it. Standard action chain:

1. **Match the subcommand to the request.** Identity to confirm -> `validate`; a single quantity to sanity-check -> `check`; a chain -> `derive`; a matrix property -> `matrix`.
2. **Add units where they matter.** Dimensional analysis only runs when units are declared; without them the dimensional check abstains.
3. **Read the report.** Report the verdict and, on failure, the worst sample point and the error class.
4. **For a multi-step chain**, `derive` localises the first breaking step and separates a dropped dimensional factor from a wrong coefficient and a wrong functional form.

---

## The five checks (D1-D5) - what each layer looks for

A formula is judged by five independent layers. Each layer can return `pass`, `fail`, `unknown`, or `conflict`; the overall verdict is the worst non-abstaining outcome.

| | Check | Failure means |
|---|---|---|
| D1 | Parse | The formula could not be read. The tool abstains here - it never guesses a meaning and continues. |
| D2 | Dimension | The two sides carry different dimensions, or a sum mixes incompatible dimensions. |
| D3 | Limit | As some variable tends to 0 or infinity, the two sides behave differently. |
| D4 | Numeric | Across ten thousand Monte-Carlo samples spanning several decades, the two sides disagree - and the worst sample point is reported. |
| D5 | Symbolic | `lhs - rhs` does not simplify to 0; a 40-digit cross-check is used near cancellation points. |

A definition such as `E = m*c**2` has a bare symbol on one side, so random sampling is meaningless; only the dimensional check runs, and the tool says so.

### Guarantees

- **Abstention is a first-class verdict.** When units are missing or a construct is unsupported, the result is `unknown` with the reason attached, never a pass.
- **Unit guessing is off by default.** A wrong guess produces a false dimensional error, which is worse than admitting ignorance. Use `--infer` only when you want the inferred units listed for review.
- **Floating-point noise is not an error.** If float64 sampling disagrees but 40-digit arithmetic agrees near a cancellation point, the run passes with a note.
- **Dimension vs. numeric conflict is surfaced, not folded in.** A disagreement between the two is reported as `conflict`, usually meaning the unit declaration is wrong.
- **Parse failures are reported with the parser's own hint**, never repaired by guesswork.

### How the report reads

The compact JSON summary names the verdict, the failed checks, and the first error. The full Markdown report (`_reports/latest.md`) highlights every failing point; open it only when the one-line summary is not enough.

---

## Limitations

- Numerical agreement is evidence, not proof. It is strong evidence across thousands of points and several decades, and it can still miss an error confined to an unsampled region.
- Undeclared units make the dimensional check abstain. Without units, a dimensionally wrong formula can pass everything else.
- Limit checking is comparative. A divergence present on both sides is reported as a property, not as an error, so a formula that is wrong and divergent in the same way on both sides will not be caught by D3.
- The symbolic prover is bounded by expression size. Large inputs come back `unresolved` rather than `proven`, which is a statement about the simplifier and not about the formula.
- `\int`, `\sum` and `\prod` in LaTeX need an unambiguous body; the parser asks for SymPy syntax instead of guessing where the integrand ends.
- Being loaded depends on the agent recognising the skill's scope; it is not guaranteed to activate in every conversation.

---

## Core features

Five threads of deterministic checking, plus localisation:

- **Parse + dimensional analysis**: a physics-aware namespace (`E` stays energy, not Euler's number) and SI-dimension propagation over the seven base units.
- **Limit-case enumeration**: every free variable against 0, +infinity and -infinity, comparing the two sides' behaviour rather than judging a divergence alone.
- **Numerical Monte-Carlo sampling**: ten thousand log-uniform samples across decades, with the worst-disagreement point reported.
- **Symbolic identity proving**: `lhs - rhs == 0` with a 40-digit high-precision cross-check when the simplifier gives up.
- **Multi-step localisation**: `derive` finds the first breaking step and separates a dropped dimensional factor from a wrong coefficient and a wrong functional form.
- **Matrix property checks**: Hermitian, unitary, anti-Hermitian, orthogonal, traceless, idempotent, real spectrum - used in group theory and quantum mechanics.
- **Bilingual, agent-grade output**: one JSON summary line for the conversation, a highlighted Markdown report on disk, and both SymPy and LaTeX input.

---

## Download and install

**Option 1 — Download the release zip (recommended)**

Open the repository's Releases page, download the latest zip, unzip it, and run `pip install -r requirements.txt` — no build step required.

**Option 2 — Let an Agent fetch it**

Copy the following instruction to your Agent, and it will locate and fetch the skill automatically:

> Please visit https://github.com/JiamingShi-JsPhys/Js_Agent-Skills/tree/main/Js_formula-validator, read the README.md in that folder, and download or install the skill according to its instructions.

You only need to tell the Agent the skill name; it handles the rest.

**Option 3 — Clone the repository**

```bash
git clone https://github.com/JiamingShi-JsPhys/Js_Agent-Skills.git
cd Js_Agent-Skills/Js_formula-validator
pip install -r requirements.txt
```

Requirements: Python 3.10+. `sympy`, `numpy`, `scipy`, `mpmath` are required (none are part of the standard library). `scipy` is imported on demand, only for the special functions NumPy lacks (`erf`, `gamma`, `besselj`, `zeta`). As an MCP server, see `mcp_server/README.md` — it speaks the wire protocol directly and needs no extra packages.

---

## Quick start

```bash
cd Js_Agent-Skills/Js_formula-validator

# 0. (optional) verify an identity
python scripts/cli.py validate --expr "1/(x*(1+x)) = 1/x - 1/(1+x)"

# 1. check a formula with declared units (dimensional analysis runs)
python scripts/cli.py validate --expr "E = m*c**2" --units E=J --units m=kg --units c=m/s

# 2. inspect a single result
python scripts/cli.py check --expr "hbar**2*k**2/(2*m)" --units hbar=J*s --units k=1/m

# 3. localise the first breaking step of a derivation
python scripts/cli.py derive --steps "1/(1-x**2)" --steps "1/((1-x)*(1+x))" --steps "1/(1-x)"

# 4. confirm a matrix property (Hermitian, unitary, ...)
python scripts/cli.py matrix --matrix "Matrix([[0, -I], [I, 0]])"
```

Other commands:

```bash
python scripts/cli.py validate --expr "x**2 = 2*x" --units x=m --infer
python scripts/cli.py check    --expr "p*c" --expect-zero --units p=kg*m/s --units c=m/s
python scripts/cli.py derive   --steps-file steps.txt
python scripts/cli.py matrix   --matrix-file M.txt --props hermitian,unitary,traceless
python scripts/cli.py validate --expr "f(x) = x**2" --report out.md --stdout-report
```

### Output shape

The CLI prints one compact JSON line (and writes the highlighted report to `_reports/latest.md` unless `--report` overrides it):

```json
{"verdict": "fail", "failed_checks": ["dimension"],
 "first_error": "a sum mixes incompatible dimensions", ...}
```

When you see `verdict: pass`, the formula held against every applicable check. When you see `verdict: fail` or `conflict`, open `_reports/latest.md` for the worst sample point and the error class.

### Step-by-step calls (library use)

```python
from scripts.core import pipeline

res = pipeline.validate_equation(
    "E = m*c**2",
    units={"E": "J", "m": "kg", "c": "m/s"},
)
print(res["verdict"], res.get("failed_checks"))
```

---

## Tests & coverage

```bash
pytest                                            # full suite
pytest --cov=scripts --cov-report=term-missing    # with coverage
```

- 246 cases
- `pytest` from this directory; the suite also asserts the documentation
  contracts (version agreement, a CJK-free README, and the design rules).

Line coverage is around 84% (target >= 80%).

---

## Project layout

```
Js_formula-validator/
+---- SKILL.md              # Skill entry (YAML frontmatter + execution guide)
+---- README.md
+---- README_zh.md         # Chinese mirror
+---- LICENSE               # MIT
+---- CHANGELOG.md
+---- CONTRIBUTING.md
+---- .gitignore
+---- requirements.txt      # sympy, numpy, scipy, mpmath
+---- scripts/
|   +---- __init__.py       # __version__
|   +---- cli.py            # CLI (validate / check / derive / matrix)
|   `---- core/
|       +---- pipeline.py   # D1-D5 orchestration + report
|       +---- parsing.py    # SymPy + LaTeX fallback parser
|       +---- dimensions.py # dimensional analysis
|       +---- limits.py     # limit-case enumeration
|       +---- numeric.py    # 10k-sample Monte-Carlo comparison
|       +---- symbolic.py   # identity proving + high-precision cross-check
|       +---- breakpoint.py # multi-step derivation localiser
|       +---- matrixprops.py# matrix property checks (Hermitian, unitary, ...)
|       +---- report.py     # Markdown + JSON report rendering
|       `---- registry.py   # check registry
+---- mcp_server/
|   +---- server.py         # zero-dependency MCP server
|   +---- mcp_config.example.json
|   `---- README.md
+---- references/
|   `---- market-analysis.md
+---- examples/
|   +---- three-cases.md
|   `---- baseline-selfcheck.md
`---- tests/
    +---- conftest.py
    +---- test_skill_docs.py   # documentation contract
    +---- test_cli_inprocess.py
    +---- test_core_direct.py
    +---- test_coverage_extra.py
    +---- test_parsing.py
    +---- test_dimensions.py
    +---- test_limits.py
    +---- test_numeric.py
    +---- test_symbolic.py
    +---- test_mcp.py
    `---- test_end_to_end.py
```

---

## Using as an agent skill

This project is a self-contained agent Skill package. `SKILL.md` carries YAML frontmatter (`name` / `description` / `version` / `author` / `license` / `allowed-tools`) followed by an "Execution steps" guide. Point any agent at this folder. When a user request matches this skill's scope, the agent reads the execution steps in `SKILL.md` and shells out to the scripts. (Whether the skill is loaded depends on the agent's recognition of its scope; it is not guaranteed to trigger in every conversation.)

You can also call the modules directly from Python:

```python
from scripts.core import pipeline

res = pipeline.validate_equation("x = 2*x", units={"x": "m"})
print(res["verdict"])
```

Or run it as a zero-dependency MCP server:

```bash
python mcp_server/server.py
```

See `mcp_server/README.md` for the wire protocol.

---

## License

MIT License, see [LICENSE](LICENSE).

---

## Report issues

Use the repo-wide entry point: see the **"Report issues"** section in the repository's top-level `README.md` (email `jiamingshi_phys@outlook.com`, subject prefix `agent-skill_report`). Reporters who submit a clear, reproducible issue (or a fix) are listed in the acknowledgement section of the next release's notes.
