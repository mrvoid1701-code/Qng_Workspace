# GR Status In 60 Seconds

Date: 2026-03-02
Status owner: QNG GR/PPN lane
Freeze contract: `docs/GR_STAGE1_FREEZE.md`

## What "GR-like" Means In This Repo

The GR-like chain is currently defined by gates `G10..G16`:

- `G10`: covariant ADM metric construction and weak-field consistency
- `G11`: Einstein-equation closure checks
- `G12`: known-solution sanity (de Sitter + Schwarzschild-like behavior)
- `G13`: covariant metric-wave dynamics
- `G14`: covariant conservation checks
- `G15`: PPN checks (`gamma`, `beta`, Shapiro, EP proxy)
- `G16`: action-functional Euler-Lagrange closure

## Official vs Diagnostic vs Candidate

- `G15b official`: `G15b-v2` (potential-quantile Shapiro proxy)
- `G15b legacy diagnostic`: `G15b-v1` (radial-shell proxy)
- `G16b official`: frozen hybrid policy
  - low-signal (`std(T11)/|mean(T11)| > 10`) -> `G16b-v2` branch
  - high-signal -> `G16b-v1` branch
- `G16b legacy diagnostic`: `G16b-v1`
- `G16b candidate component`: `G16b-v2`
- `GR-Stage-2 official policy`: `G11a-v4 + G12d-v2` governance mapping
  - effective tag: `gr-stage2-g11-v4-official`
  - source decision: `docs/GR_STAGE2_G11_V4_OFFICIAL_SWITCH.md`
- `GR-Stage-3 official policy`: `G11/G12` candidate-v2 governance mapping
  - effective tag: `gr-stage3-g11g12-v2-official`
  - source decision: `docs/GR_STAGE3_OFFICIAL_SWITCH.md`

## Baseline Used For Guard

Regression guard baseline is:

- `05_validation/evidence/artifacts/gr-regression-baseline-v1/gr_baseline_official.json`

Stage-2 governance baseline is:

- `05_validation/evidence/artifacts/gr-stage2-regression-baseline-v1/gr_stage2_baseline_official.json`

Frozen metadata:

- `effective_tag`: `gr-g16b-hybrid-official`
- `effective_commit`: `077478d`
- `effective_date_utc`: `2026-03-02`
- profiles: `53` official pass profiles from the grid source

## 3 Key Numbers

1. PHI-scale monotonicity (regime behavior, not single-point rescue)
- In `03_math/derivations/qng-phi-scale-regime-note-v1.md`, `G15a gamma_dev`, `G15d EP_ratio`, and `G15b shapiro_ratio` increase monotonically with `PHI_SCALE` on `DS-002/003/006` for `0.04..0.12`.

2. G15b-v2 robustness
- Promotion grid (`DS-002/003/006`, seeds `3401..3600`, `n=600`):
  - `G15b-v2`: `600/600` pass
  - `G15b-v1`: `523/600` pass
- Source: `05_validation/evidence/artifacts/g15b-promotion-200seed-grid-v1/`.

3. G16b hybrid non-degradation
- Hybrid prereg run (`n=600`):
  - `v1_pass=473`, `hybrid_pass=516`
  - `improved_vs_v1=43`
  - `degraded_vs_v1=0`
- Promotion/attack package passed and switch is now official.
- Source: `05_validation/evidence/artifacts/g16b-hybrid-promotion-eval-v1/`.

4. Stage-2 official closure
- Governance switch over frozen official-v3 summary (`n=600`):
  - `G11`: `594/600 -> 597/600`
  - `STAGE2`: `594/600 -> 597/600` (`99.5%`, degraded `0`)
- Source: `05_validation/evidence/artifacts/gr-stage2-official-v4/`.

5. Remaining known limitation classes (primary, v4)
- `g11b_slope_fail`: `1`
- `weak_rank_corr`: `2`
- Source: `05_validation/evidence/artifacts/gr-stage2-g11-candidate-v4/primary_ds002_003_006_s3401_3600/summary.csv`.

6. Stage-3 official-v2 mapping closure
- primary: `570/600 -> 592/600` (`degraded=0`)
- attack seed500: `1345/1500 -> 1433/1500` (`degraded=0`)
- holdout: `380/400 -> 398/400` (`degraded=0`)
- Source: `05_validation/evidence/artifacts/gr-stage3-g11-g12-promotion-eval-v1/report.md`.

## Current Readout

- GR guard against official baseline: `PASS`
- GR Stage-3 official policy: active (`gr-stage3-g11g12-v2-official`)
- Stage-3 guard against official baseline: `PASS`
- Stage-3 remaining official primary fails: `8/600`
  - `G11`: `7`
  - `G12`: `1`
  - dominant classes: `weak_corr_multi_peak`, `weak_corr_sparse_graph`
- Latest run artifact:
  - `05_validation/evidence/artifacts/gr-regression-baseline-v1/latest_check/regression_report.json`
  - `05_validation/evidence/artifacts/gr-stage3-regression-baseline-v1/latest_check/regression_report.json`
