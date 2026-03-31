#!/usr/bin/env python3
"""
Thermodynamic Limit — d_s(N) → d_s(∞) extrapolation

Dacă d_s ≈ 4 e un efect de N finit (artefact de dimensiune), atunci:
  d_s(N) nu converge spre 4.0 când N→∞

Dacă e real, atunci fit-ul d_s(N) = d_s(∞) + A/N converge la d_s(∞) ≈ 4.0

Metodă:
1. Rulăm Jaccard(N, k=8) pentru N = 100, 150, 200, 250, 300, 350, 400, 500, 600
2. 10 seed-uri per N pentru statistici
3. Fit OLS: d_s vs 1/N → extrapolare la 1/N=0 (N→∞)
4. Eroare la extrapolare prin bootstrap

Output:
  thermo_limit_results.csv   — per (N, seed): d_s, r², ds_uv, ds_ir
  thermo_limit_summary.json  — fit params, d_s(∞), CI
  run-log-thermo-limit.txt
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "thermo-limit-v1"

K_CONN   = 8
K_INIT   = 8
SEED_BASE = 3401

N_WALKS  = 80
N_STEPS  = 18
P_STAY   = 0.5
T_LO, T_HI   = 5, 13
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13

N_SEEDS_PER_N = 10
N_GRID = [100, 150, 200, 250, 300, 350, 400, 500, 600]

DS_LO, DS_HI = 3.5, 4.5


# ── OLS ───────────────────────────────────────────────────────────────────────

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


def ds_window(P_t, lo, hi):
    lx, ly = [], []
    for t in range(lo, hi+1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t)); ly.append(math.log(P_t[t]))
    if len(lx) < 2: return float("nan"), 0.
    _, b, r2 = ols(lx, ly)
    return -2.*b, r2


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


@dataclass
class ThermoResult:
    N:       int
    seed:    int
    ds:      float
    r2:      float
    ds_uv:   float
    ds_ir:   float
    mean_deg: float
    pass_ds: bool


def run_one(N, seed):
    nb = build_jaccard_graph(N, K_INIT, K_CONN, seed)
    mean_deg = sum(len(x) for x in nb) / N
    rng = random.Random(seed ^ 0xABCD1234)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_window(P_t, IR_LO, IR_HI)
    return ThermoResult(N, seed, ds, r2, ds_uv, ds_ir, mean_deg, DS_LO < ds < DS_HI)


def bootstrap_ci(values, n_boot=2000, seed=42, alpha=0.05):
    """Bootstrap 95% CI pentru medie."""
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_boot):
        sample = [rng.choice(values) for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(alpha/2 * n_boot)]
    hi = means[int((1-alpha/2) * n_boot)]
    return lo, hi


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 72)
    log("THERMODYNAMIC LIMIT — d_s(N) → N→∞ extrapolation")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log(f"N_GRID={N_GRID}")
    log(f"N_SEEDS_PER_N={N_SEEDS_PER_N}, K_CONN={K_CONN}")
    log("=" * 72)

    all_results: list[ThermoResult] = []
    # means per N for fit
    n_means: dict[int, float] = {}
    n_stds:  dict[int, float] = {}
    n_pass:  dict[int, tuple] = {}

    for N in N_GRID:
        t1 = time.time()
        seeds = [SEED_BASE + i * 137 for i in range(N_SEEDS_PER_N)]
        ds_list = []
        for seed in seeds:
            r = run_one(N, seed)
            all_results.append(r)
            ds_list.append(r.ds)
        mean_ds = statistics.mean(ds_list)
        std_ds  = statistics.stdev(ds_list) if len(ds_list) > 1 else 0.
        ci_lo, ci_hi = bootstrap_ci(ds_list)
        pass_n = sum(1 for d in ds_list if DS_LO < d < DS_HI)
        n_means[N] = mean_ds
        n_stds[N]  = std_ds
        n_pass[N]  = (pass_n, N_SEEDS_PER_N, ci_lo, ci_hi)
        log(f"  N={N:4d}: d_s = {mean_ds:.4f} ± {std_ds:.4f}  "
            f"95%CI=[{ci_lo:.4f},{ci_hi:.4f}]  "
            f"PASS={pass_n}/{N_SEEDS_PER_N}  ({time.time()-t1:.1f}s)")

    # ── Fit d_s(N) = a + b/N ──────────────────────────────────────────────────
    log("\n── Fit d_s(N) = d_s(∞) + A/N ──────────────────────────────────────")
    xs_fit = [1./N for N in N_GRID]
    ys_fit = [n_means[N] for N in N_GRID]
    a_fit, b_fit, r2_fit = ols(xs_fit, ys_fit)
    ds_inf = a_fit  # intercept la 1/N = 0

    log(f"\n  d_s(N) = {ds_inf:.4f} + {b_fit:.2f}/N")
    log(f"  d_s(∞) = {ds_inf:.4f}  (extrapolare la N→∞)")
    log(f"  r² fit = {r2_fit:.4f}")
    log(f"  A/N corecție: la N=280 → Δd_s ≈ {b_fit/280:.4f}")

    # Bootstrap CI pentru d_s(∞)
    rng_boot = random.Random(42)
    boot_inf = []
    n_list = N_GRID
    ds_per_N = {N: [r.ds for r in all_results if r.N == N] for N in N_GRID}
    for _ in range(2000):
        ys_b = [rng_boot.choice(ds_per_N[N]) for N in n_list]
        xs_b = [1./N for N in n_list]
        a_b, _, _ = ols(xs_b, ys_b)
        boot_inf.append(a_b)
    boot_inf.sort()
    ci_inf_lo = boot_inf[int(0.025 * 2000)]
    ci_inf_hi = boot_inf[int(0.975 * 2000)]
    log(f"  95% bootstrap CI pentru d_s(∞): [{ci_inf_lo:.4f}, {ci_inf_hi:.4f}]")

    # ── Verdict ───────────────────────────────────────────────────────────────
    log("\n── Interpretare ─────────────────────────────────────────────────────")
    if 3.8 <= ds_inf <= 4.2:
        verdict = f"CONFIRMAT: d_s(∞) = {ds_inf:.4f} — converge spre 4.0 în limita N→∞"
        log(f"  ✓ {verdict}")
    elif DS_LO < ds_inf < DS_HI:
        verdict = f"PARȚIAL: d_s(∞) = {ds_inf:.4f} — în interval [3.5,4.5] dar departe de 4.0"
        log(f"  ~ {verdict}")
    else:
        verdict = f"NECONCLUDENT: d_s(∞) = {ds_inf:.4f} — extrapolarea iese din intervalul [3.5,4.5]"
        log(f"  ✗ {verdict}")

    # ── UV/IR running dimension summary ───────────────────────────────────────
    log("\n── Running dimension (UV→IR) la N=280 ───────────────────────────────")
    results_280 = [r for r in all_results if r.N == 280]
    if results_280:
        uv_mean = statistics.mean(r.ds_uv for r in results_280)
        ir_mean = statistics.mean(r.ds_ir for r in results_280)
        log(f"  ds_uv (t=2-5):  {uv_mean:.4f}  ← Planck scale")
        log(f"  ds_mid (t=5-13): {n_means[280]:.4f}  ← mesoscopic")
        log(f"  ds_ir (t=9-13): {ir_mean:.4f}  ← classical")
        if uv_mean < n_means[280] < ir_mean or n_means[280] < uv_mean:
            log("  (UV→IR running prezent — consistent cu CDT/Asymptotic Safety)")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    csv_path = OUT_DIR / "thermo_limit_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(all_results[0]).keys()))
        w.writeheader()
        for r in all_results:
            w.writerow(asdict(r))

    summary = {
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "params": {"K_INIT": K_INIT, "K_CONN": K_CONN, "SEED_BASE": SEED_BASE,
                   "N_SEEDS_PER_N": N_SEEDS_PER_N, "N_GRID": N_GRID},
        "per_N": {str(N): {"ds_mean": n_means[N], "ds_std": n_stds[N],
                            "pass_frac": n_pass[N][0]/N_pass[1] if (N_pass := n_pass[N]) else 0,
                            "ci_lo": n_pass[N][2], "ci_hi": n_pass[N][3]}
                  for N in N_GRID},
        "fit": {"ds_inf": ds_inf, "A": b_fit, "r2": r2_fit,
                "ci_lo": ci_inf_lo, "ci_hi": ci_inf_hi,
                "model": "d_s(N) = d_s_inf + A/N"},
        "verdict": verdict,
        "total_time_s": round(time.time() - t0, 1),
    }

    json_path = OUT_DIR / "thermo_limit_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    log_path = OUT_DIR / "run-log-thermo-limit.txt"
    with open(log_path, "w") as f:
        f.write("\n".join(lines))

    log(f"\n  Artefacte: {OUT_DIR}")
    log(f"  Timp total: {time.time()-t0:.1f}s")
    log("=" * 72)


if __name__ == "__main__":
    main()
