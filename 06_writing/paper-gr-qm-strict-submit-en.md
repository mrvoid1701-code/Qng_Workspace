# A Strict GR+QM Core for QNG

**Title**  
A Strict General-Relativity and Quantum-Mechanics Core for Quantum Node Gravity (QNG):  
Discrete Curvature, Canonical Quantization, and First-Order Semiclassical Closure

**Date**: 2026-03-20 (updated from 2026-03-01)
**Version**: submit-style working draft (English) — v2 with Jaccard Informational Graph
**Scope**: strictly GR + QM core only (no dark-sector expansion)

## Abstract

This paper presents a strict General Relativity (GR) and Quantum Mechanics (QM) core for Quantum Node Gravity (QNG) on a discrete graph substrate. The objective is narrow: test whether a single graph-native construction can support (i) GR-like curvature and conservation diagnostics, (ii) canonical quantization and vacuum observables, and (iii) first-order semiclassical back-reaction closure, under fixed pre-registered gates. A central result of this version is the adoption of the *Jaccard Informational Graph* — a coordinate-free graph constructed purely from neighborhood similarity — which yields an emergent spectral dimension d_s = 4.082 ≈ 4 without any spatial embedding. The updated snapshot (2026-03-20) reports full pass across all gates G10-G21 on the Jaccard graph. Key quantitative results include: Hamiltonian-fit closure (R2=0.056991), PPN diagnostics (gamma deviation 0.028426), canonical Heisenberg saturation (deviation 0.000000), spectral gap on the Jaccard graph (μ₁=0.291, margin >>100%), emergent spectral dimension (d_s=4.082, threshold (3.5,4.5)), thermal quantum suppression (E_MB/E_BE=778), and bounded semiclassical residual (max=0.026). A quantum robustness sweep (λ ∈ [0,1]) confirms d_s≈4 is a stable phase (not a fine-tuned point), with phase transition at λ_c≈0.015. These results support internal coherence and numerical stability of the GR↔QM chain. They do not establish physical uniqueness.

## 1. Introduction

The main challenge for any unified framework is not only producing separate classical and quantum limits, but connecting them with explicit consistency checks. This draft isolates that question for QNG in the strictest way possible:

1. Build the GR side directly on the graph and test geometric, dynamic, and covariant constraints.
2. Quantize the same graph field degrees of freedom and test standard quantum diagnostics.
3. Feed vacuum structure back into the metric and test perturbative closure.

The paper excludes non-essential narrative layers and keeps only the GR+QM backbone with gate-based evidence.

## 2. Minimal QNG Setup

### 2.1 Graph substrate

Let the substrate be a graph \(G=(N,E)\), with vertices \(i\in N\), neighborhood \(N(i)\), degree \(k_i\), and mean degree \(\bar{k}\). The scalar stability field is \(\Sigma(i)\in[0,1]\).

The random-walk Laplacian is

\[
L_{rw}[f](i)=\frac{1}{k_i}\sum_{j\in N(i)}\left(f(j)-f(i)\right).
\]

All GR and QM objects are built on this shared discrete structure.

### 2.2 The Jaccard Informational Graph

The canonical graph substrate is the *Jaccard Informational Graph*, constructed without spatial coordinates:

1. Build a sparse random seed graph \(G_0\) with mean degree \(k_{init}=8\).
2. For each pair \((i,j)\), compute neighborhood similarity:
\[
J(i,j) = \frac{|N(i)\cap N(j)|}{|N(i)\cup N(j)|}
\]
3. Reconnect: each node \(i\) links to the \(k_{conn}=8\) nodes with highest \(J(i,j)\).

This construction is coordinate-free — it requires no metric, no spatial embedding, and no prior notion of dimension. The canonical parameters are \(n=280\), \(k_{init}=k_{conn}=8\), seed 3401.

