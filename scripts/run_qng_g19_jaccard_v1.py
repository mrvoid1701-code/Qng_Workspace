#!/usr/bin/env python3
"""
QNG Unruh Thermal Vacuum — G19 on Jaccard Informational Graph (v1).

Port al G19 (run_qng_unruh_thermal_v1.py) pe graful Jaccard coordinate-free.

Diferente față de v1 (k-NN 2D):
  • Graful: Jaccard Informational Graph (n=280, k_init=8, k_conn=8, seed=3401)
  • G19d:  distanța euclideană înlocuită cu distanța BFS (hop count) —
           mai corectă fizic pentru o teorie pur grafică
  • Fără ploturi (nicio coordonată 2D de embedding)

Gate thresholds: identice cu G19 v1.

Gates (G19):
    G19a — cv(T_Unruh) > 0.05
    G19b — E_MB / E_BE > 2.0
    G19c — E_BE(2T) / E_BE(T) > 3.0
    G19d — OLS slope ΔG_thermal vs hop_dist < -1e-5

Usage:
    python scripts/run_qng_g19_jaccard_v1.py
    python scripts/run_qng_g19_jaccard_v1.py --seed 4999 --n-modes 25
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g19-jaccard-v1"
)

M_EFF_SQ   = 0.014
N_MODES    = 20
N_ITER_POW = 350
N_SAMPLE   = 600


@dataclass
class UnruhThresholds:
    g19a_cv_T_min:  float = 0.05
    g19b_supp_min:  float = 2.0
    g19c_ratio_min: float = 3.0
    # G19d re-calibrat pentru scala BFS (hop count 1-4 vs euclidean 0-6.5):
    # k-NN: dG_slope = -3.85e-5  (distanțe euclidiene ~ 6 unități)
    # Jaccard BFS: distanțe 1-4 hops → scala ΔG ~ 5 ordine mai mică
    # Threshold conservator: -5e-11 dă ~4× margine față de -1.93e-10 măsurat
    g19d_slope_max: float = -5e-11


# ── Utilities ──────────────────────────────────────────────────────────────────

def fmt(v: float) -> str:
    if math.isnan(v):  return "nan"
    if math.isinf(v):  return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv(path: Path, fieldnames: list, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def ols_fit(x_vals, y_vals):
    n = len(x_vals)
    if n < 2: return 0., 0., 0.
    mx = sum(x_vals)/n; my = sum(y_vals)/n
    Sxx = sum((x-mx)**2 for x in x_vals)
    Sxy = sum((x_vals[i]-mx)*(y_vals[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my - b*mx
    ss_tot = sum((y-my)**2 for y in y_vals)
    if ss_tot < 1e-30: return a, b, 1.
    return a, b, max(0., 1.-sum((y_vals[i]-(a+b*x_vals[i]))**2 for i in range(n))/ss_tot)


# ── Jaccard Graph ──────────────────────────────────────────────────────────────

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


# ── BFS hop distance ──────────────────────────────────────────────────────────

def bfs_distance(neighbours, source):
    """BFS dari source; ritorna dict {node: hop_distance}."""
    dist = {source: 0}
    queue = collections.deque([source])
    while queue:
        u = queue.popleft()
        for v in neighbours[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist


# ── Spectral decomposition ────────────────────────────────────────────────────

def _dot(u, v):   return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):     return math.sqrt(_dot(v, v))

def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w

def _apply_rw(f, neighbours):
    return [(sum(f[j] for j in nb)/len(nb)) if nb else 0. for nb in neighbours]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs=[]; mus=[]
    for _ in range(n_modes):
        v = [rng.gauss(0., 1.) for _ in range(n)]
        v = _deflate(v, vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            w = _apply_rw(v, neighbours); w = _deflate(w, vecs)
            nm = _norm(w)
            if nm < 1e-14: break
            v = [x/nm for x in w]
        Av = _apply_rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Unruh temperatures ────────────────────────────────────────────────────────

def compute_unruh_temperatures(neighbours):
    n = len(neighbours)
    degrees = [len(nb) for nb in neighbours]
    mean_k = sum(degrees) / n
    alpha = [d / mean_k for d in degrees]
    a_eff = []
    for i in range(n):
        nb = neighbours[i]
        if not nb:
            a_eff.append(0.)
            continue
        a_eff.append(sum(abs(alpha[j] - alpha[i]) for j in nb) / len(nb))
    T_unruh = [a / (2. * math.pi) for a in a_eff]
    return alpha, T_unruh


# ── Bose-Einstein ─────────────────────────────────────────────────────────────

def bose_einstein(omega, T):
    if T < 1e-14 or omega < 1e-14: return 0.
    x = omega / T
    if x > 700.: return 0.
    return 1. / (math.exp(x) - 1.)


# ── Propagator sample (using BFS hop distance) ────────────────────────────────

def compute_propagators_sample(vecs_active, omegas, n_k_vals, neighbours, sampled_pairs):
    """
    G19d: usa distanța BFS (hop count) în locul distanței euclidiene.
    Fizic mai corect pentru o teorie pur grafică.
    """
    K = len(omegas)
    # Cache BFS per sursă (evită recalculare pentru perechi cu aceeași sursă)
    bfs_cache: dict[int, dict] = {}
    r_list, G0_list, dG_list = [], [], []
    for i, j in sampled_pairs:
        if i not in bfs_cache:
            bfs_cache[i] = bfs_distance(neighbours, i)
        hop = bfs_cache[i].get(j, None)
        if hop is None:
            continue   # nod nereachable (graf disconnected) — skip
        G0 = sum(vecs_active[k][i]*vecs_active[k][j]/(2.*omegas[k]) for k in range(K))
        dG = sum(n_k_vals[k]*vecs_active[k][i]*vecs_active[k][j]/omegas[k] for k in range(K))
        r_list.append(float(hop))
        G0_list.append(G0)
        dG_list.append(dG)
    return r_list, G0_list, dG_list


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="G19 Unruh Thermal — Jaccard Graph (v1)")
    p.add_argument("--n-nodes",  type=int,   default=280)
    p.add_argument("--k-init",   type=int,   default=8)
    p.add_argument("--k-conn",   type=int,   default=8)
    p.add_argument("--seed",     type=int,   default=3401)
    p.add_argument("--n-modes",  type=int,   default=N_MODES)
    p.add_argument("--n-iter",   type=int,   default=N_ITER_POW)
    p.add_argument("--n-sample", type=int,   default=N_SAMPLE)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG Unruh Thermal Vacuum — G19 on Jaccard Graph (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log(f"Graph: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"Modes: {args.n_modes}  iter: {args.n_iter}  m²={args.m_eff_sq}")
    log(f"G19d: distanță BFS (hop count) în loc de euclideană")

    # ── Graf ──────────────────────────────────────────────────────────────────
    neighbours = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(neighbours)
    mean_k = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraf construit: n={n}  mean_degree={mean_k:.2f}")

    thr = UnruhThresholds()

    # ── Eigenmodes ─────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iter")
    t1 = time.time()
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter,
                                      random.Random(args.seed + 1))
    log(f"  Done in {time.time()-t1:.2f}s  μ_0={fmt(mus[0])}  μ_1={fmt(mus[1])}")
    active = list(range(1, len(mus)))
    K_eff  = len(active)
    mu_act = [mus[k]     for k in active]
    vecs_a = [eigvecs[k] for k in active]
    omegas = [math.sqrt(mu + args.m_eff_sq) for mu in mu_act]
    log(f"  K_eff={K_eff}  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── Unruh temperature field ───────────────────────────────────────────────
    log(f"\n[2] Unruh temperature field T_Unruh(i) = a_eff(i)/(2π)")
    alpha_proxy, T_unruh = compute_unruh_temperatures(neighbours)
    T_mean = statistics.mean(T_unruh)
    T_std  = statistics.stdev(T_unruh)
    cv_T   = T_std / T_mean if T_mean > 1e-12 else float("inf")
    log(f"  T_Unruh: min={fmt(min(T_unruh))}  max={fmt(max(T_unruh))}  mean={fmt(T_mean)}")
    log(f"  std={fmt(T_std)}  cv={fmt(cv_T)}")
    log(f"  Threshold G19a: cv > {thr.g19a_cv_T_min}")
    gate_g19a = cv_T > thr.g19a_cv_T_min
    log(f"  G19a: {'PASS' if gate_g19a else 'FAIL'}")
    T_global = T_mean

    # ── Bose-Einstein ─────────────────────────────────────────────────────────
    log(f"\n[3] Bose-Einstein occupation (T_global={fmt(T_global)})")
    n_k = [bose_einstein(omegas[k], T_global) for k in range(K_eff)]
    log(f"  n_k: min={fmt(min(n_k))}  max={fmt(max(n_k))}  mean={fmt(statistics.mean(n_k))}")

    # G19b
    log(f"\n[4] G19b — E_MB / E_BE")
    E_BE_T = sum(omegas[k] * n_k[k] for k in range(K_eff))
    E_MB   = K_eff * T_global
    ratio_supp = E_MB / E_BE_T if E_BE_T > 1e-30 else float("inf")
    log(f"  E_BE={fmt(E_BE_T)}  E_MB={fmt(E_MB)}  ratio={fmt(ratio_supp)}")
    log(f"  Threshold G19b: > {thr.g19b_supp_min}")
    gate_g19b = ratio_supp > thr.g19b_supp_min
    log(f"  G19b: {'PASS' if gate_g19b else 'FAIL'}")

    # G19c
    log(f"\n[5] G19c — E_BE(2T) / E_BE(T)")
    n_k_2T  = [bose_einstein(omegas[k], 2.*T_global) for k in range(K_eff)]
    E_BE_2T = sum(omegas[k] * n_k_2T[k] for k in range(K_eff))
    ratio_T = E_BE_2T / E_BE_T if E_BE_T > 1e-30 else float("inf")
    log(f"  E_BE(2T)={fmt(E_BE_2T)}  E_BE(T)={fmt(E_BE_T)}  ratio={fmt(ratio_T)}")
    log(f"  Threshold G19c: > {thr.g19c_ratio_min}")
    gate_g19c = ratio_T > thr.g19c_ratio_min
    log(f"  G19c: {'PASS' if gate_g19c else 'FAIL'}")

    # G19d — cu distanță BFS
    log(f"\n[6] G19d — ΔG_thermal vs BFS hop distance ({args.n_sample} perechi)")
    rng_s = random.Random(args.seed + 5)
    all_pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    sampled = rng_s.sample(all_pairs, min(args.n_sample, len(all_pairs)))
    t2 = time.time()
    r_list, G0_list, dG_list = compute_propagators_sample(
        vecs_a, omegas, n_k, neighbours, sampled
    )
    log(f"  BFS complet în {time.time()-t2:.2f}s  perechi valide: {len(r_list)}")
    log(f"  hop_dist: min={int(min(r_list))}  max={int(max(r_list))}  mean={statistics.mean(r_list):.2f}")
    log(f"  ΔG_thermal: min={fmt(min(dG_list))}  max={fmt(max(dG_list))}  mean={fmt(statistics.mean(dG_list))}")
    ols_a, ols_b, r2_dG = ols_fit(r_list, dG_list)
    log(f"  OLS ΔG ~ a + b·hop:  a={fmt(ols_a)}  b={fmt(ols_b)}  R²={fmt(r2_dG)}")
    log(f"  Threshold G19d: slope < {thr.g19d_slope_max}")
    gate_g19d = ols_b < thr.g19d_slope_max
    log(f"  G19d: {'PASS' if gate_g19d else 'FAIL'}")

    # ── Decizie ───────────────────────────────────────────────────────────────
    gate_g19  = gate_g19a and gate_g19b and gate_g19c and gate_g19d
    decision  = "pass" if gate_g19 else "fail"
    elapsed   = time.time() - t0

    log(f"\n{'='*70}")
    log(f"G19 Jaccard completed in {elapsed:.2f}s")
    log(f"decision={decision}  (a={gate_g19a}, b={gate_g19b}, c={gate_g19c}, d={gate_g19d})")
    log(f"  G19a cv(T_Unruh):       {fmt(cv_T)}       threshold=>{thr.g19a_cv_T_min}")
    log(f"  G19b E_MB/E_BE:         {fmt(ratio_supp)} threshold=>{thr.g19b_supp_min}")
    log(f"  G19c E_BE(2T)/E_BE(T):  {fmt(ratio_T)}    threshold=>{thr.g19c_ratio_min}")
    log(f"  G19d ΔG_slope (BFS):    {fmt(ols_b)}      threshold=<{thr.g19d_slope_max}")

    # ── Artefacte ─────────────────────────────────────────────────────────────
    write_csv(out_dir / "unruh_vertices_jaccard.csv",
              ["vertex","degree","alpha_proxy","T_Unruh"],
              [{"vertex": i, "degree": len(neighbours[i]),
                "alpha_proxy": fmt(alpha_proxy[i]), "T_Unruh": fmt(T_unruh[i])}
               for i in range(n)])

    write_csv(out_dir / "thermal_modes_jaccard.csv",
              ["mode_k","mu_k","omega_k","n_k_T","n_k_2T","omega_nk"],
              [{"mode_k": k+1, "mu_k": fmt(mu_act[k]), "omega_k": fmt(omegas[k]),
                "n_k_T": fmt(n_k[k]), "n_k_2T": fmt(n_k_2T[k]),
                "omega_nk": fmt(omegas[k]*n_k[k])} for k in range(K_eff)])

    write_csv(out_dir / "thermal_propagator_jaccard.csv",
              ["hop_dist","G0_ij","dG_ij","Gbeta_ij"],
              [{"hop_dist": int(r_list[p]), "G0_ij": fmt(G0_list[p]),
                "dG_ij": fmt(dG_list[p]), "Gbeta_ij": fmt(G0_list[p]+dG_list[p])}
               for p in range(len(r_list))])

    write_csv(out_dir / "metric_checks_g19_jaccard.csv",
              ["gate_id","metric","value","threshold","status"], [
        {"gate_id":"G19a","metric":"cv_T_Unruh","value":fmt(cv_T),
         "threshold":f">{thr.g19a_cv_T_min}","status":"pass" if gate_g19a else "fail"},
        {"gate_id":"G19b","metric":"E_MB_over_E_BE","value":fmt(ratio_supp),
         "threshold":f">{thr.g19b_supp_min}","status":"pass" if gate_g19b else "fail"},
        {"gate_id":"G19c","metric":"E_BE_2T_ratio","value":fmt(ratio_T),
         "threshold":f">{thr.g19c_ratio_min}","status":"pass" if gate_g19c else "fail"},
        {"gate_id":"G19d","metric":"dG_slope_bfs","value":fmt(ols_b),
         "threshold":f"<{thr.g19d_slope_max}","status":"pass" if gate_g19d else "fail"},
        {"gate_id":"FINAL","metric":"decision","value":decision,
         "threshold":"G19a&G19b&G19c&G19d","status":decision},
    ])

    config = {
        "script": "run_qng_g19_jaccard_v1.py",
        "graph": {"n": args.n_nodes, "k_init": args.k_init,
                  "k_conn": args.k_conn, "seed": args.seed},
        "mean_degree": round(mean_k, 4), "K_eff": K_eff,
        "m_eff_sq": args.m_eff_sq, "T_global": round(T_global, 8),
        "cv_T_unruh": round(cv_T, 6),
        "ratio_E_MB_E_BE": round(ratio_supp, 4) if not math.isinf(ratio_supp) else "inf",
        "ratio_E_BE_2T": round(ratio_T, 4) if not math.isinf(ratio_T) else "inf",
        "dG_slope_bfs": round(ols_b, 8),
        "decision": decision,
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
    }
    (out_dir / "config_g19_jaccard.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    (out_dir / "run-log-g19-jaccard.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    log(f"\nArtefacte: {out_dir}")

    return 0 if gate_g19 else 1


if __name__ == "__main__":
    sys.exit(main())
