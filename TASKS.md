# Current Tasks

## Priority P0 (Do First) - Freeze and Reproducibility

- [x] Freeze + tag `Gold Pack v1` with fixed scripts, seeds, configs, manifests, and artifact hashes. (Tag `gold-pack-v1` created 2026-02-22. Run `git push origin gold-pack-v1` to push tag to GitHub.)
- [x] Create a locked reproducibility snapshot file for `Gold Pack v1` (inputs, commands, outputs, hashes).
- [x] Ensure run manifests and results log are fully aligned before tagging.

## Priority P1 - Gold Communication Package

- [x] Create one-page `Gold Claims Summary`.
- [x] Include gold claims: `C-058`, `C-082`.
- [x] Include dataset list + selection criteria.
- [x] Include full negative-controls list.
- [x] Include full robustness-check list.
- [x] Explicitly state which parameters are global versus fit per sample.

## Priority P0-BULLETPROOF - Paper Defensibility Add-ons

- [x] Build `Repro Pack v1` with manifest, artifact hashes, fixed commands, and `reproduce_all.ps1`.
- [x] Add `How to reproduce in 30 minutes` guide.
- [x] Add supplementary anti-leak controls for metric (`label permutation + graph rewire + graph rewire + label permutation`).
- [x] Add explicit paper-status wording: metric v3 is pipeline-level stable closure (consistency + discriminability), not physical uniqueness claim.

## Priority P2 - Next Gold Target (Trajectory REAL)

- [x] Set next gold target to Trajectory REAL.
- [x] Select 1-2 pilot missions first (not all missions at once).
- [x] Pilot objective: reproduce directional signature + consistent `tau`.
- [x] Integrate `data/trajectory/pioneer_ds005_anchor.csv` into executable validation flow.
- [x] Upgrade Pioneer from anchor-only to full test path.
- [x] Show lag-term fit after thermal/non-gravitational corrections, not before.
- [x] Run cross-domain trajectory checks for `QNG-T-028` and `QNG-T-011`.
- [x] Update evidence and `05_validation/results-log.md` after reruns.

## Priority P3 - C-086 Refactor and Pre-Registration

- [x] Promote `C-086` from fixed amplitude band to scaling-law claim.
- [x] Define scaling law inputs: perigee altitude, velocity, `||grad Sigma||`, inbound/outbound geometry, `tau(chi)`, `v.grad Sigma`.
- [x] Create `C-086a`: directional near-perigee signature (robust signature claim).
- [x] Create `C-086b`: amplitude numeric band prediction (separate numeric claim).
- [x] Archive `C-086b` v1 strict prereg outcome (`5/5` fail) without post-hoc threshold edits.
- [x] Lock `C-086b2` calibration prereg and execute `E1-E3` batch (`3/3` strict pass).
- [x] Pre-register amplitude band before running on new missions (avoid post-hoc fitting).
- [x] Lock `C-086b2` holdout prereg and run `H1-H3` with unchanged strict gates (`0/3` pass).
- [x] Introduce `C-086b3` covariate scaling prereg + executable pipeline.
- [x] Add append-only holdout registry and record b2/b3 holdout sets.
- [x] Run `C-086b3` lock execution (`blocked_missing_holdout_rows` until disjoint mission rows are ingested).
- [ ] Ingest additional non-control real flyby missions beyond `CASSINI_1` and rerun locked `C-086b2` holdout.
- [x] Ingest `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1` pass rows and execute locked `C-086b3` holdout. (Executed on 2026-02-21 with Horizons-derived geometry; holdout status moved from blocked to fail under provisional `delta_v` placeholders.)

## Priority P2 - Straton Mass-Scaling v2 (Classic Subset)

- [x] Run `QNG-T-STRATON-001` on full DS-005 (fail: alpha CV=0.775, LOO=0.886 — placeholder residuals inflate variance).
- [x] Run `QNG-T-STRATON-002`: classic subset only (GALILEO_1/2, NEAR_1, CASSINI_1, ROSETTA_1/2/3, MESSENGER_1, EPOXI_1..5). (Executed 2026-02-22; FAIL: G1 delta_bic=+5531, G2 alpha_CV=1.607, G4 LOO=1/13. Only G3 shuffle passes. 4 leverage rows detected. Evidence: `05_validation/evidence/qng-t-straton-002.md`; artifacts: `05_validation/evidence/artifacts/qng-t-straton-002/`.)

## Priority P4 - Publish Defensibility (Rotation Baseline)

- [x] Add explicit baseline note in writing: exact rotation baseline model, parameters, and priors.
- [x] Run a baseline-upgrade check with comparable flexibility.
- [x] Compare upgraded baseline vs memory model under same sample and likelihood.
- [x] Add results to paper/evidence to address underfit-baseline critique risk.

