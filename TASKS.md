# Current Tasks

## Priority P0 (Do First) - Freeze and Reproducibility

- [ ] Freeze + tag `Gold Pack v1` with fixed scripts, seeds, configs, manifests, and artifact hashes. (Freeze completed; git tag blocked because workspace is not a git repo.)
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
- [ ] Run `QNG-T-STRATON-002`: classic subset only (GALILEO_1/2, NEAR_1, CASSINI_1, ROSETTA_1/2/3, MESSENGER_1, EPOXI_1..5).
  - prereg: `05_validation/pre-registrations/qng-t-straton-002.md`
  - command: `.\.venv\Scripts\python.exe scripts\run_qng_t_straton_002.py`
  - gates: delta_bic <= -10, alpha CV < 0.30, shuffle collapse, exact LOO fraction >= 0.90
  - diagnostics: LOO influence per-row + per-mission, Model C power law (beta grid + 95% CI)

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
- [ ] Write explicit `fixed vs free` parameter contract for Core v1 (`gates/thresholds/rule fixed`, scan parameters free in declared ranges).
- [ ] Create `Core Snapshot v1` manifest (inputs, commands, seeds, artifact hashes) dedicated to closure run.
- [ ] Run sensitivity scan (`P0`) on key parameters (`sigma_min`, `sigma_birth`, growth weights) with `+-20%` perturbations.
- [ ] Record sensitivity outcome class: `stable pass`, `expected degradation`, `unstable`.
- [ ] Run ablation test (`P0`) removing phase component and record impact on `T-V-03` and `T-V-02`.
- [ ] Run ablation test (`P0`) removing structure component and record impact on `T-V-01` and `T-V-04`.
- [ ] Build ablation fingerprint table showing which gate fails when each component is removed.
- [ ] Run cross-dataset sanity (`P1`) by applying unchanged closure gates on `DS-003`.
- [ ] Confirm no post-hoc gate edits between `DS-002` and `DS-003` closure comparisons.

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
- [ ] Keep `C-086b v1` permanently frozen as falsification history.
- [ ] Keep `C-086b2` labeled calibration-only (not confirmed prediction) until out-of-sample pass.
- [ ] Enforce append-only holdout registry updates for all new mission additions.
- [ ] Replace provisional holdout residual placeholders (`JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`) with published OD residual/sigma values and rerun locked `C-086b3`.

## Priority P8 - Fundamental Theory Closure (GR/QM)

- [ ] Derivari fundamentale GR/QM (discrete-to-continuum bridge, equations and assumptions locked).
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
- [ ] Remove duplicated claims.
- [ ] Identify weakest assumptions.
- [ ] Update test plan with at least one falsifier per core claim.

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

## Priority P10 - Trajectory & Lag Tests (Claims-Derived)

Teste derivate din claims `predicted`/`testable` care nu au inca un test formal.

- [ ] `QNG-T-C055` - Verifica ca magnitudinea anomaliei directionale depinde de orientarea vitezei relativ la gradientii campului Sigma (`C-055`). Dataset: DS-005. Gates: corelatie directionala semnificativa, collapse la shuffle control.
- [ ] `QNG-T-C067` - Verifica absenta anomaliei lag pe traiectorii simetrice/circulare — control negativ formal (`C-067`). Dataset: DS-005 (segmente circulare/simetrice). Gates: delta_v aproape de zero, fara semnal directional.
- [ ] `QNG-T-C068` - Testa deviatii GPS de la GR cand intarzierea tau devine relevanta (`C-068`). Dataset: date publice GPS residuals. Gates: abatere masurabile vs GR pur.
- [ ] `QNG-T-C070` - Testa ca probele cu chi ridicat in miscare directionata arata anomalii de acceleratie masurabile (`C-070`). Dataset: DS-005 (misiuni cu masa mare + viteza directionala). Gates: corelatie chi x v x grad_Sigma, collapse la control.
- [ ] `QNG-T-C026` - Test formal: anomaliile Pioneer si flyby sunt consecinte de ordinul intai ale dinamicii lag (`C-026`). Derivare: `03_math/derivations/qng-c-026.md`. Gates: reproductibilitate cantitativa a magnitudinii anomaliei cu un singur parametru tau.

