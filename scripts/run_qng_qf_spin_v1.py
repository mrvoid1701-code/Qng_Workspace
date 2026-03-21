#!/usr/bin/env python3
"""
QNG Q-Fields — Confinement spin/qubit pentru Σ (v1)

Alternativa la double-well: tratam Σ_i ca un sistem cu 2 nivele (qubit).

Mapare:
  Σ_i ∈ {0, 1}  →  Σ̂_i = (1 + σ̂^z_i) / 2

Hamiltonianul clasic QNG în limbaj spin:
  k_sm/2 · (Σ_i - Σ_j)² = k_sm/8 · (σ^z_i - σ^z_j)²
                         = k_sm/4 · (I - σ^z_i σ^z_j)
  → interacțiune Ising: J_ij = k_sm/4  (pe muchiile grafului)

Dinamica cuantică necesită un câmp transversal Γ (echivalentul ħ_field):
  Ĥ_spin = -Γ Σ_i σ̂^x_i  +  J Σ_{<i,j>} σ̂^z_i σ̂^z_j  +  h Σ_i σ̂^z_i

  Γ = câmp transversal (fluctuații cuantice Σ)
  J = k_sm/4 (cuplaj Ising)
  h = -k_cl/2 (câmp local, simetrie spartă)

Faza cuantică (Mean-Field TFIM):
  Paramagnetic (Γ >> J·z): m → 0, Σ → 0.5, fluctuații maxime
  Feromagnetic (Γ << J·z): m → ±1, Σ → 0 sau 1, fluctuații mici
  Tranziție la: Γ* = J · z_mean

Calculăm prin Mean-Field iterativ:
  m_i = (J · Σ_{j∈N(i)} m_j) / ε_i
  ε_i = √(Γ² + (h_i^eff)²)
  h_i^eff = J · Σ_{j∈N(i)} m_j + h

Sweep Γ ∈ [0, 2Γ*] și calculăm:
  ⟨Σ_i⟩ = (1 + m_i)/2
  ⟨(δΣ_i)²⟩ = (1 - m_i²)/4
  cv_spin = σ(⟨δΣ_i²⟩) / μ(⟨δΣ_i²⟩)

Fișier nou, nu modifică nimic existent.
"""

from __future__ import annotations

import argparse
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-spin-v1"
)

N_NODES  = 280
K_INIT   = 8
K_CONN   = 8
K_SM     = 0.2
K_CL     = 0.5
CV_CLASS = 0.405
MF_MAX_ITER = 500
MF_TOL      = 1e-8


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


def build_adjacency_matrix(adj, n):
    A = np.zeros((n, n))
    for i in range(n):
        for j in adj[i]:
            A[i, j] = 1.0
    return A


def mean_field_tfim(A, n, J, Gamma, h_field, m_init=None):
    """
    Mean-Field TFIM pe graful dat.
    Returnează magnetizările {m_i} în starea fundamentală (T=0).

    Câmp efectiv per nod:  h_i^eff = J · Σ_j A_ij m_j + h_field
    Energie locală:        ε_i = √(Γ² + (h_i^eff)²)
    Magnetizare:           m_i = h_i^eff / ε_i

    Iterăm până la convergență.
    """
    if m_init is None:
        # Inițializare: magnetizare slabă (simetrie ușor spartă)
        m = np.full(n, 0.01)
    else:
        m = m_init.copy()

    for _ in range(MF_MAX_ITER):
        m_old = m.copy()
        # h_eff_i = J * Σ_j A_ij m_j + h_field
        h_eff = J * (A @ m) + h_field
        eps   = np.sqrt(Gamma**2 + h_eff**2)
        # Evită div/0
        safe_eps = np.where(eps > 1e-15, eps, 1e-15)
        m_new = h_eff / safe_eps
        m = m_new
        if np.max(np.abs(m - m_old)) < MF_TOL:
            break
    return m


