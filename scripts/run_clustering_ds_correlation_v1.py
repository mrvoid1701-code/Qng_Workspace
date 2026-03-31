#!/usr/bin/env python3
"""
Clustering ↔ d_s Correlation Analysis

Dacă d_s ≈ 4 e produs de clustering-ul specific grafului Jaccard,
atunci ar trebui să vedem o corelație clară:
  clustering_coefficient ↑  →  d_s → 4

Metodă:
1. Generăm grafuri Jaccard cu parametri variați (N=280, k variabil)
   care au clustering coefficients diferite
2. Generăm grafuri cu același grad dar clustering artificial variat
   (Watts-Strogatz: p=0 → ring (high C), p=1 → random (low C))
3. Calculăm Pearson correlation între C și d_s
4. Scatter plot date: C vs d_s, colorat per tip graf

Metrice cheie analizate:
  - clustering_coefficient (C): cât de „triunghiular" e graful
  - jaccard_homophily (J_mean): media scorurilor Jaccard pe muchii
  - transitivity: nr triunghiuri / nr tripleuri
  - d_s: dimensiunea spectrală

Output:
  clustering_ds_results.csv
  clustering_ds_summary.json
  run-log-clustering-ds.txt
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
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "clustering-ds-v1"

N        = 280
SEED_BASE = 3401

N_WALKS  = 80
N_STEPS  = 18
P_STAY   = 0.5
T_LO, T_HI   = 5, 13
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13

DS_LO, DS_HI = 3.5, 4.5


# ── OLS și metrici ────────────────────────────────────────────────────────────

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


def pearson(xs, ys):
    n = len(xs)
    if n < 3: return 0.
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    dx = math.sqrt(sum((x-mx)**2 for x in xs))
    dy = math.sqrt(sum((y-my)**2 for y in ys))
    if dx < 1e-15 or dy < 1e-15: return 0.
    return num / (dx * dy)


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


# ── Metrici topologice ─────────────────────────────────────────────────────────

def clustering_coefficient(nb):
    total = 0.; count = 0
    nb_sets = [set(x) for x in nb]
    for i in range(len(nb)):
        k = len(nb[i])
        if k < 2: continue
        triangles = sum(1 for u in nb[i] for v in nb[i] if v > u and v in nb_sets[u])
        total += 2 * triangles / (k * (k - 1))
        count += 1
    return total / count if count > 0 else 0.


def transitivity(nb):
    """Fracția tripleuri deschise care formează triunghiuri."""
    nb_sets = [set(x) for x in nb]
    triangles = 0
    triples = 0
    for i in range(len(nb)):
        k = len(nb[i])
        triples += k * (k - 1)
        for u in nb[i]:
            for v in nb[i]:
                if v != u and v in nb_sets[u]:
                    triangles += 1
    return triangles / triples if triples > 0 else 0.


def jaccard_homophily(nb):
    nb_sets = [set(x) for x in nb]
    scores = []
    for i in range(len(nb)):
        for j in nb[i]:
            if j > i:
                Ni = nb_sets[i] | {i}
                Nj = nb_sets[j] | {j}
                inter = len(Ni & Nj); union = len(Ni | Nj)
                scores.append(inter / union if union else 0.)
    if not scores: return 0., 0.
    return statistics.mean(scores), statistics.stdev(scores) if len(scores) > 1 else 0.


def mean_degree(nb):
    degs = [len(x) for x in nb]
    return sum(degs)/len(degs), (statistics.stdev(degs) if len(degs) > 1 else 0.)


def evaluate(nb, seed):
    rng = random.Random(seed)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_window(P_t, IR_LO, IR_HI)
    return ds, r2, ds_uv, ds_ir


# ── Constructori ──────────────────────────────────────────────────────────────

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


def build_watts_strogatz(n, k, p_rewire, seed):
    """
    Watts-Strogatz: inel regular k vecini, rewired cu prob p.
    p=0: inel (C înalt, d_s~1), p=1: random (C mic, d_s random)
    """
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    # Construim inelul
    for i in range(n):
        for r in range(1, k//2 + 1):
            j = (i + r) % n
            adj[i].add(j); adj[j].add(i)
    # Rewire
    for i in range(n):
        for r in range(1, k//2 + 1):
            if rng.random() < p_rewire:
                j = (i + r) % n
                # Alegem nod nou
                candidates = [x for x in range(n) if x != i and x not in adj[i]]
                if not candidates: continue
                new_j = rng.choice(candidates)
                adj[i].discard(j); adj[j].discard(i)
                adj[i].add(new_j); adj[new_j].add(i)
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


# ── Main ───────────────────────────────────────────────────────────────────────

@dataclass
class ClustResult:
    graph_type:    str
    param_label:   str
    seed:          int
    n_nodes:       int
    mean_deg:      float
    deg_std:       float
    clustering:    float
    transitivity:  float
    jaccard_mean:  float
    jaccard_std:   float
    ds:            float
    r2:            float
    ds_uv:         float
    ds_ir:         float
    pass_ds:       bool


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 72)
    log("CLUSTERING ↔ d_s CORRELATION ANALYSIS")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log(f"N={N}")
    log("=" * 72)

    results: list[ClustResult] = []

    # ── Serie 1: Jaccard k_conn = 4..14 (clustering variabil) ─────────────────
    log("\n[S1] Jaccard k_conn sweep (k=4..14, 5 seeds per k)...")
    for k_conn in range(4, 15, 2):
        ds_list, c_list = [], []
        for trial in range(5):
            seed = SEED_BASE + k_conn * 100 + trial * 37
            nb = build_jaccard_graph(N, k_conn, k_conn, seed)
            ds, r2, ds_uv, ds_ir = evaluate(nb, seed ^ 0xABCD)
            md, dstd = mean_degree(nb)
            c = clustering_coefficient(nb)
            tr = transitivity(nb)
            jm, js = jaccard_homophily(nb)
            r = ClustResult("Jaccard_k_sweep", f"k={k_conn}", seed, N,
                            md, dstd, c, tr, jm, js, ds, r2, ds_uv, ds_ir,
                            DS_LO < ds < DS_HI)
            results.append(r)
            ds_list.append(ds); c_list.append(c)
        log(f"  k={k_conn:2d}: d_s={statistics.mean(ds_list):.4f}±{statistics.stdev(ds_list):.4f}  "
            f"C={statistics.mean(c_list):.4f}  PASS={sum(DS_LO<d<DS_HI for d in ds_list)}/5")

    # ── Serie 2: Watts-Strogatz p_rewire sweep (C de la înalt la mic) ─────────
    log("\n[S2] Watts-Strogatz p_rewire sweep (C înalt→mic)...")
    p_values = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
    k_ws = 8
    for p in p_values:
        ds_list, c_list = [], []
        for trial in range(5):
            seed = SEED_BASE + int(p * 10000) + trial * 41
            nb = build_watts_strogatz(N, k_ws, p, seed)
            ds, r2, ds_uv, ds_ir = evaluate(nb, seed ^ 0xBEEF)
            md, dstd = mean_degree(nb)
            c = clustering_coefficient(nb)
            tr = transitivity(nb)
            jm, js = jaccard_homophily(nb)
            r = ClustResult("Watts_Strogatz", f"p={p}", seed, N,
                            md, dstd, c, tr, jm, js, ds, r2, ds_uv, ds_ir,
                            DS_LO < ds < DS_HI)
            results.append(r)
            ds_list.append(ds); c_list.append(c)
        log(f"  p={p:.2f}: d_s={statistics.mean(ds_list):.4f}±{statistics.stdev(ds_list):.4f}  "
            f"C={statistics.mean(c_list):.4f}  PASS={sum(DS_LO<d<DS_HI for d in ds_list)}/5")

    # ── Serie 3: Jaccard canonical (50 seeds, referință) ──────────────────────
    log("\n[S3] Jaccard canonical N=280, k=8 (50 seeds, referință)...")
    for trial in range(50):
        seed = SEED_BASE + trial * 13
        nb = build_jaccard_graph(N, 8, 8, seed)
        ds, r2, ds_uv, ds_ir = evaluate(nb, seed ^ 0xCAFE)
        md, dstd = mean_degree(nb)
        c = clustering_coefficient(nb)
        tr = transitivity(nb)
        jm, js = jaccard_homophily(nb)
        r = ClustResult("Jaccard_canonical", "k=8", seed, N,
                        md, dstd, c, tr, jm, js, ds, r2, ds_uv, ds_ir,
                        DS_LO < ds < DS_HI)
        results.append(r)
    jac_canonical = [r for r in results if r.graph_type == "Jaccard_canonical"]
    log(f"  d_s = {statistics.mean(r.ds for r in jac_canonical):.4f} ± "
        f"{statistics.stdev(r.ds for r in jac_canonical):.4f}")
    log(f"  C   = {statistics.mean(r.clustering for r in jac_canonical):.4f} ± "
        f"{statistics.stdev(r.clustering for r in jac_canonical):.4f}")
    log(f"  J   = {statistics.mean(r.jaccard_mean for r in jac_canonical):.4f} ± "
        f"{statistics.stdev(r.jaccard_mean for r in jac_canonical):.4f}")

    # ── Corelații ─────────────────────────────────────────────────────────────
    log("\n── Corelații Pearson ─────────────────────────────────────────────────")

    # Toate rezultatele împreună
    all_c  = [r.clustering for r in results if not math.isnan(r.ds)]
    all_ds = [r.ds         for r in results if not math.isnan(r.ds)]
    all_jm = [r.jaccard_mean for r in results if not math.isnan(r.ds)]
    all_tr = [r.transitivity  for r in results if not math.isnan(r.ds)]

    corr_c_ds  = pearson(all_c,  all_ds)
    corr_jm_ds = pearson(all_jm, all_ds)
    corr_tr_ds = pearson(all_tr, all_ds)

    log(f"  Pearson(clustering, d_s)       = {corr_c_ds:+.4f}")
    log(f"  Pearson(jaccard_homophily, d_s)= {corr_jm_ds:+.4f}")
    log(f"  Pearson(transitivity, d_s)     = {corr_tr_ds:+.4f}")

    # Corelații doar în seria Jaccard k-sweep
    jac_k = [r for r in results if r.graph_type == "Jaccard_k_sweep"]
    if jac_k:
        jk_c  = [r.clustering   for r in jac_k if not math.isnan(r.ds)]
        jk_ds = [r.ds           for r in jac_k if not math.isnan(r.ds)]
        jk_jm = [r.jaccard_mean for r in jac_k if not math.isnan(r.ds)]
        log(f"\n  În seria Jaccard k-sweep:")
        log(f"  Pearson(clustering, d_s)       = {pearson(jk_c, jk_ds):+.4f}")
        log(f"  Pearson(jaccard_homophily, d_s)= {pearson(jk_jm, jk_ds):+.4f}")

    # WS sweep
    ws = [r for r in results if r.graph_type == "Watts_Strogatz"]
    if ws:
        ws_c  = [r.clustering for r in ws if not math.isnan(r.ds)]
        ws_ds = [r.ds         for r in ws if not math.isnan(r.ds)]
        log(f"\n  În seria Watts-Strogatz:")
        log(f"  Pearson(clustering, d_s)       = {pearson(ws_c, ws_ds):+.4f}")
        log(f"  Notă: WS inel (p=0, C înalt) → d_s≈1 (1D); WS random (p=1) → d_s random")

    # ── Interpretare ──────────────────────────────────────────────────────────
    log("\n── Interpretare ─────────────────────────────────────────────────────")
    log(f"  Jaccard canonical: C={statistics.mean(r.clustering for r in jac_canonical):.4f}")
    log(f"  Comparativ: ER tipic C≈{1./(N-1)*(8):.4f}, WS inel C≈{3*(8//2-1)/(4*(8//2)-2):.4f}")

    if abs(corr_jm_ds) > 0.5:
        log(f"\n  ✓ Jaccard homophily corelează puternic cu d_s (r={corr_jm_ds:+.3f})")
        log(f"    Mecanismul: muchiile Jaccard plasate pe similaritate maximă → triunghi-")
        log(f"    ularitate specifică → spectru Laplacian care produce d_s≈4")
    else:
        log(f"\n  ~ Corelație slabă Jaccard homophily↔d_s (r={corr_jm_ds:+.3f})")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    csv_path = OUT_DIR / "clustering_ds_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()))
        w.writeheader()
        for r in results:
            w.writerow(asdict(r))

    summary = {
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "params": {"N": N, "SEED_BASE": SEED_BASE},
        "correlations_all": {
            "pearson_clustering_ds":        corr_c_ds,
            "pearson_jaccard_homophily_ds":  corr_jm_ds,
            "pearson_transitivity_ds":       corr_tr_ds,
        },
        "jaccard_canonical_50seeds": {
            "ds_mean":  statistics.mean(r.ds for r in jac_canonical),
            "ds_std":   statistics.stdev(r.ds for r in jac_canonical),
            "c_mean":   statistics.mean(r.clustering for r in jac_canonical),
            "c_std":    statistics.stdev(r.clustering for r in jac_canonical),
            "jm_mean":  statistics.mean(r.jaccard_mean for r in jac_canonical),
            "jm_std":   statistics.stdev(r.jaccard_mean for r in jac_canonical),
        },
        "total_time_s": round(time.time() - t0, 1),
    }

    json_path = OUT_DIR / "clustering_ds_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    log_path = OUT_DIR / "run-log-clustering-ds.txt"
    with open(log_path, "w") as f:
        f.write("\n".join(lines))

    log(f"\n  Artefacte: {OUT_DIR}")
    log(f"  Timp total: {time.time()-t0:.1f}s")
    log("=" * 72)


if __name__ == "__main__":
    main()