## Priority P11 - Lensing & Dark Sector Tests (Claims-Derived)

- [ ] `QNG-T-C059` - Verifica ca clusterele post-merger pastreaza semnaturi de memorie in hartile de lensing (`C-059`). Dataset: DS-006 (clustere post-merger vs relaxate). Gates: offset baryon-lensing mai mare la clustere recent fuzionate, collapse la permutare.
- [ ] `QNG-T-C083` - Verifica ca profilurile halo difera pentru galaxii cu masa vizibila similara dar istorii diferite (`C-083`). Dataset: DS-006 (galaxii izolate vs cu interactiuni recente). Gates: diferenta semnificativa statistica a profilului Sigma, control negativ curat.
- [ ] `QNG-T-C087` - Verifica predictia de lensing: centre deplasate, arcuri asimetrice, pattern-uri temporale (`C-087`). Dataset: DS-006. Gates: offset sistematic centru lensing vs centru barionic, asimetrie arcuri masurabile.
- [ ] `QNG-T-C089` - Verifica ca structurile cu colaps intarziat arata offset-uri baryon-dark si mismatch-uri de viteza (`C-089`). Dataset: DS-006 + date velocitate clustere. Gates: corelatie offset cu varsta/historia clusterului.
- [ ] `QNG-T-C040` - Verifica ca halourile dark sunt dependente de timp si pot disipa prin relaxare pe termen lung (`C-040`). Derivare: `03_math/derivations/qng-c-040.md`. Dataset: DS-006 (clustere la redshift diferit). Gates: trend temporal al amplitudinii Sigma-lag.
- [ ] `QNG-T-C061` - Verifica ca halourile pot disparea in sisteme izolate vechi fara influx nou de materie (`C-061`). Dataset: DS-006 (galaxii izolate vechi). Gates: amplitudine Sigma-lag mai mica la sisteme izolate vechi vs tinere/active.
- [ ] `QNG-T-C088` - Verifica ca galaxiile mai vechi arata semne de decay al haloului dark pe masura ce relaxarea progreseaza (`C-088`). Dataset: DS-006 (sample pe redshift). Gates: corelatie negativa varsta galaxie vs amplitudine halo.
- [ ] `QNG-T-C075` - Verifica ca gradientii flux-straton pot mapa regiuni gravitationale ascunse fara particule noi (`C-075`). Dataset: DS-006. Gates: predictie Sigma-gradient reproduce pozitia massei dark observate mai bine decat modelul particule.

## Priority P12 - Precision Astrophysics Tests (Claims-Derived)

- [ ] `QNG-T-C090` - Testa ca timing pulsari include intarzieri TOA oscilatorii si ecouri de memorie (`C-090`). Derivare: `03_math/derivations/qng-c-090.md`. Dataset: date publice IPTA/PPTA pulsar timing. Gates: reziduu TOA corelat cu gradientul Sigma local, control negativ curat.
- [ ] `QNG-T-C091` - Testa ca propagarea undelor gravitationale depinde de tau(chi) si ringdown-ul arata distorsiuni care scala cu asimetria masei (`C-091`). Derivare: `03_math/derivations/qng-c-091.md`. Dataset: cataloage LIGO/VIRGO (GW events). Gates: reziduu ringdown corelat cu parametrul tau estimat.
- [ ] `QNG-T-C098` - Verifica ca in afara limitelor clasice apar efecte de memorie, lag si decoerenta de faza (`C-098`). Dataset: combinat DS-005 + DS-006 (regim extrem). Gates: abatere sistematica de la GR pur in regim de viteza mare / gradient mare.

## Priority P13 - Cosmological Tests (Claims-Derived)