## Priority P5 - Node/Volume Core Closure v1

- [x] Write one-page closure spec for node, volume, chi, Sigma, and update operator.
- [x] Freeze a single v1 volume rule and document conservation policy (`V-B` selected).
- [x] Add executable closure test suite (`T-V-01..T-V-04`) with reproducible artifacts.
- [x] Run rule-comparison robustness batch and lock selection from gate outcomes.
- [x] Update `QNG-T-013` and `QNG-T-014` evidence/manifests with closure-gate metrics.

## Priority P6 - Core Closure Hardening (Immediate Credibility)

- [x] Lock Core Closure v1 with selected `V-B` rule and keep gates fixed.
- [x] Write explicit `fixed vs free` parameter contract for Core v1 (`gates/thresholds/rule fixed`, scan parameters free in declared ranges). (Done 2026-02-22; see `05_validation/pre-registrations/core-v1-fixed-free-contract.md`.)
- [x] Create `Core Snapshot v1` manifest (inputs, commands, seeds, artifact hashes) dedicated to closure run. (Done 2026-02-22; see `05_validation/core-snapshot-v1.json`.)
- [ ] Run sensitivity scan (`P0`) on key parameters (`sigma_min`, `sigma_birth`, growth weights) with `+-20%` perturbations.
- [ ] Record sensitivity outcome class: `stable pass`, `expected degradation`, `unstable`.
- [ ] Run ablation test (`P0`) removing phase component and record impact on `T-V-03` and `T-V-02`.
- [ ] Run ablation test (`P0`) removing structure component and record impact on `T-V-01` and `T-V-04`.
- [ ] Build ablation fingerprint table showing which gate fails when each component is removed.
- [x] Run cross-dataset sanity (P1) by applying unchanged closure gates on DS-003. (Confirmed 2026-02-22; see `05_validation/cross-dataset-sanity-v1.md`. All gates identical, DS-003 PASS.)
- [x] Confirm no post-hoc gate edits between DS-002 and DS-003. (Certified 2026-02-22; see `05_validation/cross-dataset-sanity-v1.md`.)

## Priority P7 - Trajectory Real-World Holdout (No Gate Changes)

- [x] Ingest `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1` rows in `DS-005` with full correction columns. (Columns are present; values currently provisional `0.0` placeholders for non-grav corrections and residuals where OD residual summaries are still missing.)
- [x] Rerun locked `C-086b3` holdout with unchanged model/gates after ingest. (Result: `fail`, no gate/model edits.)
- [x] Rerun `QNG-T-011`, `QNG-T-028`, and `QNG-T-041` on expanded DS-005 (post-horizons ingest) and sync logs/evidence metrics. (All remain `pass`; small numeric drift only, no gate/model edits.)
- [x] Audit local downloaded source bundles for holdout OD residual evidence and document what is still missing. (Report: `07_exports/reports/trajectory-holdout-source-audit-2026-02-21.md`.)
- [x] Add HELIOWeb CLI tooling + object-code notes for batch trajectory-context pulls (`scripts/fetch_helioweb_data.py`, `data/trajectory/sources/helioweb/README.md`).
- [x] Pull HELIOWeb holdout mission context (hourly mission-minus-Earth) for `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1` and parse to structured CSV summary.
- [x] Audit newly downloaded Horizons/PDF exports and integrate relevant Juno/Bepi provenance into DS-005 sources/notes. (Reports: `07_exports/reports/downloads-new-files-audit-2026-02-21-1905.md`, `07_exports/reports/downloads-new-files-audit-2026-02-21-1936.md`, `07_exports/reports/downloads-new-files-audit-2026-02-21-1954.md`, `07_exports/reports/downloads-new-files-audit-2026-02-21-2013.md`, `07_exports/reports/downloads-official-sources-pull-2026-02-21-2025.md`.)
- [x] Publish holdout status note: recent-mission validation remains ongoing and pending official radiometric residual datasets. (Report: `07_exports/reports/trajectory-holdout-ongoing-status-2026-02-21-2035.md`.)
- [x] Freeze `C-086b3` numeric holdout as data-pending while keeping prereg/model/gates locked (no retroactive edits).
- [x] Keep `C-086b v1` permanently frozen as falsification history. (Policy documented 2026-02-22; see `05_validation/pre-registrations/c-086b-policy-v1.md §1`.)
- [x] Keep `C-086b2` labeled calibration-only (not confirmed prediction) until out-of-sample pass. (Policy documented 2026-02-22; see `c-086b-policy-v1.md §2`.)
- [x] Enforce append-only holdout registry updates for all new mission additions. (Policy documented 2026-02-22; see `c-086b-policy-v1.md §3`.)
- [ ] Replace provisional holdout residual placeholders (`JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`) with published OD residual/sigma values and rerun locked `C-086b3`.

