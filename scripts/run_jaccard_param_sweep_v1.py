#!/usr/bin/env python3
"""
Jaccard Graph — Parameter Sweep (N_nodes × k_init × k_conn)

Verifică că d_s ≈ 4.0 e robust față de topologia grafului,
nu doar față de seed (care e deja confirmat: 50/50 PASS).

Grid:
  N_nodes  ∈ {100, 150, 200, 250, 300, 350, 400}
  k_init   ∈ {6, 8, 10, 12}
  k_conn   = k_init  (default; poate fi overridden)
  seed     = 3401 (canonical), + opțional avg pe 3 seed-uri

Output:
  jaccard_param_sweep.csv        — per (N, k): d_s, r², ds_uv, ds_ir, pass
  jaccard_param_sweep_matrix.txt — tabel uman-readable
  jaccard_param_sweep_summary.json
  run-log-jaccard-param-sweep.txt

Usage:
    python scripts/run_jaccard_param_sweep_v1.py
    python scripts/run_jaccard_param_sweep_v1.py --n-seeds 3
    python scripts/run_jaccard_param_sweep_v1.py --n-seeds 1 --k-conn-fixed 8
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
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "jaccard-param-sweep-v1"

# ── Grid implicit ──────────────────────────────────────────────────────────────
N_NODES_GRID = [100, 150, 200, 250, 300, 350, 400]
K_INIT_GRID  = [6, 8, 10, 12]
SEEDS_DEFAULT = [3401, 4999, 7777]   # mediat pe 3 seed-uri → mai stabil

# ── Parametri RW ───────────────────────────────────────────────────────────────
N_WALKS = 80
N_STEPS = 18
T_LO    = 5
T_HI    = 13
P_STAY  = 0.5

# ── Ferestre UV / IR ───────────────────────────────────────────────────────────
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13

# ── Threshold G18d ─────────────────────────────────────────────────────────────
DS_LO = 3.5
DS_HI = 4.5


# ── Utilitare ──────────────────────────────────────────────────────────────────

def ols(xs, ys):
    n = len(xs)
    if n < 2:
        return 0., 0., 0.
    mx = sum(xs) / n
    my = sum(ys) / n
    Sxx = sum((x - mx) ** 2 for x in xs)
    Sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    if abs(Sxx) < 1e-30:
        return my, 0., 0.
    b = Sxy / Sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    if ss_tot < 1e-30:
        return a, b, 1.
    r2 = max(0., 1. - sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n)) / ss_tot)
    return a, b, r2


def ds_from_window(P_t, lo, hi):
    lx, ly = [], []
    for t in range(lo, hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t))
            ly.append(math.log(P_t[t]))
    if len(lx) < 2:
        return float("nan"), 0.
    _, b, r2 = ols(lx, ly)
    return -2. * b, r2


# ── Graf Jaccard ───────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j)
                adj0[j].add(i)
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i:
                continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj)
            union = len(Ni | Nj)
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j)
            adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Lazy Random Walk ──────────────────────────────────────────────────────────

def lazy_rw(neighbours, n_walks, n_steps, rng, p_stay=P_STAY):
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        if not neighbours[start]:
            continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                if rng.random() > p_stay:
                    nb = neighbours[v]
                    if nb:
                        v = rng.choice(nb)
                if v == start:
                    counts[t] += 1
    return [counts[t] / total for t in range(n_steps + 1)]


# ── Rulare singulară (N, k, seed) ─────────────────────────────────────────────

def run_single(n, k_init, k_conn, seed):
    nb = build_jaccard_graph(n, k_init, k_conn, seed)
    mean_deg = sum(len(x) for x in nb) / n
    rng = random.Random(seed ^ 0xABCD1234)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_from_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_from_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_from_window(P_t, IR_LO, IR_HI)
    return ds, r2, ds_uv, ds_ir, mean_deg


@dataclass
class CellResult:
    n: int
    k_init: int
    k_conn: int
    seeds: list = field(default_factory=list)
    ds_vals: list = field(default_factory=list)
    r2_vals: list = field(default_factory=list)
    ds_uv_vals: list = field(default_factory=list)
    ds_ir_vals: list = field(default_factory=list)
    mean_deg_vals: list = field(default_factory=list)

    @property
    def ds(self):
        v = [x for x in self.ds_vals if not math.isnan(x)]
        return statistics.mean(v) if v else float("nan")

    @property
    def r2(self):
        v = [x for x in self.r2_vals if not math.isnan(x)]
        return statistics.mean(v) if v else float("nan")

    @property
    def ds_uv(self):
        v = [x for x in self.ds_uv_vals if not math.isnan(x)]
        return statistics.mean(v) if v else float("nan")

    @property
    def ds_ir(self):
        v = [x for x in self.ds_ir_vals if not math.isnan(x)]
        return statistics.mean(v) if v else float("nan")

    @property
    def mean_deg(self):
        v = [x for x in self.mean_deg_vals if not math.isnan(x)]
        return statistics.mean(v) if v else float("nan")

    @property
    def ds_std(self):
        v = [x for x in self.ds_vals if not math.isnan(x)]
        return statistics.stdev(v) if len(v) > 1 else 0.

    @property
    def pass_gate(self):
        return DS_LO < self.ds < DS_HI


# ── Main ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Jaccard parameter sweep (N × k)")
    p.add_argument("--n-seeds", type=int, default=3,
                   help="Număr seed-uri per celulă (default 3)")
    p.add_argument("--seeds", type=int, nargs="+", default=None,
                   help="Seed-uri explicite (override --n-seeds)")
    p.add_argument("--k-conn-fixed", type=int, default=None,
                   help="Dacă setat, k_conn = valoare fixă (altfel k_conn = k_init)")
    p.add_argument("--n-nodes-grid", type=int, nargs="+", default=N_NODES_GRID)
    p.add_argument("--k-init-grid",  type=int, nargs="+", default=K_INIT_GRID)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    seeds = args.seeds if args.seeds else SEEDS_DEFAULT[: args.n_seeds]

    lines = []
    def log(msg=""):
        print(msg)
        lines.append(msg)

    t0 = time.time()
    log("=" * 75)
    log("Jaccard Parameter Sweep — d_s Robustness vs (N_nodes, k_init)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 75)
    log(f"N_nodes grid : {args.n_nodes_grid}")
    log(f"k_init  grid : {args.k_init_grid}")
    log(f"k_conn       : {'= k_init' if args.k_conn_fixed is None else str(args.k_conn_fixed)}")
    log(f"Seeds        : {seeds}  (mediat pe {len(seeds)} seed-uri / celulă)")
    log(f"RW           : n_walks={N_WALKS}  n_steps={N_STEPS}  p_stay={P_STAY}")
    log(f"d_s window   : t=[{T_LO},{T_HI}]  threshold: ({DS_LO}, {DS_HI})")
    log()

    # ── Rulare grid ────────────────────────────────────────────────────────────
    grid: dict[tuple, CellResult] = {}
    n_total = len(args.n_nodes_grid) * len(args.k_init_grid)
    done = 0

    for n in args.n_nodes_grid:
        for k_init in args.k_init_grid:
            k_conn = args.k_conn_fixed if args.k_conn_fixed is not None else k_init
            cell = CellResult(n=n, k_init=k_init, k_conn=k_conn)
            for seed in seeds:
                ds, r2, ds_uv, ds_ir, mdeg = run_single(n, k_init, k_conn, seed)
                cell.seeds.append(seed)
                cell.ds_vals.append(ds)
                cell.r2_vals.append(r2)
                cell.ds_uv_vals.append(ds_uv)
                cell.ds_ir_vals.append(ds_ir)
                cell.mean_deg_vals.append(mdeg)
            grid[(n, k_init)] = cell
            done += 1
            mark = "✓" if cell.pass_gate else "✗"
            std_str = f"±{cell.ds_std:.3f}" if len(seeds) > 1 else ""
            log(f"  N={n:>3}  k={k_init:>2}  k_conn={k_conn:>2}  "
                f"d_s={cell.ds:>6.3f}{std_str:>7}  r²={cell.r2:.3f}  "
                f"deg={cell.mean_deg:>5.1f}  {mark}  [{done}/{n_total}]")

    log()

    # ── Matrice 2D ─────────────────────────────────────────────────────────────
    log("=" * 75)
    log("MATRICE d_s  (linii=N_nodes, coloane=k_init)")
    log("=" * 75)
    nk_label = "N\\k"
    header = f"{nk_label:>5}" + "".join(f"  k={k:>2}" for k in args.k_init_grid)
    log(header)
    log("-" * len(header))
    matrix_lines = [header, "-" * len(header)]

    for n in args.n_nodes_grid:
        row = f"{n:>5}"
        for k in args.k_init_grid:
            cell = grid.get((n, k))
            if cell is None:
                row += "     N/A"
            else:
                mark = "✓" if cell.pass_gate else "✗"
                row += f"  {cell.ds:>5.2f}{mark}"
        log(row)
        matrix_lines.append(row)

    log()
    log("=" * 75)
    log("MATRICE r²  (calitatea scaling-ului)")
    log("=" * 75)
    log(header)
    log("-" * len(header))

    for n in args.n_nodes_grid:
        row = f"{n:>5}"
        for k in args.k_init_grid:
            cell = grid.get((n, k))
            if cell is None:
                row += "     N/A"
            else:
                row += f"  {cell.r2:>6.3f}"
        log(row)

    log()

    # ── Statistici globale ─────────────────────────────────────────────────────
    all_cells = list(grid.values())
    n_pass = sum(1 for c in all_cells if c.pass_gate)
    n_total_cells = len(all_cells)
    frac = n_pass / n_total_cells if n_total_cells else 0.

    all_ds = [c.ds for c in all_cells if not math.isnan(c.ds)]
    all_r2 = [c.r2 for c in all_cells if not math.isnan(c.r2)]

    log("=" * 75)
    log("REZUMAT GLOBAL")
    log("=" * 75)
    log(f"  Celule rulate : {n_total_cells}  ({len(args.n_nodes_grid)} N × {len(args.k_init_grid)} k × {len(seeds)} seed-uri)")
    log(f"  PASS           : {n_pass}/{n_total_cells}  ({frac*100:.1f}%)")
    log()
    log(f"  d_s  : mean={statistics.mean(all_ds):.3f}  std={statistics.stdev(all_ds):.3f}  "
        f"min={min(all_ds):.3f}  max={max(all_ds):.3f}")
    log(f"  r²   : mean={statistics.mean(all_r2):.3f}  min={min(all_r2):.3f}  max={max(all_r2):.3f}")
    log()

    # Trend față de N
    log("  Trend d_s față de N_nodes (medie pe k):")
    for n in args.n_nodes_grid:
        cells_n = [grid[(n, k)] for k in args.k_init_grid if (n, k) in grid]
        ds_n = [c.ds for c in cells_n if not math.isnan(c.ds)]
        if ds_n:
            log(f"    N={n:>3}  d_s_mean={statistics.mean(ds_n):.3f}  ({'✓' if DS_LO < statistics.mean(ds_n) < DS_HI else '✗'})")

    log()
    log("  Trend d_s față de k_init (medie pe N):")
    for k in args.k_init_grid:
        cells_k = [grid[(n, k)] for n in args.n_nodes_grid if (n, k) in grid]
        ds_k = [c.ds for c in cells_k if not math.isnan(c.ds)]
        if ds_k:
            log(f"    k={k:>2}  d_s_mean={statistics.mean(ds_k):.3f}  ({'✓' if DS_LO < statistics.mean(ds_k) < DS_HI else '✗'})")

    log()

    if frac >= 0.90:
        decision = "ROBUST"
        log(f"  DECIZIE: ROBUST — d_s≈4.0 stabil pe {frac*100:.0f}% din configurații")
    elif frac >= 0.70:
        decision = "MARGINAL"
        log(f"  DECIZIE: MARGINAL — {frac*100:.0f}% PASS (threshold: 90%)")
    else:
        decision = "FRAGIL"
        log(f"  DECIZIE: FRAGIL — {frac*100:.0f}% PASS — revizuire necesara")

    log()
    log(f"Elapsed: {time.time()-t0:.1f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    if args.write_artifacts:
        # CSV detaliat
        csv_path = out_dir / "jaccard_param_sweep.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "n_nodes", "k_init", "k_conn", "n_seeds",
                "ds_mean", "ds_std", "ds_uv", "ds_ir",
                "r2_mean", "mean_deg", "pass_gate"
            ])
            w.writeheader()
            for (n, k), cell in sorted(grid.items()):
                w.writerow({
                    "n_nodes": n, "k_init": k, "k_conn": cell.k_conn,
                    "n_seeds": len(seeds),
                    "ds_mean": round(cell.ds, 4), "ds_std": round(cell.ds_std, 4),
                    "ds_uv": round(cell.ds_uv, 4), "ds_ir": round(cell.ds_ir, 4),
                    "r2_mean": round(cell.r2, 4), "mean_deg": round(cell.mean_deg, 3),
                    "pass_gate": cell.pass_gate,
                })

        # Matrice txt
        (out_dir / "jaccard_param_sweep_matrix.txt").write_text(
            "\n".join(matrix_lines), encoding="utf-8"
        )

        # JSON summary
        summary = {
            "version": "jaccard-param-sweep-v1",
            "run_utc": datetime.utcnow().isoformat(),
            "config": {
                "n_nodes_grid": args.n_nodes_grid,
                "k_init_grid": args.k_init_grid,
                "k_conn_fixed": args.k_conn_fixed,
                "seeds": seeds,
            },
            "threshold": {"ds_lo": DS_LO, "ds_hi": DS_HI},
            "results": {
                "n_cells": n_total_cells,
                "n_pass": n_pass,
                "frac_pass": round(frac, 4),
                "ds_mean": round(statistics.mean(all_ds), 4),
                "ds_std": round(statistics.stdev(all_ds), 4),
                "ds_min": round(min(all_ds), 4),
                "ds_max": round(max(all_ds), 4),
                "r2_mean": round(statistics.mean(all_r2), 4),
                "decision": decision,
            },
            "per_n": {
                str(n): round(statistics.mean(
                    [grid[(n, k)].ds for k in args.k_init_grid
                     if (n, k) in grid and not math.isnan(grid[(n, k)].ds)]
                ), 4)
                for n in args.n_nodes_grid
            },
            "per_k": {
                str(k): round(statistics.mean(
                    [grid[(n, k)].ds for n in args.n_nodes_grid
                     if (n, k) in grid and not math.isnan(grid[(n, k)].ds)]
                ), 4)
                for k in args.k_init_grid
            },
        }
        (out_dir / "jaccard_param_sweep_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        (out_dir / "run-log-jaccard-param-sweep.txt").write_text(
            "\n".join(lines), encoding="utf-8"
        )

        log(f"\nArtefacte salvate: {out_dir}")

    return 0 if frac >= 0.90 else 1


if __name__ == "__main__":
    sys.exit(main())
