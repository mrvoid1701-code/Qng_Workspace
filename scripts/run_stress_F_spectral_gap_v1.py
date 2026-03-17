#!/usr/bin/env python3
"""
QNG Stress Test — Categoria F: Atac pe gap-ul spectral (G17a)

G17a are marja de 10.9%: mu1=0.01109 > threshold=0.01.
Bomba eleganta: ce perturbari MINIME ale grafului inchid gap-ul?

Atacuri:
  F1  Taiere de muchii (edge removal): remove t% din muchii → mu1 scade?
  F2  Recluster: adaugam clustere izolate → graf aproape disconnected
  F3  Noise adversarial pe Laplacian: perturbam direct eigenvalues
  F4  Seed sweep (50 seed-uri noi): distributia reala a lui mu1
  F5  Shrink N: cat de mic poate fi N pana cand gap-ul dispare?
  F6  Regularizare: crestem k → mu1 creste sau scade?

Intrebari de fond:
  - E mu1=0.01109 un accident de seed sau e robust?
  - Cat de fragila e cuantizarea canonica?
  - Exista o faza critica la care gap-ul se inchide?

Dependinte: stdlib only.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-F-spectral-gap-v1"

# Parametri canonici
N_CANONICAL = 280
K_CANONICAL = 8
SEED_CANONICAL = 3401

N_MODES    = 20
N_ITER_POW = 500   # mai mult pentru acuratete gap
M_EFF_SQ   = 0.014

MU1_THRESHOLD = 0.01
MU1_CANONICAL = 0.2912   # valoarea pe Jaccard v2 (spectral gap real, nu approx)
# Nota: pe Jaccard N=280 k=8 obtinem mu1≈0.291, dar thresholdul G17a e 0.01
# (prag conservator). Marja reala e uriasa. Vom testa cand se pierde.


# ── Graf Jaccard ──────────────────────────────────────────────────────────────

def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
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
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def build_er_graph(n: int, k_avg: int, seed: int):
    rng = random.Random(seed)
    p = k_avg / (n - 1)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Perturbari de graf ────────────────────────────────────────────────────────

def remove_edges_fraction(neighbours: list[list[int]], frac: float, seed: int) -> list[list[int]]:
    """
    F1: Elimina o fractie `frac` din muchii, aleatoriu.
    Test: gap-ul scade cu numarul de legaturi taiate?
    """
    rng = random.Random(seed)
    n = len(neighbours)
    adj = [set(nb) for nb in neighbours]
    all_edges = [(i, j) for i in range(n) for j in adj[i] if i < j]
    n_remove = int(len(all_edges) * frac)
    to_remove = rng.sample(all_edges, n_remove)
    for i, j in to_remove:
        adj[i].discard(j); adj[j].discard(i)
    return [sorted(s) for s in adj]


def add_isolated_cluster(neighbours: list[list[int]], cluster_size: int, seed: int) -> list[list[int]]:
    """
    F2: Adaugam un cluster izolat (disconnected) la graf.
    Test: gap-ul se inchide la 0 cand graful devine disconnected?
    """
    rng = random.Random(seed)
    n = len(neighbours)
    adj = [set(nb) for nb in neighbours]
    # Cluster izolat: clica de cluster_size noduri (deja in graf, dar fara legaturi externe)
    cluster_nodes = rng.sample(range(n), cluster_size)
    # Taiem toate legaturile externe ale clusterului
    for v in cluster_nodes:
        external = [u for u in adj[v] if u not in cluster_nodes]
        for u in external:
            adj[v].discard(u); adj[u].discard(v)
    return [sorted(s) for s in adj]


def rewire_fraction(neighbours: list[list[int]], frac: float, seed: int) -> list[list[int]]:
    """
    F3: Rewire aleator o fractie din muchii (Watts-Strogatz style).
    Test: dezordinea distruge gap-ul sau il intareste?
    """
    rng = random.Random(seed)
    n = len(neighbours)
    adj = [set(nb) for nb in neighbours]
    all_edges = [(i, j) for i in range(n) for j in adj[i] if i < j]
    n_rewire = int(len(all_edges) * frac)
    to_rewire = rng.sample(all_edges, n_rewire)
    for i, j in to_rewire:
        adj[i].discard(j); adj[j].discard(i)
        # Reconnecteaza aleator
        attempts = 0
        while attempts < 20:
            k = rng.randrange(n)
            if k != i and k != j and k not in adj[i]:
                adj[i].add(k); adj[k].add(i)
                break
            attempts += 1
    return [sorted(s) for s in adj]


# ── Spectral ──────────────────────────────────────────────────────────────────

def _dot(u, v):    return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):
    n = math.sqrt(_dot(v, v))
    return [x/n for x in v] if n > 1e-14 else v[:]
def _defl(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i] - c*b[i] for i in range(len(w))]
    return w
def _rw(f, nb):
    return [(sum(f[j] for j in b) / len(b)) if b else 0. for b in nb]


def compute_mu1(neighbours: list[list[int]], seed: int, n_iter: int = N_ITER_POW) -> float:
    """Calculeaza doar mu0 si mu1 — rapid, pentru sweep-uri."""
    n = len(neighbours)
    if n == 0: return float("nan")
    rng = random.Random(seed + 1)
    vecs, mus = [], []
    for _ in range(2):
        v = _norm(_defl([rng.gauss(0., 1.) for _ in range(n)], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    mus_sorted = [mus[k] for k in order]
    return mus_sorted[1] if len(mus_sorted) > 1 else mus_sorted[0]


def is_connected(neighbours: list[list[int]]) -> bool:
    """BFS connectivity check."""
    n = len(neighbours)
    if n == 0: return True
    visited = [False] * n
    q = [0]; visited[0] = True; count = 1
    while q:
        v = q.pop()
        for u in neighbours[v]:
            if not visited[u]:
                visited[u] = True; count += 1; q.append(u)
    return count == n


# ── F1: Edge removal sweep ────────────────────────────────────────────────────

def test_F1_edge_removal(nb_base, fracs, seed):
    """
    Elimina fractii crescatoare de muchii si masoara mu1.
    Cautam pragul critic unde mu1 → 0 (percolation threshold).
    """
    print("\n── F1: Edge removal sweep ─────────────────────────────────────────")
    results = []
    mu1_base = compute_mu1(nb_base, seed)
    n_edges_base = sum(len(nb) for nb in nb_base) // 2
    print(f"  Baseline: mu1={mu1_base:.6f}  edges={n_edges_base}  "
          f"connected={is_connected(nb_base)}")

    for frac in fracs:
        nb_pert = remove_edges_fraction(nb_base, frac, seed + 100)
        mu1 = compute_mu1(nb_pert, seed)
        n_edges = sum(len(nb) for nb in nb_pert) // 2
        conn = is_connected(nb_pert)
        k_avg = 2 * n_edges / len(nb_pert)
        gate = mu1 > MU1_THRESHOLD
        results.append({"frac": frac, "mu1": mu1, "n_edges": n_edges,
                         "k_avg": k_avg, "connected": conn, "gate": gate})
        print(f"  frac={frac:.2f}  mu1={mu1:.6f}  k_avg={k_avg:.1f}  "
              f"connected={conn}  G17a={'PASS' if gate else 'FAIL'}")
    return results


# ── F2: Isolated cluster ──────────────────────────────────────────────────────

def test_F2_isolated_cluster(nb_base, cluster_sizes, seed):
    """
    Adaugam un cluster izolat de marimi crescatoare.
    Daca graful devine disconnected, mu1 = 0 exact (teorema algebrica).
    """
    print("\n── F2: Isolated cluster ───────────────────────────────────────────")
    results = []
    n = len(nb_base)
    for cs in cluster_sizes:
        nb_pert = add_isolated_cluster(nb_base, cs, seed + 200)
        mu1 = compute_mu1(nb_pert, seed)
        conn = is_connected(nb_pert)
        gate = mu1 > MU1_THRESHOLD
        results.append({"cluster_size": cs, "cluster_frac": cs/n,
                         "mu1": mu1, "connected": conn, "gate": gate})
        print(f"  cluster={cs:3d} ({100*cs/n:.0f}%)  mu1={mu1:.6f}  "
              f"connected={conn}  G17a={'PASS' if gate else 'FAIL'}")
    return results


# ── F3: Rewire sweep ──────────────────────────────────────────────────────────

def test_F3_rewire(nb_base, fracs, seed):
    """
    Rewire aleator: distruge structura informationala Jaccard.
    Test: gap-ul depinde de structura sau de gradul mediu?
    """
    print("\n── F3: Random rewire sweep ────────────────────────────────────────")
    results = []
    for frac in fracs:
        nb_pert = rewire_fraction(nb_base, frac, seed + 300)
        mu1 = compute_mu1(nb_pert, seed)
        gate = mu1 > MU1_THRESHOLD
        results.append({"frac": frac, "mu1": mu1, "gate": gate})
        print(f"  rewire={frac:.2f}  mu1={mu1:.6f}  G17a={'PASS' if gate else 'FAIL'}")
    return results


# ── F4: Seed sweep ────────────────────────────────────────────────────────────

def test_F4_seed_sweep(n, k, n_seeds, seed_start):
    """
    50 seed-uri noi: distributia statistica a lui mu1.
    Minim, maxim, medie, deviatie — cat de fragil e 10.9%?
    """
    print(f"\n── F4: Seed sweep ({n_seeds} seeds) ────────────────────────────────")
    mu1_vals = []
    fails = []
    for i in range(n_seeds):
        s = seed_start + i * 7919   # numere prime pentru decorelatie
        nb = build_jaccard_graph(n, k, k, s)
        mu1 = compute_mu1(nb, s, n_iter=300)
        gate = mu1 > MU1_THRESHOLD
        mu1_vals.append(mu1)
        if not gate:
            fails.append((s, mu1))

    mu_min  = min(mu1_vals)
    mu_max  = max(mu1_vals)
    mu_mean = statistics.mean(mu1_vals)
    mu_std  = statistics.stdev(mu1_vals)
    n_fail  = len(fails)
    pass_rate = 100.0 * (n_seeds - n_fail) / n_seeds

    print(f"  mu1: min={mu_min:.6f}  max={mu_max:.6f}  "
          f"mean={mu_mean:.6f}  std={mu_std:.6f}")
    print(f"  Pass rate: {n_seeds-n_fail}/{n_seeds} = {pass_rate:.1f}%")
    print(f"  Sigma-margin: (mean-threshold)/std = "
          f"{(mu_mean-MU1_THRESHOLD)/mu_std:.1f}σ")
    if fails:
        print(f"  FAIL seeds: {[(s, round(m,6)) for s,m in fails[:5]]}...")
    else:
        print(f"  Niciun FAIL in {n_seeds} seed-uri!")

    return {
        "n_seeds": n_seeds,
        "mu1_min": mu_min, "mu1_max": mu_max,
        "mu1_mean": mu_mean, "mu1_std": mu_std,
        "pass_rate": pass_rate,
        "n_fail": n_fail,
        "sigma_margin": (mu_mean - MU1_THRESHOLD) / mu_std,
        "fail_seeds": fails[:10],
        "all_mu1": mu1_vals,
    }


# ── F5: N shrink sweep ────────────────────────────────────────────────────────

def test_F5_shrink_N(n_values, k, seed):
    """
    Shrink N: cat de mic poate fi N pana cand gap-ul dispare?
    Testam teoria la scara Planck (N mic = granularitate groasa).
    """
    print(f"\n── F5: N shrink sweep ──────────────────────────────────────────────")
    results = []
    for n in n_values:
        nb = build_jaccard_graph(n, k, k, seed)
        mu1 = compute_mu1(nb, seed, n_iter=300)
        gate = mu1 > MU1_THRESHOLD
        results.append({"N": n, "mu1": mu1, "gate": gate})
        print(f"  N={n:4d}  mu1={mu1:.6f}  G17a={'PASS' if gate else 'FAIL'}")
    return results


# ── F6: k sweep ───────────────────────────────────────────────────────────────

def test_F6_k_sweep(n, k_values, seed):
    """
    Creste/descreste k: gap-ul e monoton in k?
    La k mic → graf rar → gap mic; la k mare → gap mare?
    """
    print(f"\n── F6: k sweep ─────────────────────────────────────────────────────")
    results = []
    for k in k_values:
        nb = build_jaccard_graph(n, k, k, seed)
        mu1 = compute_mu1(nb, seed, n_iter=300)
        gate = mu1 > MU1_THRESHOLD
        k_actual = sum(len(nb_i) for nb_i in nb) / n
        results.append({"k": k, "k_actual": k_actual, "mu1": mu1, "gate": gate})
        print(f"  k={k:2d} (actual k_avg={k_actual:.1f})  "
              f"mu1={mu1:.6f}  G17a={'PASS' if gate else 'FAIL'}")
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t_total = time.time()

    print("=" * 70)
    print("QNG STRESS TEST — Categoria F: Atac pe gap-ul spectral G17a")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print(f"Canonical: N={N_CANONICAL}, k={K_CANONICAL}, seed={SEED_CANONICAL}")
    print(f"Threshold: mu1 > {MU1_THRESHOLD}  (marja baseline: 10.9%)")
    print("=" * 70)
    print()
    print("Bomba: ce perturbari MINIME inchid gap-ul spectral?")
    print("Daca gap-ul e fragil, cuantizarea canonica e instabila.")
    print()

    # Graf de baza
    nb_base = build_jaccard_graph(N_CANONICAL, K_CANONICAL, K_CANONICAL, SEED_CANONICAL)

    # ── Ruleaza toate testele ──────────────────────────────────────────────────
    r_F1 = test_F1_edge_removal(nb_base,
        fracs=[0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70],
        seed=SEED_CANONICAL)

    r_F2 = test_F2_isolated_cluster(nb_base,
        cluster_sizes=[5, 10, 20, 40, 70, 100, 140],
        seed=SEED_CANONICAL)

    r_F3 = test_F3_rewire(nb_base,
        fracs=[0.10, 0.25, 0.50, 0.75, 1.0],
        seed=SEED_CANONICAL)

    r_F4 = test_F4_seed_sweep(N_CANONICAL, K_CANONICAL,
        n_seeds=50, seed_start=SEED_CANONICAL)

    r_F5 = test_F5_shrink_N(
        n_values=[20, 40, 70, 100, 140, 200, 280],
        k=K_CANONICAL, seed=SEED_CANONICAL)

    r_F6 = test_F6_k_sweep(N_CANONICAL,
        k_values=[3, 4, 5, 6, 7, 8, 10, 12, 16],
        seed=SEED_CANONICAL)

    # ── Sumar final ───────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SUMAR FINAL — Robustete gap spectral")
    print("=" * 70)

    # F1: la ce fractie de muchii eliminate cade?
    f1_fail = next((r for r in r_F1 if not r["gate"]), None)
    if f1_fail:
        print(f"F1 Edge removal: FAIL la frac={f1_fail['frac']:.2f} "
              f"(k_avg={f1_fail['k_avg']:.1f})")
    else:
        print(f"F1 Edge removal: PASS la toate fractiile testate!")

    # F2: cluster izolat
    f2_fail = next((r for r in r_F2 if not r["gate"]), None)
    if f2_fail:
        print(f"F2 Isolated cluster: FAIL la cluster={f2_fail['cluster_size']} "
              f"({100*f2_fail['cluster_frac']:.0f}% din noduri)")
    else:
        print(f"F2 Isolated cluster: PASS (graful ramane connected)")

    # F3: rewire
    f3_fail = next((r for r in r_F3 if not r["gate"]), None)
    if f3_fail:
        print(f"F3 Rewire: FAIL la frac={f3_fail['frac']:.2f}")
    else:
        print(f"F3 Rewire: PASS la toate fractiile testate!")

    # F4: seed sweep
    print(f"F4 Seed sweep: pass_rate={r_F4['pass_rate']:.1f}%  "
          f"mu1_min={r_F4['mu1_min']:.6f}  sigma_margin={r_F4['sigma_margin']:.1f}σ")

    # F5: N shrink
    f5_fail = next((r for r in r_F5 if not r["gate"]), None)
    if f5_fail:
        print(f"F5 N shrink: FAIL la N={f5_fail['N']}")
    else:
        print(f"F5 N shrink: PASS la toate N testate")

    # F6: k sweep
    f6_fail = next((r for r in r_F6 if not r["gate"]), None)
    if f6_fail:
        print(f"F6 k sweep: FAIL la k={f6_fail['k']}")
    else:
        print(f"F6 k sweep: PASS la toate k testate")

    # Verdict
    print()
    any_fail = (f1_fail or f2_fail or f3_fail or
                r_F4["n_fail"] > 0 or f5_fail or f6_fail)
    if not any_fail:
        print("VERDICT: Gap spectral ROBUST sub toate atacurile.")
        print("  G17a e mai stabila decat sugera marja de 10.9%.")
        verdict = "ROBUST"
    else:
        print("VERDICT: Gap spectral VULNERABIL la urmatoarele atacuri:")
        if f1_fail: print(f"  - Edge removal >= {f1_fail['frac']:.0%}")
        if f2_fail: print(f"  - Cluster izolat >= {f2_fail['cluster_size']} noduri")
        if f3_fail: print(f"  - Rewire >= {f3_fail['frac']:.0%}")
        if r_F4["n_fail"] > 0: print(f"  - {r_F4['n_fail']} seed-uri din 50 FAIL")
        if f5_fail: print(f"  - N <= {f5_fail['N']}")
        if f6_fail: print(f"  - k <= {f6_fail['k']}")
        verdict = "VULNERABLE"

    print(f"\nTimp total: {time.time()-t_total:.1f}s")

    # ── Salvare ───────────────────────────────────────────────────────────────
    json_path = OUT_DIR / "stress_F_spectral_gap.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "canonical": {"N": N_CANONICAL, "k": K_CANONICAL, "seed": SEED_CANONICAL},
        "mu1_threshold": MU1_THRESHOLD,
        "verdict": verdict,
        "F1_edge_removal": r_F1,
        "F2_isolated_cluster": r_F2,
        "F3_rewire": r_F3,
        "F4_seed_sweep": {k: v for k, v in r_F4.items() if k != "all_mu1"},
        "F4_all_mu1": r_F4["all_mu1"],
        "F5_shrink_N": r_F5,
        "F6_k_sweep": r_F6,
    }, indent=2), encoding="utf-8")

    # CSV seed sweep pentru analiza statistica
    csv_path = OUT_DIR / "stress_F4_seed_distribution.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", "mu1", "gate"])
        for i, m in enumerate(r_F4["all_mu1"]):
            w.writerow([i, round(m, 8), "PASS" if m > MU1_THRESHOLD else "FAIL"])

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {json_path.name}")
    print(f"  {csv_path.name}")
    print()
    print("=" * 70)
    print(f"STRESS TEST F COMPLET | verdict={verdict}")
    print("=" * 70)

    return 0 if verdict == "ROBUST" else 1


if __name__ == "__main__":
    sys.exit(main())
