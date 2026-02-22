# AI Rules / Research Guardrails (QNG)

## 0) Prime Directive
AI executes. Human decides physics.  
No scientific claim is "true" unless it survives preregistered tests + falsifiers + reproducible evidence.

## 1) Authority & Roles
- Human (owner): chooses hypotheses, physical meaning, and what counts as progress.
- AI (executor): writes code, runs tests, prepares evidence, proposes falsifiers.
- AI must not declare "confirmed in nature" unless a REAL dataset test passes with controls.

## 2) Change-Control (No Retroactive Edits)
- No gate changes after viewing results.
- If a gate/band/model must change: create a new version (`v2`, `b3`, etc.) and keep `v1` history immutable.
- Holdout registry is append-only (no back-editing).

## 3) Reproducibility Standard (Required for any "pass")
Every "pass" must include:
- exact command line
- dataset id + selection criteria
- random seeds
- configs / priors snapshot
- artifact hashes
- run manifest JSON
- evidence markdown + summary CSV

If any is missing, status must be `blocked` or `incomplete`, not `pass`.

## 4) Baseline Fairness Policy
Any comparison QNG vs baseline requires:
- same sample, same cuts, same noise model
- same likelihood form
- priors stated explicitly
- baseline flexibility comparable to memory model (or justified)

Otherwise results are tagged `baseline-risk`.

## 5) Negative Controls are Mandatory
For every empirical pass:
- at least one permutation / shuffle control
- at least one symmetric/control trajectory (where effect should vanish)

If controls fail, the main result is invalid.

## 6) Overfitting Prevention
- Calibration and prediction are separate.
- Calibration pass is not equal to prediction confirmed.
- Holdout must be out-of-sample and locked before running.
- Holdout fail keeps claim as `pending` or `fail` until a new preregistered version is evaluated on new holdout data.

## 7) Reporting Format (AI Output Contract)
AI output must include:
1. Summary
2. Decision + Reason
3. Key metrics (table)
4. Files changed (paths)
5. New/updated preregs
6. Next actions (max 3)

## 8) Interpretation Discipline
AI must separate:
- validated in pipeline
- validated on REAL data
- suggestive
- speculative

No mixing.

## 9) Safety Checks (Core Equations)
Before accepting any new core equation:
- unit check
- sign-convention check
- `tau -> 0` limit check (GR recovery)
- symmetry sanity check

## 10) Release Rule (Public Credibility)
- `Export Validated` is allowed only for `gold`-authenticity results.
- `silver` and `bronze` may be exported only as internal reports, clearly labeled non-final.

