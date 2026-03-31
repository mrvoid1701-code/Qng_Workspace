#!/usr/bin/env python3
"""
Jaccard Graph — Multi-Seed Sweep (d_s Robustness)

Rulează graful Jaccard Informational pe N_SEEDS seed-uri diferite și
măsoară d_s la fiecare iterație. Verifică că d_s ∈ (3.5, 4.5) e robust
față de seed, nu un accident al seed-ului 3401.

Output:
  jaccard_seed_sweep.csv     — per seed: d_s, r², mean_degree, ds_uv, ds_ir
  jaccard_sweep_summary.json — mean, std, min, max, frac_pass
  run-log-jaccard-sweep.txt

Usage:
    python scripts/run_jaccard_seed_sweep_v1.py
    python scripts/run_jaccard_seed_sweep_v1.py --n-seeds 100
    python scripts/run_jaccard_seed_sweep_v1.py --n-seeds 20 --n-nodes 200
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "jaccard-sweep-v1"

# Parametri graf
N_NODES_DEFAULT = 280
K_INIT_DEFAULT  = 8
K_CONN_DEFAULT  = 8

# Parametri RW
N_WALKS  = 80
N_STEPS  = 18
T_LO     = 5
T_HI     = 13
P_STAY   = 0.5

# Threshold G18d v2
DS_LO = 3.5
DS_HI = 4.5

# Ferestre UV/IR pentru running dimension
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13


# ── Utilitare ──────────────────────────────────────────────────────────────────

def ols(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my-b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    return a, b, max(0., 1.-sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))/ss_tot)


def ds_from_window(P_t, lo, hi):
    lx, ly = [], []
    for t in range(lo, hi+1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t)); ly.append(math.log(P_t[t]))
    if len(lx) < 2: return float("nan"), 0.
    _, b, r2 = ols(lx, ly)
    return -2.*b, r2


# ── Graf Jaccard ───────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
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
            scores.append((inter/union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Lazy Random Walk ──────────────────────────────────────────────────────────

def lazy_rw(neighbours, n_walks, n_steps, rng, p_stay=P_STAY):
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        if not neighbours[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps+1):
                if rng.random() > p_stay:
                    nb = neighbours[v]
                    if nb: v = rng.choice(nb)
                if v == start: counts[t] += 1
    return [counts[t]/total for t in range(n_steps+1)]


# ── Sweep ──────────────────────────────────────────────────────────────────────

@dataclass
class SeedResult:
    seed: int
    mean_degree: float
    ds: float
    r2: float
    ds_uv: float
    ds_ir: float
    pass_gate: bool


def run_seed(n, k_init, k_conn, seed):
    nb = build_jaccard_graph(n, k_init, k_conn, seed)
    mean_deg = sum(len(x) for x in nb) / n
    rng = random.Random(seed ^ 0xABCD1234)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_from_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_from_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_from_window(P_t, IR_LO, IR_HI)
    pass_gate = DS_LO < ds < DS_HI
    return SeedResult(seed, mean_deg, ds, r2, ds_uv, ds_ir, pass_gate)


# ── CLI + main ─────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Jaccard multi-seed d_s sweep")
    p.add_argument("--n-seeds",  type=int, default=50)
    p.add_argument("--n-nodes",  type=int, default=N_NODES_DEFAULT)
    p.add_argument("--k-init",   type=int, default=K_INIT_DEFAULT)
    p.add_argument("--k-conn",   type=int, default=K_CONN_DEFAULT)
    p.add_argument("--seed-start", type=int, default=1000,
                   help="Primul seed din sweep (implicit 1000)")
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log(f"Jaccard Multi-Seed Sweep — d_s Robustness (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log(f"n_nodes={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}")
    log(f"n_seeds={args.n_seeds}  seed_start={args.seed_start}")
    log(f"RW: n_walks={N_WALKS}  n_steps={N_STEPS}  p_stay={P_STAY}")
    log(f"d_s window: t=[{T_LO},{T_HI}]  threshold: ({DS_LO}, {DS_HI})")
    log()

    seeds = list(range(args.seed_start, args.seed_start + args.n_seeds))
    results = []

    log(f"{'Seed':>6}  {'d_s':>7}  {'r²':>6}  {'d_s UV':>7}  {'d_s IR':>7}  {'deg':>6}  {'PASS?':>5}")
    log("-" * 55)

    for i, seed in enumerate(seeds):
        r = run_seed(args.n_nodes, args.k_init, args.k_conn, seed)
        results.append(r)
        mark = "✓" if r.pass_gate else "✗"
        log(f"{seed:>6}  {r.ds:>7.3f}  {r.r2:>6.3f}  {r.ds_uv:>7.3f}  {r.ds_ir:>7.3f}  {r.mean_degree:>6.2f}  {mark:>5}")

        # Progress a fiecare 10 seed-uri
        if (i+1) % 10 == 0:
            so_far = [x.ds for x in results if not math.isnan(x.ds)]
            pct = sum(1 for x in results if x.pass_gate) / len(results) * 100
            log(f"  → [{i+1}/{args.n_seeds}]  mean_d_s={statistics.mean(so_far):.3f}  pass_rate={pct:.0f}%")

    log()

    # ── Statistici finale ──────────────────────────────────────────────────────
    ds_vals  = [r.ds  for r in results if not math.isnan(r.ds)]
    uv_vals  = [r.ds_uv for r in results if not math.isnan(r.ds_uv)]
    ir_vals  = [r.ds_ir for r in results if not math.isnan(r.ds_ir)]
    r2_vals  = [r.r2  for r in results if not math.isnan(r.r2)]
    n_pass   = sum(1 for r in results if r.pass_gate)
    frac     = n_pass / len(results)

    log("=" * 70)
    log("REZUMAT")
    log("=" * 70)
    log(f"  Seeds rulate:       {len(results)}")
    log(f"  PASS ({DS_LO}<d_s<{DS_HI}):  {n_pass}/{len(results)}  ({frac*100:.1f}%)")
    log()
    log(f"  d_s:   mean={statistics.mean(ds_vals):.3f}  std={statistics.stdev(ds_vals):.3f}  min={min(ds_vals):.3f}  max={max(ds_vals):.3f}")
    log(f"  d_s UV: mean={statistics.mean(uv_vals):.3f}  (running dim la scala Planck)")
    log(f"  d_s IR: mean={statistics.mean(ir_vals):.3f}  (running dim clasica)")
    log(f"  r²:    mean={statistics.mean(r2_vals):.3f}  (calitate scaling)")
    log()

    # Decizie
    if frac >= 0.90:
        decision = "ROBUST"
        log(f"  DECIZIE: ROBUST — d_s≈4.0 e stabil pe {frac*100:.0f}% din seed-uri")
    elif frac >= 0.70:
        decision = "MARGINAL"
        log(f"  DECIZIE: MARGINAL — {frac*100:.0f}% PASS (threshold: 90%)")
    else:
        decision = "FRAGIL"
        log(f"  DECIZIE: FRAGIL — doar {frac*100:.0f}% PASS — revizuire necesara")

    log()
    log(f"Elapsed: {time.time()-t0:.1f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    if args.write_artifacts:
        csv_path = out_dir / "jaccard_seed_sweep.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["seed","ds","r2","ds_uv","ds_ir","mean_degree","pass_gate"])
            w.writeheader()
            for r in results:
                w.writerow({"seed": r.seed, "ds": round(r.ds,4), "r2": round(r.r2,4),
                            "ds_uv": round(r.ds_uv,4), "ds_ir": round(r.ds_ir,4),
                            "mean_degree": round(r.mean_degree,3), "pass_gate": r.pass_gate})

        summary = {
            "version": "jaccard-sweep-v1",
            "run_utc": datetime.utcnow().isoformat(),
            "config": {"n_nodes": args.n_nodes, "k_init": args.k_init,
                       "k_conn": args.k_conn, "n_seeds": args.n_seeds,
                       "seed_start": args.seed_start},
            "threshold": {"ds_lo": DS_LO, "ds_hi": DS_HI},
            "results": {
                "n_seeds": len(results), "n_pass": n_pass,
                "frac_pass": round(frac, 4),
                "ds_mean": round(statistics.mean(ds_vals), 4),
                "ds_std":  round(statistics.stdev(ds_vals), 4),
                "ds_min":  round(min(ds_vals), 4),
                "ds_max":  round(max(ds_vals), 4),
                "ds_uv_mean": round(statistics.mean(uv_vals), 4),
                "ds_ir_mean": round(statistics.mean(ir_vals), 4),
                "r2_mean": round(statistics.mean(r2_vals), 4),
                "decision": decision,
            }
        }
        (out_dir / "jaccard_sweep_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        (out_dir / "run-log-jaccard-sweep.txt").write_text(
            "\n".join(lines), encoding="utf-8"
        )

        log(f"\nArtefacte: {out_dir}")

    return 0 if frac >= 0.90 else 1


if __name__ == "__main__":
    sys.exit(main())
