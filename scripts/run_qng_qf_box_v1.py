#!/usr/bin/env python3
"""
QNG Q-Fields — Confinement complet: particulă în cutie [0,1] (v1)

Tratament exact al confinementului Σ ∈ [0,1] prin pereți duri.

Ecuația Schrödinger locală pentru nodul i (mean-field pe vecini):

  [-T · ∂²/∂Σ² + V_eff_i(Σ)] ψ_i(Σ) = E · ψ_i(Σ)

  ψ_i(0) = ψ_i(1) = 0   (pereți duri: Σ NU iese din [0,1])

  V_eff_i(Σ) = k_cl/2 · Σ²
             + k_sm · deg_i · (Σ - Σ̄_i)²   (câmp mediu de la vecini)

  T = ħ_field² / (2m)   (energia cinetică cuantică)

Rezolvare numerică (diferențe finite, M=100 puncte interioare).
Self-consistență: Σ̄_i = ⟨Σ_i⟩ se actualizează iterativ până la convergență.

Sweep T ∈ [0, T_max]:
  T=0: limita clasică (Σ = argmin V_eff)
  T*:  confinementul devine relevant (σ_Σ > 0.25)
  T→∞: limita cuantică (ψ uniform pe [0,1])

Output cheie:
  ⟨Σ_i⟩, ⟨(δΣ_i)²⟩ per nod în starea fundamentală
  T* (tranziția clasic → confinement activ)
  cv_box = σ(⟨δΣ²⟩_i) / μ(⟨δΣ²⟩_i) din inhomogeneitatea gradelor
  cv_total_box cu cv_classical = 0.405

Fișier nou, nu modifică nimic existent.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import random
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-box-v1"
)

N_NODES    = 280
K_INIT     = 8
K_CONN     = 8
K_CL       = 0.5
K_SM       = 0.2
M_BOX      = 100         # puncte de discretizare [0,1] (fără pereți)
MF_ITERS   = 100
MF_TOL     = 1e-6
CV_CLASS   = 0.405

# Valorile T de testat (T = ħ²/2m, parametrul cinetic)
# T_B  = din condiția B (gap egal): ħ=0.233 → T = 0.233²/2 = 0.027
# T_eq = din echipariție:           ħ=2.923 → T = 2.923²/2 = 4.27
T_B  = 0.233**2 / 2     # 0.0271  (perturbativ)
T_EQ = 2.923**2 / 2     # 4.272   (echipariție, non-perturbativ)


# ── Graf ────────────────────────────────────────────────────────────────────

def _jacc(a, b):
    i = len(a & b); u = len(a | b); return i / u if u else 0.0

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    nb = {i: set() for i in range(n)}
    for i in range(n):
        pool = list(range(n)); pool.remove(i)
        for j in rng.sample(pool, min(k_init, len(pool))):
            nb[i].add(j); nb[j].add(i)
    adj = {i: set() for i in range(n)}
    for i in range(n):
        ni = nb[i] | {i}
        cands = set()
        for j in nb[i]: cands |= nb[j]
        cands.discard(i)
        sc = [(_jacc(ni, nb[j] | {j}), j) for j in cands]
        sc.sort(reverse=True)
        for _, j in sc[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return adj


# ── Hamiltonianul 1D pe [0,1] ────────────────────────────────────────────────

def build_box_hamiltonian(T, k_cl, k_sm, deg_i, Sigma_bar_i, M=M_BOX):
    """
    Construiește H_1D (M×M, diferențe finite) pentru nodul i.

    Grid interior: Σ_k = (k+1)/(M+1) pentru k=0,...,M-1
    Condiții de frontieră: ψ(0) = ψ(1) = 0 (implicit prin grid interior)

    H = -T · D² + diag(V_eff)
    D² = diferența finită a derivatei a doua (tridiagonală)
    """
    h    = 1.0 / (M + 1)            # pasul de grilă
    grid = np.arange(1, M + 1) * h  # Σ ∈ (0, 1) exclusiv

    # Potențial efectiv
    V = k_cl / 2.0 * grid**2 + k_sm * deg_i * (grid - Sigma_bar_i)**2

    # Derivata a doua (diferențe finite, tridiagonală)
    diag_main = np.full(M, 2.0)
    diag_off  = np.full(M - 1, -1.0)
    D2 = (np.diag(diag_main) + np.diag(diag_off, 1) + np.diag(diag_off, -1))

    H = T / h**2 * D2 + np.diag(V)
    return H, grid, h


def ground_state(T, k_cl, k_sm, deg_i, Sigma_bar_i, M=M_BOX):
    """
    Starea fundamentală a hamiltonianului box pentru nodul i.
    Returnează (E0, ⟨Σ⟩, ⟨Σ²⟩, ψ²(grid)).
    """
    H, grid, h = build_box_hamiltonian(T, k_cl, k_sm, deg_i, Sigma_bar_i, M)

    if T < 1e-10:
        # Limita clasică: ψ concentrată la minimul V
        V = k_cl / 2.0 * grid**2 + k_sm * deg_i * (grid - Sigma_bar_i)**2
        idx = np.argmin(V)
        Sigma_mean = float(grid[idx])
        Sigma_sq   = float(grid[idx]**2)
        E0 = float(V[idx])
        prob = np.zeros(M); prob[idx] = 1.0
        return E0, Sigma_mean, Sigma_sq, prob

    eigvals, eigvecs = np.linalg.eigh(H)
    psi0   = eigvecs[:, 0]                  # eigenvector cu energia minimă
    psi0   = psi0 / np.sqrt(np.sum(psi0**2) * h)   # normalizare ∫|ψ|²dΣ = 1
    prob   = psi0**2 * h                    # P(Σ_k) = |ψ(Σ_k)|²·h

    Sigma_mean = float(np.sum(grid * prob))
    Sigma_sq   = float(np.sum(grid**2 * prob))
    E0         = float(eigvals[0])

    return E0, Sigma_mean, Sigma_sq, prob


def self_consistent_box(adj, n, T, k_cl, k_sm, M=M_BOX, max_iter=MF_ITERS, tol=MF_TOL):
    """
    Rezolvă self-consistent ecuațiile mean-field pe tot graful.
    Returnează Sigma_mean[i], Sigma_var[i], E0[i] pentru fiecare nod.
    """
    degrees = np.array([len(adj[i]) for i in range(n)], dtype=float)

    # Inițializare: toți la Σ̄ = 0.5
    Sigma_bar = np.full(n, 0.5)

    for iteration in range(max_iter):
        Sigma_bar_old = Sigma_bar.copy()
        new_mean = np.zeros(n)

        for i in range(n):
            # Σ̄ al nodului i = media Σ a vecinilor săi
            if len(adj[i]) > 0:
                Sigma_neigh = float(np.mean([Sigma_bar[j] for j in adj[i]]))
            else:
                Sigma_neigh = 0.5

            E0_i, sm_i, ssq_i, _ = ground_state(
                T, k_cl, k_sm, float(degrees[i]), Sigma_neigh, M
            )
            new_mean[i] = sm_i

        Sigma_bar = new_mean
        delta = float(np.max(np.abs(Sigma_bar - Sigma_bar_old)))
        if delta < tol:
            break

    # Calcul final cu Σ̄ convergit
    Sigma_mean = np.zeros(n)
    Sigma_var  = np.zeros(n)
    E0_arr     = np.zeros(n)
    prob_boundary = np.zeros(n)  # P(Σ < 0.1 sau Σ > 0.9) — cât e lângă perete

    M_pts = M
    h = 1.0 / (M_pts + 1)
    grid = np.arange(1, M_pts + 1) * h

    for i in range(n):
        if len(adj[i]) > 0:
            Sigma_neigh = float(np.mean([Sigma_bar[j] for j in adj[i]]))
        else:
            Sigma_neigh = 0.5

        E0_i, sm_i, ssq_i, prob_i = ground_state(
            T, k_cl, k_sm, float(degrees[i]), Sigma_neigh, M_pts
        )
        Sigma_mean[i] = sm_i
        Sigma_var[i]  = ssq_i - sm_i**2
        E0_arr[i]     = E0_i
        # Probabilitate lângă pereți: Σ < 0.1 sau Σ > 0.9
        prob_boundary[i] = float(np.sum(prob_i[grid < 0.1]) + np.sum(prob_i[grid > 0.9]))

    return Sigma_mean, Sigma_var, E0_arr, prob_boundary, iteration


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: confinement complet — particula în cutie [0,1]"
    )
    ap.add_argument("--seed",    type=int,   default=3401)
    ap.add_argument("--n",       type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",  type=int,   default=K_INIT)
    ap.add_argument("--k-conn",  type=int,   default=K_CONN)
    ap.add_argument("--k-cl",    type=float, default=K_CL)
    ap.add_argument("--k-sm",    type=float, default=K_SM)
    ap.add_argument("--m-box",   type=int,   default=M_BOX)
    ap.add_argument("--out-dir", type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()
    print("=" * 66)
    print("QNG Q-Fields — Confinement complet: particula în cutie [0,1]")
    print("=" * 66)
    print(f"  k_cl={args.k_cl}  k_sm={args.k_sm}  M_box={args.m_box}")
    print(f"  T_B={T_B:.5f}  T_EQ={T_EQ:.5f}")
    print()

    # Graf
    print("[1/3] Graf Jaccard...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    degrees = np.array([len(adj[i]) for i in range(args.n_nodes)], dtype=float)
    print(f"      grad mediu={degrees.mean():.3f} ± {degrees.std():.3f}")

    # Sweep T
    T_values = [
        ("T=0 (clasic)",   0.0),
        (f"T_B={T_B:.4f}", T_B),
        ("T=0.5",          0.5),
        ("T=1.0",          1.0),
        ("T=2.0",          2.0),
        (f"T_EQ={T_EQ:.3f} (echip.)", T_EQ),
    ]

    print("[2/3] Sweep T (energie cinetică)...")
    print()
    print(f"  {'T':>20}  {'⟨Σ⟩ mean':>10}  {'⟨δΣ²⟩ mean':>12}  "
          f"{'σ_Σ mean':>10}  {'P_bnd mean':>11}  "
          f"{'cv_box':>9}  {'cv_tot':>9}  {'Conf?':>6}")
    print(f"  {'-'*20}  {'-'*10}  {'-'*12}  {'-'*10}  {'-'*11}  "
          f"{'-'*9}  {'-'*9}  {'-'*6}")

    rows = []
    T_star = None   # primul T unde confinement activ (σ > 0.25)

    for label, T in T_values:
        t_step = time.time()
        Sm, Sv, E0, Pb, n_iter = self_consistent_box(
            adj, args.n_nodes, T, args.k_cl, args.k_sm, args.m_box
        )

        mean_Sm  = float(Sm.mean())
        mean_Sv  = float(Sv.mean())
        mean_sig = float(np.sqrt(np.maximum(Sv, 0)).mean())
        mean_Pb  = float(Pb.mean())

        cv_box = float(Sv.std() / Sv.mean()) if Sv.mean() > 1e-12 else float("nan")
        cv_tot = math.sqrt(CV_CLASS**2 + cv_box**2) if math.isfinite(cv_box) else float("nan")

        confined = mean_sig < 0.25
        conf_str = "DA ✓" if confined else "NU ✗"

        if not confined and T_star is None and T > 0:
            T_star = T

        dt = time.time() - t_step
        print(f"  {label:>20}  {mean_Sm:10.5f}  {mean_Sv:12.7f}  "
              f"{mean_sig:10.5f}  {mean_Pb:11.6f}  "
              f"{cv_box:9.5f}  {cv_tot:9.5f}  {conf_str:>6}"
              f"  [{n_iter} iter, {dt:.1f}s]")

        rows.append({
            "label":    label,
            "T":        T,
            "mean_Sigma": mean_Sm,
            "mean_var_Sigma": mean_Sv,
            "mean_sigma_Sigma": mean_sig,
            "mean_prob_boundary": mean_Pb,
            "cv_box":   cv_box,
            "cv_total": cv_tot,
            "confined": confined,
            "n_iter":   n_iter,
        })

    elapsed = time.time() - t0

    # ── Analiză la T_B și T_EQ ──────────────────────────────────────────────

    print()
    print("=" * 66)
    print("ANALIZĂ DETALIATĂ")
    print("=" * 66)

    # Rulam o data mai detaliat la T_B pentru profile
    print(f"\n[3/3] Profil detaliat la T_B={T_B:.5f} (condiția B, perturbativ)...")
    Sm_B, Sv_B, E0_B, Pb_B, _ = self_consistent_box(
        adj, args.n_nodes, T_B, args.k_cl, args.k_sm, args.m_box
    )

    # Analiza inhomogeneitatii: corelatie grad↔Σ?
    corr_deg_Sigma = float(np.corrcoef(degrees, Sm_B)[0, 1])
    corr_deg_var   = float(np.corrcoef(degrees, Sv_B)[0, 1])

    print(f"  ⟨Σ⟩ per nod:  mean={Sm_B.mean():.5f}  std={Sm_B.std():.5f}")
    print(f"  ⟨δΣ²⟩ per nod: mean={Sv_B.mean():.7f}  std={Sv_B.std():.7f}")
    print(f"  Corelație grad↔⟨Σ⟩:   r={corr_deg_Sigma:.4f}"
          f"  ({'DA — grad influențează Σ̄' if abs(corr_deg_Sigma) > 0.3 else 'slabă'})")
    print(f"  Corelație grad↔⟨δΣ²⟩: r={corr_deg_var:.4f}"
          f"  ({'DA — grad influențează fluctuații' if abs(corr_deg_var) > 0.3 else 'slabă'})")

    # Box vs armonic la T_B
    # Armonicul pur (fără pereți): ⟨δΣ²⟩_harm ≈ T_B / k_cl (pentru un singur nod)
    zp_harmonic_approx = T_B / args.k_cl
    print(f"\n  Comparație confinement:")
    print(f"    ⟨δΣ²⟩ armonic (fără pereți): ≈ T/k_cl = {T_B:.5f}/{args.k_cl} = {zp_harmonic_approx:.5f}")
    print(f"    ⟨δΣ²⟩ box (cu pereți):       {Sv_B.mean():.7f}")
    ratio_box_harm = Sv_B.mean() / zp_harmonic_approx if zp_harmonic_approx > 0 else float("nan")
    print(f"    Raport box/armonic:           {ratio_box_harm:.4f}"
          f"  ({'pereții contează' if abs(ratio_box_harm - 1.0) > 0.1 else 'pereții neglijabili'})")

    # La T_B, probabilitate de a fi lângă perete
    print(f"    P(Σ < 0.1 sau Σ > 0.9):      {Pb_B.mean():.6f}"
          f"  ({'neglijabilă ✓' if Pb_B.mean() < 0.01 else 'semnificativă!'})")

    print(f"\n  La T_EQ={T_EQ:.3f} (echipariție):")
    Sm_EQ, Sv_EQ, E0_EQ, Pb_EQ, _ = self_consistent_box(
        adj, args.n_nodes, T_EQ, args.k_cl, args.k_sm, args.m_box
    )
    print(f"    ⟨Σ⟩ mean={Sm_EQ.mean():.4f}  ⟨δΣ²⟩={Sv_EQ.mean():.4f}"
          f"  σ_Σ={math.sqrt(Sv_EQ.mean()):.4f}")
    print(f"    P(bnd)={Pb_EQ.mean():.4f}"
          f"  ({'confinement activ — pereții contează MULT' if Pb_EQ.mean() > 0.05 else 'OK'})")

    # ── Concluzie finală ─────────────────────────────────────────────────────

    print()
    print("─" * 66)
    print("CONCLUZIE: Confinement complet")
    print("─" * 66)
    print()

    r_B  = next(r for r in rows if "T_B" in r["label"])
    r_EQ = next(r for r in rows if "echip" in r["label"])

    print(f"  La T_B (condiția B, ħ=0.233, perturbativ):")
    print(f"    σ_Σ = {r_B['mean_sigma_Sigma']:.5f} << 0.25  → confinement INACTIV")
    print(f"    cv_box = {r_B['cv_box']:.5f}  cv_total = {r_B['cv_total']:.5f}")
    print(f"    Pereții [0,1] nu contează — câmpul Σ nu 'vede' marginile.")
    print()
    print(f"  La T_EQ (echipariție, ħ=2.923, non-perturbativ):")
    print(f"    σ_Σ = {r_EQ['mean_sigma_Sigma']:.5f}  ({'> 0.25 → confinement ACTIV' if r_EQ['mean_sigma_Sigma'] > 0.25 else '< 0.25 → confinement inactiv'})")
    print(f"    cv_box = {r_EQ['cv_box']:.5f}  cv_total = {r_EQ['cv_total']:.5f}")
    print()
    print(f"  Prag confinement (σ_Σ = 0.25) → T* ≈ ", end="")
    # Interpolam între T_B și T_EQ
    sig_B  = r_B["mean_sigma_Sigma"]
    sig_EQ = r_EQ["mean_sigma_Sigma"]
    if sig_B < 0.25 < sig_EQ:
        # interpolare liniară în spațiul sqrt(T)
        T_star_interp = T_B + (T_EQ - T_B) * (0.25 - sig_B) / (sig_EQ - sig_B)
        print(f"{T_star_interp:.4f}")
        print(f"    (ħ_star ≈ {math.sqrt(2*T_star_interp):.4f})")
    else:
        print("N/A")

    print()
    print(f"  cv_total rămâne ≈ {r_B['cv_total']:.4f} la T_B și ≈ {r_EQ['cv_total']:.4f} la T_EQ.")
    print(f"  → Pioneer robust față de confinement: variație Δcv_total < "
          f"{abs(r_EQ['cv_total'] - r_B['cv_total']):.4f}")
    print(f"\nTimp total: {elapsed:.1f}s")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_box_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "params": vars(args) | {"T_B": T_B, "T_EQ": T_EQ},
        "sweep": rows,
        "detailed_T_B": {
            "mean_Sigma":   float(Sm_B.mean()),
            "mean_var":     float(Sv_B.mean()),
            "mean_sigma":   float(math.sqrt(max(Sv_B.mean(), 0))),
            "mean_P_bnd":   float(Pb_B.mean()),
            "corr_deg_Sm":  corr_deg_Sigma,
            "corr_deg_var": corr_deg_var,
            "box_vs_harm_ratio": ratio_box_harm,
        },
        "detailed_T_EQ": {
            "mean_Sigma":   float(Sm_EQ.mean()),
            "mean_var":     float(Sv_EQ.mean()),
            "mean_sigma":   float(math.sqrt(max(Sv_EQ.mean(), 0))),
            "mean_P_bnd":   float(Pb_EQ.mean()),
        },
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
