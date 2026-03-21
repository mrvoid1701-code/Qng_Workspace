#!/usr/bin/env python3
"""
QNG Q-Fields — Confinement double-well pentru Σ (v1)

Problema: la scara naturală (echipariție cu G17), ħ_field = 2.92 → ⟨δΣ²⟩ ≈ 1,
adică fluctuațiile acoperă tot [0,1]. Confinementul Σ ∈ [0,1] e esențial.

Soluție: înlocuiește potențialul armonic cu un double-well care are minime la
Σ=0 și Σ=1 și un maxim la Σ=0.5:

  V_dw(Σ) = λ · Σ²(1-Σ)²

Expansie în jurul minimelui Σ=0 (sau Σ=1):
  V_dw''(0) = V_dw''(1) = 2λ  → forță de restaurare suplimentară

Deci K_dw = K_armonic cu k_cl → k_cl_eff = k_cl + 2λ.
Restul structurii K rămâne identic.

Sweep λ ∈ [0, λ_max]:
- Cum se schimbă ω_min, ⟨δΣ²⟩, cv_quantum?
- La ce λ_min sistemul devine perturbativ sub ħ_field = 2.92 (echipariție)?
- cv_quantum rămâne invariant față de λ?  (nu — λ schimbă structura modurilor)

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-double-well-v1"
)

N_NODES  = 280
K_INIT   = 8
K_CONN   = 8
K_CL     = 0.5
K_SM     = 0.2
K_CHI    = 0.3
K_MIX    = 0.1
HBAR_EQ  = 2.92297   # din ancorare echipariție (run_qng_qf_hbar_anchor_v1)
CV_CLASS = 0.405


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

def graph_laplacian(adj, n):
    L = np.zeros((n, n))
    for i in range(n):
        L[i, i] = float(len(adj[i]))
        for j in adj[i]: L[i, j] = -1.0
    return L


def compute_observables(L, n, k_cl_eff, k_sm, k_chi, k_mix):
    """Calculeaza ω_min, E0/mod, zp_sigma, cv_quantum pentru k_cl_eff dat."""
    M_s = k_cl_eff * np.eye(n) + k_sm * L
    M_c = k_chi * np.eye(n)
    M_x = k_mix * np.eye(n)
    K = np.block([[M_s, M_x], [M_x, M_c]])

    eigvals, eigvecs = np.linalg.eigh(K)
    omega = np.where(eigvals > 0, np.sqrt(np.maximum(eigvals, 0.0)), 0.0)
    pos = omega > 1e-10
    safe_w = np.where(pos, omega, np.inf)
    weights = 1.0 / (2.0 * safe_w)   # ħ=1

    U_s = eigvecs[:n, :]
    zp = np.einsum("ia,a,ia->i", U_s, weights, U_s)

    omega_min   = float(omega[pos].min()) if pos.any() else 0.0
    E0_per_mode = float(omega.sum() / (2 * n))
    zp_mean     = float(zp.mean())
    zp_std      = float(zp.std())
    cv_q        = zp_std / zp_mean if zp_mean > 1e-12 else float("nan")

    # Cu ħ_field = HBAR_EQ
    zp_phys = HBAR_EQ * zp_mean
    sig_phys = math.sqrt(zp_phys)
    valid = sig_phys < 0.5   # σ_Σ < 0.5 (perturbativ în [0,1])

    cv_tot = math.sqrt(CV_CLASS**2 + cv_q**2) if math.isfinite(cv_q) else float("nan")

    return {
        "k_cl_eff":     k_cl_eff,
        "omega_min":    omega_min,
        "E0_per_mode":  E0_per_mode,
        "zp_mean_h1":   zp_mean,
        "zp_std_h1":    zp_std,
        "cv_quantum":   cv_q,
        "cv_total":     cv_tot,
        "zp_phys_eq":   zp_phys,
        "sigma_phys_eq": sig_phys,
        "valid_pert":   valid,
    }


def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: confinement double-well"
    )
    ap.add_argument("--seed",    type=int,   default=3401)
    ap.add_argument("--n",       type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",  type=int,   default=K_INIT)
    ap.add_argument("--k-conn",  type=int,   default=K_CONN)
    ap.add_argument("--k-cl",    type=float, default=K_CL)
    ap.add_argument("--k-sm",    type=float, default=K_SM)
    ap.add_argument("--k-chi",   type=float, default=K_CHI)
    ap.add_argument("--k-mix",   type=float, default=K_MIX)
    ap.add_argument("--n-steps", type=int,   default=20)
    ap.add_argument("--lam-max", type=float, default=5.0)
    ap.add_argument("--out-dir", type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()
    print("=" * 64)
    print("QNG Q-Fields — Confinement double-well pentru Σ")
    print("=" * 64)
    print(f"  k_cl={args.k_cl}  k_sm={args.k_sm}  k_chi={args.k_chi}  k_mix={args.k_mix}")
    print(f"  ħ_equip={HBAR_EQ:.5f}  sweep λ ∈ [0, {args.lam_max}]")
    print()

    print("[1/2] Graf Jaccard...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    L   = graph_laplacian(adj, args.n_nodes)

    print("[2/2] Sweep λ (confinement)...")
    print()
    print(f"  {'λ':>6}  {'k_cl_eff':>10}  {'ω_min':>8}  {'⟨δΣ²⟩(ħ_eq)':>13}  "
          f"{'σ_Σ(ħ_eq)':>10}  {'cv_q':>8}  {'cv_tot':>8}  {'Pert?':>6}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*8}  {'-'*13}  {'-'*10}  {'-'*8}  {'-'*8}  {'-'*6}")

    lam_values = [args.lam_max * i / (args.n_steps - 1) for i in range(args.n_steps)]
    rows = []
    lam_star = None   # primul λ unde devine perturbativ

    for lam in lam_values:
        k_eff = args.k_cl + 2.0 * lam
        r = compute_observables(L, args.n_nodes, k_eff, args.k_sm, args.k_chi, args.k_mix)
        rows.append({"lambda": round(lam, 5), **r})

        pert = "DA ✓" if r["valid_pert"] else "NU"
        print(f"  {lam:6.3f}  {k_eff:10.4f}  {r['omega_min']:8.4f}  "
              f"{r['zp_phys_eq']:13.6f}  {r['sigma_phys_eq']:10.6f}  "
              f"{r['cv_quantum']:8.5f}  {r['cv_total']:8.5f}  {pert:>6}")

        if r["valid_pert"] and lam_star is None:
            lam_star = lam

    elapsed = time.time() - t0

    # ── Rezumat ──────────────────────────────────────────────────────────────
    r0 = rows[0]    # λ=0 (armonic pur, fără confinement)
    r_star = next((r for r in rows if r["valid_pert"]), None)

    print()
    print("=" * 64)
    print("REZUMAT")
    print("=" * 64)
    print(f"\n  Fără confinement (λ=0):")
    print(f"    ω_min = {r0['omega_min']:.4f}  ⟨δΣ²⟩ = {r0['zp_phys_eq']:.4f}  "
          f"cv_q = {r0['cv_quantum']:.5f}  cv_tot = {r0['cv_total']:.5f}")

    if r_star:
        print(f"\n  Cu confinement (λ={r_star['lambda']:.3f}, "
              f"k_cl_eff={r_star['k_cl_eff']:.4f}):")
        print(f"    ω_min = {r_star['omega_min']:.4f}  "
              f"⟨δΣ²⟩ = {r_star['zp_phys_eq']:.4f}  "
              f"cv_q = {r_star['cv_quantum']:.5f}  "
              f"cv_tot = {r_star['cv_total']:.5f}")

    # Analiza cv_quantum: variaza cu λ?
    cv_vals = [r["cv_quantum"] for r in rows if math.isfinite(r["cv_quantum"])]
    cv_range = max(cv_vals) - min(cv_vals)
    print(f"\n  cv_quantum ∈ [{min(cv_vals):.5f}, {max(cv_vals):.5f}]  "
          f"variație: {cv_range:.5f}")
    if cv_range < 0.01:
        print("  → cv_quantum ≈ CONSTANT față de λ  (confinementul nu-l schimbă)")
    else:
        print(f"  → cv_quantum VARIAZA cu λ  (Δcv = {cv_range:.5f})")

    print()
    print("Interpretare fizică:")
    if r_star:
        dk = r_star["k_cl_eff"] - args.k_cl
        print(f"  → Double-well cu λ={r_star['lambda']:.3f} adaugă k_cl_eff += {dk:.3f}")
        print(f"  → Aceasta ÎNTĂREȘTE restabilizarea Σ: ω_min crește")
        print(f"  → {r_star['lambda']:.3f} / k_cl = {r_star['lambda']/args.k_cl:.2f}"
              f" → confinementul e de {r_star['lambda']/args.k_cl:.1f}x mai puternic decât k_cl")
    print(f"  → cv_total rămâne ≈ {rows[-1]['cv_total']:.4f} → Pioneer predicție robustă")
    print(f"\nTimp: {elapsed:.1f}s")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_double_well_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "params": vars(args) | {"hbar_equip": HBAR_EQ},
        "lambda_star": lam_star,
        "k_cl_eff_star": (args.k_cl + 2*lam_star) if lam_star else None,
        "cv_quantum_range": [min(cv_vals), max(cv_vals)],
        "cv_total_range": [
            min(r["cv_total"] for r in rows if math.isfinite(r["cv_total"])),
            max(r["cv_total"] for r in rows if math.isfinite(r["cv_total"])),
        ],
        "scan": rows,
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
