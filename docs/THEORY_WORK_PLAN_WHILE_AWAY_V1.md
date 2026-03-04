# Theory Work Plan (While Away) - v1

Date: 2026-03-04
Policy: anti post-hoc only (`prereg -> run -> decide`, no threshold retuning).

## Goal

Strengthen the formal base for **stability** and **GR-QM bridge** so the next paper draft is defensible mathematically and reproducibly.

## 0-2h: Formal Stability Contract

Deliverables:

- `docs/STABILITY_THEORY_CONTRACT_V1.md`
- clear split: `S2 structural` vs `S1 energetic`
- explicit official observables and fail criteria

Content target:

- what is guaranteed (boundedness/positivity constraints)
- what is observed empirically (gate pass-rates)
- what remains open (full theorem gaps)

## 2-4h: Variational Alignment Note

Deliverables:

- `03_math/derivations/qng-discrete-action-noether-alignment-v1.md`

Content target:

- explicit discrete action symbols/conventions
- Euler-Lagrange to implemented update map (proof sketch)
- why covariant energy is the correct stability observable

## 4-6h: Convergence v6 Theory Hardening

Deliverables:

- `03_math/derivations/qng-convergence-contract-v1.md`
- optional tiny helper script for convergence diagnostic summary (no gate changes)

Content target:

- discrete->continuum assumptions written explicitly
- error model form (`h, dt, kernel scale`) and expected trend class
- limitations: low support / mixed regimes / insufficient statistical power

## 6-8h: GR-QM Bridge Formalization

Deliverables:

- `docs/QM_GR_BRIDGE_FORMAL_STATUS_V1.md`
- short paper note update in `06_writing/`

Content target:

- define what Stage-1 coupling *proves operationally*
- define what it *does not* prove yet (strong-field 3+1 tensor-full regime)
- lock promotion policy for future candidate gates

## Stop Conditions

- If any step requires formula/threshold changes, stop and open `candidate/prereg` lane instead of editing official policy.
- If evidence risk appears, move outputs to dedicated artifact folder; never overwrite official evidence.

## Immediate next run after return

1. `G11-v5` candidate prereg execution.
2. `degraded=0` check across primary/attack/holdout.
3. decide: promote or keep as known limitation.
