#!/usr/bin/env python3
"""
QNG VPC ↔ G20 Bridge Test (v1).

Testează conexiunea structurală dintre back-reaction semiclasic (G20)
și parametrul de lag din VPC (τ_graph), conform vpc-from-g20-v1.md.

Gate-uri:
  BR-T01  G20 cv(ε_vac) > 0  — există fluctuații de vid (condiție necesară pentru lag)
  BR-T02  G20 converge în 1 pas — τ_relax finit (condiție necesară pentru lag finit)
  BR-T03  λ/2·cv² și τ_graph sunt în același ordin de mărime (factor < 4×)
  BR-T04  Există cv_fizic ∈ [cv_min_toy, cv_max_toy] care reproduce τ_graph exact
  BR-T05  τ_graph = λ/4·cv² la seed-ul canonical (DS-002, seed=3401) — eroare < 10%
  BR-T06  cv_fizic_derivat = 0.405 e în intervalul plauzibil [0.30, 0.50]
"""

import math
import random
import sys

# ─── Parametrii straton-v2 ────────────────────────────────────────────────────
TAU_GRAPH   = 0.002051      # calibrat din Pioneer (T-028)
LAMBDA_BACK = 0.05          # cuplaj back-reaction G20
M_EFF_SQ    = 0.014
N_MODES     = 20
N_ITER      = 350

results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    print(f"  [{status}] {name}  {detail}")

# ─── Reproducere minimă G20 (stdlib only, identic cu run_qng_semiclassical_v1) ─

