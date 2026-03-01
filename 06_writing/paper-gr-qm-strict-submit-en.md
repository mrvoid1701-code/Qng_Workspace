# A Strict GR+QM Core for QNG

**Title**  
A Strict General-Relativity and Quantum-Mechanics Core for Quantum Node Gravity (QNG):  
Discrete Curvature, Canonical Quantization, and First-Order Semiclassical Closure

**Date**: 2026-03-01  
**Version**: submit-style working draft (English)  
**Scope**: strictly GR + QM core only (no dark-sector expansion)

## Abstract

This paper presents a strict General Relativity (GR) and Quantum Mechanics (QM) core for Quantum Node Gravity (QNG) on a discrete graph substrate. The objective is narrow: test whether a single graph-native construction can support (i) GR-like curvature and conservation diagnostics, (ii) canonical quantization and vacuum observables, and (iii) first-order semiclassical back-reaction closure, under fixed pre-registered gates. The current rerun snapshot (2026-03-01) reports full pass across GR gates G5-G16, QM gates G17-G20, and bridge gates B1-B5. Quantitatively, key checks include: Hamiltonian-fit closure in the Einstein block (R2=0.056991), PPN consistency diagnostics (gamma deviation 0.028426), canonical Heisenberg saturation (deviation 0.000000), thermal quantum suppression (E_MB/E_BE=778.373368), and bounded semiclassical self-consistency residual (max=0.026486). These results support internal coherence and numerical stability of the GR<->QM chain in the declared QNG pipeline. They do not establish physical uniqueness.

## 1. Introduction

The main challenge for any unified framework is not only producing separate classical and quantum limits, but connecting them with explicit consistency checks. This draft isolates that question for QNG in the strictest way possible:

1. Build the GR side directly on the graph and test geometric, dynamic, and covariant constraints.
2. Quantize the same graph field degrees of freedom and test standard quantum diagnostics.
3. Feed vacuum structure back into the metric and test perturbative closure.

The paper excludes non-essential narrative layers and keeps only the GR+QM backbone with gate-based evidence.

## 2. Minimal QNG Setup

Let the substrate be a graph \(G=(N,E)\), with vertices \(i\in N\), neighborhood \(N(i)\), degree \(k_i\), and mean degree \(\bar{k}\). The scalar stability field is \(\Sigma(i)\in[0,1]\).

The random-walk Laplacian is

\[
L_{rw}[f](i)=\frac{1}{k_i}\sum_{j\in N(i)}\left(f(j)-f(i)\right).
\]

All GR and QM objects are built on this shared discrete structure.

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
| G17a | spectral gap | 0.010782 | >0.01 | pass |
| G17b | propagator slope | -0.013552 | <-0.01 | pass |
| G17c | E0 per mode | 0.176394 | (0.05, 5.0) | pass |
| G17d | Heisenberg deviation | 0.000000 | <0.01 | pass |
| G18a | binary entropy SA | 13.130097 | >6.584898 | pass |
| G18b | n*mean(IPR) | 3.962257 | <5.0 | pass |
| G18c | cv(Gii) | 0.258589 | <0.5 | pass |
| G18d | spectral dimension ds | 1.283920 | (1.2, 3.5) | pass |
| G19a | cv(T_Unruh) | 0.438404 | >0.05 | pass |
| G19b | E_MB / E_BE | 778.373368 | >2.0 | pass |
| G19c | E_BE(2T)/E_BE(T) | 39.474272 | >3.0 | pass |
| G19d | dG thermal slope | -3.849481e-05 | <-1e-05 | pass |
| G20a | semiclassical energy error | 1.325053e-16 | <0.01 | pass |
| G20b | cv(eps_vac) | 0.413501 | >0.05 | pass |
| G20c | abs(dE0)/E0 | 0.004259 | (1e-05, 0.3) | pass |
| G20d | max residual | 0.026486 | <0.2 | pass |

### 7.4 Additional quantitative notes

- QM bridge run reports \(K_{eff}=19\), \(\omega\in[0.157422,0.532398]\), \(E_0=3.351481\), and exact Heisenberg saturation to reporting precision.
- Unruh block shows strong quantum suppression versus Maxwell-Boltzmann equipartition (ratio 778.373368), with preserved spatial decay in thermal increment.
- Semiclassical block yields perturbative correction scale: abs(dE0)/E0=0.004259 and max residual 0.026486, consistent with first-order closure.

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

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/run_qng_dynamics_wave_v1.py
python scripts/run_qng_einstein_v1.py
python scripts/run_qng_conservation_v1.py
python scripts/run_qng_covariant_metric_v1.py
python scripts/run_qng_einstein_eq_v1.py
python scripts/run_qng_gr_solutions_v1.py
python scripts/run_qng_covariant_wave_v1.py
python scripts/run_qng_covariant_cons_v1.py
python scripts/run_qng_ppn_v1.py
python scripts/run_qng_action_v1.py
python scripts/run_qng_metric_gr_bridge_v2.py
python scripts/run_qng_qm_bridge_v1.py
python scripts/run_qng_qm_info_v1.py
python scripts/run_qng_unruh_thermal_v1.py
python scripts/run_qng_semiclassical_v1.py
```

Primary evidence paths:

- `05_validation/evidence/artifacts/*/metric_checks_*.csv`
- `05_validation/evidence/artifacts/qng-metric-gr-bridge-v2/bridge_checks.csv`
- `05_validation/evidence/artifacts/*/run-log-*.txt`

## 11. Conclusion

Under the strict scope of this paper, QNG currently exhibits a coherent GR->QM->semiclassical chain with full pass status on the declared checks (G5-G20, B1-B5). The result is best interpreted as a robust internal milestone: discrete geometry, canonical quantization, and first-order back-reaction are mutually compatible in one fixed pipeline. The next step is not to broaden claims, but to keep this core frozen and evaluate harder out-of-sample stress tests against the same thresholds.

## References (Repository-local)

1. `scripts/run_qng_einstein_v1.py`
2. `scripts/run_qng_einstein_eq_v1.py`
3. `scripts/run_qng_ppn_v1.py`
4. `scripts/run_qng_action_v1.py`
5. `scripts/run_qng_qm_bridge_v1.py`
6. `scripts/run_qng_qm_info_v1.py`
7. `scripts/run_qng_unruh_thermal_v1.py`
8. `scripts/run_qng_semiclassical_v1.py`
9. `scripts/run_qng_metric_gr_bridge_v2.py`
10. `05_validation/evidence/artifacts/qng-*/metric_checks_*.csv`
11. `05_validation/evidence/artifacts/qng-metric-gr-bridge-v2/bridge_checks.csv`