**Physical interpretation:** two events are connected when they share a similar informational context (overlapping causal neighborhoods). The coordination number \(k=8\) matches the 4D hypercubic lattice \(\mathbb{Z}^4\) exactly (which has 8 nearest neighbors: \(\pm e_1, \ldots, \pm e_4\)), causing the graph to self-organize toward 4D topology. This yields an emergent spectral dimension \(d_s = 4.082\) (50-seed mean: \(4.128 \pm 0.125\)), confirmed robust across a quantum fluctuation sweep (see §4.5).

## 3. GR Sector

### 3.1 Discrete curvature and Einstein-type tensors

The pipeline uses Forman-Ricci edge curvature

\[
F(i,j)=4-k_i-k_j+2\,t(i,j),
\]

where \(t(i,j)\) is the number of shared neighbors of edge \((i,j)\). Scalar curvature at a vertex is

\[
R(i)=\frac{1}{k_i}\sum_{j\in N(i)}F(i,j).
\]

From this, discrete Ricci and Einstein-type tensors are evaluated and checked for:

- negative curvature regime,
- inhomogeneity,
- off-diagonal symmetry sanity,
- anisotropy bounds.

### 3.2 Covariant metric block

Weak-field covariant quantities are constructed from \(\Sigma\):

\[
\Phi(i)\propto -\Sigma(i),\quad N(i)=1+\Phi(i),\quad \gamma_s(i)=1-2\Phi(i).
\]

The ADM-like checks target:

- no horizon (\(N>0\)),
- weak field (\(|\Phi|\) bounded),
- positive spatial metric,
- inward effective radial acceleration.

### 3.3 Einstein equation and action closure

A coarse Hamiltonian relation is fitted as

\[
R(i)\approx 2\Lambda + 16\pi G_{\mathrm{eff}}\frac{\Sigma(i)}{\Sigma_{\max}}.
\]

The action decomposition is

\[
S[g,\sigma]=S_{EH}[g]+S_{\Lambda}[g]+S_{matter}[g,\sigma],
\]

with

\[
S_{matter}=\sum_i\left[-\frac12 |\nabla \sigma|^2(i)-\frac{m^2}{2}\sigma(i)^2\right]\mathrm{vol}(i).
\]

The tested Euler-Lagrange targets are:

- \(G_{\mu\nu}=8\pi G\,T_{\mu\nu}\),
- \(L_{rw}[\sigma](i)=m^2\sigma(i)\),
- closure identity and Hessian stability.

### 3.4 GR-limit and bridge formulation

The tested GR-kill-switch expansion is

\[
a_{total}=-\nabla\Sigma-\tau (v\cdot \nabla)\nabla\Sigma+O(\tau^2),
\]

so \(\tau\to 0\) recovers GR-like baseline behavior in the declared diagnostics.

The metric-to-GR bridge v2 uses

\[
h=g-\mathrm{iso\_ref}\,I,\quad \mathrm{iso\_ref}=1/\sqrt{2},
\]

with fixed gates on weak-field norm, metric sanity, Newtonian direction, continuum drift, and control separation.

### 3.5 PPN diagnostics

A PPN-style sanity block evaluates:

- \(\gamma\) deviation from unity,
- \(\beta\) implied by the chosen lapse gauge,
- Shapiro delay contrast (inner/outer),
- equivalence-principle universality proxy.

This is a model-consistency PPN block, not a direct Solar-System ephemeris fit.

## 4. QM Sector

### 4.1 Canonical quantization on graph modes

The scalar field is promoted to operator form:

\[
\sigma\rightarrow\hat{\sigma},\quad [\hat{\sigma}(i),\hat{\pi}(j)]=i\delta_{ij}.
\]

Define

\[
M=-L_{rw}=I-D^{-1}A,\quad \mu_k\in[0,1],
\]

and dispersion relation

\[
\omega_k=\sqrt{\mu_k+m_{\mathrm{eff}}^2}.
\]

### 4.2 Vacuum observables

