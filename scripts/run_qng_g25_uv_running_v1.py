#!/usr/bin/env python3
"""
QNG G25 — UV Running of Spectral Dimension (v1).

Aceasta e cea mai importantă predicție distinctivă a QNG față de CDT/LQG/AS:

    QNG:  d_s(UV) ≈ 3.0,  d_s(IR) ≈ 4.0
    CDT:  d_s(UV) ≈ 2.0,  d_s(IR) ≈ 4.0
    LQG:  d_s(UV) ≈ 2.0
    AS:   d_s(UV) ≈ 2.0

Dacă QNG e corect, măsurătorile la scara Planck ar trebui să arate d_s≈3,
NU d_s≈2 cum prezic celelalte teorii. Aceasta e o predicție testabilă.

Metoda:
  - "UV" = time scale scurt al random walk (t mic → sonde locale, granulare)
  - "IR" = time scale lung al random walk (t mare → sonde globale, netede)
  - Analogie cu CDT: t ↔ diffusion time ↔ scara energetică (UV↔mic, IR↔mare)

Gates:
    G25a — d_s_UV ∈ (2.0, 3.9)  : UV dimensional reduction (< 4D)
    G25b — d_s_IR ∈ (3.5, 5.0)  : IR recovery of ~4D
    G25c — d_s_UV < d_s_IR - 0.2: running semnificativ (UV < IR)
    G25d — d_s_UV ∈ (2.5, 3.8)  : predicție distinctiva QNG (CDT ar da < 2.5)

Fizica:
  La t mic, random walk-ul sondează structura locală discretă a grafului.
  La t mare, sondează topologia globală emergentă.
  Running-ul d_s(UV) → d_s(IR) reflectă tranziția de la discretitate la
  geometrie continuă emergentă — analog cu running-ul cuantic din CDT/AS.

  QNG face o predicție specifică: d_s_UV ≈ 3 (nu 2), pentru că structura
  locală a grafului Jaccard are mai multă regularitate decât simplexurile
  CDT sau spin-foam-urile LQG.

Usage:
    python scripts/run_qng_g25_uv_running_v1.py
    python scripts/run_qng_g25_uv_running_v1.py --seed 4999
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g25-uv-running-v1"
)

N_NODES_DEFAULT = 280
K_INIT_DEFAULT  = 8
K_CONN_DEFAULT  = 8
SEED_DEFAULT    = 3401

N_WALKS    = 200    # mai multe walk-uri pentru stabilitate statistică
N_STEPS    = 30     # pași totali (mai mult pentru UV-IR separation clară)
P_STAY     = 0.5    # lazy RW

# Ferestre temporale pentru UV vs IR
# UV: t ∈ [T_UV_LO, T_UV_HI] — scale mici (structură locală)
# IR: t ∈ [T_IR_LO, T_IR_HI] — scale mari (topologie globală)
T_UV_LO, T_UV_HI = 2,  6    # UV window
T_IR_LO, T_IR_HI = 12, 22   # IR window


@dataclass
class UVRunningThresholds:
    # G25a: d_s UV redus față de 4D
    g25a_uv_lo: float = 2.0
    g25a_uv_hi: float = 3.9
    # G25b: d_s IR recuperează ~4D
    g25b_ir_lo: float = 3.5
    g25b_ir_hi: float = 5.0
    # G25c: running semnificativ UV < IR
    g25c_running_min: float = 0.2
    # G25d: predicție distinctivă QNG — UV > 2.5 (nu 2 ca CDT/LQG)
    g25d_uv_above_cdt: float = 2.5


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

    return [sorted(s) for s in adj]


# ── P(return|t) pentru toate t ───────────────────────────────────────────────
def compute_return_probs(
    neighbours, n_walks: int, n_steps: int, p_stay: float, rng
) -> list[tuple[int, float]]:
    """
    Calculează P(return|t) pentru t=1..n_steps prin lazy RW.
    Returns list of (t, p_return).
    """
    n = len(neighbours)
    active = [i for i in range(n) if neighbours[i]]

    results = []
    for t in range(1, n_steps + 1):
        returns = 0
        for _ in range(n_walks):
            pos = active[rng.randrange(len(active))]
            start = pos
            for _ in range(t):
                if rng.random() < p_stay:
                    continue
                nb = neighbours[pos]
                if not nb:
                    break
                pos = nb[rng.randrange(len(nb))]
            if pos == start:
                returns += 1
        p_ret = returns / n_walks
        results.append((t, p_ret))

    return results


def ds_from_window(
    return_probs: list[tuple[int, float]],
    t_lo: int,
    t_hi: int
) -> tuple[float, float]:
    """Calculează d_s prin OLS pe fereastra [t_lo, t_hi]."""
    log_t, log_p = [], []
    for t, p in return_probs:
        if t_lo <= t <= t_hi and p > 0:
            log_t.append(math.log(t))
            log_p.append(math.log(p))
    if len(log_t) < 3:
        return float("nan"), 0.
    _, slope, r2 = ols_fit(log_t, log_p)
    return -2.0 * slope, r2


# ── Main ──────────────────────────────────────────────────────────────────────
def run(n: int, k_init: int, k_conn: int, seed: int, out_dir: Path) -> dict:
    t0 = time.time()
    rng = random.Random(seed + 25)

    print(f"[G25] Construiesc graful Jaccard (N={n}, k={k_conn}, seed={seed})")
    neighbours = build_jaccard_graph(n, k_init, k_conn, seed)

    print(f"[G25] Rulând {N_WALKS} walk-uri × {N_STEPS} pași...")
    return_probs = compute_return_probs(neighbours, N_WALKS, N_STEPS, P_STAY, rng)

    # ── d_s în ferestrele UV și IR ────────────────────────────────────────────
    d_s_uv, r2_uv = ds_from_window(return_probs, T_UV_LO, T_UV_HI)
    d_s_ir, r2_ir = ds_from_window(return_probs, T_IR_LO, T_IR_HI)
    d_s_full, r2_full = ds_from_window(return_probs, 5, 13)  # fereastra standard G18d

    running = d_s_ir - d_s_uv if not (math.isnan(d_s_ir) or math.isnan(d_s_uv)) else float("nan")

    print(f"[G25] d_s_UV (t∈[{T_UV_LO},{T_UV_HI}]) = {fmt(d_s_uv)}  r²={fmt(r2_uv)}")
    print(f"[G25] d_s_IR (t∈[{T_IR_LO},{T_IR_HI}]) = {fmt(d_s_ir)}  r²={fmt(r2_ir)}")
    print(f"[G25] d_s_full (t∈[5,13])        = {fmt(d_s_full)}  r²={fmt(r2_full)}")
    print(f"[G25] Running d_s(IR) - d_s(UV)   = {fmt(running)}")

    # ── Profilul complet P(t) ─────────────────────────────────────────────────
    print("\n[G25] Profilul complet P(return|t):")
    for t, p in return_probs:
        if t <= N_STEPS and p > 0:
            ds_local = -2.0 * math.log(p) / math.log(t) if t > 1 else float("nan")
            print(f"  t={t:2d}: P={p:.4f}  d_s_local≈{fmt(ds_local)}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    thr = UVRunningThresholds()

    g25a = (not math.isnan(d_s_uv)) and (thr.g25a_uv_lo < d_s_uv < thr.g25a_uv_hi)
    g25b = (not math.isnan(d_s_ir)) and (thr.g25b_ir_lo < d_s_ir < thr.g25b_ir_hi)
    g25c = (not math.isnan(running)) and (running > thr.g25c_running_min)
    g25d = (not math.isnan(d_s_uv)) and (d_s_uv > thr.g25d_uv_above_cdt)

    all_pass = g25a and g25b and g25c and g25d

    elapsed = time.time() - t0
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # ── Output ────────────────────────────────────────────────────────────────
    print()
    print("══ G25 UV RUNNING RESULTS ════════════════════════════════════════")
    print(f"  d_s_UV  (t∈[{T_UV_LO:2d},{T_UV_HI:2d}]) = {fmt(d_s_uv)}  r²={fmt(r2_uv)}")
    print(f"  d_s_IR  (t∈[{T_IR_LO:2d},{T_IR_HI:2d}]) = {fmt(d_s_ir)}  r²={fmt(r2_ir)}")
    print(f"  Running = {fmt(running)}")
    print()
    print(f"  Comparatie cu literatura:")
    print(f"    QNG (prezis): d_s_UV ≈ 3.0  ← acest rezultat: {fmt(d_s_uv)}")
    print(f"    CDT/LQG/AS:  d_s_UV ≈ 2.0  ← prezic altceva")
    print()
    print(f"  G25a d_s_UV ∈ ({thr.g25a_uv_lo},{thr.g25a_uv_hi}): {fmt(d_s_uv)} → {'PASS' if g25a else 'FAIL'}")
    print(f"  G25b d_s_IR ∈ ({thr.g25b_ir_lo},{thr.g25b_ir_hi}): {fmt(d_s_ir)} → {'PASS' if g25b else 'FAIL'}")
    print(f"  G25c running > {thr.g25c_running_min}:           {fmt(running)} → {'PASS' if g25c else 'FAIL'}")
    print(f"  G25d d_s_UV > {thr.g25d_uv_above_cdt} (>CDT):    {fmt(d_s_uv)} → {'PASS' if g25d else 'FAIL'}")
    print()
    print(f"  G25 ALL_PASS: {'✓ PASS' if all_pass else '✗ FAIL'}")
    print(f"  Elapsed: {elapsed:.1f}s")
    if all_pass:
        print(f"  ★ PREDICȚIE DISTINCTIVĂ: d_s_UV={fmt(d_s_uv)} > 2.5")
        print(f"    QNG se distinge de CDT/LQG/AS la nivel UV")
    print("═════════════════════════════════════════════════════════════════")

    summary = {
        "gate": "G25",
        "version": "v1",
        "timestamp": ts,
        "seed": seed,
        "n_nodes": n,
        "k_init": k_init,
        "k_conn": k_conn,
        "t_uv_lo": T_UV_LO,
        "t_uv_hi": T_UV_HI,
        "t_ir_lo": T_IR_LO,
        "t_ir_hi": T_IR_HI,
        "d_s_uv": d_s_uv,
        "r2_uv": r2_uv,
        "d_s_ir": d_s_ir,
        "r2_ir": r2_ir,
        "d_s_full": d_s_full,
        "r2_full": r2_full,
        "running": running,
        "thresholds": {
            "g25a_uv_lo": thr.g25a_uv_lo,
            "g25a_uv_hi": thr.g25a_uv_hi,
            "g25b_ir_lo": thr.g25b_ir_lo,
            "g25b_ir_hi": thr.g25b_ir_hi,
            "g25c_running_min": thr.g25c_running_min,
            "g25d_uv_above_cdt": thr.g25d_uv_above_cdt,
        },
        "literature_comparison": {
            "QNG_prediction_uv": "~3.0",
            "CDT_prediction_uv": "~2.0",
            "LQG_prediction_uv": "~2.0",
            "AS_prediction_uv":  "~2.0",
            "this_result_uv": d_s_uv,
        },
        "gates": {
            "g25a": "PASS" if g25a else "FAIL",
            "g25b": "PASS" if g25b else "FAIL",
            "g25c": "PASS" if g25c else "FAIL",
            "g25d": "PASS" if g25d else "FAIL",
        },
        "all_pass": all_pass,
        "elapsed_s": round(elapsed, 2),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # CSV: full t-profile
    rows = [
        {
            "t": t,
            "p_return": p,
            "log_t": math.log(t) if t > 0 else float("nan"),
            "log_p": math.log(p) if p > 0 else float("nan"),
            "ds_local": -2.0 * math.log(p) / math.log(t) if (t > 1 and p > 0) else float("nan"),
            "window": "UV" if T_UV_LO <= t <= T_UV_HI else ("IR" if T_IR_LO <= t <= T_IR_HI else "mid"),
        }
        for t, p in return_probs
    ]
    with (out_dir / "return_profile.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["t", "p_return", "log_t", "log_p", "ds_local", "window"])
        w.writeheader(); w.writerows(rows)

    print(f"[G25] Artefacte salvate în: {out_dir}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="QNG G25 — UV Running of Spectral Dimension")
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
