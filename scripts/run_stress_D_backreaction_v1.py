#!/usr/bin/env python3
"""
QNG Stress Test — Categoria D: Atac pe back-reaction semiclasica

G20 e calibrat la λ=0.05 cu δE₀/E₀ = 0.00426 (marja 41500%).
Bomba: ce se intampla la λ → ∞?

Formula back-reaction (G20):
  α¹(i) = α⁰(i) · (1 + λ·f(i))
  f(i)   = (ε_vac(i) − ε̄) / ε̄
  δω_k   = (λ/2) · ω_k · <f>_k     [<f>_k = Σ_i f(i)·ψ_k(i)²]
  ω_k¹   = ω_k⁰ + δω_k

Punct critic: cand ω_k¹ < 0, teoria se rupe (frecvente imaginare = instabilitate).

Atacuri:
  D1  λ = 0         — trivial (fara back-reaction)
  D2  λ sweep       — cauta λ_crit unde ω_k¹ < 0 (instabilitate)
  D3  Iteratii       — back-reaction iterat pana la auto-consistenta sau divergenta
  D4  Conservare     — E_0 conservat sub iteratii multiple?
  D5  Sensibilitate f — ce se intampla daca f(i) e perturbat cu zgomot?

Dependinte: stdlib only.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-D-backreaction-v1"

N = 280; K = 8; SEED = 3401
N_MODES = 20; N_ITER_POW = 350; M_EFF_SQ = 0.014
LAMBDA_CANONICAL = 0.05


# ── Graf Jaccard ──────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Spectral ──────────────────────────────────────────────────────────────────

def _dot(u, v):    return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):
    n = math.sqrt(_dot(v, v))
    return [x/n for x in v] if n > 1e-14 else v[:]
def _defl(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i] - c*b[i] for i in range(len(w))]
    return w
def _rw(f, nb):
    return [(sum(f[j] for j in b) / len(b)) if b else 0. for b in nb]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs = []; mus = []
    for _ in range(n_modes):
        v = _norm(_defl([rng.gauss(0., 1.) for _ in range(n)], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


def compute_epsilon_vac(vecs_active, omegas, n):
    eps = [0.] * n
    for k, omega in enumerate(omegas):
        hw = 0.5 * omega
        for i in range(n):
            eps[i] += hw * vecs_active[k][i]**2
    return eps


def first_order_correction(vecs_active, omegas, f_field, lam):
    """
    δω_k = (λ/2) · ω_k · <f>_k
    ω_k¹ = ω_k + δω_k
    δE₀  = ½ Σ δω_k
    """
    K = len(omegas)
    d_omega = []
    omega1  = []
    for k in range(K):
        f_avg_k = sum(f_field[i] * vecs_active[k][i]**2 for i in range(len(f_field)))
        dw = (lam / 2.) * omegas[k] * f_avg_k
        d_omega.append(dw)
        omega1.append(omegas[k] + dw)
    delta_E0 = 0.5 * sum(d_omega)
    return d_omega, omega1, delta_E0


# ── D2: λ sweep → λ_crit ─────────────────────────────────────────────────────

def test_D2_lambda_sweep(vecs_a, omegas_0, n, rng):
    """
    Sweep λ de la 0 la 100+.
    La fiecare λ, calculam ω_k¹ si detectam:
      - Prima instabilitate: min(ω_k¹) < 0
      - Divergenta relativa: |δE₀/E₀| > threshold
    Cautam λ_crit.
    """
    print("\n── D2: λ sweep — cauta λ_crit (instabilitate ω_k < 0) ────────────")

    E0 = 0.5 * sum(omegas_0)
    eps_vac0 = compute_epsilon_vac(vecs_a, omegas_0, n)
    mean_eps = statistics.mean(eps_vac0)
    f_field  = [(eps_vac0[i] - mean_eps) / mean_eps for i in range(n)]

    # Precomputa <f>_k pentru fiecare mod (invariant la λ pentru ordini 1)
    f_avg_k = [sum(f_field[i] * vecs_a[k][i]**2 for i in range(n))
               for k in range(len(omegas_0))]

    # Range de λ: log-uniform de la 0.001 la 500
    lambdas = [10**(i*0.1) for i in range(-20, 30)]  # 0.01 .. 100
    lambdas = [0.0] + lambdas

    rows = []
    lambda_crit = None
    for lam in lambdas:
        omega1 = [omegas_0[k] + (lam/2.) * omegas_0[k] * f_avg_k[k]
                  for k in range(len(omegas_0))]
        E0_1   = 0.5 * sum(omega1)
        dE_rel = abs(E0_1 - E0) / E0
        min_omega1 = min(omega1)
        max_omega1 = max(omega1)
        has_negative = min_omega1 < 0.
        gate_g20c = 1e-5 < dE_rel < 0.30

        rows.append({"lambda": lam, "min_omega1": min_omega1,
                     "max_omega1": max_omega1, "dE_rel": dE_rel,
                     "has_negative": has_negative, "gate_g20c": gate_g20c})

        if lam in [0., 0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10., 20., 50., 100.]:
            print(f"  λ={lam:6.3f}  ω_min¹={min_omega1:.6f}  "
                  f"δE₀/E₀={dE_rel:.4e}  neg={has_negative}  G20c={'PASS' if gate_g20c else 'FAIL'}")

        if has_negative and lambda_crit is None:
            lambda_crit = lam

    if lambda_crit:
        print(f"\n  λ_crit = {lambda_crit:.4f}  (prima ω_k¹ < 0)")
        print(f"  λ_canonical/λ_crit = {LAMBDA_CANONICAL/lambda_crit:.4f}  "
              f"(marja de siguranta)")
    else:
        print(f"\n  λ_crit > {lambdas[-1]:.0f}  (nicio instabilitate pana la λ={lambdas[-1]:.0f}!)")

    return rows, lambda_crit


# ── D3 + D4: Iteratii auto-consistente ───────────────────────────────────────

def test_D34_iterations(vecs_a, omegas_0, neighbours, n, lam, max_iter=20):
    """
    Iteratii auto-consistente:
      i=0: ω_k⁰, f⁰(i) din ε_vac⁰
      i=1: ω_k¹ = ω_k⁰(1 + λ/2 <f⁰>_k), recalculeaza ε_vac¹, f¹
      i=2: ω_k² = ω_k¹(1 + λ/2 <f¹>_k), etc.

    Test: converge sau diverge?
    """
    print(f"\n── D3+D4: Iteratii back-reaction (λ={lam:.3f}, max_iter={max_iter}) ─")

    E0_0    = 0.5 * sum(omegas_0)
    omegas  = list(omegas_0)
    rows    = []

    for it in range(max_iter + 1):
        E0_it    = 0.5 * sum(omegas)
        eps_vac  = compute_epsilon_vac(vecs_a, omegas, n)
        mean_eps = statistics.mean(eps_vac)
        f_field  = [(eps_vac[i] - mean_eps) / mean_eps for i in range(n)]
        f_avg_k  = [sum(f_field[i] * vecs_a[k][i]**2 for i in range(n))
                    for k in range(len(omegas))]

        dE_rel   = abs(E0_it - E0_0) / E0_0
        max_f    = max(abs(f_field[i]) for i in range(n))
        min_omega = min(omegas)
        rows.append({"it": it, "E0": E0_it, "dE_rel": dE_rel,
                     "max_f": max_f, "min_omega": min_omega})

        print(f"  iter={it:2d}  E₀={E0_it:.8f}  δE₀/E₀={dE_rel:.4e}  "
              f"max|f|={max_f:.4f}  ω_min={min_omega:.6f}")

        if min_omega < 0:
            print(f"  INSTABILITATE la iter={it}: ω_k < 0!")
            break

        if it == max_iter: break

        # Aplica corectia
        d_omega, omegas, _ = first_order_correction(vecs_a, omegas, f_field, lam)

    # Analiza convergenta
    E0_final  = rows[-1]["E0"]
    dE_total  = abs(E0_final - E0_0) / E0_0
    converged = dE_total < 0.01 and rows[-1]["min_omega"] > 0
    diverged  = rows[-1]["min_omega"] < 0

    if converged:
        print(f"  CONVERGE: δE₀/E₀ total = {dE_total:.4e} < 1%")
    elif diverged:
        print(f"  DIVERGE: instabilitate la iter={rows[-1]['it']}")
    else:
        print(f"  OSCILEAZA: δE₀/E₀ = {dE_total:.4e} (>1%, dar stabil)")

    return rows, converged, diverged


# ── D5: Sensibilitate la zgomot pe f ─────────────────────────────────────────

def test_D5_noise_sensitivity(vecs_a, omegas_0, n, lam, noise_levels, seed):
    """
    Perturbam f(i) cu zgomot gaussian si masuram variatia lui δE₀.
    Test: back-reaction e sensibila la erori mici in ε_vac?
    """
    print(f"\n── D5: Sensibilitate f la zgomot (λ={lam}) ────────────────────────")

    eps_vac0 = compute_epsilon_vac(vecs_a, omegas_0, n)
    mean_eps = statistics.mean(eps_vac0)
    f_clean  = [(eps_vac0[i] - mean_eps) / mean_eps for i in range(n)]
    _, _, dE_clean = first_order_correction(vecs_a, omegas_0, f_clean, lam)
    E0 = 0.5 * sum(omegas_0)

    rows = []
    rng  = random.Random(seed + 500)

    print(f"  Baseline δE₀/E₀ = {abs(dE_clean)/E0:.6e}")
    for noise_level in noise_levels:
        # Medie pe 10 realizari de zgomot
        dE_samples = []
        for _ in range(10):
            f_noisy = [f_clean[i] + rng.gauss(0., noise_level) for i in range(n)]
            _, _, dE = first_order_correction(vecs_a, omegas_0, f_noisy, lam)
            dE_samples.append(abs(dE) / E0)
        mean_dE = statistics.mean(dE_samples)
        std_dE  = statistics.stdev(dE_samples)
        rows.append({"noise": noise_level, "mean_dE": mean_dE, "std_dE": std_dE})
        print(f"  noise={noise_level:.3f}  δE₀/E₀ = {mean_dE:.4e} ± {std_dE:.2e}")

    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("=" * 70)
    print("QNG STRESS TEST — Categoria D: Atac back-reaction semiclasica")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print(f"Canonical: N={N}, k={K}, λ={LAMBDA_CANONICAL}")
    print("=" * 70)
    print()
    print("Bomba: la ce λ se rupe teoria? Iteratiile converg sau explodeaza?")

    # ── Construieste graful si eigenmodes ──────────────────────────────────────
    print(f"\n[0] Graf Jaccard + eigenmodes...", end=" ", flush=True)
    nb = build_jaccard_graph(N, K, K, SEED)
    rng = random.Random(SEED + 1)
    mus, eigvecs = compute_eigenmodes(nb, N_MODES, N_ITER_POW, rng)
    active  = list(range(1, len(mus)))
    vecs_a  = [eigvecs[i] for i in active]
    omegas_0 = [math.sqrt(mus[i] + M_EFF_SQ) for i in active]
    K_eff   = len(omegas_0)
    E0      = 0.5 * sum(omegas_0)
    print(f"done  K_eff={K_eff}  E₀={E0:.6f}")
    n = N  # len(nb)

    # D2: λ sweep
    d2_rows, lambda_crit = test_D2_lambda_sweep(vecs_a, omegas_0, n, rng)

    # D3+D4: iteratii la λ canonical
    d34_rows_05, conv_05, div_05 = test_D34_iterations(
        vecs_a, omegas_0, nb, n, lam=0.05, max_iter=20)

    # D3+D4: iteratii la λ=1 (20x canonical)
    d34_rows_1, conv_1, div_1 = test_D34_iterations(
        vecs_a, omegas_0, nb, n, lam=1.0, max_iter=20)

    # D3+D4: iteratii la λ=5
    d34_rows_5, conv_5, div_5 = test_D34_iterations(
        vecs_a, omegas_0, nb, n, lam=5.0, max_iter=20)

    # D5: zgomot pe f
    d5_rows = test_D5_noise_sensitivity(
        vecs_a, omegas_0, n, lam=LAMBDA_CANONICAL,
        noise_levels=[0.001, 0.01, 0.1, 0.5, 1.0, 2.0],
        seed=SEED)

    # ── Verdict ───────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SUMAR FINAL — Robustete back-reaction")
    print("=" * 70)

    print(f"\nD2 λ_crit = {lambda_crit if lambda_crit else '>100'}")
    if lambda_crit:
        margin = lambda_crit / LAMBDA_CANONICAL
        print(f"  λ_canonical / λ_crit = {1/margin:.4f}  (marja: λ_crit e {margin:.0f}x mai mare)")
    else:
        print(f"  λ_canonical = {LAMBDA_CANONICAL}  <<  λ_crit  → teorie stabila departe de λ_crit")

    print(f"\nD3+D4 Iteratii:")
    print(f"  λ=0.05: converge={conv_05}  diverge={div_05}")
    print(f"  λ=1.00: converge={conv_1}   diverge={div_1}")
    print(f"  λ=5.00: converge={conv_5}   diverge={div_5}")

    print(f"\nD5 Zgomot pe f: back-reaction sensibila la zgomot micut pe f?")
    for r in d5_rows:
        print(f"  noise={r['noise']:.3f}  δE₀/E₀={r['mean_dE']:.4e}")

    # Verdict global
    stable = (lambda_crit is None or lambda_crit > 1.0) and conv_05
    verdict = "STABLE" if stable else "UNSTABLE"
    print(f"\nverdict={verdict}")
    print(f"Timp: {time.time()-t0:.1f}s")

    if stable:
        print()
        print("Back-reaction complet stabila.")
        print("λ_canonical e cu ordine de marime sub pragul de instabilitate.")
        print("Iteratiile converg la λ=0.05.")
    else:
        print()
        print("ATENTIE: instabilitate detectata!")

    # ── Salvare ───────────────────────────────────────────────────────────────
    csv_lambda = OUT_DIR / "stress_D2_lambda_sweep.csv"
    with csv_lambda.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["lambda", "min_omega1", "max_omega1",
                                           "dE_rel", "has_negative", "gate_g20c"])
        w.writeheader()
        for r in d2_rows:
            w.writerow({k: str(v) for k, v in r.items()})

    json_path = OUT_DIR / "stress_D_results.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "canonical_lambda": LAMBDA_CANONICAL,
        "verdict": verdict,
        "lambda_crit": lambda_crit,
        "D3_lambda_005": {"converged": conv_05, "diverged": div_05,
                           "n_iter": len(d34_rows_05)},
        "D3_lambda_100": {"converged": conv_1,  "diverged": div_1},
        "D3_lambda_500": {"converged": conv_5,  "diverged": div_5},
        "D5_noise": d5_rows,
        "D2_sweep": [{"lambda": r["lambda"], "min_omega": r["min_omega1"],
                       "dE_rel": r["dE_rel"]} for r in d2_rows],
    }, indent=2, default=str), encoding="utf-8")

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {csv_lambda.name}  {json_path.name}")
    print()
    print("=" * 70)
    print(f"STRESS TEST D COMPLET | verdict={verdict}")
    print("=" * 70)

    return 0 if stable else 1


if __name__ == "__main__":
    sys.exit(main())
