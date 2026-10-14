---
name: Js_formula-validator
version: 1.0.0
description: >
  Formula verifier for theoretical physics and mathematics. Use whenever a
  formula, derivation, or matrix enters the conversation in any form - written
  by the user, produced by an AI derivation, copied from a paper, or attached as
  a file - and the user is checking, validating, debugging, sanity-testing, or
  expressing doubt about it, or is about to rely on it in a later step. The
  trigger is the situation (a symbolic claim whose correctness matters), not a
  checklist of words: the example verbs below are illustrative, not exhaustive,
  because new phrasings will always surface and no keyword list can enumerate
  them all. Runs five deterministic CAS checks - parse, dimensional analysis,
  limit-case enumeration, 10k-sample numerical comparison, symbolic identity
  proving - and returns a compact verdict with the failing point highlighted.
  Also fires for multi-step derivations, where it localises the first breaking
  step and separates a dropped dimensional factor from a wrong coefficient and a
  wrong functional form, and for matrix properties such as Hermiticity and
  unitarity - independent of how the formula arrived, independent of how many
  lines it spans - even a single formula pasted with no explanation fires it,
  and even when the user only says it "looks wrong" without naming any check.
---

# Js_formula-validator

## When to use

- A formula, identity, or derived result appears and its correctness matters -
  whether the user asks for a check, states it confidently, or says it "looks
  wrong".
- A multi-step derivation needs to be checked line by line, or a wrong result
  needs the specific broken step located.
- A matrix from group theory or quantum mechanics must be confirmed Hermitian,
  unitary, traceless, and so on.
- A formula is about to be used as input to a later step, so an error now
  propagates.
- The user asks for a dimensional check, a limiting-case check, or a numerical
  spot-check by name.

## When NOT to use

- Purely numeric evaluation with no symbolic claim (`compute 3.7**2`) - that is
  arithmetic, not verification.
- Prose, references, or literature search with no formula to check.
- Curve fitting or statistics on measured data - this tool checks algebra, not
  empirical models.
- Numerical simulation or ODE integration - use a solver, not a verifier.

## Hard constraints

- **Never compute the algebra yourself.** Extraction and interpretation are
  yours; every computation runs through `scripts/cli.py` or the MCP tool. If a
  check did not run, say it did not run.
- **Never report a verdict the tool did not produce.** `unknown` is a valid
  result and must be passed through as `unknown`, not softened into a pass.
- **Never guess a unit silently.** Leave the symbol undeclared so the
  dimensional check abstains, or pass `--infer` and repeat the guessed units
  back to the user.
- **SymPy syntax is the preferred input.** LaTeX works, but SymPy syntax parses
  more reliably and avoids `\int`, `\sum`, and unmatched-brace failures.

## Execution steps

### 1. Extract the formula (your only computational job)

Turn the user's formula into an equation `lhs = rhs` written in SymPy syntax.
Map the notation: `**` for powers, `sqrt()`, `exp()`, `log()`, `I` for the
imaginary unit, `Derivative(f(x), x)`, `Integral(f(x), (x, 0, oo))`,
`Matrix([[a, b], [c, d]])`.

Also: `Sum(f, (i, a, b))` for a bounded sum (write a *conditional* sum such as
`i != j` as "full sum minus the diagonal terms"), and `D(f, x, n)` /
`Derivative(f, (x, n))` for an n-th derivative. Traps that produce parse
errors: bare `sum_i` subscripts, `sum_(j!=i)` conditional notation, and
`Sum(F(i,j),(i,1,N))` with mismatched arity - use the forms above. A bare
sub-script summation such as `sum_i F_ij` is rejected (not guessed), because the
fallback would silently read it as the product `s*u*m_i*F_i*j`.

Keep the original notation for the reply - you will need it in step 5.

### 2. Collect units

If the physical meanings are clear, declare them with repeatable
`--units NAME=UNIT`. Units are products with `*` and powers with `**`
(`kg*m/s**2`, `J`, `eV`, `T`). Names resolve against SI (`kg m s A K mol cd`,
`N J W Pa C V F ohm Wb T H Hz eV`).

If the meanings are unclear, **leave them undeclared**. The dimensional check
then abstains instead of guessing. Only use `--infer` when asked, and then
repeat every inferred unit back to the user.

For a pure-mathematics identity with no physical content, declare nothing.

### 3. Run the check

```bash
python scripts/cli.py validate --expr "sqrt(k/m) = omega" \
    --units k=kg/(s**2) --units m=kg
```

Add what the situation needs:

