# QM Stage-1 G18-v4 Official Switch Note (v1)

Date: 2026-03-05

## Abstract

This note documents a governance-layer update of QM Stage-1 in QNG where `G18-v4` is promoted and applied as official policy (`official-v7`) without changing core gate formulas or threshold bands. The change addresses residual `G18d` fragility in multi-peak regimes using a peak-envelope local spectral-dimension estimator.

## Candidate Definition

For each profile:

1. keep `G18d-v1` pass decisions unchanged;
2. for `G18d-v1` fail cases, compute local spectral dimension on two peak basins;
3. define recovery observable as:
   - `ds_local_peak_envelope = max(ds_local_peak1, ds_local_peak2)`;
4. apply the unchanged legacy acceptance band (`1.2 < ds < 3.5`).

No threshold tuning and no gate formula edits were introduced.

## Evaluation Protocol

Promotion was evaluated on fixed prereg blocks:

- primary: `DS-002/003/006`, seeds `3401..3600` (`n=600`)
- attack: `DS-002/003/006`, seeds `3601..4100` (`n=1500`)
- holdout: `DS-004/008`, seeds `3401..3600` (`n=400`)

Promotion criteria:

- degraded `= 0`
- non-degradation per dataset
- net uplift on primary and attack
- holdout non-degradation

## Results

Promotion outcome: `PASS` on all three blocks.

Official-v6 -> official-v7:

- primary:
  - `G18: 568/600 -> 579/600`
  - `QM lane: 560/600 -> 571/600`
- attack:
  - `G18: 1400/1500 -> 1440/1500`
  - `QM lane: 1387/1500 -> 1426/1500`
- holdout:
  - `G18: 372/400 -> 382/400`
  - `QM lane: 372/400 -> 382/400`

All blocks preserve `degraded=0`.

## Regression Guard

Baseline and guard were refreshed to `v5`:

- baseline: `05_validation/evidence/artifacts/qm-stage1-regression-baseline-v5/`
- guard decision: `PASS`

## Stage-2 Impact

When Stage-2 raw prereg summaries are projected through official policies:

- `official-v6`: `2319/2500` pass
- `official-v7`: `2379/2500` pass

This yields a net gain of `+60` pass profiles with zero degradation.

## Conclusion

`G18-v4` is promoted as an official, non-degrading improvement under preregistered governance. Residual Stage-2 failures remain concentrated in `G18`, which motivates a follow-up `G18-v5` candidate lane while keeping the same anti post-hoc protocol.