## Priority P8 - Fundamental Theory Closure (GR/QM)

- [x] Derivari fundamentale GR/QM (discrete-to-continuum bridge, equations and assumptions locked). (Done 2026-02-22; see `03_math/derivations/qng-discrete-to-continuum-v1.md`. 5 core assumptions identified and classified. QM sector remains open sketch.)
- [x] Necesitatea fizica a lui `chi (chi)` (show non-redundancy vs pure reparameterization).
- [x] Emergenta metricii continue (derive effective metric from coarse-grain and verify GR-limit consistency).

## Priority P8-METRIC - Emergent Continuous Metric Hardening (v1)

- [x] Lock v1 definitions (`01_notes/metric/metric-lock-v1.md`) with fixed distance/smoothing/scales/chart/sampling/normalization.
- [x] Add boxed core metric derivation + discrete Hessian estimator in `03_math/derivations/qng-core-emergent-metric-v1.md`.
- [x] Implement executable runner `scripts/run_qng_metric_hardening_v1.py`.
- [x] Add prereg gates D1-D4 in `05_validation/pre-registrations/qng-metric-hardening-v1.md`.
- [x] Generate metric hardening artifacts + evidence page (`05_validation/evidence/qng-metric-hardening-v1.md`).
- [x] Integrate into `test-plan`, `results-log`, run manifest, and snapshot export.
- [x] Open `metric-lock-v2` only after v1 fail, with new prereg and unchanged gates.
- [x] Archive v2 fail history (`D1/D4` recovered, `D2/D3-tail` fail) as immutable audit trail.
- [x] Open `metric-lock-v3` with conformal gauge + fixed anisotropy shrinkage and unchanged gates.
- [x] Run `QNG-T-METRIC-003` and record full pass (`D1-D4`) with reproducible artifacts.
- [x] Run locked v3 cross-dataset replication on `DS-003` and `DS-006` before any v4 edits.
- [x] Add and run `QNG-T-METRIC-005` (GR Bridge v1) on locked `qng-metric-hardening-v3*` artifacts and record full `B1-B5` pass.
- [x] Open `metric-lock-v4` (Frobenius normalization, vacuum singularity fix): lock definition, prereg, implement `run_qng_metric_hardening_v4.py`, run G0+D1-D4 on DS-002/DS-003/DS-006 — all PASS (κ_max≈1.94, D3 med≈0.994). (Done 2026-02-24; evidence: `05_validation/evidence/qng-metric-hardening-v4.md`.)
- [x] `QNG-T-CURL-001` — Curl of acceleration field test: lock prereg, implement script, run on DS-002/DS-003/DS-006. C1 PASS (curl_rel ~1e-11, machine precision — exactly curl-free in constant-metric regime). C2 PASS. (Done 2026-02-24; evidence: `05_validation/evidence/qng-t-curl-001.md`.)
- [x] Lock Σ dynamics minimal equation (EOM-Σ): selected generalized Poisson `Δ_g Σ = α ρ`, proved Newtonian limit recovery, 1 new free parameter (α = 4πG), T-SIG-003 analytic PASS. (Done 2026-02-24; derivation: `03_math/derivations/qng-sigma-dynamics-v1.md`; prereg: `qng-sigma-dynamics-prereg-v1.md`.)

## Priority P9 - High-Impact Next Tests (Requested)

- [x] `QNG-T-TAUMAP-001` - Build real-data `tau` map per event/arc and test intra-mission stability + cross-mission transferability + geometry coupling (`|(v·nabla)nablaSigma|`) with negative controls. (Pass, evidence: `05_validation/evidence/qng-t-taumap-001.md`; report: `07_exports/reports/qng-t-taumap-001-2026-02-21-2126.md`.)
- [x] `QNG-T-UNIFY-001` - Fit one global memory law (single kernel/parameter set) jointly on lensing offsets + rotation curves, same sample/likelihood comparability locked. (Pass, evidence: `05_validation/evidence/qng-t-unify-001.md`; report: `07_exports/reports/qng-t-unify-001-2026-02-21-2126.md`.)
- [x] `QNG-T-HYST-001` - Test temporal hysteresis prediction (`Sigma(t)=integral K(t-t')chi(t')dt'`) by comparing relaxed vs merging cluster subsets without adding new free parameters. (Pass, evidence: `05_validation/evidence/qng-t-hyst-001.md`; report: `07_exports/reports/qng-t-hyst-001-2026-02-21-2126.md`.)
- [x] `QNG-T-GEODESIC-001` - Run geodesic sanity checks on metric v3 (numeric stability, Newtonian recovery, local alignment with `-nablaSigma`). (Pass, evidence: `05_validation/evidence/qng-t-geodesic-001.md`; report: `07_exports/reports/qng-t-geodesic-001-2026-02-21-2126.md`.)
- [x] `QNG-T-GRSWEEP-001` - Run hard kill-switch sweep `tau -> 0` and verify monotonic signal collapse while controls remain clean. (Pass, evidence: `05_validation/evidence/qng-t-grsweep-001.md`; report: `07_exports/reports/qng-t-grsweep-001-2026-02-21-2126.md`.)
- [x] `QNG-T-TRJ-CTRL-001` - Add adversarial anti-shortcut controls for trajectory (orientation/segment/window randomization) and require controlled signal collapse. (Pass, evidence: `05_validation/evidence/qng-t-trj-ctrl-001.md`; report: `07_exports/reports/qng-t-trj-ctrl-001-2026-02-21-2126.md`.)
- [ ] `QNG-T-STRATON-001` - Straton mass-scaling test (τ = α·m vs τ constant). Gates: ΔBIC(modelB−modelA) ≤ -10 (“strong support”), bootstrap CV(α) < threshold, shuffle-mass negative control collapses ΔBIC, leave-10%-out pass_fraction ≥ 0.9. Inputs: add `spacecraft_mass_kg` per flyby row in `DS-005`; prereg + evidence path to be created. Related claims: `QNG-C-014` (τ(χ)), straton relevance.