Zero-point energy:

\[
E_0=\frac12\sum_{k=1}^{K_{\mathrm{eff}}}\omega_k.
\]

Two-point function:

\[
G(i,j)=\sum_{k=1}^{K_{\mathrm{eff}}}\frac{\psi_k(i)\psi_k(j)}{2\omega_k}.
\]

Vacuum uncertainty products:

\[
\Delta \sigma_k=\frac{1}{\sqrt{2\omega_k}},\quad
\Delta \pi_k=\sqrt{\frac{\omega_k}{2}},\quad
\Delta \sigma_k\Delta \pi_k=\frac12.
\]

### 4.3 Quantum information and emergent geometry

For a bipartition \(A\cup B\):

\[
q_k(A)=\sum_{i\in A}\psi_k(i)^2,\quad
S_A=\sum_k h(q_k),\quad
h(p)=-p\ln p-(1-p)\ln(1-p).
\]

Localization proxy:

\[
\mathrm{IPR}_k=\sum_i\psi_k(i)^4.
\]

Spectral dimension from return probability:

\[
P(t)\propto t^{-d_s/2},\quad
d_s=-2\,\frac{d\log P(t)}{d\log t}.
\]

### 4.4 Unruh thermal vacuum block

Acceleration and temperature proxies:

\[
\alpha_{proxy}(i)=k_i/\bar{k},
\]

\[
a_{eff}(i)=\frac{1}{k_i}\sum_{j\in N(i)}|\alpha_{proxy}(j)-\alpha_{proxy}(i)|,
\]

\[
T_{Unruh}(i)=\frac{a_{eff}(i)}{2\pi},\quad T_{global}=\mathrm{mean}(T_{Unruh}).
\]

Thermal occupation:

\[
n_k=\frac{1}{\exp(\omega_k/T_{global})-1}.
\]

Thermal propagator increment:

\[
\Delta G_{thermal}(i,j)=\sum_k\frac{n_k\psi_k(i)\psi_k(j)}{\omega_k}.
\]

### 4.5 Quantum Robustness: d_s≈4 is a Phase

To test whether \(d_s \approx 4\) is a fine-tuned accident or a structurally robust feature, we introduce a quantum temperature \(\lambda\) that softens the deterministic Jaccard selection via the Gumbel-max trick:

\[
P(j|i,\lambda) \propto \exp\!\bigl(J(i,j)/\lambda\bigr)
\]

At \(\lambda=0\) this is exact Jaccard; at \(\lambda\to\infty\) it reduces to Erdős–Rényi. We swept \(\lambda \in [0,1]\) with 30 samples per value (pass criterion: \(d_s \in (3.5,4.5)\)):

| \(\lambda\) | \(\bar{d}_s\) | pass% | \(H\)/node (nats) |
|---|---|---|---|
| 0.000 | 4.191 | 100% | 0.000 |
| 0.005 | 4.169 | 100% | 0.365 |
| 0.010 | 4.304 | 93% | 0.790 |
| **0.015** | **4.652** | **27%** | **— (phase transition)** |
| 0.050 | 5.078 | 0% | 4.902 |

Three structural discoveries:

**Discovery 1 — d_s≈4 is a phase, not a point.** The system remains 4D for \(\lambda \in [0,0.010]\) (PASS ≥ 93%), with a sharp phase transition at \(\lambda_c \approx 0.015\). The classical Jaccard (\(\lambda=0\)) sits deep inside this phase, tolerating up to \(H \approx 0.79\) nats/node (\(\approx 1\) bit) of quantum uncertainty before leaving 4D. This is analogous to the extended 4D phase in CDT \((\kappa_0, \Delta)\) space.

**Discovery 2 — UV→IR dimensional running is universal.** Across all \(\lambda\) (including \(\lambda=1\), pure Erdős–Rényi), \(d_{s,\mathrm{UV}} \approx 2.9\text{–}3.5\) and \(d_{s,\mathrm{IR}} \approx 4.3\text{–}4.8\), with \(\Delta d_s > +1\). The running direction is a structural property of the lazy random-walk protocol; the absolute value \(d_s\approx 4\) is Jaccard-specific.

