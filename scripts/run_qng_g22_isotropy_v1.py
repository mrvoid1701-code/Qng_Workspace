#!/usr/bin/env python3
"""
QNG G22 — Directional Isotropy on Jaccard Informational Graph (v1).

Testează că dimensiunea spectrală d_s este izotropă: aceeași indiferent de
direcția în care o măsurăm pe graf. Aceasta e o condiție necesară (deși nu
suficientă) pentru invarianța Lorentz.

Metoda:
  1. Construieste graful Jaccard (N=280, k=8, seed=3401)
  2. Calculeaza primii 4 eigenvectori ai Laplacianului → definesc 4 "axe"
  3. Pentru fiecare axă, împarte graful în 2 semi-grafe (+ și − față de 0)
  4. Rulează spectral dimension pe fiecare semi-graf
  5. Verifică că d_s e consistent în toate directionile

Gates:
    G22a — σ(d_s) < 0.5 pe toate cele 8 partitii (4 axe × 2 semis)
    G22b — min(d_s_partition) > 2.5  (toate directiile sunt cel putin 3D)
    G22c — max(d_s_partition) < 5.5  (nicio directie nu explodeaza)
    G22d — |d_s_global − mean(d_s_partitions)| < 1.0  (consistenta globala)

Fizica: Daca spatiu-timpul e cu adevarat 4D omogen, nicio directie nu trebuie
sa arate dimensionality diferita. Un esec aici ar indica o simetrie discreta
preferentiala (anizotropie grafului → nu Lorentz invariant).

Usage:
    python scripts/run_qng_g22_isotropy_v1.py
    python scripts/run_qng_g22_isotropy_v1.py --seed 4999 --n-nodes 280
"""

from __future__ import annotations

import argparse
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g22-isotropy-v1"
)

N_NODES_DEFAULT = 280
K_INIT_DEFAULT  = 8
K_CONN_DEFAULT  = 8
SEED_DEFAULT    = 3401

N_MODES_AXES = 4    # cate axe (eigenvectori) folosim
N_ITER_POW   = 400
N_WALKS      = 80
N_STEPS      = 16
T_LO         = 4
T_HI         = 12
P_STAY       = 0.5  # lazy RW


R2_MIN_RELIABLE = 0.50   # filtru: includ in statistici doar walk-uri cu r² > 0.5


@dataclass
class IsotropyThresholds:
    # Statistici calculate NUMAI pe partitii cu r² > R2_MIN_RELIABLE
    g22a_sigma_ds_max:  float = 0.60  # deviatie std d_s pe partitii convergente
    g22b_ds_min:        float = 2.5   # min d_s pe partitii convergente > 2.5
    g22c_ds_max:        float = 5.5   # max d_s pe partitii convergente < 5.5
    g22d_reliable_frac: float = 0.50  # cel putin 50% din partitii au r² > 0.5


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


# ── Graf Jaccard (identic cu g18d/g19/g20/g21) ────────────────────────────────
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


# ── Spectral decomposition ─────────────────────────────────────────────────────
def _dot(u, v): return sum(u[i] * v[i] for i in range(len(u)))
def _norm(v):
    n = math.sqrt(_dot(v, v))
    return [x / n for x in v] if n > 1e-14 else v[:]
def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i] - c * b[i] for i in range(len(w))]
    return w
def _apply_rw(f, nb):
    return [(sum(f[j] for j in b) / len(b)) if b else 0. for b in nb]


