# Cross-Dataset Gate Validation — v1

Date: 2026-03-07
Seed: 3401 (standard anchor seed)

## Scope

Full gate suite run (G10–G20) on DS-002, DS-003, DS-006.
Primary focus: G17–G20 QM gates per NEXT_STEPS Prioritate 2.

## Results

| Dataset | G10 | G11 | G12 | G13 | G14 | G15 | G16 | G17 | G18 | G19 | G20 | Total |
|---------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|
| DS-002  | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | 11/11 |
| DS-003  | ✓   | ✓   | ✓   | ✓   | ✓   | **FAIL** | ✓ | ✓ | ✓ | ✓ | ✓ | 10/11 |
| DS-006  | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | ✓   | 11/11 |

## QM Gate Summary (G17–G20)

**All PASS on all three datasets.** Prioritate 2 from NEXT_STEPS is complete.

| Dataset | G17 | G18 | G19 | G20 |
|---------|-----|-----|-----|-----|
| DS-002  | ✓   | ✓   | ✓   | ✓   |
| DS-003  | ✓   | ✓   | ✓   | ✓   |
| DS-006  | ✓   | ✓   | ✓   | ✓   |

## Fragile Metrics (margin < 20%)

| Dataset | Gate | Metric | Value | Threshold | Margin |
|---------|------|--------|-------|-----------|--------|
| DS-002  | G16d | hessian_frac_neg | 1.000 | >0.9 | 11.1% |
| DS-002  | G17a | spectral_gap | 0.01109 | >0.01 | 10.9% |
| DS-002  | G18d | spectral_dim_ds | 1.284 | (1.0, 3.5) | 11.4% |
| DS-003  | G12c | radial_ratio | 1.142 | >1.0 | 14.2% |
| DS-003  | G16d | hessian_frac_neg | 1.000 | >0.9 | 11.1% |
| DS-003  | G17a | spectral_gap | 0.01060 | >0.01 | 6.0% |
| DS-006  | G16d | hessian_frac_neg | 1.000 | >0.9 | 11.1% |
| DS-006  | G17a | spectral_gap | 0.01046 | >0.01 | 4.6% |
| DS-006  | G17b | propagator_slope | -0.01067 | <-0.01 | 6.6% |

**Note**: G17a spectral_gap is fragile across all datasets (4.6%–10.9% margin).
This is an expected characteristic of sparse discrete graphs near the connectivity threshold.

## Known Limitation: DS-003 G15b Failure

**G15b Shapiro ratio: 1.944 (threshold >2.0, margin -2.8%)**

DS-003 systematically fails G15b (Shapiro delay inner/outer ratio) at all tested
phi_scale values (0.04–0.12, ratios 1.92–1.97). This is a structural property of
the DS-003 graph topology: the inner/outer radial shell Shapiro contrast is
insufficient to satisfy the >2.0 threshold.

**Scope of impact:**
- Affects GR gate G15 (PPN parameters) only
- Does NOT affect QM gates G17–G20
- DS-003 is used in QM Stage-1/Stage-2 evaluation where G15 is not part of the QM lane
- G15b-v2 (top/bottom 10% quantile variant) was not checked separately

**Status:** Known limitation, not blocking for QM Stage-2 or paper submission.
Documented here for transparency. Potential fix: investigate whether a different
radial shell definition or phi_scale resolves the gap, or lower G15b threshold
with justification.

## Commands

```bash
python run_all_gates.py --dataset-id DS-002  # 11/11 PASS
python run_all_gates.py --dataset-id DS-003  # 10/11 (G15 FAIL)
python run_all_gates.py --dataset-id DS-006  # 11/11 PASS
```
