#!/usr/bin/env python3
"""
Null Model Test — Configuration Model Randomization

Argumentul central: dacă d_s ≈ 4 e produs de STRUCTURA Jaccard (clustering,
distribuție Jaccard a similarităților) și nu de simplul fapt că graful are
~8 conexiuni per nod, atunci:

  randomizând muchiile cu păstrarea gradelor (configuration model)
  → d_s ar trebui să se schimbe semnificativ față de Jaccard original

Protocoale de randomizare:
  R0: Jaccard original (baseline)
  R1: Configuration model (edge swap, 10× m swaps) — păstrează exact gradele
  R2: Erdős-Rényi cu același k_avg — grad distribuit uniform
  R3: Jaccard cu context ER diferit (alt seed inițial, aceeași regulă Jaccard)
  R4: Jaccard cu k_conn ±2 față de optim (±25%)

Dacă d_s(R1) ≠ d_s(R0): structura topologică contează, nu doar gradul.
Dacă d_s(R3) ≈ d_s(R0): regula Jaccard e robustă la seed-ul contextului.
Dacă d_s(R4) iese din (3.5,4.5): k=8 e punctul critic, nu un accident.

Output:
  null_model_results.csv
  null_model_summary.json
  run-log-null-model.txt
"""

from __future__ import annotations

import json
import math
import random
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "null-model-v1"

# Parametri canonici
N       = 280
K_INIT  = 8
K_CONN  = 8
SEED    = 3401

# Random walk
N_WALKS = 100
N_STEPS = 18
P_STAY  = 0.5
T_LO, T_HI   = 5, 13
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13

# Câte randomizări R1 facem (pentru statistici)
N_RANDOMIZATIONS = 20
# Câte swap-uri per randomizare R1 (standard: 10 × nr_muchii)
SWAP_FACTOR = 10

DS_LO, DS_HI = 3.5, 4.5


# ── Utilitare OLS ──────────────────────────────────────────────────────────────

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


# ── Lazy Random Walk ───────────────────────────────────────────────────────────

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


def evaluate_graph(nb, rng_seed):
    """Calculează d_s, r², ds_uv, ds_ir pe un graf dat."""
    rng = random.Random(rng_seed)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_window(P_t, IR_LO, IR_HI)
    mean_deg = sum(len(x) for x in nb) / len(nb)
    return ds, r2, ds_uv, ds_ir, mean_deg


# ── Constructori de grafuri ────────────────────────────────────────────────────

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


def configuration_model_rewire(nb_orig, n_swaps, seed):
    """
    Edge swap (configuration model): la fiecare swap alege 2 muchii random
    (a-b) și (c-d) și le înlocuiește cu (a-c) și (b-d) sau (a-d) și (b-c),
    dacă nu creează self-loops sau multi-edges.
    Păstrează EXACT secvența de grade.
    """
    rng = random.Random(seed)
    n = len(nb_orig)
    # Construim lista de muchii
    adj = [set(nb_orig[i]) for i in range(n)]
    edges = []
    for i in range(n):
        for j in adj[i]:
            if j > i:
                edges.append([i, j])

    attempted = 0
    success = 0
    max_attempts = n_swaps * 10  # evităm loop infinit

    while success < n_swaps and attempted < max_attempts:
        attempted += 1
        # Alege 2 muchii distincte
        idx1, idx2 = rng.sample(range(len(edges)), 2)
        a, b = edges[idx1]
        c, d = edges[idx2]
        # Alege orientare random
        if rng.random() < 0.5:
            new1, new2 = (a, c), (b, d)
        else:
            new1, new2 = (a, d), (b, c)
        # Normalizăm (min, max)
        new1 = (min(new1), max(new1))
        new2 = (min(new2), max(new2))
        # Verificăm validitate: no self-loop, no multi-edge, distincte
        if (new1[0] == new1[1] or new2[0] == new2[1]
                or new1 == new2
                or new1[1] in adj[new1[0]]
                or new2[1] in adj[new2[0]]):
            continue
        # Aplicăm swap
        adj[a].discard(b); adj[b].discard(a)
        adj[c].discard(d); adj[d].discard(c)
        adj[new1[0]].add(new1[1]); adj[new1[1]].add(new1[0])
        adj[new2[0]].add(new2[1]); adj[new2[1]].add(new2[0])
        edges[idx1] = list(new1)
        edges[idx2] = list(new2)
        success += 1

    return [sorted(s) for s in adj]


