#!/usr/bin/env python3
"""
QNG Q-Fields — Scanarea k_mix critic (v1)

Determină valoarea critică k_mix* la care Hamiltonianul cuantic K devine singular
(tranziție de fază cuantică: sistem stabil → instabil).

Teoria analitică (Schur complement):
  K pozitiv definit ⟺ M_sigma - k_mix²·M_chi⁻¹ pozitiv definit
  M_chi = k_chi·I  →  M_chi⁻¹ = (1/k_chi)·I
  Condiție: k_cl + k_sm·λ_L(i) - k_mix²/k_chi > 0  ∀ λ_L(i)
  Minim la λ_L = 0 (zero-mod Laplacian):
    k_mix* = √(k_cl · k_chi)

Verificare numerică: sweep k_mix ∈ [0, k_mix_max], calculez ω_min(K) la fiecare pas.
La k_mix = k_mix*: ω_min → 0.

Fișier nou, nu modifică nimic existent.
Derivare: 03_math/derivations/qng-quantum-sigma-chi-v1.md
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-kmix-scan-v1"
)

N_NODES = 280
K_INIT  = 8
K_CONN  = 8
K_CL    = 0.5
K_SM    = 0.2
K_CHI   = 0.3
HBAR    = 1.0


# ── Graf Jaccard (identic cu run_qng_q_fields_v1.py) ──────────────────────

def _jaccard(a: set, b: set) -> float:
    i = len(a & b); u = len(a | b)
    return i / u if u else 0.0

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    nbrs: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        pool = list(range(n)); pool.remove(i)
        for j in rng.sample(pool, min(k_init, len(pool))):
            nbrs[i].add(j); nbrs[j].add(i)
    adj: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        ni = nbrs[i] | {i}
        cands = set()
        for j in nbrs[i]: cands |= nbrs[j]
        cands.discard(i)
        scores = [(_jaccard(ni, nbrs[j] | {j}), j) for j in cands]
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return adj

def graph_laplacian(adj, n):
    L = np.zeros((n, n))
    for i in range(n):
        L[i, i] = float(len(adj[i]))
        for j in adj[i]: L[i, j] = -1.0
    return L


# ── Scan ───────────────────────────────────────────────────────────────────

def omega_min_for_kmix(L, n, k_cl, k_sm, k_chi, k_mix):
    """Returnează ω_min al lui K pentru un k_mix dat."""
    M_sigma = k_cl * np.eye(n) + k_sm * L
    M_chi   = k_chi * np.eye(n)
    M_cross = k_mix * np.eye(n)
    K = np.block([[M_sigma, M_cross], [M_cross, M_chi]])
    # Nevoie doar de eigenvalue minim — mai rapid cu eigvalsh fără vectori
    lmin = np.linalg.eigvalsh(K)[0]
    omega_min = math.sqrt(max(lmin, 0.0))
    return omega_min, lmin


def analytical_kmix_critical(k_cl, k_chi):
    """k_mix* = √(k_cl · k_chi) din condiția Schur complement."""
    return math.sqrt(k_cl * k_chi)


def analytical_omega_min(k_cl, k_sm, k_chi, k_mix, lambda_L_min=0.0):
    """
    ω_min analitic din complementul Schur:
      λ_min(K) ≈ k_cl + k_sm·λ_L_min - k_mix²/k_chi    (la primul ordin)
    Valabil exact când L și I comutează, adică pe graful complet sau în limita
    k_sm → 0. Pe graful real e o aproximare bună pentru λ_L_min ≈ 0.
    """
    lambda_K_min = k_cl + k_sm * lambda_L_min - k_mix**2 / k_chi
    if lambda_K_min <= 0:
        return 0.0
    return math.sqrt(lambda_K_min)


def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: scanare k_mix critic"
    )
    ap.add_argument("--seed",     type=int,   default=3401)
    ap.add_argument("--n",        type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",   type=int,   default=K_INIT)
    ap.add_argument("--k-conn",   type=int,   default=K_CONN)
    ap.add_argument("--k-cl",     type=float, default=K_CL)
    ap.add_argument("--k-sm",     type=float, default=K_SM)
    ap.add_argument("--k-chi",    type=float, default=K_CHI)
    ap.add_argument("--n-steps",  type=int,   default=40,
                    help="Număr de puncte în sweep k_mix")
    ap.add_argument("--kmix-max", type=float, default=0.50)
    ap.add_argument("--out-dir",  type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()

    # Predicție analitică
    k_mix_star_analytic = analytical_kmix_critical(args.k_cl, args.k_chi)
    print("=" * 62)
    print("QNG Q-Fields — Scanare k_mix critic")
    print("=" * 62)
    print(f"  Parametri: k_cl={args.k_cl} k_sm={args.k_sm} k_chi={args.k_chi}")
    print(f"  Predicție analitică:  k_mix* = √(k_cl·k_chi) = "
          f"√({args.k_cl}·{args.k_chi}) = {k_mix_star_analytic:.6f}")
    print()

    # Graf
    print(f"[1/2] Construiesc graful Jaccard (seed={args.seed})...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    L   = graph_laplacian(adj, args.n_nodes)
    l_eigs = np.linalg.eigvalsh(L)
    lambda_L_min = float(l_eigs[0])    # ≈ 0 (zero-mod)
    lambda_L_max = float(l_eigs[-1])
    print(f"      λ_min(L)={lambda_L_min:.6f}  λ_max(L)={lambda_L_max:.4f}")

    # Sweep
    print(f"[2/2] Sweep k_mix ∈ [0, {args.kmix_max}] cu {args.n_steps} pași...")
    print()
    print(f"  {'k_mix':>8}  {'ω_min numeric':>14}  {'ω_min analitic':>14}  "
          f"{'λ_min(K)':>12}  {'Status':>8}")
    print(f"  {'-'*8}  {'-'*14}  {'-'*14}  {'-'*12}  {'-'*8}")

    kmix_values = [args.kmix_max * i / (args.n_steps - 1)
                   for i in range(args.n_steps)]
    scan_rows = []
    k_mix_numeric_critical = None

    for k_mix in kmix_values:
        omega_num, lmin = omega_min_for_kmix(
            L, args.n_nodes, args.k_cl, args.k_sm, args.k_chi, k_mix
        )
        omega_ana = analytical_omega_min(
            args.k_cl, args.k_sm, args.k_chi, k_mix, lambda_L_min
        )
        stable = lmin > 0
        status = "STABIL" if stable else "INSTABIL"

        print(f"  {k_mix:8.4f}  {omega_num:14.6f}  {omega_ana:14.6f}  "
              f"{lmin:12.6f}  {status:>8}")

        row = {
            "k_mix":         round(k_mix, 6),
            "omega_min_num": float(omega_num),
            "omega_min_ana": float(omega_ana),
            "lambda_min_K":  float(lmin),
            "stable":        bool(stable),
        }
        scan_rows.append(row)

        # Detectez prima trecere în instabil
        if not stable and k_mix_numeric_critical is None:
            k_mix_numeric_critical = k_mix

    # Interpolare liniară pentru k_mix* numeric (mai precis)
    k_mix_star_numeric = None
    for i in range(len(scan_rows) - 1):
        r0, r1 = scan_rows[i], scan_rows[i + 1]
        if r0["lambda_min_K"] > 0 >= r1["lambda_min_K"]:
            # interpolare liniară între r0 și r1
            lm0, lm1 = r0["lambda_min_K"], r1["lambda_min_K"]
            km0, km1 = r0["k_mix"],        r1["k_mix"]
            k_mix_star_numeric = km0 + (km1 - km0) * (-lm0) / (lm1 - lm0)
            break

    elapsed = time.time() - t0

    print()
    print("=" * 62)
    print("REZULTATE")
    print("=" * 62)
    err_abs = abs(k_mix_star_numeric - k_mix_star_analytic) if k_mix_star_numeric else None
    err_pct = 100 * err_abs / k_mix_star_analytic if err_abs is not None else None

    print(f"  k_mix* analitic:   {k_mix_star_analytic:.6f}  "
          f"(formula: √(k_cl·k_chi))")
    if k_mix_star_numeric:
        print(f"  k_mix* numeric:    {k_mix_star_numeric:.6f}  "
              f"(interpolare liniară)")
        print(f"  Eroare:            {err_abs:.6f}  ({err_pct:.2f}%)")
        agrees = err_pct < 5.0
        print(f"  Acord:             {'DA ✓' if agrees else 'NU ✗'}  "
              f"(prag 5%)")
    else:
        print("  k_mix* numeric:    nedetectat (k_mix_max prea mic?)")

    print()
    print("Interpretare fizică:")
    print(f"  → La k_mix < {k_mix_star_analytic:.3f}: câmpurile Σ și χ sunt stabile cuantic.")
    print(f"  → La k_mix = {k_mix_star_analytic:.3f}: tranziție de fază cuantică (ω_min → 0).")
    print(f"  → La k_mix > {k_mix_star_analytic:.3f}: instabilitate — Hamiltonianul nu mai e")
    print(f"    mărginit inferior; cuantificarea naivă eșuează.")
    print(f"  → k_mix nominal (0.1) este la {100*0.1/k_mix_star_analytic:.1f}% din k_mix*.")
    print(f"    Sistemul e departe de tranziție → stabilitate robustă.")

    # Verificare: ω_min ≈ 0 la k_mix*
    # Testul principal al scriptului
    gate_pass = (k_mix_star_numeric is not None
                 and err_pct is not None
                 and err_pct < 5.0)

    print()
    print(f"GATE:  {'PASS ✓' if gate_pass else 'FAIL ✗'}  "
          f"(acord analitic-numeric < 5%)")
    print(f"Timp:  {elapsed:.1f}s")

    # Salvare artefact
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_kmix_scan_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status":    "PASS" if gate_pass else "FAIL",
        "params": {
            "seed": args.seed, "n_nodes": args.n_nodes,
            "k_cl": args.k_cl, "k_sm": args.k_sm, "k_chi": args.k_chi,
            "n_steps": args.n_steps, "kmix_max": args.kmix_max,
        },
        "results": {
            "k_mix_star_analytic": k_mix_star_analytic,
            "k_mix_star_numeric":  k_mix_star_numeric,
            "error_abs":           err_abs,
            "error_pct":           err_pct,
            "gate_pass":           gate_pass,
            "lambda_L_min":        lambda_L_min,
            "lambda_L_max":        lambda_L_max,
            "k_mix_nominal_pct_of_critical": round(100 * 0.1 / k_mix_star_analytic, 1),
        },
        "scan": scan_rows,
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