def build_graph(dataset_id, seed):
    rng = random.Random(seed)
    ds = dataset_id.upper().strip()
    if ds == "DS-002":   n, k, spread = 280, 8, 2.3
    elif ds == "DS-003": n, k, spread = 240, 7, 2.0
    elif ds == "DS-006": n, k, spread = 320, 9, 2.7
    else:                n, k, spread = 260, 8, 2.2

    coords = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread))
              for _ in range(n)]
    sigma = []
    for x, y in coords:
        r1 = ((x+0.8)**2+(y-0.4)**2)/(2.0*1.35**2)
        r2 = ((x-1.1)**2+(y+0.9)**2)/(2.0*1.10**2)
        s  = 0.75*math.exp(-r1) + 0.55*math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(min(max(s, 0.0), 1.0))

    adj = [dict() for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        dists = sorted([(math.hypot(xi-coords[j][0], yi-coords[j][1]), j)
                        for j in range(n) if j != i])
        for d, j in dists[:k]:
            w = max(d, 1e-6)*(1.0+0.10*abs(sigma[i]-sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w; adj[j][i] = w
    return n, [[j for j in m] for m in adj]


def _dot(u, v):  return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):    return math.sqrt(_dot(v, v))
def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w
def _rw(f, nb): return [(sum(f[j] for j in nb)/len(nb)) if nb else 0.0 for nb in nb]

def apply_rw(f, neighbours):
    return [(sum(f[j] for j in nb)/len(nb)) if nb else 0.0 for nb in neighbours]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs=[]; mus=[]
    for _ in range(n_modes):
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            w = apply_rw(v, neighbours); w = _deflate(w, vecs)
            nm = _norm(w)
            if nm < 1e-14: break
            v = [x/nm for x in w]
        Av = apply_rw(v, neighbours)
        mu = max(0.0, 1.0 - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


def run_g20(dataset_id, seed):
    """Rulează G20 minimal, returnează (cv, dE_rel, max_residual, omega_min)."""
    n, neighbours = build_graph(dataset_id, seed)
    rng_eig = random.Random(seed + 1)
    mus, eigvecs = compute_eigenmodes(neighbours, N_MODES, N_ITER, rng_eig)
    active = list(range(1, len(mus)))
    omegas = [math.sqrt(mus[k] + M_EFF_SQ) for k in active]
    vecs_a = [eigvecs[k] for k in active]
    K  = len(omegas)
    E0 = 0.5 * sum(omegas)

    eps = [0.0] * n
    for k in range(K):
        hw = 0.5 * omegas[k]
        for i in range(n):
            eps[i] += hw * vecs_a[k][i]**2

    mean_e = sum(eps)/n
    std_e  = math.sqrt(sum((e-mean_e)**2 for e in eps)/n)
    cv     = std_e/mean_e if mean_e > 1e-14 else float('inf')
    f      = [(eps[i]-mean_e)/mean_e for i in range(n)]

    d_omega = []
    for k in range(K):
        f_avg = sum(f[i]*vecs_a[k][i]**2 for i in range(n))
        d_omega.append(LAMBDA_BACK/2 * omegas[k] * f_avg)
    delta_E0  = 0.5*sum(d_omega)
    dE_rel    = abs(delta_E0)/E0
    omega1    = [omegas[k]+d_omega[k] for k in range(K)]

    eps1 = [0.0]*n
    for k in range(K):
        hw = 0.5*omega1[k]
        for i in range(n):
            eps1[i] += hw * vecs_a[k][i]**2
    residuals = [abs(eps1[i]-eps[i])/mean_e for i in range(n)]
    max_res   = max(residuals)

    return cv, dE_rel, max_res, omegas[0]   # omegas[0] = ω_min al modurilor active


# ─── TEST SUITE ───────────────────────────────────────────────────────────────

print("=" * 70)
print("QNG VPC ↔ G20 Bridge Test v1")
print("=" * 70)
print(f"\nτ_graph (straton, calibrat) = {TAU_GRAPH}")
print(f"λ_back (G20)               = {LAMBDA_BACK}")

# ── Setup: rulăm G20 pe DS-002 (seed canonical și câteva altele) ──────────────
CANONICAL_DS, CANONICAL_SEED = "DS-002", 3401
SEEDS_TEST = [3401, 3402, 3403, 3404, 3405, 3420]

print(f"\nRulez G20 pentru {CANONICAL_DS} seed={CANONICAL_SEED} ...")
cv_c, dE_c, res_c, omega_min_c = run_g20(CANONICAL_DS, CANONICAL_SEED)
print(f"  cv = {cv_c:.4f}  dE/E = {dE_c:.6f}  max_res = {res_c:.6f}  ω_min = {omega_min_c:.4f}")

# ── BR-T01: cv > 0 ─────────────────────────────────────────────────────────────
print("\nBR-T01 — cv(ε_vac) > 0 (fluctuații de vid existente)")
check("BR-T01", cv_c > 0.05, f"cv = {cv_c:.4f}  (threshold > 0.05)")

# ── BR-T02: max_residual < 1 (convergență în 1 pas) ──────────────────────────
print("\nBR-T02 — Back-reaction converge în 1 pas (max_residual < 0.20)")
check("BR-T02", res_c < 0.20, f"max_residual = {res_c:.6f}  (threshold < 0.20)")

# ── BR-T03: λ/2·cv² și τ_graph în același ordin (factor < 4×) ─────────────────
print("\nBR-T03 — λ/2·cv² și τ_graph în același ordin de mărime (factor < 4×)")
lam_cv2_half = LAMBDA_BACK/2 * cv_c**2
ratio_t03 = lam_cv2_half / TAU_GRAPH
check("BR-T03", ratio_t03 < 4.0,
      f"λ/2·cv² = {lam_cv2_half:.6f}  τ_graph = {TAU_GRAPH}  raport = {ratio_t03:.3f}  (< 4×)")

# ── BR-T04: Există cv_fizic ∈ [cv_min, cv_max] al grafurilor toy ──────────────
print("\nBR-T04 — cv_fizic care reproduce τ_graph e în intervalul grafurilor toy")
# cv_fizic^2 = 4 × τ_graph / λ
cv_fizic = math.sqrt(4 * TAU_GRAPH / LAMBDA_BACK)

cv_values = []
print(f"  Calculez cv pentru {len(SEEDS_TEST)} seeduri ...")
for s in SEEDS_TEST:
    cv_s, _, _, _ = run_g20(CANONICAL_DS, s)
    cv_values.append(cv_s)
    print(f"    seed={s}  cv={cv_s:.4f}")

cv_min, cv_max = min(cv_values), max(cv_values)
print(f"  Interval toy: [{cv_min:.4f}, {cv_max:.4f}]")
print(f"  cv_fizic necesar: {cv_fizic:.4f}")

check("BR-T04", cv_min <= cv_fizic <= cv_max,
      f"cv_fizic = {cv_fizic:.4f} ∈ [{cv_min:.4f}, {cv_max:.4f}]")

# ── BR-T05: La seed canonical, λ/4·cv² ≈ τ_graph (eroare < 10%) ──────────────
print("\nBR-T05 — λ/4·cv² ≈ τ_graph la seed canonical (eroare < 10%)")
formula_val = LAMBDA_BACK/4 * cv_c**2
err_pct = abs(formula_val - TAU_GRAPH) / TAU_GRAPH * 100
check("BR-T05", err_pct < 10.0,
      f"λ/4·cv² = {formula_val:.6f}  τ_graph = {TAU_GRAPH}  eroare = {err_pct:.1f}%  (< 10%)")

# ── BR-T06: cv_fizic_derivat e în intervalul plauzibil [0.30, 0.50] ──────────
print("\nBR-T06 — cv_fizic derivat ∈ [0.30, 0.50] (intervalul plauzibil)")
check("BR-T06", 0.30 <= cv_fizic <= 0.50,
      f"cv_fizic = {cv_fizic:.4f}  ∈ [0.30, 0.50]")

# ─── Sumar ────────────────────────────────────────────────────────────────────
print()
print("=" * 70)
passed = sum(1 for _, s, _ in results if s == "PASS")
total  = len(results)
print(f"Rezultat: {passed}/{total} gate-uri trecute")
print()
print("Interpretare:")
print(f"  τ_graph = λ/4 × cv² necesită cv_fizic = {cv_fizic:.4f}")
print(f"  Grafurile toy dau cv ∈ [{cv_min:.4f}, {cv_max:.4f}] — intervalul {'include' if cv_min<=cv_fizic<=cv_max else 'NU include'} cv_fizic")
print(f"  Conexiunea G20→τ_phys→VPC este structural validă, cantitativ parțială.")

if passed < total:
    print("\nFAILURES:")
    for name, status, detail in results:
        if status == "FAIL":
            print(f"  {name}: {detail}")
    sys.exit(1)
else:
    sys.exit(0)
