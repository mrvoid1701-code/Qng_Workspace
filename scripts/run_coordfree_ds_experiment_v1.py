#!/usr/bin/env python3
"""
Coordinate-Free Spectral Dimension Experiment (v1)

Motivatie: graful standard QNG e construit din k-NN pe puncte random 2D.
Dimensiunea spectral d_s ≈ 1.3 reflecta topologia planara impusa artificial
prin embedding-ul 2D.

Intrebarea: daca construim graful FARA coordonate spatiale, din principii
abstracte, ce d_s iese spontan?

Trei tipuri de graf coordinate-free:
  A) Erdos-Renyi (random pur) - conectivitate uniforma, fara geometrie
  B) Barabasi-Albert (preferential attachment) - scale-free, ca retele reale
  C) Causal-random (DAG transitivizat) - inspirat din causal sets / CDT

Fiecare graf e masurat prin aceeasi metoda random-walk ca G18d din QNG.

Output: tabel comparativ d_s pentru fiecare tip de graf vs. graful 2D k-NN.
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path


# ── Parametri ────────────────────────────────────────────────────────────────
N_NODES   = 280     # identic cu DS-002 din QNG
K_TARGET  = 8       # grad mediu aproximativ (ca k-NN QNG)
N_WALKS   = 80      # identic cu G18d
N_STEPS   = 12      # identic cu G18d
T_LO      = 4       # identic cu G18d
T_HI      = 10      # identic cu G18d
SEED      = 3401    # identic cu QNG default


# ── Utilitare ─────────────────────────────────────────────────────────────────
def ols_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    Sxx = sum((x - mx) ** 2 for x in xs)
    Sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    if abs(Sxx) < 1e-30:
        return my, 0.0, 0.0
    b = Sxy / Sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    if ss_tot < 1e-30:
        return a, b, 1.0
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n))
    return a, b, max(0.0, 1.0 - ss_res / ss_tot)


def random_walk_return_prob(
    neighbours: list[list[int]], n_walks: int, n_steps: int, rng: random.Random
) -> list[float]:
    """P(t) = probabilitate revenire la origine dupa t pasi."""
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        nb_start = neighbours[start]
        if not nb_start:
            continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                nb = neighbours[v]
                v = rng.choice(nb) if nb else v
                if v == start:
                    counts[t] += 1
    return [counts[t] / total for t in range(n_steps + 1)]


def spectral_dimension(P_t: list[float], t_lo: int, t_hi: int) -> tuple[float, float, float]:
    """d_s = -2 * slope(log P vs log t). Returneaza (d_s, slope, r2)."""
    log_t, log_P = [], []
    for t in range(t_lo, t_hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            log_t.append(math.log(t))
            log_P.append(math.log(P_t[t]))
    if len(log_t) < 2:
        return float("nan"), float("nan"), 0.0
    a, b, r2 = ols_fit(log_t, log_P)
    return -2.0 * b, b, r2


def graph_stats(neighbours: list[list[int]]) -> dict:
    """Statistici de baza despre graf."""
    degrees = [len(nb) for nb in neighbours]
    n = len(degrees)
    avg_deg = sum(degrees) / n if n else 0
    # componenta conectata (BFS)
    visited = [False] * n
    queue = [0]
    visited[0] = True
    count = 1
    while queue:
        v = queue.pop()
        for u in neighbours[v]:
            if not visited[u]:
                visited[u] = True
                count += 1
                queue.append(u)
    return {
        "n": n,
        "edges": sum(degrees) // 2,
        "avg_degree": round(avg_deg, 2),
        "max_degree": max(degrees),
        "lcc_fraction": round(count / n, 3),
    }


# ── Constructori de graf ──────────────────────────────────────────────────────

def build_knn_2d(n: int, k: int, rng: random.Random) -> list[list[int]]:
    """Graful standard QNG: k-NN pe puncte random 2D. Baseline."""
    spread = 2.3
    coords = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread)) for _ in range(n)]
    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        dists = sorted(
            [(math.hypot(xi - coords[j][0], yi - coords[j][1]), j) for j in range(n) if j != i]
        )
        for d, j in dists[:k]:
            w = max(d, 1e-6)
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
    return [[j for j in m] for m in adj]


def build_erdos_renyi(n: int, k_avg: int, rng: random.Random) -> list[list[int]]:
    """Erdos-Renyi G(n, p): fara geometrie, conectivitate uniforma.
    p = k_avg / (n-1) ca sa avem grad mediu similar."""
    p = k_avg / (n - 1)
    adj: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j)
                adj[j].add(i)
    return [sorted(s) for s in adj]


def build_barabasi_albert(n: int, m: int, rng: random.Random) -> list[list[int]]:
    """Barabasi-Albert: preferential attachment. Scale-free.
    m = numarul de muchii noi per nod adaugat (~ k_avg/2)."""
    # Porneste cu un clique initial de m+1 noduri
    m0 = max(m + 1, 3)
    adj: list[set[int]] = [set() for _ in range(n)]
    for i in range(m0):
        for j in range(i + 1, m0):
            adj[i].add(j)
            adj[j].add(i)

    # Degree sequence pentru preferential attachment
    degree = [len(adj[i]) for i in range(n)]

    for new_node in range(m0, n):
        # Construieste lista de candidati ponderata de grad
        candidates = []
        total_deg = sum(degree[:new_node])
        if total_deg == 0:
            chosen = rng.sample(range(new_node), min(m, new_node))
        else:
            # Sampling cu repetitie ponderata, fara inlocuire
            chosen = set()
            attempts = 0
            while len(chosen) < min(m, new_node) and attempts < 10 * n:
                r = rng.uniform(0, total_deg)
                cum = 0
                for node in range(new_node):
                    cum += degree[node]
                    if cum >= r:
                        if node not in chosen:
                            chosen.add(node)
                        break
                attempts += 1
            chosen = list(chosen)

        for target in chosen:
            adj[new_node].add(target)
            adj[target].add(new_node)
            degree[new_node] += 1
            degree[target] += 1

    return [sorted(s) for s in adj]


def build_causal_random(n: int, k_avg: int, rng: random.Random) -> list[list[int]]:
    """Graf cauzal: nodurile au ordine cauzala (index = timp cauzal).
    Fiecare nod se conecteaza la k_avg/2 predecesori aleatori din fereastra locala,
    iar graful nedirectionat rezultat aproximeaza o retea de tip causal set.
    Fara embedding spatial — conectivitatea vine din ordinea cauzala."""
    window = min(n - 1, k_avg * 4)  # fereastra causala
    adj: list[set[int]] = [set() for _ in range(n)]
    k_links = max(1, k_avg // 2)

    for i in range(1, n):
        # Conecteaza la k_links predecesori din fereastra causala
        lo = max(0, i - window)
        predecessors = list(range(lo, i))
        chosen = rng.sample(predecessors, min(k_links, len(predecessors)))
        for j in chosen:
            adj[i].add(j)
            adj[j].add(i)

    # Adauga legaturi forward aleatorii pentru simetrie (ca un causal set undirected)
    for i in range(n - window, n):
        lo = max(0, i - window)
        hi = min(n - 1, i + window)
        candidates = [j for j in range(i + 1, hi + 1)]
        if candidates:
            extra = rng.sample(candidates, min(k_links, len(candidates)))
            for j in extra:
                adj[i].add(j)
                adj[j].add(i)

    return [sorted(s) for s in adj]


def build_random_regular(n: int, k: int, rng: random.Random) -> list[list[int]]:
    """Graf regular aleator: fiecare nod are exact k vecini.
    Fara geometrie, grad uniform — testeaza efectul pur al regularitatii."""
    # Algoritm: lista stub + shuffle
    if (n * k) % 2 != 0:
        k = k - 1  # ajusteaza ca suma gradelor sa fie para
    stubs = list(range(n)) * k
    rng.shuffle(stubs)

    adj: list[set[int]] = [set() for _ in range(n)]
    max_attempts = 10
    for _ in range(max_attempts):
        rng.shuffle(stubs)
        adj = [set() for _ in range(n)]
        success = True
        i = 0
        while i < len(stubs) - 1:
            u, v = stubs[i], stubs[i + 1]
            if u == v or v in adj[u]:
                # Cauta o pereche de swapping
                swapped = False
                for j in range(i + 2, len(stubs) - 1, 2):
                    a, b = stubs[j], stubs[j + 1]
                    if a != u and b != u and a != v and b != v:
                        if a not in adj[u] and b not in adj[v]:
                            stubs[i + 1], stubs[j] = stubs[j], stubs[i + 1]
                            u, v = stubs[i], stubs[i + 1]
                            swapped = True
                            break
                if not swapped:
                    success = False
                    break
            adj[u].add(v)
            adj[v].add(u)
            i += 2
        if success:
            break

    return [sorted(s) for s in adj]


# ── Main ──────────────────────────────────────────────────────────────────────
@dataclass
class GraphResult:
    name: str
    description: str
    stats: dict
    d_s: float
    slope: float
    r2: float
    P_sample: list[float]  # P_t[4..10] pentru afisare


def run_experiment() -> None:
    print("=" * 70)
    print("QNG Coordinate-Free Graph Experiment")
    print("Masurare d_s (dimensiune spectrala) fara embedding 2D")
    print("=" * 70)
    print()

    experiments = [
        ("2D k-NN (BASELINE)", "Standard QNG: k-NN pe puncte random 2D",
         lambda rng: build_knn_2d(N_NODES, K_TARGET, rng)),
        ("Erdos-Renyi",        "Random pur: p = k_avg/(n-1), fara geometrie",
         lambda rng: build_erdos_renyi(N_NODES, K_TARGET, rng)),
        ("Barabasi-Albert",    "Scale-free: preferential attachment",
         lambda rng: build_barabasi_albert(N_NODES, K_TARGET // 2 + 1, rng)),
        ("Causal-Random",      "Retea cauzala: conexiuni dupa ordine temporala",
         lambda rng: build_causal_random(N_NODES, K_TARGET, rng)),
        ("Random-Regular",     "Graf regular: fiecare nod cu exact k vecini",
         lambda rng: build_random_regular(N_NODES, K_TARGET, rng)),
    ]

    results: list[GraphResult] = []

    for name, desc, builder in experiments:
        rng = random.Random(SEED)
        print(f"Construiesc: {name}...", end=" ", flush=True)
        neighbours = builder(rng)
        stats = graph_stats(neighbours)
        P_t = random_walk_return_prob(neighbours, N_WALKS, N_STEPS, rng)
        d_s, slope, r2 = spectral_dimension(P_t, T_LO, T_HI)
        P_sample = [round(P_t[t], 5) if t < len(P_t) else 0.0 for t in range(T_LO, T_HI + 1)]
        results.append(GraphResult(name, desc, stats, d_s, slope, r2, P_sample))
        print(f"d_s = {d_s:.3f} (r²={r2:.3f})")

    print()
    print("=" * 70)
    print("REZULTATE COMPARATIVE")
    print("=" * 70)
    print()

    # Header
    print(f"{'Graf':<22} {'n':>5} {'k_avg':>6} {'LCC':>6} {'d_s':>8} {'r²':>6}  Interpretare")
    print("-" * 80)

    interpretations = {
        "2D k-NN (BASELINE)": "artificiala (embedding 2D)",
        "Erdos-Renyi":        "infinita (spatiu infinit-dim)",
        "Barabasi-Albert":    "sub-1D sau > 4D (hub-spoke)",
        "Causal-Random":      "1D-2D (lantul cauzal)",
        "Random-Regular":     "regulara, fara geometrie",
    }

    baseline_ds = None
    for r in results:
        if r.name == "2D k-NN (BASELINE)":
            baseline_ds = r.d_s

        interp = interpretations.get(r.name, "?")
        ds_str = f"{r.d_s:.3f}" if not math.isnan(r.d_s) else " nan "
        marker = " <-- BASELINE" if r.name == "2D k-NN (BASELINE)" else ""
        print(
            f"{r.name:<22} {r.stats['n']:>5} {r.stats['avg_degree']:>6} "
            f"{r.stats['lcc_fraction']:>6.3f} {ds_str:>8} {r.r2:>6.3f}  {interp}{marker}"
        )

    print()
    print("=" * 70)
    print("ANALIZA")
    print("=" * 70)
    print()
    print("d_s teoretic pentru manifolduri continue:")
    print("  d_s = 1  → lant (1D)")
    print("  d_s = 2  → plan (2D)")
    print("  d_s = 3  → spatiu 3D")
    print("  d_s = 4  → spatiu-timp 4D (tinta fizica)")
    print("  d_s → ∞  → Erdos-Renyi (nu are geometrie locala)")
    print()

    for r in results:
        if r.name == "2D k-NN (BASELINE)":
            continue
        if math.isnan(r.d_s):
            print(f"  {r.name}: d_s = nan (graful poate fi deconectat)")
            continue
        delta = r.d_s - (baseline_ds or 0)
        sign = "+" if delta >= 0 else ""
        print(f"  {r.name}: d_s = {r.d_s:.3f} ({sign}{delta:.3f} fata de baseline)")

    print()
    print("CONCLUZIE:")
    print("  Graful k-NN 2D are d_s impus de embedding-ul spatial.")
    print("  Grafurile coordinate-free au d_s diferite, emergente din")
    print("  principiul de constructie — nu din coordonate.")
    print()
    print("  Calea catre d_s ≈ 4 (lumea fizica) nu e prin embedding 4D")
    print("  ci prin alegerea unui principiu de conectivitate care sa")
    print("  genereze spontan dimensionalitate 4D.")
    print()

    # Salvam rezultatele
    out_dir = Path(__file__).parent.parent / "05_validation" / "evidence" / "artifacts" / "coordfree-ds-v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "results.txt"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("Graf,n,edges,avg_degree,lcc_fraction,d_s,slope,r2\n")
        for r in results:
            f.write(
                f"{r.name},{r.stats['n']},{r.stats['edges']},"
                f"{r.stats['avg_degree']},{r.stats['lcc_fraction']},"
                f"{r.d_s:.4f},{r.slope:.4f},{r.r2:.4f}\n"
            )
    print(f"Rezultate salvate in: {out_path}")


if __name__ == "__main__":
    run_experiment()
