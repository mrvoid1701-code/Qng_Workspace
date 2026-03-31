# QM-GR Bridge Note (Stage-1)

Date: 2026-03-03  
Status: internal technical note

## 1) Setup

QNG uses a graph-discrete pipeline with two governance-separated lanes:

- `GR lane` (`G10..G16`): metric/covariant/action checks
- `QM lane` (`G17..G20`): quantization/info/thermal/semiclassical checks

The coupling point is `G20`, where semiclassical terms are evaluated while preserving GR guard invariants.

## 2) What Is Frozen

- GR official policy: `gr-stage3-g11-v5-official`
- QM official policy: `qm-stage1-g18-v3-official`
- Stability convergence official policy: `stability-convergence-v6-official`

Reference contracts:

- `docs/GR_STAGE1_FREEZE.md`
- `docs/QM_STAGE1_FREEZE.md`
- `docs/STABILITY_CONVERGENCE_V6_LOCK_IN.md`

## 3) Bridge Evidence Package

Coupling audit package:

- `05_validation/evidence/artifacts/qm-gr-coupling-audit-v2/`

Coverage:

- primary: `DS-002/003/006`, seeds `3401..3600` (`600` profiles)
- attack: `DS-002/003/006`, seeds `3601..4100` (`1500` profiles)
- holdout: `DS-004/008`, seeds `3401..3600` (`400` profiles)

Observed readout (frozen package):

- `G20 pass`: `2500/2500`
- GR guard pre/post per chunk: `PASS`
- no profile loss in completed packages

## 4) Interpretation

Operationally, Stage-1 bridge means:

1. QM lane can run at full block scale without breaking frozen GR guard checks.
2. Semiclassical coupling artifacts are reproducible via chunked/resumable tooling.
3. Governance remains anti post-hoc:
   - candidate changes are evaluated before switch
   - official mapping and tags are explicit
   - baselines/guards are versioned

## 5) Explicit Non-Claims

This note does **not** claim:

1. full strong-field closure,
2. full `3+1` tensor-mode closure,
3. complete theorem-level continuum proof.

These are Stage-2+ objectives and remain candidate/prereg work.

## 6) Minimal Reproduce

```bash
make qm_stage1_regression_guard_v3
make qm_gr_coupling_audit_primary_chunked
make qm_gr_coupling_audit_attack_chunked
make qm_gr_coupling_audit_holdout_chunked
```

For faster confirmation:

```bash
make qm_gr_coupling_audit_smoke
```

## 7) Next Controlled Step

Use `QM Stage-2` as a separate prereg lane:

- prereg doc: `docs/QM_STAGE2_PREREG.md`
- orchestration runner: `scripts/tools/run_qm_stage2_prereg_v1.py`