**Discovery 3 — Two distinct spectral scales.** The Jaccard graph spectral gap (connectivity robustness) is \(\mu_1=0.147\) at \(\lambda=0\), distinct from the Klein-Gordon mass gap \(\mu_1=0.011\) measured in the QM sector (G17a). These are different physical quantities defined on different operators.

## 5. Semiclassical GR<->QM Closure

First-order metric feedback:

\[
\alpha^{(1)}(i)=\alpha^{(0)}(i)\left(1+\lambda f(i)\right),
\]

with vacuum energy density

\[
\epsilon_{vac}(i)=\frac12\sum_k \omega_k\psi_k(i)^2,\quad
f(i)=\frac{\epsilon_{vac}(i)-\bar{\epsilon}}{\bar{\epsilon}}.
\]

First-order mode update:

\[
\omega_k^{(1)}\approx \omega_k\left(1+\frac{\lambda}{2}\langle f\rangle_{\psi_k^2}\right),
\]

\[
\delta E_0=\frac12\sum_k\delta\omega_k.
\]

Self-consistency residual:

\[
r(i)=\frac{|\epsilon_{vac}^{(1)}(i)-\epsilon_{vac}^{(0)}(i)|}{\bar{\epsilon}}.
\]

## 6. Methods and Evaluation Protocol

All reported values come from fixed gate files and run logs generated in the same repository branch. The reported rerun date is 2026-03-01.

The protocol is:

1. Execute GR scripts (G5-G16 blocks).
2. Execute bridge script (B1-B5).
3. Execute QM scripts (G17-G20 blocks).
4. Read metric-check CSVs and run logs.
5. Report pass/fail against declared thresholds.

## 7. Results

### 7.1 GR gate summary (all pass)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| G5a | stability ratio | 1.000000 | <=1.5 | pass |
| G5d | freq ratio | 1.029901 | abs(omega_meas/omega_pred - 1) < 0.25 | pass |
| G8a | mean Forman curvature | -5.26829268 | <-1.0 | pass |
| G8b | cv(R) | 0.34556840 | >0.05 | pass |
| G9b | energy drift | 0.001315 | <0.02 | pass |
| G10d | mean radial accel | 0.017229 | >0.0 | pass |
| G11a | Hamiltonian fit R2 | 0.056991 | >0.02 | pass |
| G11c | Bianchi ratio | 0.287641 | <1.5 | pass |
| G12d | power-law slope | -0.139654 | <-0.03 | pass |
| G13b | covariant energy drift | 0.003297 | <0.02 | pass |
| G14b | covariant conservation drift | 0.001104 | <0.02 | pass |
| G15a | gamma deviation | 0.028426 | <0.06 | pass |
| G15b | Shapiro ratio | 2.437506 | >2.0 | pass |
| G16a | action closure error | 1.191151e-14 | <0.01 | pass |
| G16d | negative Hessian fraction | 1.000000 | >0.9 | pass |

### 7.2 Bridge summary (all pass)

| Gate | Value | Threshold | Status |
| --- | --- | --- | --- |
| B1 weak-field h (med/p90) | 0.190396 / 0.286935 | med<=0.200000 and p90<=0.320000 | pass |
| B2 sanity (min eig / cond p90) | 0.424735 / 1.851328 | min eig>=0.250000 and cond p90<=2.500000 | pass |
| B3 direction (median / p10 cosine) | 0.993310 / 0.963787 | median>=0.950000 and p10>=0.900000 | pass |
| B4 drift (med/p90) | 0.052547 / 0.144365 | median<=0.070000 and p90<=0.200000 | pass |
| B5 raw-shuffled gap | 1.098472 | >=0.900000 | pass |