def build_er_graph(n, k_avg, seed):
    rng = random.Random(seed)
    p = k_avg / (n - 1)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p:
                adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Metrici suplimentare: clustering și proprietăți topologice ─────────────────

def clustering_coefficient(nb):
    """Coeficient de clustering global (media locală)."""
    total = 0.
    count = 0
    for i, neighbors in enumerate(nb):
        k = len(neighbors)
        if k < 2:
            continue
        triangles = 0
        for u in neighbors:
            for v in neighbors:
                if v > u and v in set(nb[u]):
                    triangles += 1
        total += 2 * triangles / (k * (k - 1))
        count += 1
    return total / count if count > 0 else 0.


def degree_stats(nb):
    degrees = [len(x) for x in nb]
    mean = sum(degrees) / len(degrees)
    var = sum((d - mean)**2 for d in degrees) / len(degrees)
    return mean, math.sqrt(var)


def jaccard_homophily(nb):
    """
    Măsurăm cât de 'Jaccard-like' e un graf:
    pentru fiecare muchie (i,j) calculăm J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)|.
    Un graf Jaccard are muchii plasate acolo unde J e mare.
    """
    nb_sets = [set(x) for x in nb]
    scores = []
    for i in range(len(nb)):
        for j in nb[i]:
            if j > i:
                Ni = nb_sets[i] | {i}
                Nj = nb_sets[j] | {j}
                inter = len(Ni & Nj)
                union = len(Ni | Nj)
                scores.append(inter / union if union else 0.)
    return statistics.mean(scores) if scores else 0., statistics.stdev(scores) if len(scores) > 1 else 0.


# ── Main ───────────────────────────────────────────────────────────────────────

