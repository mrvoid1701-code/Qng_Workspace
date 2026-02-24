# Cross-Dataset Sanity Confirmation v1

Date: 2026-02-22
Authored by: Claude Sonnet 4.6
Purpose: Satisfy TASKS.md items 82-83 — confirm cross-dataset sanity check on DS-003 and explicitly state no post-hoc gate edits were made between DS-002 and DS-003 comparisons.

---

## Scope

This document certifies the cross-dataset closure sanity check for Core Closure v1 metric tests:
- Primary dataset (calibration): DS-002
- Sanity check dataset: DS-003
- Additional replication: DS-006

---

## Confirmation: No Post-Hoc Gate Edits

**Certified:** The gates used for DS-003 and DS-006 runs are byte-for-byte identical to those locked in the DS-002 pre-registration (`qng-metric-hardening-v3.md`).

Specific confirmation:

| Gate | DS-002 threshold | DS-003 threshold | DS-006 threshold | Modified? |
|---|---|---|---|---|
| D1 min_eig | `>= 1e-8` | `>= 1e-8` | `>= 1e-8` | NO |
| D2 median(Delta_g) | `<= 0.10` | `<= 0.10` | `<= 0.10` | NO |
| D2 p90(Delta_g) | `<= 0.25` | `<= 0.25` | `<= 0.25` | NO |
| D3 median(cos_sim) | `>= 0.90` | `>= 0.90` | `>= 0.90` | NO |
| D3 p10(cos_sim) | `>= 0.70` | `>= 0.70` | `>= 0.70` | NO |
| D4 shuffled median | `< 0.55` | `< 0.55` | `< 0.55` | NO |

Method lock (`metric-lock-v3.md`) was not modified between DS-002, DS-003, and DS-006 runs. Seed, scale set, and sample count were identical.

---

## Cross-Dataset Results

| Dataset | D1 min_eig | D2 median/p90 | D3 median/p10 | D4 shuffled | Decision |
|---|---|---|---|---|---|
| DS-002 (calibration) | 0.300856 | 0.056367 / 0.178355 | 0.992374 / 0.960620 | -0.133569 | PASS |
| DS-003 (sanity) | 0.300461 | 0.048771 / 0.149748 | 0.994201 / 0.951281 | -0.111837 | PASS |
| DS-006 (replication) | 0.300471 | 0.059885 / 0.139852 | 0.995345 / 0.959466 | -0.430659 | PASS |

All three datasets pass with unchanged gates. DS-003 and DS-006 results are genuine cross-dataset replications.

---

## Anti-Leak Cross-Dataset Results

| Dataset | positive_median | label_perm_median | rewire_median | rewire_shuffled_median | Decision |
|---|---|---|---|---|---|
| DS-002 (calibration) | 0.992374 | 0.242666 | 0.036314 | -0.068478 | PASS |
| DS-003 (sanity) | 0.994201 | 0.143302 | 0.036521 | -0.015755 | PASS |
| DS-006 (replication) | 0.995345 | 0.022733 | -0.119704 | -0.033509 | PASS |

No gate edits between datasets. All anti-leak controls collapse as expected on all three datasets.

---

## Certification

- Cross-dataset sanity: **CONFIRMED PASS** on DS-003 and DS-006
- Post-hoc gate edits: **NONE** — gates identical across all datasets
- Method changes: **NONE** — metric-lock-v3 unchanged across runs
- Seed changes: **NONE** — seed 3401 used for all runs
- Evidence source: `05_validation/pre-registrations/qng-metric-hardening-v3-ds003-run-record.md` and `qng-metric-hardening-v3-ds006-run-record.md`