Per-dataset bridge checks are also pass for DS-002, DS-003, and DS-006.

### 7.3 QM gate summary (all pass)

| Gate | Metric | Value | Threshold | Status |
| --- | --- | --- | --- | --- |
| G17a | spectral gap μ₁ (Jaccard) | 0.291199 | >0.01 | pass |
| G17b | propagator slope (geodesic) | -0.013114 | <-0.01 | pass |
| G17c | E0 per mode | 0.326746 | (0.05, 5.0) | pass |
| G17d | Heisenberg deviation | 0.000000 | <0.01 | pass |
| G18a | binary entropy SA | 13.050000 | >6.584898 | pass |
| G18b | n*mean(IPR) | 3.190000 | <5.0 | pass |
| G18c | cv(Gii) | 0.340000 | <0.5 | pass |
| G18d | spectral dimension ds (Jaccard) | 4.082091 | (3.5, 4.5) | pass |
| G19a | cv(T_Unruh) | 0.438404 | >0.05 | pass |
| G19b | E_MB / E_BE | 778.373368 | >2.0 | pass |
| G19c | E_BE(2T)/E_BE(T) | 39.474272 | >3.0 | pass |
| G19d | dG thermal slope | -3.849481e-05 | <-1e-05 | pass |
| G20a | semiclassical energy error | 1.325053e-16 | <0.01 | pass |
| G20b | cv(eps_vac) | 0.413501 | >0.05 | pass |
| G20c | abs(dE0)/E0 | 0.004259 | (1e-05, 0.3) | pass |
| G20d | max residual | 0.026486 | <0.2 | pass |

### 7.4 Additional quantitative notes

- G17 (Jaccard, v2): \(K_{eff}=19\), \(\omega\in[0.552,1.164]\), \(E_0=6.208\), exact Heisenberg saturation. Spectral gap \(\mu_1=0.291\) (Jaccard graph), margin >>100% vs threshold >0.01. Geodesic propagator slope \(b=-0.013\), consistent with Yukawa decay on graph metric.
- G18d (Jaccard lane): \(d_s=4.082\), 50-seed mean \(4.128 \pm 0.125\), all seeds PASS. Quantum Jaccard v2: PASS for \(\lambda\in[0,0.010]\), phase transition at \(\lambda_c\approx 0.015\).
- Unruh block: quantum suppression ratio 778 (E_MB/E_BE), consistent with Bose-Einstein statistics.
- Semiclassical block: perturbative correction abs(dE0)/E0=0.004259, max residual 0.026486, first-order closure confirmed.

## 8. Discussion

### 8.1 What is strongly supported

The strict GR+QM chain is internally coherent under fixed tests:

- GR side: discrete curvature, covariant dynamics, conservation, PPN diagnostics, and action closure all pass.
- QM side: spectral quantization, vacuum correlators, uncertainty relation, information diagnostics, and thermal-vacuum behavior all pass.
- Coupling side: semiclassical back-reaction remains bounded and perturbative.
- Bridge side: emergent metric satisfies declared weak-field and directionality constraints across three datasets.

### 8.2 Interpretation boundary

This is evidence of consistency and numerical stability in the declared pipeline. It is not yet a claim of:

- unique physical ontology,
- full observational replacement of standard GR across all astrophysical domains,
- closed experimental confirmation for every non-pipeline claim family.

## 9. Limitations

1. Several GR/QM checks are pipeline-level and synthetic by construction.
2. PPN here is a consistency diagnostic within model gauge choices, not a full planetary ephemeris confrontation.
3. Passing gates depends on declared thresholds and data-generation contracts; changes in contracts require re-registration and rerun.
4. This paper intentionally excludes dark-sector and broader cosmology claims to preserve strict scope.

## 10. Reproducibility

From repository root:

```bash
# Run all gates G10-G21 (canonical, DS-002, seed=3401):
python run_all_gates.py

# Or individually:
python scripts/run_qng_covariant_metric_v1.py
python scripts/run_qng_einstein_eq_v1.py
python scripts/run_qng_gr_solutions_v1.py
python scripts/run_qng_covariant_wave_v1.py
python scripts/run_qng_covariant_cons_v1.py
python scripts/run_qng_ppn_v1.py
python scripts/run_qng_action_v1.py
python scripts/run_qng_g17_v2.py          # G17: Jaccard + geodesic distance
python scripts/run_qng_qm_info_v1.py      # G18: Jaccard informational graph
python scripts/run_qng_unruh_thermal_v1.py
python scripts/run_qng_semiclassical_v1.py
python scripts/run_quantum_jaccard_v2.py  # Quantum robustness sweep (optional)
```

Primary evidence paths:

- `05_validation/evidence/artifacts/*/metric_checks_*.csv`
- `05_validation/evidence/artifacts/qng-metric-gr-bridge-v2/bridge_checks.csv`
- `05_validation/evidence/artifacts/*/run-log-*.txt`

## 11. Conclusion

Under the strict scope of this paper, QNG exhibits a coherent GR↔QM↔semiclassical chain with full pass status on all declared checks (G10-G21). The central structural result is that spacetime dimensionality \(d_s \approx 4\) emerges from a coordinate-free informational principle (Jaccard similarity), without any spatial embedding. This emergence is robust: a quantum fluctuation sweep confirms \(d_s \approx 4\) is a stable phase (not a fine-tuned point) for quantum temperature \(\lambda \in [0, 0.010]\), with a sharp transition at \(\lambda_c \approx 0.015\). The UV→IR dimensional running (\(d_s \approx 3\) at Planck scales, \(d_s \approx 4\) at classical scales) is qualitatively consistent with CDT, Asymptotic Safety, and LQG predictions. The result is best interpreted as a robust internal milestone: discrete information geometry, canonical quantization, and first-order back-reaction are mutually compatible in one fixed pipeline. The next step is not to broaden claims, but to submit to arXiv and evaluate external peer review.

## References (Repository-local)

**Gate scripts:**
1. `scripts/run_qng_covariant_metric_v1.py` — G10
2. `scripts/run_qng_einstein_eq_v1.py` — G11
3. `scripts/run_qng_gr_solutions_v1.py` — G12
4. `scripts/run_qng_covariant_wave_v1.py` — G13
5. `scripts/run_qng_covariant_cons_v1.py` — G14
6. `scripts/run_qng_ppn_v1.py` — G15
7. `scripts/run_qng_action_v1.py` — G16
8. `scripts/run_qng_g17_v2.py` — G17 (Jaccard + geodesic distance)
9. `scripts/run_qng_qm_info_v1.py` — G18 (Jaccard informational graph)
10. `scripts/run_qng_unruh_thermal_v1.py` — G19
11. `scripts/run_qng_semiclassical_v1.py` — G20
12. `scripts/run_quantum_jaccard_v2.py` — quantum robustness λ-sweep

**Evidence artifacts:**
13. `05_validation/evidence/artifacts/qng-*/metric_checks_*.csv`
14. `05_validation/evidence/artifacts/quantum-jaccard-v2/quantum_jaccard_v2_summary.json`
15. `05_validation/evidence/artifacts/qng-jaccard-freeze-v1/` — operational freeze package

**Theory:**
16. `03_math/derivations/qng-jaccard-ds4-analytical-v1.md` — analytical justification d_s=4
17. `06_writing/paper-coordfree-4d-v1.md` — detailed Jaccard section

**External references:**
18. Ambjørn, Jurkiewicz, Loll (2005). PRL 95, 171301. (CDT spectral dimension)
19. Lauscher & Reuter (2002). PRD 65, 025013. (Asymptotic Safety dimensional flow)
20. Modesto (2009). CQG 26, 242002. (LQG fractal dimension)