| Need | Flag |
|---|---|
| A suspected pole at `x = 1` | `--critical x=1` |
| A symbol that must stay positive | `--positive m,k` |
| `I` meaning current, not `sqrt(-1)` | `--symbols I` |
| Fewer or more samples | `--samples 20000` |
| A looser tolerance | `--tol 1e-6` |
| Skip the symbolic prover on huge input | `--no-symbolic` |

For a single expression with nothing to compare it to, use `check` instead of
`validate`. For a derivation chain, use `derive --steps-file <file>` (one step
per line). For matrices, use `matrix --matrix "Matrix([[...]])"`.

**Windows / PowerShell**: any argument containing `*`, `/`, `(`, or `,` must be
quoted as a whole, otherwise the shell mangles it. Correct:
    --units "m=kg" --units "a=m/s**2" --units "F=kg*m/s**2"
Incorrect (bash-style, breaks on Windows):
    --units m=kg/s**2
The compact JSON summary is one line; on a narrow terminal it may wrap. Pass
`--json-pretty` to print it indented, or read the report file (see step 4).

### 4. Read the compact summary

The command prints one line of JSON. That summary is what belongs in your
context. The full Markdown report is written to `_reports/` - each run gets its
own file named from the request (e.g. `validate-<hash>-<timestamp>.md`) so batch
checks do not overwrite one another; `_reports/latest.md` always points at the
most recent one. Open the report only when the verdict is not a clean pass. Pass
`--report PATH` to choose the file, or `--json-pretty` to indent the summary.

Exit codes: `0` pass, `1` fail/conflict, `2` unknown, `3` parse error,
`4` internal error. `unknown` means the decidable check was *abstained*, not
that no check ran - name in your report which check abstained (dimension needs
a unit declaration; an expression checked with `--expect-zero` needs the
`validate` form when it is only zero conditional on a solution). Never report
`unknown` as "no check ran".

### 5. Report back in the user's notation

State the verdict, then the single most actionable finding, translated back into
the user's own symbols. Lead with the error, not with the list of checks that
passed.

## Verification

Five deterministic checks run in order, cheapest and most decisive first:

| | Check | What a failure means |
|---|---|---|
| D1 | Parse | The input could not be read; we abstain rather than guess. |
| D2 | Dimension | The two sides carry different dimensions, or a sum adds unlike quantities. |
| D3 | Limit | The two sides behave differently as some variable runs to 0 or infinity. |
| D4 | Numeric | They disagree at random points; the worst point is reported. |
| D5 | Symbolic | `lhs - rhs` will not reduce to zero. |

Two safety behaviours you must not override:

- **D2 disagrees but D4 agrees** → verdict `conflict`. Almost always the unit
  *declaration* is wrong, not the formula. Fix the units before touching the
  algebra.
- **D4 disagrees but 40-digit arithmetic agrees** → reported as a pass with a
  floating-point note. Near a root, two correct forms can differ by many ulps;
  this is not an algebraic error.

## Failure handling

- **Exit 3 (parse error)** - retry in SymPy syntax. If it still fails, quote the
  parser's hint to the user; do not "fix" the formula by guessing what they
  meant.
- **Exit 2 (unknown)** - report it as unknown and name what was not checked.
  Add units, or restate the claim as an identity between two full expressions,
  to turn it into a decidable check.
- **Exit 4** - report the message verbatim and stop. Do not fall back to
  checking by hand.
- **Definition, not identity** - `E = m*c**2` has a bare symbol on one side, so
  numerical sampling would reject a correct formula. The tool detects this,
  checks dimensions only, and says so. To get the full check, compare two
  independent derivations of the same quantity. Minimal decidable template:
  state it as an identity between two full expressions (no bare symbol), e.g.
  the work-energy theorem:
      validate --expr "0.5*m*vf**2 - 0.5*m*vi**2 = F_net*dx" \
               --units "m=kg" --units "vf=m/s" --units "vi=m/s" \
               --units "F_net=kg*m/s**2" --units "dx=m"
- **Residual expected to be zero** - when you have a single expression that
  should reduce to zero (an equation-of-motion residual, a cycloid identity),
  run `check --expr "<residual>" --expect-zero`. The symbolic prover then tests
  `expr == 0` directly. A genuine identity (e.g. `sin(x)**2 + cos(x)**2 - 1`)
  returns `pass`; an expression that is zero only *conditional* on a solution or
  a parametrisation is reported honestly as not-identically-zero. Without
  `--expect-zero`, `check` only diagnoses dimension and singularities.

## Requirements

`sympy`, `numpy`, `scipy` (see `requirements.txt`). The MCP server needs no
additional packages.

On Windows, install into a project-local venv (do not pollute the global
environment):
    python -m venv .venv
    .venv\Scripts\python -m pip install -r requirements.txt
    .venv\Scripts\python scripts/cli.py validate --expr "..."