@dataclass
class Result:
    protocol:    str
    trial:       int
    ds:          float
    r2:          float
    ds_uv:       float
    ds_ir:       float
    mean_deg:    float
    deg_std:     float
    clustering:  float
    jaccard_mean: float
    jaccard_std:  float
    pass_ds:     bool
    note:        str


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 72)
    log("NULL MODEL TEST — Structura Jaccard vs Gradul Pur")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log(f"N={N}, K_INIT={K_INIT}, K_CONN={K_CONN}, SEED={SEED}")
    log(f"N_RANDOMIZATIONS={N_RANDOMIZATIONS}, SWAP_FACTOR={SWAP_FACTOR}")
    log("=" * 72)

    results: list[Result] = []

    # ── R0: Jaccard original (baseline) ───────────────────────────────────────
    log("\n[R0] Jaccard original (baseline)...")
    t1 = time.time()
    nb_jaccard = build_jaccard_graph(N, K_INIT, K_CONN, SEED)
    ds, r2, ds_uv, ds_ir, mean_deg = evaluate_graph(nb_jaccard, SEED ^ 0xABCD)
    deg_mean, deg_std = degree_stats(nb_jaccard)
    clust = clustering_coefficient(nb_jaccard)
    jh_mean, jh_std = jaccard_homophily(nb_jaccard)
    r = Result("R0_Jaccard_original", 0, ds, r2, ds_uv, ds_ir,
               mean_deg, deg_std, clust, jh_mean, jh_std,
               DS_LO < ds < DS_HI, "baseline")
    results.append(r)
    log(f"  d_s={ds:.4f}  r²={r2:.3f}  ds_uv={ds_uv:.3f}  ds_ir={ds_ir:.3f}")
    log(f"  mean_deg={mean_deg:.2f}±{deg_std:.2f}  clustering={clust:.4f}")
    log(f"  Jaccard homophily: {jh_mean:.4f}±{jh_std:.4f}")
    log(f"  PASS={r.pass_ds}  ({time.time()-t1:.1f}s)")

    # ── R1: Configuration model (degree-preserving randomization) ─────────────
    log(f"\n[R1] Configuration model ({N_RANDOMIZATIONS} randomizări)...")
    m = sum(len(x) for x in nb_jaccard) // 2  # nr muchii
    n_swaps = SWAP_FACTOR * m
    log(f"  Nr muchii: {m}, swaps per randomizare: {n_swaps}")
    r1_ds = []
    for trial in range(N_RANDOMIZATIONS):
        t1 = time.time()
        nb_rand = configuration_model_rewire(nb_jaccard, n_swaps, seed=SEED + trial * 1000)
        ds, r2, ds_uv, ds_ir, mean_deg = evaluate_graph(nb_rand, SEED ^ 0xDEAD + trial)
        deg_mean, deg_std = degree_stats(nb_rand)
        clust = clustering_coefficient(nb_rand)
        jh_mean, jh_std = jaccard_homophily(nb_rand)
        r = Result(f"R1_config_model", trial, ds, r2, ds_uv, ds_ir,
                   mean_deg, deg_std, clust, jh_mean, jh_std,
                   DS_LO < ds < DS_HI, f"swap_factor={SWAP_FACTOR}")
        results.append(r)
        r1_ds.append(ds)
        log(f"  [trial {trial+1:2d}/{N_RANDOMIZATIONS}] d_s={ds:.4f}  clust={clust:.4f}  "
            f"J_mean={jh_mean:.4f}  PASS={r.pass_ds}  ({time.time()-t1:.1f}s)")

    r1_mean = statistics.mean(r1_ds)
    r1_std  = statistics.stdev(r1_ds) if len(r1_ds) > 1 else 0.
    r1_pass = sum(1 for d in r1_ds if DS_LO < d < DS_HI)
    log(f"\n  R1 summary: d_s = {r1_mean:.4f} ± {r1_std:.4f}  "
        f"PASS={r1_pass}/{N_RANDOMIZATIONS} ({100*r1_pass/N_RANDOMIZATIONS:.0f}%)")

    # ── R2: Erdős-Rényi cu același k_avg ─────────────────────────────────────
    log(f"\n[R2] Erdős-Rényi k_avg≈{K_CONN} (10 instanțe)...")
    r2_ds_list = []
    nb_jaccard_mean_deg = sum(len(x) for x in nb_jaccard) / N
    for trial in range(10):
        t1 = time.time()
        nb_er = build_er_graph(N, nb_jaccard_mean_deg, seed=SEED + 200 + trial)
        ds_er, r2_er, ds_uv_er, ds_ir_er, mean_deg_er = evaluate_graph(nb_er, SEED ^ 0xBEEF + trial)
        deg_mean_er, deg_std_er = degree_stats(nb_er)
        clust_er = clustering_coefficient(nb_er)
        jh_mean_er, jh_std_er = jaccard_homophily(nb_er)
        r = Result("R2_ER", trial, ds_er, r2_er, ds_uv_er, ds_ir_er,
                   mean_deg_er, deg_std_er, clust_er, jh_mean_er, jh_std_er,
                   DS_LO < ds_er < DS_HI, f"er_k_avg={nb_jaccard_mean_deg:.1f}")
        results.append(r)
        r2_ds_list.append(ds_er)
        log(f"  [trial {trial+1:2d}/10] d_s={ds_er:.4f}  clust={clust_er:.4f}  "
            f"J_mean={jh_mean_er:.4f}  PASS={r.pass_ds}  ({time.time()-t1:.1f}s)")

    r2_mean = statistics.mean(r2_ds_list)
    r2_std  = statistics.stdev(r2_ds_list) if len(r2_ds_list) > 1 else 0.
    r2_pass = sum(1 for d in r2_ds_list if DS_LO < d < DS_HI)
    log(f"\n  R2 summary: d_s = {r2_mean:.4f} ± {r2_std:.4f}  "
        f"PASS={r2_pass}/10 ({100*r2_pass/10:.0f}%)")

    # ── R3: Jaccard cu seed de context diferit (robustețea regulii) ───────────
    log(f"\n[R3] Jaccard cu seed de context diferit (10 instanțe)...")
    r3_ds_list = []
    for trial in range(10):
        t1 = time.time()
        nb_j2 = build_jaccard_graph(N, K_INIT, K_CONN, seed=SEED + 5000 + trial * 137)
        ds_j2, r2_j2, ds_uv_j2, ds_ir_j2, mean_deg_j2 = evaluate_graph(nb_j2, SEED ^ 0xCAFE + trial)
        deg_mean_j2, deg_std_j2 = degree_stats(nb_j2)
        clust_j2 = clustering_coefficient(nb_j2)
        jh_mean_j2, jh_std_j2 = jaccard_homophily(nb_j2)
        r = Result("R3_Jaccard_diff_seed", trial, ds_j2, r2_j2, ds_uv_j2, ds_ir_j2,
                   mean_deg_j2, deg_std_j2, clust_j2, jh_mean_j2, jh_std_j2,
                   DS_LO < ds_j2 < DS_HI, f"ctx_seed={SEED+5000+trial*137}")
        results.append(r)
        r3_ds_list.append(ds_j2)
        log(f"  [trial {trial+1:2d}/10] d_s={ds_j2:.4f}  clust={clust_j2:.4f}  "
            f"J_mean={jh_mean_j2:.4f}  PASS={r.pass_ds}  ({time.time()-t1:.1f}s)")

    r3_mean = statistics.mean(r3_ds_list)
    r3_std  = statistics.stdev(r3_ds_list) if len(r3_ds_list) > 1 else 0.
    r3_pass = sum(1 for d in r3_ds_list if DS_LO < d < DS_HI)
    log(f"\n  R3 summary: d_s = {r3_mean:.4f} ± {r3_std:.4f}  "
        f"PASS={r3_pass}/10 ({100*r3_pass/10:.0f}%)")

    # ── R4: Jaccard cu k_conn deviat (±1, ±2) ────────────────────────────────
    log(f"\n[R4] Jaccard k_conn deviat față de optim (k={K_CONN})...")
    r4_results = {}
    for k_test in [K_CONN - 2, K_CONN - 1, K_CONN, K_CONN + 1, K_CONN + 2]:
        ds_list_k = []
        for trial in range(5):
            nb_k = build_jaccard_graph(N, K_INIT, k_test, seed=SEED + 300 + trial * 77)
            ds_k, r2_k, ds_uv_k, ds_ir_k, mean_deg_k = evaluate_graph(nb_k, SEED ^ 0x1234 + trial)
            deg_mean_k, deg_std_k = degree_stats(nb_k)
            clust_k = clustering_coefficient(nb_k)
            jh_mean_k, jh_std_k = jaccard_homophily(nb_k)
            r = Result(f"R4_k{k_test}", trial, ds_k, r2_k, ds_uv_k, ds_ir_k,
                       mean_deg_k, deg_std_k, clust_k, jh_mean_k, jh_std_k,
                       DS_LO < ds_k < DS_HI, f"k_conn={k_test}")
            results.append(r)
            ds_list_k.append(ds_k)
        r4_results[k_test] = ds_list_k
        mean_k = statistics.mean(ds_list_k)
        pass_k = sum(1 for d in ds_list_k if DS_LO < d < DS_HI)
        log(f"  k_conn={k_test}: d_s = {mean_k:.4f} ± {statistics.stdev(ds_list_k):.4f}  "
            f"PASS={pass_k}/5")

    # ── Sumar final ────────────────────────────────────────────────────────────
    log("\n" + "=" * 72)
    log("SUMAR COMPARATIV")
    log("=" * 72)

    baseline_ds = results[0].ds
    log(f"\n  Jaccard original (R0):        d_s = {baseline_ds:.4f}")
    log(f"  Config model R1 ({N_RANDOMIZATIONS}x):     d_s = {r1_mean:.4f} ± {r1_std:.4f}  "
        f"PASS={r1_pass}/{N_RANDOMIZATIONS}")
    log(f"  Erdős-Rényi R2 (10x):          d_s = {r2_mean:.4f} ± {r2_std:.4f}  "
        f"PASS={r2_pass}/10")
    log(f"  Jaccard diff seed R3 (10x):    d_s = {r3_mean:.4f} ± {r3_std:.4f}  "
        f"PASS={r3_pass}/10")

    delta_R1 = abs(r1_mean - baseline_ds)
    delta_R2 = abs(r2_mean - baseline_ds)
    delta_R3 = abs(r3_mean - baseline_ds)

    log(f"\n  Δd_s(R1 vs R0) = {delta_R1:.4f}  (configuration model vs Jaccard)")
    log(f"  Δd_s(R2 vs R0) = {delta_R2:.4f}  (ER vs Jaccard)")
    log(f"  Δd_s(R3 vs R0) = {delta_R3:.4f}  (Jaccard diff seed vs Jaccard)")

    log("\n── Interpretare ──────────────────────────────────────────────────────")

    # Criteriu: dacă R1 diferă >0.3 față de R0, structura contează
    if delta_R1 > 0.3:
        log(f"  ✓ R1: Δd_s={delta_R1:.3f} > 0.3 — STRUCTURA Jaccard produce d_s≈4,")
        log(f"    NU simplul grad. Randomizarea muchiilor (cu grad fix) rupe d_s≈4.")
        struct_verdict = "CONFIRMAT: structura topologică Jaccard e esențială"
    elif delta_R1 > 0.1:
        log(f"  ~ R1: Δd_s={delta_R1:.3f} ∈ (0.1, 0.3) — structura contează parțial.")
        struct_verdict = "PARȚIAL: structura contribuie, dar nu e singurul factor"
    else:
        log(f"  ✗ R1: Δd_s={delta_R1:.3f} < 0.1 — d_s≈4 e determinat DOAR de grad,")
        log(f"    nu de structura Jaccard specifică. Investigație suplimentară necesară.")
        struct_verdict = "NECONCLUDENT: gradul domină, structura Jaccard nu pare esențială"

    if delta_R3 < 0.15:
        seed_verdict = "CONFIRMAT: regula Jaccard e robustă la seed-ul contextului ER"
    else:
        seed_verdict = "ATENȚIE: d_s variază cu seed-ul contextului ER inițial"

    log(f"\n  Seed robustness: {seed_verdict}")
    log(f"\n  VERDICT FINAL: {struct_verdict}")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    import csv

    csv_path = OUT_DIR / "null_model_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        w.writeheader()
        for r in results:
            w.writerow(asdict(r))

    summary = {
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "params": {"N": N, "K_INIT": K_INIT, "K_CONN": K_CONN, "SEED": SEED,
                   "N_RANDOMIZATIONS": N_RANDOMIZATIONS, "SWAP_FACTOR": SWAP_FACTOR},
        "R0_Jaccard_original": {"ds": results[0].ds, "r2": results[0].r2,
                                 "clustering": results[0].clustering,
                                 "jaccard_homophily_mean": results[0].jaccard_mean},
        "R1_config_model": {"ds_mean": r1_mean, "ds_std": r1_std,
                            "pass_frac": r1_pass/N_RANDOMIZATIONS,
                            "delta_vs_R0": delta_R1},
        "R2_ER": {"ds_mean": r2_mean, "ds_std": r2_std,
                  "pass_frac": r2_pass/10, "delta_vs_R0": delta_R2},
        "R3_Jaccard_diff_seed": {"ds_mean": r3_mean, "ds_std": r3_std,
                                  "pass_frac": r3_pass/10, "delta_vs_R0": delta_R3},
        "R4_k_sweep": {str(k): {"ds_mean": statistics.mean(v),
                                 "ds_std": statistics.stdev(v) if len(v) > 1 else 0.,
                                 "pass_frac": sum(1 for d in v if DS_LO < d < DS_HI)/len(v)}
                       for k, v in r4_results.items()},
        "struct_verdict": struct_verdict,
        "seed_verdict": seed_verdict,
        "total_time_s": round(time.time() - t0, 1),
    }

    json_path = OUT_DIR / "null_model_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    log_path = OUT_DIR / "run-log-null-model.txt"
    with open(log_path, "w") as f:
        f.write("\n".join(lines))

    log(f"\n  Artefacte salvate în: {OUT_DIR}")
    log(f"  Timp total: {time.time()-t0:.1f}s")
    log("=" * 72)


if __name__ == "__main__":
    main()