- [ ] `QNG-T-C105` - Testa interpretarea CMB ca suprafata de relaxare a turbulentei nodale timpurii (`C-105`). Dataset: date CMB Planck (`data/cmb/`). Gates: corelatie pattern CMB cu model relaxare QNG, BIC vs LCDM.
- [ ] `QNG-T-C106` - Verifica ca anizotropiile CMB si deplasarile peak-urilor provin din domenii de fluctuatie timpurii (`C-106`). Dataset: date CMB Planck. Gates: reproductibilitate peak-uri CMB cu model QNG vs LCDM.
- [ ] `QNG-T-C107` - Verifica ca formarea structurilor urmeaza acretie coerenta de-a lungul gradientilor de stabilitate (`C-107`). Derivare: `03_math/derivations/qng-c-107.md`. Dataset: survey-uri de structura la scara mare. Gates: corelatie filament/void cu model Sigma-gradient.
- [ ] `QNG-T-C108` - Verifica ca filamentele cosmice sunt coridoare phase-stabile unde coerenta directionala supravietuieste (`C-108`). Derivare: `03_math/derivations/qng-c-108.md`. Dataset: date structura la scara mare. Gates: anizotropie tau mai mica in filamente vs void-uri.
- [ ] `QNG-T-C109` - Verifica ca acceleratia cosmica aparenta poate emerge din schimbarea ratei de update si desincronizare globala (`C-109`). Derivare: `03_math/derivations/qng-c-109.md`. Dataset: date supernova tip Ia / CMB. Gates: reproductibilitate expansiune accelerata fara Lambda, BIC vs LCDM.
- [ ] `QNG-T-C110` - Verifica predictia QNG de anomalii timpurii: non-Gaussianitate, cold spots, aliniere axe (`C-110`). Dataset: date CMB Planck. Gates: detectie non-Gaussianitate la nivel prevazut de model.
- [ ] `QNG-T-C112` - Testa ca inflatia poate fi inlocuita cu mecanism coherence-burst cu sincronizare globala rapida (`C-112`). Dataset: date CMB (spectru putere primordial). Gates: reproductibilitate spectru plat fara inflaton, BIC comparabil.
- [ ] `QNG-T-C102` - Verifica ca universul incepe ca retea nodala minima stabila deasupra Sigma_min, evitand singularitatea initiala (`C-102`). Dataset: simulare sintetica (bootstrap nodal). Gates: absenta singularitatii in model, consistenta cu observatii timpurii CMB.

## Priority P14 - Falsification Completeness (Claims-Derived)

- [ ] `QNG-T-C092` - Test formal de falsificare: absenta semnaturilor lag constrange tau si chi si poate falsifica variante QNG (`C-092`, `C-118`). Derivare: `03_math/derivations/qng-c-118.md`. Gates: limita superioara tau din non-detectie, eliminare variante cu tau prea mare.
- [ ] `QNG-T-C118` - Executa formal criteriile de falsificare: esec la fit tau-lag, absenta Sigma-lag lensing, GR recovery esuata in simulari nodale (`C-118`). Derivare: `03_math/derivations/qng-c-118.md`. Gates: toate cele 3 criterii testate si documentate cu rezultat explicit.
- [ ] Adauga cel putin un falsifier formal per claim de tip `predicted` cu confidence `medium` sau `high` care nu are inca un test in test-plan.

## Priority P15 - Simulation & Lab Analogues (Claims-Derived)

- [ ] `QNG-T-C062` - Ruleaza simulari N-body cu kernel-uri de memorie si verifica reproductibilitatea semnaturilor de structura QNG-consistente (`C-062`). Derivare: `03_math/derivations/qng-c-062.md`. Gates: BIC model-memorie vs model standard, control curat la kernel zero.
- [ ] `QNG-T-C063` - Construieste analoguri graf de laborator care reproduc stabilitate, lag si atractori emergenti (`C-063`). Dataset: simulare sintetica (graf discret). Gates: tranzitii de stabilitate reproductibile, lag masurabil, atractor persistent.

## Later / Not Now (Parking)

- [ ] Environment lock hardening: add explicit Python version + `requirements.txt` / `pip freeze` snapshot to repro pack.
- [ ] Environment lock hardening: add lockfile (`conda-lock` or `poetry.lock`) for deterministic dependency resolution.
- [ ] Environment lock hardening (bonus): add `Dockerfile` for portable reproducible runtime.
- [ ] Single-command CI: add GitHub workflow to run `07_exports/repro-pack-v1/reproduce_all.ps1` (or equivalent) on each commit.
- [ ] No-double-dipping explicitness: in metric prereg/evidence, mark clearly what is calibration set vs holdout set.
- [ ] No-double-dipping explicitness: in metric prereg/evidence, mark clearly what is tuning vs what is locked gates.