def compute_spin_observables(m, Gamma, J, h_field):
    """Calculează observabilele din magnetizările MF."""
    h_eff  = J * np.sum(m) / len(m) * len(m)   # placeholder, calculat din m
    # ⟨Σ_i⟩ = (1 + m_i)/2
    Sigma_mean = (1.0 + m) / 2.0
    # ⟨(δΣ_i)²⟩ = (1 - m_i²)/4
    dSigma_sq = (1.0 - m**2) / 4.0

    mean_m   = float(np.mean(m))
    std_m    = float(np.std(m))
    mean_dSq = float(dSigma_sq.mean())
    std_dSq  = float(dSigma_sq.std())
    cv_spin  = std_dSq / mean_dSq if mean_dSq > 1e-12 else float("nan")

    cv_tot = math.sqrt(CV_CLASS**2 + cv_spin**2) if math.isfinite(cv_spin) else float("nan")

    # Sigma medie globală
    mean_Sigma = float(Sigma_mean.mean())
    std_Sigma  = float(Sigma_mean.std())

    return {
        "Gamma":       Gamma,
        "mean_m":      mean_m,
        "std_m":       std_m,
        "mean_Sigma":  mean_Sigma,
        "std_Sigma":   std_Sigma,
        "mean_dSq":    mean_dSq,
        "std_dSq":     std_dSq,
        "cv_spin":     cv_spin,
        "cv_total":    cv_tot,
        "ordered":     abs(mean_m) > 0.01,
    }