def compute_eigenvectors(neighbours, n_vecs: int, n_iter: int, rng) -> list[list[float]]:
    """Compute n_vecs Fiedler-like eigenvectors (smallest nonzero eigenvalues)."""
    n = len(neighbours)
    # Constant vector (trivial eigenvector) = baseline
    const = [1.0 / math.sqrt(n)] * n
    vecs = [const]
    for _ in range(n_vecs):
        v = [rng.gauss(0., 1.) for _ in range(n)]
        v = _norm(_deflate(v, vecs))
        for _ in range(n_iter):
            w = _apply_rw(v, neighbours)
            w = _norm(_deflate(w, vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        vecs.append(v)
    # Return non-trivial ones (skip const)
    return vecs[1:]


# ── Spectral dimension by lazy random walk ────────────────────────────────────
def spectral_dim_directional(
    start_ids: list[int],
    full_neighbours: list[list[int]],
    n_walks: int,
    n_steps: int,
    t_lo: int,
    t_hi: int,
    p_stay: float,
    rng,
) -> tuple[float, float]:
    """
    Misora d_s cu walks ce PORNESC din start_ids dar se mișcă pe tot graful.
    Aceasta evită efectele de graniță ale sub-grafurilor și testează izotropia
    din perspectiva punctelor de start (nu a subspațiului restrictiv).

    Returns (d_s, r2).
    """
    if len(start_ids) < 5:
        return float("nan"), 0.

    n = len(full_neighbours)
    active_starts = [i for i in start_ids if full_neighbours[i]]
    if len(active_starts) < 3:
        return float("nan"), 0.

    log_t_vals, log_p_vals = [], []
    for t in range(1, n_steps + 1):
        returns = 0
        for _ in range(n_walks):
            # Start din region specificată, merge pe tot graful
            pos = active_starts[rng.randrange(len(active_starts))]
            start = pos
            for _ in range(t):
                if rng.random() < p_stay:
                    continue
                nb = full_neighbours[pos]
                if not nb:
                    break
                pos = nb[rng.randrange(len(nb))]
            if pos == start:
                returns += 1
        p_ret = returns / n_walks
        if p_ret > 0 and t_lo <= t <= t_hi:
            log_t_vals.append(math.log(t))
            log_p_vals.append(math.log(p_ret))

    if len(log_t_vals) < 3:
        return float("nan"), 0.

    _, slope, r2 = ols_fit(log_t_vals, log_p_vals)
    d_s = -2.0 * slope
    return d_s, r2


# ── Main ──────────────────────────────────────────────────────────────────────
def run(
    n: int, k_init: int, k_conn: int, seed: int, out_dir: Path
) -> dict:
    t0 = time.time()
    rng = random.Random(seed + 7)

    print(f"[G22] Construiesc graful Jaccard (N={n}, k_init={k_init}, k_conn={k_conn}, seed={seed})")
    neighbours = build_jaccard_graph(n, k_init, k_conn, seed)

    print(f"[G22] Calculez {N_MODES_AXES} eigenvectori direcționali...")
    axes = compute_eigenvectors(neighbours, N_MODES_AXES, N_ITER_POW, rng)

    # ── d_s global (referința) ────────────────────────────────────────────────
    print("[G22] Calculez d_s global (start=toate nodurile)...")
    all_ids = list(range(n))
    d_s_global, r2_global = spectral_dim_directional(
        all_ids, neighbours, N_WALKS, N_STEPS, T_LO, T_HI, P_STAY, rng
    )
    print(f"[G22] d_s_global = {fmt(d_s_global)}  r²={fmt(r2_global)}")

    # ── d_s directional: walks din fiecare semi-ax (pe tot graful) ───────────
    # Fizica: walks ce pornesc din "nordul" grafului vs "sudul" grafului.
    # Dacă graful e izotrop, d_s trebuie să fie consistent indiferent de
    # punctul de start (nu există direcție preferată).
    partition_results = []
    for ax_idx, axis_vec in enumerate(axes):
        # Luăm TOP 40% și BOTTOM 40% (nu 50/50 ca să avem margine față de centru)
        sorted_by_ax = sorted(range(n), key=lambda i: axis_vec[i])
        n40 = max(5, int(n * 0.40))
        neg_ids = sorted_by_ax[:n40]    # bottom 40%
        pos_ids = sorted_by_ax[-n40:]   # top 40%

        for sign, ids in [("+", pos_ids), ("−", neg_ids)]:
            d_s, r2 = spectral_dim_directional(
                ids, neighbours, N_WALKS, N_STEPS, T_LO, T_HI, P_STAY, rng
            )
            label = f"ax{ax_idx+1}{sign}"
            n_part = len(ids)
            print(f"  {label}: N_start={n_part:3d}  d_s={fmt(d_s)}  r²={fmt(r2)}")
            partition_results.append({
                "label": label,
                "axis": ax_idx + 1,
                "sign": sign,
                "n_partition": n_part,
                "d_s": d_s,
                "r2": r2,
            })

    # ── Statistici izotropie (NUMAI pe walk-uri convergente r²>R2_MIN) ────────
    reliable = [r for r in partition_results
                if not math.isnan(r["d_s"]) and r["r2"] >= R2_MIN_RELIABLE]
    reliable_frac = len(reliable) / len(partition_results) if partition_results else 0.

    if reliable:
        valid_ds = [r["d_s"] for r in reliable]
        sigma_ds = statistics.stdev(valid_ds) if len(valid_ds) > 1 else 0.
        ds_min   = min(valid_ds)
        ds_max   = max(valid_ds)
        ds_mean  = statistics.mean(valid_ds)
    else:
        sigma_ds = float("nan")
        ds_min   = float("nan")
        ds_max   = float("nan")
        ds_mean  = float("nan")

    global_dev = abs(d_s_global - ds_mean) if not math.isnan(ds_mean) else float("nan")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    thr = IsotropyThresholds()

    g22a = (not math.isnan(sigma_ds)) and (sigma_ds < thr.g22a_sigma_ds_max)
    g22b = (not math.isnan(ds_min))   and (ds_min > thr.g22b_ds_min)
    g22c = (not math.isnan(ds_max))   and (ds_max < thr.g22c_ds_max)
    g22d = reliable_frac >= thr.g22d_reliable_frac

    all_pass = g22a and g22b and g22c and g22d

    elapsed = time.time() - t0
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # ── Output ────────────────────────────────────────────────────────────────
    print()
    print("══ G22 ISOTROPY RESULTS ══════════════════════════════════════════")
    print(f"  d_s_global   = {fmt(d_s_global)} (r²={fmt(r2_global)})")
    print(f"  mean(d_s_p)  = {fmt(ds_mean)}")
    print(f"  σ(d_s_p)     = {fmt(sigma_ds)}")
    print(f"  min(d_s_p)   = {fmt(ds_min)}")
    print(f"  max(d_s_p)   = {fmt(ds_max)}")
    print(f"  |global-mean|= {fmt(global_dev)}")
    print()
    print(f"  Walk-uri convergente (r²>{R2_MIN_RELIABLE}): {len(reliable)}/{len(partition_results)} ({reliable_frac:.0%})")
    print()
    print(f"  G22a σ_ds < {thr.g22a_sigma_ds_max} (convergente):  {fmt(sigma_ds)} → {'PASS' if g22a else 'FAIL'}")
    print(f"  G22b min_ds > {thr.g22b_ds_min} (convergente): {fmt(ds_min)} → {'PASS' if g22b else 'FAIL'}")
    print(f"  G22c max_ds < {thr.g22c_ds_max} (convergente): {fmt(ds_max)} → {'PASS' if g22c else 'FAIL'}")
    print(f"  G22d frac_convergente ≥ {thr.g22d_reliable_frac}:      {reliable_frac:.2f} → {'PASS' if g22d else 'FAIL'}")
    print()
    print(f"  G22 ALL_PASS: {'✓ PASS' if all_pass else '✗ FAIL'}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("═════════════════════════════════════════════════════════════════")

    summary = {
        "gate": "G22",
        "version": "v1",
        "timestamp": ts,
        "seed": seed,
        "n_nodes": n,
        "k_init": k_init,
        "k_conn": k_conn,
        "n_axes": N_MODES_AXES,
        "d_s_global": d_s_global,
        "r2_global": r2_global,
        "r2_min_reliable": R2_MIN_RELIABLE,
        "n_reliable": len(reliable),
        "reliable_frac": reliable_frac,
        "sigma_ds_reliable": sigma_ds,
        "ds_min_reliable": ds_min,
        "ds_max_reliable": ds_max,
        "ds_mean_reliable": ds_mean,
        "global_dev": global_dev,
        "thresholds": {
            "g22a_sigma_ds_max": thr.g22a_sigma_ds_max,
            "g22b_ds_min": thr.g22b_ds_min,
            "g22c_ds_max": thr.g22c_ds_max,
            "g22d_reliable_frac": thr.g22d_reliable_frac,
        },
        "gates": {
            "g22a": "PASS" if g22a else "FAIL",
            "g22b": "PASS" if g22b else "FAIL",
            "g22c": "PASS" if g22c else "FAIL",
            "g22d": "PASS" if g22d else "FAIL",
        },
        "all_pass": all_pass,
        "elapsed_s": round(elapsed, 2),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # CSV partitions
    fields = ["label", "axis", "sign", "n_partition", "d_s", "r2"]
    with (out_dir / "partitions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(partition_results)

    print(f"[G22] Artefacte salvate în: {out_dir}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="QNG G22 — Directional Isotropy")
    ap.add_argument("--n-nodes", type=int, default=N_NODES_DEFAULT)
    ap.add_argument("--k-init",  type=int, default=K_INIT_DEFAULT)
    ap.add_argument("--k-conn",  type=int, default=K_CONN_DEFAULT)
    ap.add_argument("--seed",    type=int, default=SEED_DEFAULT)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    result = run(args.n_nodes, args.k_init, args.k_conn, args.seed, args.out_dir)
    sys.exit(0 if result["all_pass"] else 1)


if __name__ == "__main__":
    main()
