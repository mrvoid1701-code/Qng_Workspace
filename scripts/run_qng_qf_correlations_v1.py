#!/usr/bin/env python3
"""
QNG Q-Fields — Corelații la două puncte și metrică cuantică (v1)

Calculează G_ij = ⟨δΣ_i · δΣ_j⟩ (funcția Green a câmpului Σ cuantic)
și extrage:

  1. Lungimea de corelație cuantică ξ
     G(r) ~ A · exp(-r/ξ) față de distanța geodezică r_ij (BFS)
     Comparăm cu ξ_G17 = 1/√M_EFF_SQ ≈ 8.5 (din propagatorul Yukawa G17)

  2. Metrica cuantică
     Corecție relativă față de metrica clasică:
     δg_ij / g_ij = G_ij / ⟨Σ⟩²  (primele corecții loop)

  3. Parametrul spin-boson α
     Modelul Σ (spin) + χ (oscilator) = spin-boson model.
     α = k_mix² / (k_chi · ω_c)
     Dacă α < 1: faza coerentă (spin tunelează liber)
     Dacă α > 1: faza localizată (spin prins de baia de oscilatori)

  4. Spectrul matricei de corelație G (eigenvalue distribution)
     Câte moduri contribuie dominant la corelații?

Formula: G_ij = ħ_field/2 · Σ_a U_a^Σ(i) · U_a^Σ(j) / ω_a
         (suma peste moduri pozitive ale lui K)

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-correlations-v1"
)

N_NODES   = 280
K_INIT    = 8
K_CONN    = 8
K_CL      = 0.5
K_SM      = 0.2
K_CHI     = 0.3
K_MIX     = 0.1
HBAR_FIELD = 0.233    # condiția B (gap spectral egal): perturbativ și fizic motivat
M_EFF_SQ   = 0.014    # din G17 (pentru comparatie xi_G17)
CV_CLASS   = 0.405


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

def graph_laplacian(adj, n):
    L = np.zeros((n, n))
    for i in range(n):
        L[i, i] = float(len(adj[i]))
        for j in adj[i]: L[i, j] = -1.0
    return L

def bfs_distances(adj, n):
    """Matricea distanțelor geodezice BFS (N×N). Returnează numpy array."""
    dist = np.full((n, n), -1, dtype=np.int32)
    for src in range(n):
        dist[src, src] = 0
        q = collections.deque([src])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[src, v] < 0:
                    dist[src, v] = dist[src, u] + 1
                    q.append(v)
    return dist


# ── Q-fields ────────────────────────────────────────────────────────────────

def build_K(L, n, k_cl, k_sm, k_chi, k_mix):
    return np.block([
        [k_cl * np.eye(n) + k_sm * L,  k_mix * np.eye(n)],
        [k_mix * np.eye(n),             k_chi * np.eye(n)],
    ])

def compute_correlation_matrix(K, n, hbar):
    """
    G_ij = ħ/2 · Σ_a U_a^Σ(i) · U_a^Σ(j) / ω_a
    Returnează G (N×N), omega (2N,), eigvecs (2N, 2N).
    """
    eigvals, eigvecs = np.linalg.eigh(K)
    omega = np.where(eigvals > 0, np.sqrt(np.maximum(eigvals, 0.0)), 0.0)
    pos = omega > 1e-10
    safe_w = np.where(pos, omega, np.inf)
    weights = hbar / (2.0 * safe_w)     # (2N,)

    U_sigma = eigvecs[:n, :]             # (N, 2N)

    # G_ij = Σ_a U_sigma[i,a] * weights[a] * U_sigma[j,a]
    # = U_sigma @ diag(weights) @ U_sigma.T
    G = U_sigma @ (weights[:, np.newaxis] * U_sigma.T)   # (N, N) — se scrie si ca einsum
    return G, omega, eigvecs


# ── Corelații vs distanță ────────────────────────────────────────────────────

def bin_correlations(G, dist_matrix, n, max_r=None):
    """
    Grupează G_ij după distanța geodezică r = dist_matrix[i,j].
    Returnează: bins = {r: {"mean": ..., "std": ..., "count": ...}}
    """
    if max_r is None:
        max_r = int(dist_matrix.max())
    bins = collections.defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            r = int(dist_matrix[i, j])
            if 0 < r <= max_r:
                bins[r].append(float(G[i, j]))
    result = {}
    for r in sorted(bins.keys()):
        vals = bins[r]
        result[r] = {
            "r":     r,
            "mean":  float(np.mean(vals)),
            "std":   float(np.std(vals)),
            "count": len(vals),
        }
    return result


def fit_exponential_decay(bins):
    """
    Fit G(r) ~ A · exp(-r/ξ) prin regresia log(G) ~ log(A) - r/ξ.
    Returnează (A, xi, r2).
    """
    rs   = []
    vals = []
    for r, b in sorted(bins.items()):
        if b["mean"] > 1e-15:    # numai valori pozitive
            rs.append(r)
            vals.append(math.log(b["mean"]))
    if len(rs) < 3:
        return None, None, None

    rs_arr = np.array(rs, dtype=float)
    v_arr  = np.array(vals, dtype=float)

    # Regresie liniară: v = a0 + a1 * r
    ones  = np.ones(len(rs_arr))
    X     = np.stack([ones, rs_arr], axis=1)
    coefs, _, _, _ = np.linalg.lstsq(X, v_arr, rcond=None)
    a0, a1 = coefs

    A   = math.exp(a0)
    xi  = -1.0 / a1 if abs(a1) > 1e-12 else float("inf")

    # R² al fit-ului
    y_pred = a0 + a1 * rs_arr
    ss_res = float(np.sum((v_arr - y_pred)**2))
    ss_tot = float(np.sum((v_arr - v_arr.mean())**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return A, xi, r2


# ── Spin-boson ───────────────────────────────────────────────────────────────

def spin_boson_alpha(k_mix, k_chi, omega_c):
    """
    Parametrul de cuplaj al modelului spin-boson (la primul ordin).
    α = k_mix² / (k_chi · ω_c)
    α < 1: faza coerentă; α > 1: faza localizată (Ohmic bath)
    """
    return k_mix**2 / (k_chi * omega_c) if (k_chi * omega_c) > 0 else float("inf")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: corelații la două puncte și metrică cuantică"
    )
    ap.add_argument("--seed",       type=int,   default=3401)
    ap.add_argument("--n",          type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",     type=int,   default=K_INIT)
    ap.add_argument("--k-conn",     type=int,   default=K_CONN)
    ap.add_argument("--k-cl",       type=float, default=K_CL)
    ap.add_argument("--k-sm",       type=float, default=K_SM)
    ap.add_argument("--k-chi",      type=float, default=K_CHI)
    ap.add_argument("--k-mix",      type=float, default=K_MIX)
    ap.add_argument("--hbar-field", type=float, default=HBAR_FIELD)
    ap.add_argument("--m-eff-sq",   type=float, default=M_EFF_SQ)
    ap.add_argument("--out-dir",    type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()
    xi_G17 = 1.0 / math.sqrt(args.m_eff_sq)

    print("=" * 66)
    print("QNG Q-Fields — Corelații ⟨δΣ_i δΣ_j⟩ și metrică cuantică")
    print("=" * 66)
    print(f"  ħ_field={args.hbar_field}  (condiția B: gap spectral egal)")
    print(f"  ξ_G17 = 1/√M_EFF_SQ = 1/√{args.m_eff_sq} = {xi_G17:.4f}  (referință Yukawa)")
    print()

    # 1. Graf + Laplacian + distanțe BFS
    print("[1/4] Graf Jaccard + distanțe BFS...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    L   = graph_laplacian(adj, args.n_nodes)
    print("      Calculez distanțele geodezice (BFS, N×N)...")
    dist = bfs_distances(adj, args.n_nodes)
    diam = int(dist.max())
    d_mean = float(dist[dist > 0].mean())
    print(f"      Diametru={diam}  d_medie={d_mean:.2f}")

    # 2. Matricea de corelație G
    print("[2/4] Matricea de corelații G_ij = ⟨δΣ_i δΣ_j⟩...")
    K  = build_K(L, args.n_nodes, args.k_cl, args.k_sm, args.k_chi, args.k_mix)
    G, omega, eigvecs = compute_correlation_matrix(K, args.n_nodes, args.hbar_field)

    # Statistici G
    G_diag  = np.diag(G)   # = ⟨(δΣ_i)²⟩
    G_off   = G[np.triu_indices(args.n_nodes, k=1)]   # off-diagonal
    print(f"      G_ii (fluctuații): mean={G_diag.mean():.6f}  std={G_diag.std():.6f}")
    print(f"      G_ij (corelații):  mean={G_off.mean():.6f}  std={G_off.std():.6f}")
    print(f"      |G_ij|/G_ii (relativ): {abs(float(G_off.mean()))/float(G_diag.mean()):.4f}")

    # 3. Decădere cu distanța + fit
    print("[3/4] Binare corelații vs distanță geodezică...")
    bins = bin_correlations(G, dist, args.n_nodes, max_r=diam)
    A_fit, xi_fit, r2_fit = fit_exponential_decay(bins)

    print()
    print(f"  {'r':>4}  {'G_mean':>12}  {'G_std':>12}  {'count':>7}")
    print(f"  {'-'*4}  {'-'*12}  {'-'*12}  {'-'*7}")
    for r, b in sorted(bins.items()):
        print(f"  {r:4d}  {b['mean']:12.6f}  {b['std']:12.6f}  {b['count']:7d}")

    print()
    if A_fit is not None:
        print(f"  Fit G(r) = {A_fit:.6f} · exp(-r / {xi_fit:.4f}),  R²={r2_fit:.4f}")
    else:
        print("  Fit eșuat (prea puține valori pozitive)")

    # 4. Spectrul lui G + spin-boson
    print("[4/4] Spectrul lui G și parametrul spin-boson...")
    G_eigvals = np.linalg.eigvalsh(G)
    G_eig_top5 = G_eigvals[::-1][:5]
    G_trace = float(np.trace(G))
    G_frac_top1 = float(G_eigvals[-1]) / G_trace if G_trace > 0 else float("nan")
    G_frac_top5 = float(G_eigvals[-5:].sum()) / G_trace if G_trace > 0 else float("nan")

    # Spin-boson: ω_c = omega_min (frecvența tăiere a baii de oscilatori)
    omega_c = float(omega[omega > 1e-10].min())
    alpha_sb = spin_boson_alpha(args.k_mix, args.k_chi, omega_c)

    elapsed = time.time() - t0

    # ── Rezumat ──────────────────────────────────────────────────────────────
    print()
    print("=" * 66)
    print("REZULTATE")
    print("=" * 66)

    print(f"\n--- Lungimea de corelație ---")
    if xi_fit is not None:
        print(f"  ξ_quantum (Σ-field):  {xi_fit:.4f}  (pași de graf)")
        print(f"  ξ_G17     (Yukawa):   {xi_G17:.4f}  (1/√M_EFF_SQ)")
        ratio_xi = xi_fit / xi_G17
        print(f"  Raport ξ_q / ξ_G17:  {ratio_xi:.4f}")
        if ratio_xi < 0.5:
            print("  → Corelațiile cuantice Σ sunt MULT mai scurte decât cele G17.")
            print("    Câmpul Σ cuantic e mai 'local' decât câmpul de pe graf (Yukawa).")
        elif ratio_xi < 2.0:
            print("  → Lungimi de corelație COMPARABILE → aceeași scală de fizică.")
        else:
            print("  → Corelațiile cuantice Σ sunt mai lungi. Sistemul e mai corelat.")
    print(f"  R² fit exponențial:   {r2_fit:.4f}  "
          f"({'fit bun ✓' if r2_fit and r2_fit > 0.9 else 'fit slab'})")

    print(f"\n--- Spectrul matricei G ---")
    print(f"  Top 5 eigenvalori G:  {[round(float(v),6) for v in G_eig_top5]}")
    print(f"  Fracție din Tr(G) în λ₁:    {100*G_frac_top1:.1f}%")
    print(f"  Fracție din Tr(G) în top-5: {100*G_frac_top5:.1f}%")
    if G_frac_top1 > 0.5:
        print("  → Corelațiile dominate de UN singur mod → structură simplă.")
    elif G_frac_top5 > 0.8:
        print("  → Corelațiile dominate de câteva moduri (top-5 > 80%).")
    else:
        print("  → Corelații distribuite pe mulți mozi → fără mod dominant.")

    print(f"\n--- Spin-Boson (Σ ↔ χ cuplaj) ---")
    print(f"  ω_c (frecvența de tăiere) = ω_min(K) = {omega_c:.6f}")
    print(f"  α = k_mix² / (k_chi · ω_c) = {args.k_mix}² / ({args.k_chi} · {omega_c:.4f})")
    print(f"  α = {alpha_sb:.6f}")
    if alpha_sb < 0.1:
        print("  → α << 1: faza SUPER-COERENTĂ (spin tunelează liber, nesuprimat)")
    elif alpha_sb < 1.0:
        print("  → α < 1: faza COERENTĂ (spin tunelează liber)")
    else:
        print("  → α > 1: faza LOCALIZATĂ (spin prins de baia χ)")

    print(f"\n--- Metrică cuantică (corecție la metrica clasică) ---")
    sigma_g_cl = 0.5   # ⟨Σ⟩ clasic aproximat
    delta_metric_rel = float(G_off.mean()) / sigma_g_cl**2
    print(f"  ⟨δΣ_i δΣ_j⟩ / ⟨Σ⟩² = {delta_metric_rel:.6f}")
    print(f"  Corecție relativă la metrica clasică: {100*abs(delta_metric_rel):.4f}%")
    if abs(delta_metric_rel) < 0.01:
        print("  → Corecția cuantică la metrică e NEGLIJABILĂ (< 1%)")
    elif abs(delta_metric_rel) < 0.1:
        print("  → Corecție de ordinul %-ului — detectabilă în principiu")
    else:
        print("  → Corecție semnificativă la metrică!")

    print(f"\nTimp: {elapsed:.1f}s")

    # Salvare
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_correlations_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "params": {
            "seed": args.seed, "n_nodes": args.n_nodes,
            "k_cl": args.k_cl, "k_sm": args.k_sm,
            "k_chi": args.k_chi, "k_mix": args.k_mix,
            "hbar_field": args.hbar_field, "m_eff_sq": args.m_eff_sq,
        },
        "graph": {"diameter": diam, "d_mean": d_mean},
        "correlations": {
            "G_diag_mean":  float(G_diag.mean()),
            "G_diag_std":   float(G_diag.std()),
            "G_off_mean":   float(G_off.mean()),
            "G_off_std":    float(G_off.std()),
            "G_rel_off_diag": float(abs(G_off.mean()) / G_diag.mean()),
        },
        "decay_fit": {
            "A": A_fit, "xi_quantum": xi_fit, "r2": r2_fit,
            "xi_G17": xi_G17,
            "xi_ratio": (xi_fit / xi_G17) if xi_fit else None,
        },
        "binned": {str(r): b for r, b in bins.items()},
        "spectrum_G": {
            "top5_eigvals": [float(v) for v in G_eig_top5],
            "frac_top1":    G_frac_top1,
            "frac_top5":    G_frac_top5,
            "trace":        G_trace,
        },
        "spin_boson": {
            "omega_c": omega_c,
            "alpha":   alpha_sb,
            "phase":   ("coherent" if alpha_sb < 1.0 else "localized"),
        },
        "metric_correction": {
            "delta_metric_rel": delta_metric_rel,
            "delta_metric_pct": 100 * abs(delta_metric_rel),
        },
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
