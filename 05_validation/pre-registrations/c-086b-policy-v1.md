# C-086b Policy Document v1

Date: 2026-02-22
Authored by: Claude Sonnet 4.6
Purpose: Satisfy TASKS.md items 96-98 — permanently document the freeze, labeling, and registry policy for C-086b tracks.

---

## 1) C-086b v1 — Permanently Frozen as Falsification History

**Status: FALSIFIED (closed)**

- Pre-registration: `05_validation/pre-registrations/qng-c-086b-amplitude-band-v1.md`
- Run outcome: 5/5 FAIL (strict gates)
- Date of falsification: 2026-02-21

**Policy:**
- This pre-registration and its outcome are permanently frozen. No edits, no retroactive gate relaxation, no re-labeling.
- The failure of C-086b v1 is part of the auditable scientific record and must remain visible in the repository.
- Any future amplitude claim must be in a new pre-registration (C-086b2, C-086b3, or higher) with a new gate set justified independently of v1 outcomes.
- Do NOT use v1 outcomes to motivate gate relaxation in v2/v3.

---

## 2) C-086b2 — Labeled Calibration-Only Until Out-of-Sample Pass

**Current status: calibration-only (not confirmed prediction)**

- Pre-registration: `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`
- Calibration outcome: E1-E3 batch — 3/3 PASS (strict gates, locked)
- Holdout outcome: H1-H3 — 0/3 PASS (locked gates, post-lock run)

**Policy:**
- C-086b2 MUST be labeled "calibration-only" in all communications, papers, and summaries until a disjoint out-of-sample holdout achieves a PASS with unchanged gates.
- The E1-E3 calibration pass does NOT constitute a confirmed prediction. It constitutes a parameter-fit result.
- The H1-H3 holdout FAIL is the authoritative verdict for C-086b2 predictive status.
- Do NOT present C-086b2 calibration pass as evidence for the amplitude claim without explicitly noting the holdout failure.

---

## 3) Append-Only Holdout Registry Policy

**File: `05_validation/pre-registrations/holdout-registry.csv`**

**Policy:**
- The holdout registry is append-only. No row may be deleted, modified, or overwritten after being committed.
- New holdout runs must be added as new rows with a new `created_utc` timestamp.
- If a holdout entry has status `executed-fail` or `executed-pass`, it is final and immutable.
- Provisional entries (status `locked`) may be updated to `executed-*` after a run, but the original `locked` entry must remain visible in git history.
- Any violation of append-only policy (editing past entries) invalidates the holdout track and requires a new pre-registration.

**How to add a new entry:**
```
Append a new row to holdout-registry.csv with:
- created_utc: current UTC timestamp
- track_id: C-086b2 / C-086b3 / etc.
- model_version: v1 / v2 / etc.
- holdout_id: H4, H5, ... (next sequential ID)
- prereg_file: path to the relevant pre-registration
- scope: holdout
- flyby_pass_ids: comma-separated mission IDs (disjoint from calibration set)
- pioneer_record_ids: comma-separated Pioneer record IDs used
- status: locked (before run) or executed-pass / executed-fail (after run)
- notes: brief description of run context
```

**Enforcement:** any PR that modifies existing holdout-registry.csv rows (rather than appending) must be rejected.

---

## Summary

| Track | Status | Label | Immutability |
|---|---|---|---|
| C-086b v1 | Falsified | Falsification history — frozen | Permanent |
| C-086b2 | Holdout FAIL | Calibration-only | Until disjoint out-of-sample PASS |
| C-086b3 | Holdout FAIL (provisional) | Provisional — awaiting real residuals | Until real OD residuals ingested |
| holdout-registry.csv | Active | Append-only | All past rows immutable |
