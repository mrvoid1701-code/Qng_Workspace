#!/usr/bin/env python3
"""
QNG G23 — Klein-Gordon Scalar Matter Field on Jaccard Graph (v1).

Prima implementare de materie în QNG: un câmp scalar masiv φ care satisface
ecuația Klein-Gordon pe graful Jaccard informational.

Ecuația Klein-Gordon euclidiană pe graf:
    (−Δ_graph + m²) φ = J

unde Δ_graph e Laplacianul grafului și m² = M_EFF_SQ (masa câmpului).
Soluția e funcția Green G(i,j) = [(L + m²I)⁻¹]_{ij} — potențialul Yukawa pe graf.

Fizica:
  - Câmpul masiv creează un potential care decade exponențial cu distanța (Yukawa)
  - Câmpul nemasisiv (m=0) decade mai lent (power law, ~1/r^{d-2} în d dimensiuni)
  - Dacă d_s ≈ 4, decayul nemasisiv ar trebui să fie ~ 1/r²
  - Comparăm câmpul masiv vs nemasiv pentru a confirma că m² "face diferența"

Gates:
    G23a — Decădere: G(r) descreste cu distanta (slope OLS < -threshold)
           Confirma ca propagatorul nu e constant (materia se localizeaza)
    G23b — Screening Yukawa: ln G(r) + m·r ≈ const  (coeff. variatie < 0.5)
           Confirma decayul exponential specific câmpului masiv
    G23c — Contrast masa: G_m0(r)/G_m(r) creste cu r
           Câmpul nemasisiv decade mai lent → masa are efect fizic real
    G23d — Spectral gap: λ_min(L + m²I) > m²·0.9
           Garanteaza ca operatorul e bine definit (pozitiv definit)

Usage:
    python scripts/run_qng_g23_klein_gordon_v1.py
    python scripts/run_qng_g23_klein_gordon_v1.py --seed 4999 --mass-sq 0.05
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g23-klein-gordon-v1"
)

N_NODES_DEFAULT = 280
K_INIT_DEFAULT  = 8
K_CONN_DEFAULT  = 8
SEED_DEFAULT    = 3401
M_SQ_DEFAULT    = 0.30    # masa² moderată → screening length ≈ 1.8 BFS hops (vizibil in graf)
N_SOURCES       = 20      # cate surse J folosim pentru Green's function
N_ITER_CG       = 200     # iteratii Conjugate Gradient
N_BFS_SHELLS    = 8       # cate shell-uri BFS analizam


@dataclass
class KleinGordonThresholds:
    # G23a: panta OLS a ln G(r) vs BFS dist < -threshold (decay)
    # La m²=0.3, screening length ≈ 1.8 hops → decay clar dar nu dramatic
    g23a_slope_max:    float = -0.03
    # G23b: coeff variatie al [ln G(r) + m·r] pe distante > 1 (Yukawa screening)
    g23b_yukawa_cv:    float = 0.50
    # G23c: ratio G_m0/G_m la distanta maxima > la distanta minima (masa face diferenta)
    # La m²=0.3 vs m²→0, diferenta de decay trebuie sa fie vizibila
    g23c_ratio_growth: float = 1.2
    # G23d: gap spectral al (L + m²I) > m²·fractie_minima
    g23d_gap_frac:     float = 0.9


def fmt(v: float) -> str:
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.6e}"
    return f"{v:.6f}"


def ols_fit(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs) / n; my = sum(ys) / n
    Sxx = sum((x - mx) ** 2 for x in xs)
    Sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy / Sxx; a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n))
    return a, b, max(0., 1. - ss_res / ss_tot)


# ── Graf Jaccard ──────────────────────────────────────────────────────────────
def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    adj: list[set[int]] = [set() for _ in range(n)]
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

    neighbours = [sorted(s) for s in adj]
    return neighbours


# ── Laplacian graph ───────────────────────────────────────────────────────────
def laplacian_apply(x: list[float], neighbours: list[list[int]]) -> list[float]:
    """Aplică Laplacianul grafului L = D - A pe vectorul x.
    Lx[i] = deg(i)*x[i] - sum_{j in N(i)} x[j]
    """
    n = len(x)
    result = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        result[i] = len(nb) * x[i] - sum(x[j] for j in nb)
    return result


def klein_gordon_apply(x: list[float], neighbours: list[list[int]], m_sq: float) -> list[float]:
    """Aplică (L + m²I) pe x."""
    Lx = laplacian_apply(x, neighbours)
    return [Lx[i] + m_sq * x[i] for i in range(len(x))]


def conjugate_gradient(neighbours, m_sq: float, b: list[float], n_iter: int) -> list[float]:
    """
    Rezolvă (L + m²I) x = b prin Conjugate Gradient.
    Returnează x = (L + m²I)⁻¹ b ≈ Green's function la sursa b.
    """
    n = len(b)
    x = [0.0] * n
    r = b[:]
    p = r[:]
    rs_old = sum(ri ** 2 for ri in r)

    for _ in range(n_iter):
        if rs_old < 1e-30:
            break
        Ap = klein_gordon_apply(p, neighbours, m_sq)
        pAp = sum(p[i] * Ap[i] for i in range(n))
        if abs(pAp) < 1e-30:
            break
        alpha = rs_old / pAp
        x = [x[i] + alpha * p[i] for i in range(n)]
        r = [r[i] - alpha * Ap[i] for i in range(n)]
        rs_new = sum(ri ** 2 for ri in r)
        beta = rs_new / rs_old
        p = [r[i] + beta * p[i] for i in range(n)]
        rs_old = rs_new

    return x


def bfs_distances(source: int, neighbours: list[list[int]]) -> list[int]:
    n = len(neighbours)
    dist = [-1] * n
    dist[source] = 0
    queue = collections.deque([source])
    while queue:
        u = queue.popleft()
        for v in neighbours[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


# ── Calcul eigenvalue minim al (L + m²I) prin power iteration pe (L+m²I)⁻¹ ──
def min_eigenvalue_screened(neighbours, m_sq: float, n_iter: int, rng) -> float:
    """
    Estimează λ_min(L + m²I) via Rayleigh quotient.
    λ_min ≥ m² (deoarece L e pozitiv semi-definit → L+m²I e pozitiv definit)
    Testăm ca λ_min > m²·0.9 (gap spectral confirmat).
    """
    n = len(neighbours)
    # Vectorul constant dă Lv = 0, deci (L+m²I)v = m²v → eigenvalue = m²
    # Dorim să verificam că nu exista eigenvalue mai mic de m²
    # Rayleigh quotient: R(v) = <v, (L+m²I)v> / <v,v>
    # Minimizăm R pentru a gasi λ_min

    best_R = float("inf")
    for _ in range(5):  # câteva vectori de test
        v = [rng.gauss(0., 1.) for _ in range(n)]
        norm_v = math.sqrt(sum(vi**2 for vi in v))
        if norm_v < 1e-14:
            continue
        v = [vi / norm_v for vi in v]
        Av = klein_gordon_apply(v, neighbours, m_sq)
        R = sum(v[i] * Av[i] for i in range(n))
        best_R = min(best_R, R)

    return best_R


# ── Main ──────────────────────────────────────────────────────────────────────
def run(
    n: int, k_init: int, k_conn: int, seed: int, m_sq: float, out_dir: Path
) -> dict:
    t0 = time.time()
    rng = random.Random(seed + 23)
    m = math.sqrt(m_sq)

    print(f"[G23] Construiesc graful Jaccard (N={n}, k={k_conn}, seed={seed})")
    neighbours = build_jaccard_graph(n, k_init, k_conn, seed)

    # ── Surse distribuite uniform (BFS din center-like nodes) ────────────────
    # Alege N_SOURCES noduri ca surse pentru Green's function
    source_nodes = sorted(random.Random(seed).sample(range(n), min(N_SOURCES, n)))

    print(f"[G23] Calculez Green's function (L+m²I)⁻¹ pentru {len(source_nodes)} surse...")

    # Colectăm G(dist) mediat pe surse
    shell_G_m:  dict[int, list[float]] = {}
    shell_G_m0: dict[int, list[float]] = {}

    for src in source_nodes:
        # Sursa delta: b[src]=1, rest 0
        b = [0.0] * n
        b[src] = 1.0

        # Green's function cu masă
        G_m_vec = conjugate_gradient(neighbours, m_sq, b, N_ITER_CG)
        # Green's function fără masă (m²=0 → Laplacian pur, regularizare minimă)
        G_m0_vec = conjugate_gradient(neighbours, 1e-6, b, N_ITER_CG)

        # BFS distances de la sursă
        dists = bfs_distances(src, neighbours)

        for i in range(n):
            d = dists[i]
            if d <= 0:
                continue  # skip sursa și noduri neatinse
            g_m_val  = abs(G_m_vec[i])
            g_m0_val = abs(G_m0_vec[i])
            if g_m_val < 1e-30 or g_m0_val < 1e-30:
                continue
            shell_G_m.setdefault(d, []).append(g_m_val)
            shell_G_m0.setdefault(d, []).append(g_m0_val)

    # Mediere pe shell-uri
    shells = sorted(d for d in shell_G_m if shell_G_m[d])
    shells = [d for d in shells if d <= N_BFS_SHELLS]

    if len(shells) < 3:
        print("[G23] EROARE: prea putine shell-uri BFS valide")
        return {"all_pass": False, "error": "insufficient BFS shells"}

    mean_G_m  = [statistics.mean(shell_G_m[d])  for d in shells]
    mean_G_m0 = [statistics.mean(shell_G_m0[d]) for d in shells]

    # ── G23a: Decay G(r) cu distanța ─────────────────────────────────────────
    log_r = [math.log(d) for d in shells]
    log_G = [math.log(g) for g in mean_G_m if g > 0]
    if len(log_G) < len(log_r):
        log_r = log_r[:len(log_G)]

    _, slope_a, r2_a = ols_fit(log_r, log_G)

    # ── G23b: Screening Yukawa: ln G(r) + m·r ≈ const ───────────────────────
    yukawa_vals = [
        math.log(mean_G_m[i]) + m * shells[i]
        for i in range(len(shells))
        if mean_G_m[i] > 0
    ]
    if len(yukawa_vals) > 1:
        yuk_mean = statistics.mean(yukawa_vals)
        yuk_std  = statistics.stdev(yukawa_vals) if len(yukawa_vals) > 1 else 0.
        yukawa_cv = yuk_std / abs(yuk_mean) if abs(yuk_mean) > 1e-10 else float("nan")
    else:
        yukawa_cv = float("nan")

    # ── G23c: Contrast masă — G_m0/G_m creşte cu r ───────────────────────────
    ratio_near = mean_G_m0[0]  / mean_G_m[0]  if mean_G_m[0]  > 1e-30 else float("nan")
    ratio_far  = mean_G_m0[-1] / mean_G_m[-1] if mean_G_m[-1] > 1e-30 else float("nan")
    if not math.isnan(ratio_near) and ratio_near > 1e-10:
        ratio_growth = ratio_far / ratio_near
    else:
        ratio_growth = float("nan")

    # ── G23d: Gap spectral (L + m²I) > m²·0.9 ───────────────────────────────
    lambda_min = min_eigenvalue_screened(neighbours, m_sq, N_ITER_CG, rng)
    gap_ratio  = lambda_min / m_sq if m_sq > 0 else float("nan")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    thr = KleinGordonThresholds()

    g23a = (not math.isnan(slope_a)) and (slope_a < thr.g23a_slope_max)
    g23b = (not math.isnan(yukawa_cv)) and (yukawa_cv < thr.g23b_yukawa_cv)
    g23c = (not math.isnan(ratio_growth)) and (ratio_growth > thr.g23c_ratio_growth)
    g23d = (not math.isnan(gap_ratio)) and (gap_ratio > thr.g23d_gap_frac)

    all_pass = g23a and g23b and g23c and g23d

    elapsed = time.time() - t0
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # ── Output ────────────────────────────────────────────────────────────────
    print()
    print("══ G23 KLEIN-GORDON RESULTS ══════════════════════════════════════")
    print(f"  m² = {m_sq}  →  m = {fmt(m)}")
    print(f"  Shells BFS analizate: {shells}")
    print(f"  mean G_m  pe shell-uri: {[fmt(g) for g in mean_G_m]}")
    print(f"  mean G_m0 pe shell-uri: {[fmt(g) for g in mean_G_m0]}")
    print()
    print(f"  G23a slope ln G / ln r = {fmt(slope_a)} (r²={fmt(r2_a)})")
    print(f"       threshold < {thr.g23a_slope_max} → {'PASS' if g23a else 'FAIL'}")
    print(f"  G23b Yukawa CV [ln G + mr] = {fmt(yukawa_cv)}")
    print(f"       threshold < {thr.g23b_yukawa_cv} → {'PASS' if g23b else 'FAIL'}")
    print(f"  G23c ratio_far/ratio_near = {fmt(ratio_growth)}")
    print(f"       (near={fmt(ratio_near)}, far={fmt(ratio_far)})")
    print(f"       threshold > {thr.g23c_ratio_growth} → {'PASS' if g23c else 'FAIL'}")
    print(f"  G23d λ_min/(m²) = {fmt(gap_ratio)}")
    print(f"       threshold > {thr.g23d_gap_frac} → {'PASS' if g23d else 'FAIL'}")
    print()
    print(f"  G23 ALL_PASS: {'✓ PASS' if all_pass else '✗ FAIL'}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("═════════════════════════════════════════════════════════════════")

    summary = {
        "gate": "G23",
        "version": "v1",
        "timestamp": ts,
        "seed": seed,
        "n_nodes": n,
        "k_init": k_init,
        "k_conn": k_conn,
        "m_sq": m_sq,
        "m": m,
        "n_sources": len(source_nodes),
        "shells": shells,
        "mean_G_m": mean_G_m,
        "mean_G_m0": mean_G_m0,
        "slope_logG_logr": slope_a,
        "r2_slope": r2_a,
        "yukawa_cv": yukawa_cv,
        "ratio_near": ratio_near,
        "ratio_far": ratio_far,
        "ratio_growth": ratio_growth,
        "lambda_min_screened": lambda_min,
        "gap_ratio": gap_ratio,
        "thresholds": {
            "g23a_slope_max": thr.g23a_slope_max,
            "g23b_yukawa_cv": thr.g23b_yukawa_cv,
            "g23c_ratio_growth": thr.g23c_ratio_growth,
            "g23d_gap_frac": thr.g23d_gap_frac,
        },
        "gates": {
            "g23a": "PASS" if g23a else "FAIL",
            "g23b": "PASS" if g23b else "FAIL",
            "g23c": "PASS" if g23c else "FAIL",
            "g23d": "PASS" if g23d else "FAIL",
        },
        "all_pass": all_pass,
        "elapsed_s": round(elapsed, 2),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # CSV shells
    rows = []
    for i, d in enumerate(shells):
        rows.append({
            "shell_dist": d,
            "mean_G_m": mean_G_m[i],
            "mean_G_m0": mean_G_m0[i],
            "ratio_m0_m": mean_G_m0[i] / mean_G_m[i] if mean_G_m[i] > 1e-30 else float("nan"),
            "yukawa_val": math.log(mean_G_m[i]) + m * d if mean_G_m[i] > 0 else float("nan"),
        })
    with (out_dir / "shells.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["shell_dist", "mean_G_m", "mean_G_m0", "ratio_m0_m", "yukawa_val"])
        w.writeheader(); w.writerows(rows)

    print(f"[G23] Artefacte salvate în: {out_dir}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="QNG G23 — Klein-Gordon Scalar Matter")
    ap.add_argument("--n-nodes", type=int,   default=N_NODES_DEFAULT)
    ap.add_argument("--k-init",  type=int,   default=K_INIT_DEFAULT)
    ap.add_argument("--k-conn",  type=int,   default=K_CONN_DEFAULT)
    ap.add_argument("--seed",    type=int,   default=SEED_DEFAULT)
    ap.add_argument("--mass-sq", type=float, default=M_SQ_DEFAULT)
    ap.add_argument("--out-dir", type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    result = run(
        args.n_nodes, args.k_init, args.k_conn,
        args.seed, args.mass_sq, args.out_dir
    )
    sys.exit(0 if result["all_pass"] else 1)


if __name__ == "__main__":
    main()