def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: confinement spin/qubit TFIM"
    )
    ap.add_argument("--seed",    type=int,   default=3401)
    ap.add_argument("--n",       type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",  type=int,   default=K_INIT)
    ap.add_argument("--k-conn",  type=int,   default=K_CONN)
    ap.add_argument("--k-sm",    type=float, default=K_SM)
    ap.add_argument("--k-cl",    type=float, default=K_CL)
    ap.add_argument("--n-steps", type=int,   default=30)
    ap.add_argument("--out-dir", type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()

    # Parametri Ising din QNG
    J      = args.k_sm / 4.0      # J = k_sm/4 (cuplaj Ising)
    h_loc  = -args.k_cl / 2.0     # câmp local din k_cl

    print("=" * 64)
    print("QNG Q-Fields — Confinement spin/qubit (Transverse-Field Ising)")
    print("=" * 64)
    print(f"  k_sm={args.k_sm}  k_cl={args.k_cl}")
    print(f"  J = k_sm/4 = {J:.4f}  (cuplaj Ising)")
    print(f"  h = -k_cl/2 = {h_loc:.4f}  (câmp local)")

    # Graf
    print("\n[1/3] Graf Jaccard...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    A   = build_adjacency_matrix(adj, args.n_nodes)
    degrees = np.array([len(adj[i]) for i in range(args.n_nodes)])
    z_mean  = float(degrees.mean())
    z_std   = float(degrees.std())
    print(f"      grad mediu z={z_mean:.3f} ± {z_std:.3f}")

    # Gamma critic (MF: Γ* = J · z_mean pentru h=0)
    Gamma_star_mf = J * z_mean
    print(f"\n[2/3] Tranziție de fază MF:")
    print(f"  Γ* (h=0) = J · z_mean = {J:.4f} · {z_mean:.3f} = {Gamma_star_mf:.4f}")
    # Cu câmp local h≠0, tranziția e estompată (faza ordonată preferă un semn)
    print(f"  h={h_loc:.4f} ≠ 0 → tranziție estompată (faza ordonată Σ→0 preferată)")

    # Sweep Gamma
    Gamma_max = 2.5 * Gamma_star_mf
    Gamma_values = [Gamma_max * i / (args.n_steps - 1)
                    for i in range(args.n_steps)]

    print(f"\n[3/3] Sweep Γ ∈ [0, {Gamma_max:.4f}] ({args.n_steps} pași)...")
    print()
    print(f"  {'Γ':>8}  {'Γ/Γ*':>7}  {'⟨m⟩':>8}  {'⟨Σ⟩':>8}  "
          f"{'⟨δΣ²⟩':>9}  {'cv_spin':>9}  {'cv_tot':>9}  {'Faza':>10}")
    print(f"  {'-'*8}  {'-'*7}  {'-'*8}  {'-'*8}  "
          f"{'-'*9}  {'-'*9}  {'-'*9}  {'-'*10}")

    rows = []
    m_prev = None

    for Gamma in Gamma_values:
        m = mean_field_tfim(A, args.n_nodes, J, Gamma, h_loc, m_init=m_prev)
        m_prev = m.copy()   # warm start pentru convergență mai rapidă
        r = compute_spin_observables(m, Gamma, J, h_loc)
        rows.append(r)

        phase = "ORDONAT" if r["ordered"] else "DEZORDONAT"
        ratio = Gamma / Gamma_star_mf if Gamma_star_mf > 0 else 0
        cv_str = f"{r['cv_spin']:.5f}" if math.isfinite(r["cv_spin"]) else "   nan"
        ct_str = f"{r['cv_total']:.5f}" if math.isfinite(r["cv_total"]) else "   nan"
        print(f"  {Gamma:8.4f}  {ratio:7.3f}  {r['mean_m']:8.4f}  "
              f"{r['mean_Sigma']:8.4f}  {r['mean_dSq']:9.6f}  "
              f"{cv_str:>9}  {ct_str:>9}  {phase:>10}")

    elapsed = time.time() - t0

    # ── Rezumat ──────────────────────────────────────────────────────────────
    print()
    print("=" * 64)
    print("REZUMAT SPIN MODEL")
    print("=" * 64)

    r_ord  = rows[0]   # Γ=0: complet ordonat
    # Gasim Gamma de tranziție (unde |m| trece sub 0.01)
    r_trans = None
    Gamma_trans = None
    for i in range(len(rows)-1):
        if rows[i]["ordered"] and not rows[i+1]["ordered"]:
            Gamma_trans = (rows[i]["Gamma"] + rows[i+1]["Gamma"]) / 2
            r_trans = rows[i+1]
            break
    r_dis = rows[-1]   # Γ_max: dezordonat

    print(f"\n  Faza ordonată (Γ→0):")
    print(f"    ⟨m⟩={r_ord['mean_m']:.4f}  ⟨Σ⟩={r_ord['mean_Sigma']:.4f}  "
          f"⟨δΣ²⟩={r_ord['mean_dSq']:.6f}")

    if Gamma_trans:
        print(f"\n  Tranziție de fază la Γ≈{Gamma_trans:.4f}  "
              f"(Γ*/Γ_MF = {Gamma_trans/Gamma_star_mf:.3f})")

    print(f"\n  Faza dezordonată (Γ={r_dis['Gamma']:.4f}):")
    print(f"    ⟨m⟩={r_dis['mean_m']:.4f}  ⟨Σ⟩={r_dis['mean_Sigma']:.4f}  "
          f"⟨δΣ²⟩={r_dis['mean_dSq']:.6f}")
    if math.isfinite(r_dis["cv_spin"]):
        print(f"    cv_spin={r_dis['cv_spin']:.5f}  cv_tot={r_dis['cv_total']:.5f}")

    # cv_spin range
    cv_spins = [r["cv_spin"] for r in rows if math.isfinite(r["cv_spin"])]
    if cv_spins:
        print(f"\n  cv_spin ∈ [{min(cv_spins):.5f}, {max(cv_spins):.5f}]")

    print()
    print("Interpretare fizică:")
    print(f"  → Γ joacă rolul ħ_field în modelul spin (setează fluctuațiile cuantice)")
    print(f"  → La Γ < Γ* = {Gamma_star_mf:.4f}: Σ ≈ 0 (ordonat, metric 'ferm')")
    print(f"  → La Γ > Γ*: Σ fluctuează liber în [0,1] (metric 'topit')")
    print(f"  → Inhomogeneitatea gradelor (σ_z={z_std:.3f}) produce cv_spin ≠ 0")
    print(f"  → Aceasta e cv-ul 'natural' al modelului spin, fără tuning")
    if cv_spins:
        max_cv_spin = max(cv_spins)
        ratio_to_cl = max_cv_spin / CV_CLASS
        print(f"  → cv_spin_max = {max_cv_spin:.4f}  "
              f"({100*ratio_to_cl:.1f}% din cv_classical=0.405)")
    print(f"\nTimp: {elapsed:.1f}s")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_spin_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "params": {
            "seed": args.seed, "n_nodes": args.n_nodes,
            "k_sm": args.k_sm, "k_cl": args.k_cl,
            "J": J, "h_loc": h_loc,
        },
        "graph": {
            "z_mean": z_mean, "z_std": z_std,
            "Gamma_star_mf": Gamma_star_mf,
            "Gamma_trans_numeric": Gamma_trans,
        },
        "cv_spin_range": [min(cv_spins), max(cv_spins)] if cv_spins else None,
        "scan": rows,
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
