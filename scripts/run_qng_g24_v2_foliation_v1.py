#!/usr/bin/env python3
"""
QNG G24 v2 — Spectral Foliation: Temporal Gradient Test (v1).

Problema cu G24 v1 și prima tentativă v2:
  Graful Jaccard e small-world → sub-grafurile induse pe noduri ecuatoriale
  pierd conectivitate rapid → d_s artificial mic.

Abordare corectă: walks pe GRAFUL COMPLET, dar pornind din quintile
temporale diferite (5 benzi Fiedler). Testează dacă "poziția temporală"
a nodurilor de start afectează d_s observat.

Ipoteza 3+1:
  Dacă spațiu-timpul e 3+1, atunci nodurile din centrul temporal (ecuator
  Fiedler) ar trebui să "vadă" mai multă geometrie spațială la scale mici
  → d_s_UV ≈ 3 din echivalent "slicuri temporale pure"

  Dacă spațiu-timpul e 4D euclidian fără structură temporală, d_s_UV
  ar trebui să fie consistent între toate quintilele (~4 oriunde).

Gates:
    G24v2a — λ₂ > 1e-5 (Fiedler direction bine definit)
    G24v2b — max(d_s_quintile) - min(d_s_quintile) > 0.15  (variație temporală)
    G24v2c — d_s_equatorial ∈ (2.5, 4.5) (echivalent walk stabil)
    G24v2d — Pearson(|Fiedler_rank - median|, d_s) semnificativ (corelație temporalitate-dimensionalitate)

Fizica: Orice asimetrie d_s între quintilele temporale e evidență că
direcția Fiedler nu e echivalentă cu direcțiile spațiale — structura 3+1.

Usage:
    python scripts/run_qng_g24_v2_foliation_v1.py
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g24v2-foliation-v1"
)

N_NODES_DEFAULT  = 280
K_INIT_DEFAULT   = 8
K_CONN_DEFAULT   = 8
SEED_DEFAULT     = 3401

N_ITER_POW       = 500
N_WALKS          = 100
N_STEPS          = 16
T_LO             = 3
T_HI             = 11
P_STAY           = 0.5
N_QUINTILES      = 5


@dataclass
class FoliationV2Thresholds:
    g24v2a_lambda2_min:  float = 1e-5   # Fiedler value > 0
    g24v2b_range_min:    float = 0.15   # max-min d_s pe quintile > 0.15
    g24v2c_ds_lo:        float = 2.5    # d_s echatorial ∈ (2.5, 4.5)
    g24v2c_ds_hi:        float = 4.5
    g24v2d_pearson_abs:  float = 0.30   # |Pearson(dist_temporal, d_s)| > 0.3


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


def pearson(xs, ys):
    n = len(xs)
    if n < 3: return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx < 1e-14 or sy < 1e-14: return float("nan")
    return num / (sx * sy)


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
    return [sorted(s) for s in adj]


# ── Fiedler vector ────────────────────────────────────────────────────────────
def _dot(u, v): return sum(u[i] * v[i] for i in range(len(u)))
def _norm(v):
    s = math.sqrt(_dot(v, v))
    return [x / s for x in v] if s > 1e-14 else v[:]
def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i] - c * b[i] for i in range(len(w))]
    return w
def _apply_rw(f, nb):
    return [(sum(f[j] for j in b) / len(b)) if b else 0. for b in nb]


def compute_fiedler(neighbours, n_iter, rng):
    n = len(neighbours)
    const = [1.0 / math.sqrt(n)] * n
    v = _norm(_deflate([rng.gauss(0., 1.) for _ in range(n)], [const]))
    mu_prev = 0.
    for it in range(n_iter):
        w = _apply_rw(v, neighbours)
        w = _norm(_deflate(w, [const]))
        if math.sqrt(_dot(w, w)) < 1e-14: break
        mu_new = _dot(v, _apply_rw(v, neighbours))
        if it > 50 and abs(mu_new - mu_prev) < 1e-9: break
        mu_prev = mu_new; v = w
    Av = _apply_rw(v, neighbours)
    mu1 = _dot(v, Av)
    return 1.0 - mu1, v


# ── d_s directional (walks pe tot graful, start din subset) ──────────────────
def spectral_dim_from_starts(
    start_ids, full_nb, n_walks, n_steps, t_lo, t_hi, p_stay, rng
) -> tuple[float, float]:
    active = [i for i in start_ids if full_nb[i]]
    if len(active) < 5:
        return float("nan"), 0.

    log_t_vals, log_p_vals = [], []
    for t in range(1, n_steps + 1):
        returns = 0
        for _ in range(n_walks):
            pos = active[rng.randrange(len(active))]
            start = pos
            for _ in range(t):
                if rng.random() < p_stay:
                    continue
                nb = full_nb[pos]
                if not nb: break
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
    return -2.0 * slope, r2


# ── Main ──────────────────────────────────────────────────────────────────────
def run(n: int, k_init: int, k_conn: int, seed: int, out_dir: Path) -> dict:
    t0 = time.time()
    rng = random.Random(seed + 242)

    print(f"[G24v2] Construiesc graful Jaccard (N={n}, k={k_conn}, seed={seed})")
    neighbours = build_jaccard_graph(n, k_init, k_conn, seed)

    print(f"[G24v2] Calculez vectorul Fiedler...")
    lambda2, fiedler = compute_fiedler(neighbours, N_ITER_POW, rng)
    print(f"[G24v2] λ₂ = {fmt(lambda2)}")

    # ── d_s global ────────────────────────────────────────────────────────────
    d_s_full, r2_full = spectral_dim_from_starts(
        list(range(n)), neighbours, N_WALKS, N_STEPS, T_LO, T_HI, P_STAY, rng
    )
    print(f"[G24v2] d_s_full = {fmt(d_s_full)}  r²={fmt(r2_full)}")

    # ── Quintile Fiedler ──────────────────────────────────────────────────────
    sorted_by_f = sorted(range(n), key=lambda i: fiedler[i])
    q_size = n // N_QUINTILES

    quintile_results = []
    print(f"\n[G24v2] d_s per quintilă Fiedler (walks pe tot graful):")
    for qi in range(N_QUINTILES):
        lo = qi * q_size
        hi = (qi + 1) * q_size if qi < N_QUINTILES - 1 else n
        q_ids = sorted_by_f[lo:hi]
        f_lo  = fiedler[q_ids[0]]
        f_hi  = fiedler[q_ids[-1]]
        f_med = fiedler[q_ids[len(q_ids) // 2]]

        d_s, r2 = spectral_dim_from_starts(
            q_ids, neighbours, N_WALKS, N_STEPS, T_LO, T_HI, P_STAY, rng
        )
        label = "pol−" if qi == 0 else ("pol+" if qi == N_QUINTILES - 1 else f"Q{qi+1}")
        print(f"  {label} (f∈[{fmt(f_lo)},{fmt(f_hi)}]): d_s={fmt(d_s)}  r²={fmt(r2)}")

        quintile_results.append({
            "quintile": qi,
            "label": label,
            "f_lo": f_lo,
            "f_hi": f_hi,
            "f_med": f_med,
            "n_nodes": len(q_ids),
            "d_s": d_s,
            "r2": r2,
        })

    # ── Analiza gradientului temporal ─────────────────────────────────────────
    # "Distanța temporală de la ecuator" = |f_med| (0=ecuator, max=pol)
    valid_q = [q for q in quintile_results if not math.isnan(q["d_s"]) and q["r2"] > 0.3]
    ds_values = [q["d_s"] for q in valid_q]
    temporal_dist = [abs(q["f_med"]) for q in valid_q]

    pearson_r = pearson(temporal_dist, ds_values) if len(valid_q) >= 3 else float("nan")

    # Quintila echatorială = mijlocul (Q3 din 5)
    equatorial_q = quintile_results[N_QUINTILES // 2]
    ds_equatorial = equatorial_q["d_s"]

    ds_valid_all = [q["d_s"] for q in quintile_results if not math.isnan(q["d_s"])]
    ds_range = (max(ds_valid_all) - min(ds_valid_all)) if len(ds_valid_all) >= 2 else float("nan")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    thr = FoliationV2Thresholds()

    g24v2a = lambda2 > thr.g24v2a_lambda2_min
    g24v2b = (not math.isnan(ds_range)) and (ds_range > thr.g24v2b_range_min)
    g24v2c = (not math.isnan(ds_equatorial)) and \
             (thr.g24v2c_ds_lo < ds_equatorial < thr.g24v2c_ds_hi)
    g24v2d = (not math.isnan(pearson_r)) and (abs(pearson_r) > thr.g24v2d_pearson_abs)

    all_pass = g24v2a and g24v2b and g24v2c and g24v2d

    elapsed = time.time() - t0
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # ── Output ────────────────────────────────────────────────────────────────
    print()
    print("══ G24v2 TEMPORAL GRADIENT RESULTS ══════════════════════════════")
    print(f"  λ₂              = {fmt(lambda2)}")
    print(f"  d_s_full        = {fmt(d_s_full)}")
    print(f"  d_s_equatorial  = {fmt(ds_equatorial)}")
    print(f"  Range quintile  = {fmt(ds_range)}")
    print(f"  Pearson(|f|,d_s)= {fmt(pearson_r)}")
    print(f"  (pos = mai temporal → mai mare d_s = 4D-like; structura 3+1 daca neg)")
    print()
    print(f"  G24v2a λ₂ > {thr.g24v2a_lambda2_min}:           {fmt(lambda2)} → {'PASS' if g24v2a else 'FAIL'}")
    print(f"  G24v2b range > {thr.g24v2b_range_min}:          {fmt(ds_range)} → {'PASS' if g24v2b else 'FAIL'}")
    print(f"  G24v2c d_s_eq ∈ ({thr.g24v2c_ds_lo},{thr.g24v2c_ds_hi}): {fmt(ds_equatorial)} → {'PASS' if g24v2c else 'FAIL'}")
    print(f"  G24v2d |Pearson| > {thr.g24v2d_pearson_abs}:    {fmt(abs(pearson_r) if not math.isnan(pearson_r) else float('nan'))} → {'PASS' if g24v2d else 'FAIL'}")
    print()
    print(f"  G24v2 ALL_PASS: {'✓ PASS' if all_pass else '✗ FAIL'}")
    if not math.isnan(pearson_r):
        if pearson_r > 0.3:
            print(f"  ★ Pearson={fmt(pearson_r)} > 0: poli temporali arata d_s mai mare decat ecuatorul")
            print(f"    → Asimetrie temporala confirmata: polii 'vad' mai multa geometrie globala")
        elif pearson_r < -0.3:
            print(f"  ★ Pearson={fmt(pearson_r)} < 0: poli temporali arata d_s mai mic")
    print(f"  Elapsed: {elapsed:.1f}s")
    print("═════════════════════════════════════════════════════════════════")

    summary = {
        "gate": "G24v2",
        "version": "v1",
        "timestamp": ts,
        "seed": seed,
        "n_nodes": n,
        "k_init": k_init,
        "k_conn": k_conn,
        "fiedler_lambda2": lambda2,
        "d_s_full": d_s_full,
        "r2_full": r2_full,
        "n_quintiles": N_QUINTILES,
        "quintile_results": quintile_results,
        "ds_equatorial": ds_equatorial,
        "ds_range": ds_range,
        "pearson_temporal_ds": pearson_r,
        "thresholds": {
            "g24v2a_lambda2_min": thr.g24v2a_lambda2_min,
            "g24v2b_range_min": thr.g24v2b_range_min,
            "g24v2c_ds_lo": thr.g24v2c_ds_lo,
            "g24v2c_ds_hi": thr.g24v2c_ds_hi,
            "g24v2d_pearson_abs": thr.g24v2d_pearson_abs,
        },
        "gates": {
            "g24v2a": "PASS" if g24v2a else "FAIL",
            "g24v2b": "PASS" if g24v2b else "FAIL",
            "g24v2c": "PASS" if g24v2c else "FAIL",
            "g24v2d": "PASS" if g24v2d else "FAIL",
        },
        "all_pass": all_pass,
        "elapsed_s": round(elapsed, 2),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    with (out_dir / "quintiles.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["quintile", "label", "f_lo", "f_hi", "f_med", "n_nodes", "d_s", "r2"])
        w.writeheader(); w.writerows(quintile_results)

    print(f"[G24v2] Artefacte salvate în: {out_dir}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="QNG G24 v2 — Temporal Gradient Foliation")
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