## Backlog / Secondary

- [ ] Graph section upgrade in UI (`Explorer -> Graph`) with improved usability and workflow guidance.
- [x] Remove duplicated claims. (Checked 2026-02-22 — no duplicates found: 118 claims, sequential numbering, no duplicate titles or statements.)
- [x] Identify weakest assumptions. (Done 2026-02-22; see `04_models/weakest-assumptions-v1.md`. Weakest: chi=m/c mass scaling — FAIL on STRATON-002. Most robust: emergent metric from Hessian(Sigma).)
- [x] Update test plan with at least one falsifier per core claim. (Done 2026-02-22; see `05_validation/falsifiers-per-core-claim-v1.md`.)

## Mission Test Queue (Ordered)

### Priority A (Critical)

- [ ] `QNG-T-SYS01` - Global Solar System universal `tau` fit (single-parameter consistency target).
- [ ] `QNG-T-P02` - Pioneer directional dependence (`v . nabla Sigma`) after all non-grav corrections.
- [x] `QNG-T-F02` - Flyby cross-mission `tau` consistency with fixed gates. (Expanded classical published-residual set pass on 2026-02-21; evidence: `05_validation/evidence/qng-t-f02-cross-mission-tau.md`; report: `07_exports/reports/trajectory-f02-cross-mission-2026-02-21-2038.md`.)
- [x] `QNG-T-F03` - Flyby inbound vs outbound directional sign signature.
- [x] `QNG-T-F01` - Flyby near-perigee lag spike signature.

### Priority B (High)

- [ ] `QNG-T-P01` - Pioneer residual acceleration persistence after thermal/SRP/maneuver controls.
- [ ] `QNG-T-DS02` - Deep-space acceleration correlation vs solar gravitational gradient.
- [ ] `QNG-T-V02` - Voyager regime transition (heliosphere to interstellar) parameter-shift test.

### Priority C (Supportive)

- [ ] `QNG-T-P03` - Pioneer acceleration evolution vs heliocentric distance.
- [ ] `QNG-T-DS01` - Deep-space lag persistence at large distance (Cassini/Juno segments).
- [ ] `QNG-T-V03` - Voyager directional acceleration test.
- [ ] `QNG-T-V01` - Voyager residual acceleration detection under strict systematics.

## Later / Not Now (Parking)

- [x] Environment lock hardening: add explicit Python version + `requirements.txt` / `pip freeze` snapshot to repro pack. (Done 2026-02-22; python_version and environment block added to `07_exports/repro-pack-v1/repro-pack-v1-manifest.json`. requirements.txt updated with all core packages.)
- [ ] Environment lock hardening: add lockfile (`conda-lock` or `poetry.lock`) for deterministic dependency resolution.
- [ ] Environment lock hardening (bonus): add `Dockerfile` for portable reproducible runtime.
- [ ] Single-command CI: add GitHub workflow to run `07_exports/repro-pack-v1/reproduce_all.ps1` (or equivalent) on each commit.
- [x] No-double-dipping explicitness: in metric prereg/evidence, mark clearly what is calibration set vs holdout set. (Done 2026-02-22; added calibration vs holdout section to `qng-metric-hardening-v3.md` and `qng-metric-anti-leak-v1.md`.)
- [x] No-double-dipping explicitness: in metric prereg/evidence, mark clearly what is tuning vs what is locked gates. (Done 2026-02-22; same sections above. Also formalized in `core-v1-fixed-free-contract.md`.)
