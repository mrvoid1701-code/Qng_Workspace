#!/usr/bin/env python3
"""
QNG Stress Test — Categoria A: Robustete fata de tipul grafului

Bomba eleganta: daca d_s=4 emerge si pe grafuri ER/BA (fara principiu
informational), atunci Jaccard e irelevant — d_s=4 e un artifact al
gradului mediu k≈8, nu al conectivitatii informationale.

Daca d_s=4 apare NUMAI pe Jaccard, atunci principiul
  J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)|
este ingredientul fizic esential care genereaza spatiu-timp 4D.

Grafuri testate (toate N=280, k_avg≈8):
  A0  Jaccard Informational   — baseline (teoretic canonical)
  A1  Erdős-Rényi (ER)        — pur aleatoriu, fara structura
  A2  Barabási-Albert (BA)    — scale-free, hub-uri, lege putere
  A3  Grid 2D (periodic BC)   — retea cristalina, d_s=2 asteptat
  A4  k-NN 2D (vechi)         — embedding spatial, d_s≈1.35 asteptat
  A5  Sparse (k=3)            — sub pragul saturat, aproape de arbore
  A6  Complete K_N            — orice nod conectat la toti

Metrici masurate uniform:
  d_s     — dimensiune spectrala (lazy RW)
  mu1     — gap spectral (cuantizare canonica, G17a)
  cv_G    — omogenitate vacuum (G18c)
  n_IPR   — localizare moduri (G18b)
  E0_mode — energie zero-point per mod (G17c)

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

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-A-graph-types-v1"

# Parametri canonici (identici cu Jaccard baseline)
N      = 280
K_AVG  = 8
SEED   = 3401

# Spectral
N_MODES    = 20
N_ITER_POW = 350
M_EFF_SQ   = 0.014

# Lazy RW
N_WALKS = 100
N_STEPS = 18
T_LO    = 5
T_HI    = 13
P_STAY  = 0.5

# Thresholds (identice cu G17-G18 oficiale)
THRESH = {
    "mu1_min":    0.01,
    "cv_G_max":   0.50,
    "n_IPR_max":  5.0,
    "E0_lo":      0.05,
    "E0_hi":      5.0,
    "ds_lo":      3.5,
    "ds_hi":      4.5,
}


# ── Constructori de grafuri ────────────────────────────────────────────────────

def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int):
    """Jaccard Informational Graph — principiu similaritate informationala."""
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
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs) if degs else 1
    sigma = [min(max(d / mx + rng.gauss(0., 0.02), 0.), 1.) for d in degs]
    return sigma, nb


def build_er_graph(n: int, k_avg: int, seed: int):
    """Erdős-Rényi — grafuri pur aleatorii, fara structura informationala."""
    rng = random.Random(seed)
    p = k_avg / (n - 1)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j); adj[j].add(i)
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs) if degs else 1
    sigma = [d / mx for d in degs]
    return sigma, nb


def build_ba_graph(n: int, m: int, seed: int):
    """
    Barabási-Albert — scale-free, preferential attachment.
    m legaturi per nod nou → k_avg ≈ 2m.
    La m=4: k_avg ≈ 8.
    """
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    # Initializare: clica completa de m+1 noduri
    init = min(m + 1, n)
    for i in range(init):
        for j in range(i + 1, init):
            adj[i].add(j); adj[j].add(i)
    degrees = [len(adj[i]) for i in range(n)]
    for v in range(init, n):
        total_deg = sum(degrees[:v])
        if total_deg == 0:
            targets = rng.sample(range(v), min(m, v))
        else:
            # Preferential attachment: prob ~ degree
            chosen = set()
            attempts = 0
            while len(chosen) < min(m, v) and attempts < m * 20:
                attempts += 1
                r = rng.random() * total_deg
                cum = 0.
                for u in range(v):
                    cum += degrees[u]
                    if cum >= r:
                        chosen.add(u); break
            targets = list(chosen)
        for u in targets:
            adj[v].add(u); adj[u].add(v)
            degrees[v] += 1; degrees[u] += 1
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs) if degs else 1
    sigma = [d / mx for d in degs]
    return sigma, nb


def build_grid_2d_graph(n: int, seed: int):
    """
    Grid 2D periodic (torus) — retea cristalina.
    Cel mai apropiat patrat: L = floor(sqrt(n)).
    Conexiuni: sus/jos/stanga/dreapta + diagonale → k≈8.
    Asteptat: d_s ≈ 2 (dimensiune topologica a torului).
    """
    rng = random.Random(seed)
    L = int(math.isqrt(n))
    n_actual = L * L
    adj = [set() for _ in range(n_actual)]
    for r in range(L):
        for c in range(L):
            v = r * L + c
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    u = ((r + dr) % L) * L + ((c + dc) % L)
                    adj[v].add(u); adj[u].add(v)
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs) if degs else 1
    sigma = [d / mx + rng.gauss(0., 0.01) for d in degs]
    sigma = [min(max(s, 0.), 1.) for s in sigma]
    return sigma, nb


def build_knn_2d_graph(n: int, k: int, seed: int):
    """
    k-NN 2D (metoda veche, pre-Jaccard).
    Puncte aleatoare in [0,1]^2, fiecare conectat la cei mai apropiati k vecini.
    Asteptat: d_s ≈ 1.3 (artifact embedding 2D).
    """
    rng = random.Random(seed)
    pts = [(rng.random(), rng.random()) for _ in range(n)]
    adj = [set() for _ in range(n)]
    for i in range(n):
        dists = []
        for j in range(n):
            if j == i: continue
            dx = pts[i][0] - pts[j][0]; dy = pts[i][1] - pts[j][1]
            dists.append((dx*dx + dy*dy, j))
        dists.sort()
        for _, j in dists[:k]:
            adj[i].add(j); adj[j].add(i)
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs) if degs else 1
    sigma = [d / mx for d in degs]
    return sigma, nb


def build_sparse_graph(n: int, k: int, seed: int):
    """
    Graf rar (k=3) — aproape de pragul de conexitate.
    Test: sub-saturat, d_s ar trebui sa cada.
    """
    return build_er_graph(n, k, seed)


def build_complete_graph(n: int):
    """
    Graf complet K_N — fiecare nod conectat la toti.
    Test extrem: d_s → nedefinit sau 0 (random walk se intoarce imediat).
    """
    nb = [[j for j in range(n) if j != i] for i in range(n)]
    sigma = [1.0] * n
    return sigma, nb


# ── Algoritmi spectral (identici cu G17/G18) ──────────────────────────────────

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


def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    vecs, mus = [], []
    n = len(neighbours)
    for _ in range(n_modes):
        v = _norm(_defl([rng.gauss(0., 1.) for _ in range(n)], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


def lazy_rw_simulation(neighbours, n_walks, n_steps, rng, p_stay=P_STAY):
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        if not neighbours[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                if rng.random() > p_stay:
                    nb = neighbours[v]
                    if nb: v = rng.choice(nb)
                if v == start: counts[t] += 1
    return [counts[t] / total for t in range(n_steps + 1)]


def ols_fit(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my - b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    ss_res = sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))
    return a, b, max(0., 1. - ss_res/ss_tot)


def spectral_dimension(P_t, t_lo, t_hi):
    log_t, log_P = [], []
    for t in range(t_lo, t_hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            log_t.append(math.log(t)); log_P.append(math.log(P_t[t]))
    if len(log_t) < 2: return float("nan"), 0.
    _, b, r2 = ols_fit(log_t, log_P)
    return -2. * b, r2


# ── Evaluare completa a unui graf ─────────────────────────────────────────────

def evaluate_graph(name: str, sigma, neighbours, seed: int) -> dict:
    n = len(neighbours)
    if n == 0:
        return {"name": name, "n": 0, "error": "empty graph"}

    degs = [len(nb) for nb in neighbours]
    k_avg = sum(degs) / n
    k_max = max(degs)
    k_min = min(degs)

    t0 = time.time()

    # Spectral
    rng_spec = random.Random(seed + 1)
    mus, eigvecs = compute_eigenmodes(neighbours, N_MODES, N_ITER_POW, rng_spec)

    mu0  = mus[0]
    mu1  = mus[1] if len(mus) > 1 else 0.
    mu_max = mus[-1]

    active_idx  = list(range(1, len(mus)))
    K_eff       = len(active_idx)
    mu_active   = [mus[k]     for k in active_idx]
    vecs_active = [eigvecs[k] for k in active_idx]
    omegas      = [math.sqrt(mu + M_EFF_SQ) for mu in mu_active]

    # Zero-point energy
    E0 = 0.5 * sum(omegas)
    E0_mode = E0 / K_eff if K_eff > 0 else float("nan")

    # IPR
    ipr_vals = [sum(x**4 for x in v) for v in vecs_active]
    n_ipr = n * statistics.mean(ipr_vals)

    # Propagator local G(i,i) → cv
    G_diag = [0.] * n
    for k in range(K_eff):
        inv2w = 1. / (2. * omegas[k])
        for i in range(n):
            G_diag[i] += vecs_active[k][i]**2 * inv2w
    mean_G = statistics.mean(G_diag)
    std_G  = statistics.stdev(G_diag)
    cv_G   = std_G / mean_G if mean_G > 1e-12 else float("inf")

    # Lazy RW → d_s
    rng_walk = random.Random(seed + 4)
    P_t = lazy_rw_simulation(neighbours, N_WALKS, N_STEPS, rng_walk)
    d_s, r2_ds = spectral_dimension(P_t, T_LO, T_HI)

    # Running dimension
    running = {}
    for tl, th in [(2, 5), (5, 9), (9, 13)]:
        ds_w, r2_w = spectral_dimension(P_t, tl, th)
        running[f"ds_t{tl}-{th}"] = round(ds_w, 3) if not math.isnan(ds_w) else None

    elapsed = time.time() - t0

    # Gate evaluation
    gate_mu1   = mu1     > THRESH["mu1_min"]
    gate_cv    = cv_G    < THRESH["cv_G_max"]
    gate_ipr   = n_ipr   < THRESH["n_IPR_max"]
    gate_E0    = THRESH["E0_lo"] < E0_mode < THRESH["E0_hi"]
    gate_ds    = not math.isnan(d_s) and THRESH["ds_lo"] < d_s < THRESH["ds_hi"]
    all_pass   = gate_mu1 and gate_cv and gate_ipr and gate_E0 and gate_ds

    def p(b): return "PASS" if b else "FAIL"

    return {
        "name":    name,
        "n":       n,
        "k_avg":   round(k_avg, 2),
        "k_max":   k_max,
        "k_min":   k_min,
        "mu0":     round(mu0,   6),
        "mu1":     round(mu1,   6),
        "mu_max":  round(mu_max, 4),
        "E0_mode": round(E0_mode, 4),
        "n_IPR":   round(n_ipr,  4),
        "cv_G":    round(cv_G,   4),
        "d_s":     round(d_s, 4) if not math.isnan(d_s) else None,
        "r2_ds":   round(r2_ds, 4),
        "running": running,
        "gates": {
            "mu1":  p(gate_mu1),
            "cv":   p(gate_cv),
            "IPR":  p(gate_ipr),
            "E0":   p(gate_E0),
            "ds":   p(gate_ds),
            "ALL":  p(all_pass),
        },
        "elapsed_s": round(elapsed, 2),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("QNG STRESS TEST — Categoria A: Robustete fata de tipul grafului")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print(f"N={N}, K_AVG≈{K_AVG}, SEED={SEED}")
    print("=" * 72)
    print()
    print("Bomba eleganta: d_s=4 e un accident al tipului de graf,")
    print("sau e proprietatea unica a principiului informational Jaccard?")
    print()

    # ── Construieste grafuri ───────────────────────────────────────────────────
    configs = [
        ("A0_Jaccard",    lambda: build_jaccard_graph(N, K_AVG, K_AVG, SEED)),
        ("A1_ER",         lambda: build_er_graph(N, K_AVG, SEED)),
        ("A2_BA_m4",      lambda: build_ba_graph(N, 4, SEED)),       # k_avg≈8
        ("A3_Grid2D",     lambda: build_grid_2d_graph(N, SEED)),     # k=8 (8-connected)
        ("A4_kNN2D",      lambda: build_knn_2d_graph(N, K_AVG, SEED)),
        ("A5_Sparse_k3",  lambda: build_sparse_graph(N, 3, SEED)),
        ("A6_Complete",   lambda: build_complete_graph(N)),
    ]

    results = []
    for name, builder in configs:
        print(f"[{name}] Construiesc graful...", end=" ", flush=True)
        t_build = time.time()
        sigma, nb = builder()
        n_actual = len(nb)
        k_actual = sum(len(b) for b in nb) / n_actual if n_actual else 0
        print(f"n={n_actual}, k_avg={k_actual:.1f}  ({time.time()-t_build:.2f}s)")

        print(f"[{name}] Evaluez metrici...", end=" ", flush=True)
        res = evaluate_graph(name, sigma, nb, SEED)
        results.append(res)
        g = res["gates"]
        print(f"done ({res['elapsed_s']}s)")
        print(f"  d_s={res['d_s']}  μ₁={res['mu1']}  cv_G={res['cv_G']}  "
              f"n_IPR={res['n_IPR']}  E0/mode={res['E0_mode']}")
        print(f"  Gates: mu1={g['mu1']} cv={g['cv']} IPR={g['IPR']} "
              f"E0={g['E0']} ds={g['ds']} | ALL={g['ALL']}")
        print()

    # ── Tabel comparativ ──────────────────────────────────────────────────────
    print("=" * 72)
    print("TABEL COMPARATIV — metrici cheie vs baseline Jaccard")
    print("=" * 72)
    header = f"{'Graf':<18} {'d_s':>6} {'mu1':>8} {'cv_G':>6} {'n_IPR':>6} {'E0/mod':>7} {'k_avg':>6} | {'ALL':>4}"
    print(header)
    print("-" * 72)
    baseline = next(r for r in results if r["name"] == "A0_Jaccard")
    for r in results:
        ds_str  = f"{r['d_s']:.3f}" if r['d_s'] is not None else " nan"
        mark = " ←" if r["name"] == "A0_Jaccard" else "  "
        flag = r["gates"]["ALL"]
        print(f"{r['name']:<18} {ds_str:>6} {r['mu1']:>8.4f} {r['cv_G']:>6.3f} "
              f"{r['n_IPR']:>6.2f} {r['E0_mode']:>7.4f} {r['k_avg']:>6.1f} | "
              f"{flag:>4}{mark}")
    print()

    # ── Analiza critica ───────────────────────────────────────────────────────
    print("=" * 72)
    print("ANALIZA CRITICA")
    print("=" * 72)
    baseline_ds = baseline["d_s"] or 0.

    ds_pass = [r for r in results if r["gates"]["ds"] == "PASS"]
    ds_fail = [r for r in results if r["gates"]["ds"] == "FAIL"]

    print(f"\nGrafuri cu d_s ∈ (3.5, 4.5):")
    for r in ds_pass:
        print(f"  {r['name']:<18} d_s={r['d_s']}")

    print(f"\nGrafuri cu d_s ∉ (3.5, 4.5):")
    for r in ds_fail:
        print(f"  {r['name']:<18} d_s={r['d_s']}")

    print()
    if len(ds_pass) == 1 and ds_pass[0]["name"] == "A0_Jaccard":
        print("VERDICT: d_s=4 este UNIC pentru Jaccard.")
        print("  Principiul informational J(i,j) este ingredientul fizic esential.")
        print("  Teoria QNG NU e un artifact al tipului de graf.")
        verdict = "JACCARD_UNIQUE"
    elif len(ds_pass) > 1:
        others = [r["name"] for r in ds_pass if r["name"] != "A0_Jaccard"]
        print(f"VERDICT: d_s=4 apare si pe: {others}")
        print("  ATENTIE: Jaccard nu e singurul graf cu d_s≈4.")
        print("  Intrebare deschisa: ce proprietate comuna produce d_s=4?")
        verdict = "NOT_UNIQUE"
    else:
        print("VERDICT: Niciun graf nu produce d_s ∈ (3.5, 4.5)!")
        print("  EROARE CRITICA: teoria QNG e sensibila la seed/parametri.")
        verdict = "NONE_PASS"

    # ── Dimensiune ruleaza (scale-dependence) ────────────────────────────────
    print()
    print("DIMENSIUNE RULEAZA pe Jaccard (scale-dependence d_s vs t):")
    jac = next(r for r in results if r["name"] == "A0_Jaccard")
    for window, ds_val in jac["running"].items():
        print(f"  {window}: d_s = {ds_val}")
    print("  (Daca d_s creste cu t: UV-IR running, ca in CDT/LQG)")

    # ── Salvare artefacte ──────────────────────────────────────────────────────
    # CSV comparativ
    csv_path = OUT_DIR / "stress_A_comparison.csv"
    fieldnames = ["name", "n", "k_avg", "k_max", "k_min",
                  "mu0", "mu1", "mu_max", "E0_mode", "n_IPR", "cv_G",
                  "d_s", "r2_ds",
                  "gate_mu1", "gate_cv", "gate_IPR", "gate_E0", "gate_ds", "gate_ALL",
                  "elapsed_s"]
    rows = []
    for r in results:
        g = r["gates"]
        rows.append({
            "name": r["name"], "n": r["n"], "k_avg": r["k_avg"],
            "k_max": r["k_max"], "k_min": r["k_min"],
            "mu0": r["mu0"], "mu1": r["mu1"], "mu_max": r["mu_max"],
            "E0_mode": r["E0_mode"], "n_IPR": r["n_IPR"], "cv_G": r["cv_G"],
            "d_s": r["d_s"] if r["d_s"] is not None else "nan",
            "r2_ds": r["r2_ds"],
            "gate_mu1": g["mu1"], "gate_cv": g["cv"], "gate_IPR": g["IPR"],
            "gate_E0": g["E0"], "gate_ds": g["ds"], "gate_ALL": g["ALL"],
            "elapsed_s": r["elapsed_s"],
        })
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)

    # JSON complet
    json_path = OUT_DIR / "stress_A_results.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "params": {"N": N, "K_AVG": K_AVG, "SEED": SEED,
                   "N_MODES": N_MODES, "N_WALKS": N_WALKS, "N_STEPS": N_STEPS},
        "thresholds": THRESH,
        "verdict": verdict,
        "results": results,
    }, indent=2), encoding="utf-8")

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {csv_path.name}")
    print(f"  {json_path.name}")
    print()
    print("=" * 72)
    print(f"STRESS TEST A COMPLET | verdict={verdict}")
    print("=" * 72)

    # Exit code: 0 daca Jaccard e unic sau robust, 1 daca teoria cade
    return 0 if verdict in ("JACCARD_UNIQUE", "NOT_UNIQUE") else 1


if __name__ == "__main__":
    sys.exit(main())
