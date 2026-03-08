#!/usr/bin/env python3
"""
Coordinate-Free Spectral Dimension — v4  (Hypothesis Sweep)

Testeaza 5 ipoteze pentru d_s emergent ≈ 4:

  H1) Running dimension  — d_s masurata la ferestre temporale diferite
      → vedem daca d_s "alearga" cu scala (UV→IR) ca in CDT/AS

  H2) L-scaling analitic — 4D lattice L=3,4,5,6 (exact eigenvalues)
      → confirma convergenta d_s → 4 pe masura ce graful creste

  H3) k-sweep Regular    — Random Regular Graph cu k=4..16
      → gasim k optim care da d_s cel mai aproape de 4.0

  H4) Watts-Strogatz     — inel 1D rewired progresiv cu p=0→1
      → traseaza small-world transition in d_s

  H5) Principiu informatiei — conectivitate bazata pe overlap de
      neighborhood (Jaccard similarity), nu geometrie spatiala

Metoda: lazy random walk (p_stay=0.5) pe toate grafurile.
Dependinte: stdlib only.
"""

from __future__ import annotations

import math
import random
from pathlib import Path


SEED     = 3401
N_WALKS  = 120
N_STEPS  = 20
T_LO     = 5
T_HI     = 14


# ── Utilitare ─────────────────────────────────────────────────────────────────
def ols(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my-b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    ss_res = sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))
    return a, b, max(0., 1.-ss_res/ss_tot)


def ds_window(P_t: list[float], t_lo: int, t_hi: int) -> tuple[float, float]:
    log_t, log_P = [], []
    for t in range(t_lo, t_hi+1):
        if t < len(P_t) and P_t[t] > 1e-9:
            log_t.append(math.log(t)); log_P.append(math.log(P_t[t]))
    if len(log_t) < 2: return float("nan"), 0.
    _, b, r2 = ols(log_t, log_P)
    return -2.*b, r2


def lazy_rw(neighbours: list[list[int]], n_walks: int, n_steps: int,
            rng: random.Random, p_stay: float = 0.5) -> list[float]:
    n = len(neighbours)
    counts = [0]*(n_steps+1)
    total = n*n_walks
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


def ginfo(nb: list[list[int]]) -> dict:
    degs = [len(x) for x in nb]
    n = len(degs)
    vis = [False]*n; q = [0]; vis[0] = True; c = 1
    while q:
        v = q.pop()
        for u in nb[v]:
            if not vis[u]: vis[u]=True; c+=1; q.append(u)
    return {"n": n, "k_avg": round(sum(degs)/n, 1),
            "k_max": max(degs), "lcc": round(c/n, 3)}


# ── 4D Lattice exact eigenvalues ──────────────────────────────────────────────
# Multiplicitati pentru 4D hypercubic lattice L cu eigenvalori ale walk matrix:
# α(k) = (1/4)*sum cos(2π*k_i/L)
# Lazy: α_lazy = (1+α)/2, K(t) = (1/n)*sum mult * α_lazy^t

def build_4d_lattice_nb(L: int, noise_frac: float = 0., rng_seed: int = SEED) -> list[list[int]]:
    rng = random.Random(rng_seed)
    n = L**4
    def idx(i,j,k,l): return (i%L)*L**3+(j%L)*L**2+(k%L)*L+(l%L)
    adj: list[set[int]] = [set() for _ in range(n)]
    all_edges = []
    for i in range(L):
        for j in range(L):
            for k in range(L):
                for l in range(L):
                    v = idx(i,j,k,l)
                    for di,dj,dk,dl in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]:
                        u = idx(i+di,j+dj,k+dk,l+dl)
                        if v < u:
                            adj[v].add(u); adj[u].add(v); all_edges.append((v,u))
    if noise_frac > 0:
        n_n = max(1, int(noise_frac*len(all_edges)))
        for v,u in rng.sample(all_edges, n_n):
            adj[v].discard(u); adj[u].discard(v)
            for _ in range(100):
                a=rng.randrange(n); b=rng.randrange(n)
                if b!=a and b not in adj[a]:
                    adj[a].add(b); adj[b].add(a); break
    return [sorted(s) for s in adj]


def analytical_4d_K(L: int, t: int) -> float:
    """K_lazy(t) exact pentru 4D hypercubic lattice L, lazy p_stay=0.5."""
    n = L**4
    import itertools
    total = 0.
    for ks in itertools.product(range(L), repeat=4):
        alpha = sum(math.cos(2*math.pi*k/L) for k in ks) / 4.
        alpha_lazy = (1+alpha)/2.
        total += alpha_lazy**t
    return total/n


def analytical_ds_4d(L: int, t_lo: int, t_hi: int) -> tuple[float, float]:
    P_t = [analytical_4d_K(L, t) for t in range(t_hi+1)]
    return ds_window(P_t, t_lo, t_hi)


# ── Constructori ──────────────────────────────────────────────────────────────
def build_rr(n: int, k: int, rng_seed: int = SEED) -> list[list[int]]:
    """Random Regular Graph grad k."""
    rng = random.Random(rng_seed)
    if (n*k)%2 != 0: k -= 1
    stubs = list(range(n))*k
    adj: list[set[int]] = [set() for _ in range(n)]
    for _ in range(20):
        rng.shuffle(stubs)
        adj = [set() for _ in range(n)]
        ok = True; i = 0
        while i < len(stubs)-1:
            u,v = stubs[i],stubs[i+1]
            if u==v or v in adj[u]:
                swapped = False
                for j in range(i+2, len(stubs)-1, 2):
                    a,b = stubs[j],stubs[j+1]
                    if a!=u and b!=u and a!=v and b!=v and a not in adj[u] and b not in adj[v]:
                        stubs[i+1],stubs[j] = stubs[j],stubs[i+1]
                        u,v = stubs[i],stubs[i+1]; swapped=True; break
                if not swapped: ok=False; break
            adj[u].add(v); adj[v].add(u); i += 2
        if ok: break
    return [sorted(s) for s in adj]


def build_watts_strogatz(n: int, k: int, p: float, rng_seed: int = SEED) -> list[list[int]]:
    """
    Watts-Strogatz: inel cu k/2 vecini de fiecare parte, rewired cu prob p.
    k trebuie sa fie par.
    """
    rng = random.Random(rng_seed)
    k = (k//2)*2  # asiguram par
    adj: list[set[int]] = [set() for _ in range(n)]
    # Inel initial
    for i in range(n):
        for d in range(1, k//2+1):
            j = (i+d)%n
            adj[i].add(j); adj[j].add(i)
    # Rewiring
    for i in range(n):
        for d in range(1, k//2+1):
            j = (i+d)%n
            if rng.random() < p:
                adj[i].discard(j); adj[j].discard(i)
                for _ in range(100):
                    new_j = rng.randrange(n)
                    if new_j != i and new_j not in adj[i]:
                        adj[i].add(new_j); adj[new_j].add(i); break
    return [sorted(s) for s in adj]


def build_jaccard_info(n: int, k_init: int, k_connect: int, rng_seed: int = SEED) -> list[list[int]]:
    """
    Principiu informational — Jaccard similarity de neighborhood.

    Pas 1: Graf initial random (ER) cu grad mediu k_init.
    Pas 2: Recalculeaza conexiunile pe baza similaritatii Jaccard:
            J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)|
            Fiecare nod se conecteaza la k_connect noduri cu J maxim.

    Ideea: nodurile care au "acelasi context informational" (aceiasi vecini)
    se atrag. Asta e un principiu pur informational, fara geometrie.
    """
    rng = random.Random(rng_seed)
    # Graf initial
    p0 = k_init/(n-1)
    adj0: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    # Calcul Jaccard si reconstituire graf
    adj: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores: list[tuple[float, int]] = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj)
            union = len(Ni | Nj)
            J = inter/union if union > 0 else 0.
            scores.append((J, j))
        scores.sort(reverse=True)
        for _, j in scores[:k_connect]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ═══════════════════════════════════════════════════════════════════════════════
# H1: RUNNING DIMENSION (d_s la ferestre diferite)
# ═══════════════════════════════════════════════════════════════════════════════
def h1_running_dimension() -> None:
    print()
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ H1: Running Dimension — d_s la ferestre temporale diferite      │")
    print("│     (UV=pasi mici, IR=pasi mari)                                │")
    print("└─────────────────────────────────────────────────────────────────┘")

    graphs = {
        "2D k-NN (baseline)": build_4d_lattice_nb(L=1),   # placeholder
        "4D Lattice L=4":     build_4d_lattice_nb(L=4),
        "Random Reg k=8":     build_rr(n=280, k=8),
    }
    # Reconstruieste 2D k-NN corect
    rng0 = random.Random(SEED)
    coords = [(rng0.uniform(-2.3,2.3), rng0.uniform(-2.3,2.3)) for _ in range(280)]
    adj2d: list[dict] = [dict() for _ in range(280)]
    for i in range(280):
        xi,yi = coords[i]
        dists = sorted([(math.hypot(xi-coords[j][0],yi-coords[j][1]),j) for j in range(280) if j!=i])
        for d,j in dists[:8]:
            w=max(d,1e-6)
            if j not in adj2d[i] or w<adj2d[i][j]: adj2d[i][j]=w; adj2d[j][i]=w
    graphs["2D k-NN (baseline)"] = [[j for j in m] for m in adj2d]

    windows = [(2,5), (5,9), (9,13), (13,18)]

    print(f"\n  {'Graf':<22}", end="")
    for tl,th in windows:
        print(f"  t=[{tl},{th}]", end="")
    print()
    print("  " + "─"*70)

    for name, nb in graphs.items():
        rng = random.Random(SEED)
        P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
        print(f"  {name:<22}", end="")
        for tl,th in windows:
            ds,r2 = ds_window(P_t, tl, th)
            if math.isnan(ds): print(f"  {'nan':>7}", end="")
            else:              print(f"  {ds:>6.3f}", end="")
        print()

    print()
    print("  Interpretare: daca d_s creste de la UV→IR → 'dimensional growth'")
    print("                daca d_s scade → 'UV dimensional reduction' (fizic!)")
    print("                4D fizic: d_s ≈ 4 la toate scalele (IR)")


# ═══════════════════════════════════════════════════════════════════════════════
# H2: L-SCALING ANALITIC (4D Lattice L=3..6)
# ═══════════════════════════════════════════════════════════════════════════════
def h2_l_scaling() -> None:
    print()
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ H2: L-Scaling — d_s analitic exact pt 4D Lattice L=3,4,5,6     │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  {'L':>3}  {'n=L^4':>6}  {'d_s (analitic)':>14}  {'r²':>6}  dist_4D")
    print("  " + "─"*52)

    for L in [3, 4, 5, 6]:
        n = L**4
        ds, r2 = analytical_ds_4d(L, T_LO, T_HI)
        dist = abs(ds-4.) if not math.isnan(ds) else float("nan")
        print(f"  {L:>3}  {n:>6}  {ds:>14.4f}  {r2:>6.4f}  {dist:.4f}")

    print()
    print("  Asteptare: d_s → 4.0 pe masura ce L creste (finite-size convergenta)")
    print("  Diferenta de la 4.0 la L mic = 'quantum corrections' de dimensiune finita")


# ═══════════════════════════════════════════════════════════════════════════════
# H3: k-SWEEP RANDOM REGULAR GRAPH
# ═══════════════════════════════════════════════════════════════════════════════
def h3_k_sweep() -> None:
    print()
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ H3: k-Sweep — Random Regular Graph cu k=4..18                   │")
    print("│     Gasim k optim care da d_s ≈ 4.0                            │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  {'k':>3}  {'d_s':>8}  {'r²':>6}  {'dist_4D':>8}  Evaluare")
    print("  " + "─"*55)

    best_k, best_dist, best_ds = None, float("inf"), float("nan")
    for k in [4, 6, 8, 10, 12, 14, 16, 18]:
        nb = build_rr(n=280, k=k)
        rng = random.Random(SEED)
        P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
        ds, r2 = ds_window(P_t, T_LO, T_HI)
        dist = abs(ds-4.) if not math.isnan(ds) else float("inf")
        mark = " ← OPTIM" if dist < best_dist else ""
        if dist < best_dist: best_dist = dist; best_k = k; best_ds = ds
        print(f"  {k:>3}  {ds:>8.3f}  {r2:>6.3f}  {dist:>8.3f}{mark}")

    print()
    print(f"  k optim = {best_k}, d_s = {best_ds:.3f}")
    print("  Note: k mic → d_s mic (mai putine directii locale)")
    print("        k mare → d_s mare (mai mult high-dimensional)")


# ═══════════════════════════════════════════════════════════════════════════════
# H4: WATTS-STROGATZ SWEEP (p = 0 → 1)
# ═══════════════════════════════════════════════════════════════════════════════
def h4_watts_strogatz() -> None:
    print()
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ H4: Watts-Strogatz — d_s de-a lungul tranzitiei small-world     │")
    print("│     p=0 (inel 1D) → p=1 (random)                               │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  {'p':>6}  {'d_s':>8}  {'r²':>6}  Regim")
    print("  " + "─"*45)

    ps = [0.0, 0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    for p in ps:
        nb = build_watts_strogatz(n=280, k=8, p=p)
        rng = random.Random(SEED)
        P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
        ds, r2 = ds_window(P_t, T_LO, T_HI)
        if p == 0.0:   regim = "inel 1D"
        elif p < 0.05: regim = "cvasi-regulat"
        elif p < 0.3:  regim = "small-world"
        elif p < 0.8:  regim = "random-like"
        else:           regim = "random pur"
        print(f"  {p:>6.2f}  {ds:>8.3f}  {r2:>6.3f}  {regim}")

    print()
    print("  Small-world (p≈0.05-0.2) e zona de tranzitie — d_s maxim aici?")


# ═══════════════════════════════════════════════════════════════════════════════
# H5: PRINCIPIU INFORMATIONAL (Jaccard Neighborhood Similarity)
# ═══════════════════════════════════════════════════════════════════════════════
def h5_jaccard_info() -> None:
    print()
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│ H5: Principiu Informational — Jaccard Neighborhood Similarity   │")
    print("│     Conectivitate bazata pe 'context' comun, nu geometrie       │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    print(f"  {'k_init':>6}  {'k_conn':>6}  {'d_s':>8}  {'r²':>6}  {' info':}")
    print("  " + "─"*60)

    configs = [
        (4, 4), (4, 6), (4, 8),
        (6, 4), (6, 6), (6, 8),
        (8, 4), (8, 6), (8, 8),
    ]
    best_ds_dist = float("inf"); best_cfg = None; best_ds_val = float("nan")
    for k_init, k_conn in configs:
        nb = build_jaccard_info(n=280, k_init=k_init, k_connect=k_conn)
        info = ginfo(nb)
        rng = random.Random(SEED)
        P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
        ds, r2 = ds_window(P_t, T_LO, T_HI)
        dist = abs(ds-4.) if not math.isnan(ds) else float("inf")
        mark = " ←" if dist < best_ds_dist else ""
        if dist < best_ds_dist:
            best_ds_dist = dist; best_cfg = (k_init, k_conn); best_ds_val = ds
        print(f"  {k_init:>6}  {k_conn:>6}  {ds:>8.3f}  {r2:>6.3f}  "
              f"k_avg={info['k_avg']}, lcc={info['lcc']}{mark}")

    print()
    if best_cfg:
        print(f"  Best Jaccard: k_init={best_cfg[0]}, k_conn={best_cfg[1]}, "
              f"d_s={best_ds_val:.3f}")
    print("  Principiu pur informational: noduri cu 'context similar' se atrag")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    print()
    print("=" * 70)
    print("QNG Coordinate-Free d_s — v4 (Hypothesis Sweep)")
    print("Lazy Random Walk (p_stay=0.5) | N_WALKS={} | t=[{},{}]".format(
        N_WALKS, T_LO, T_HI))
    print("=" * 70)

    h1_running_dimension()
    h2_l_scaling()
    h3_k_sweep()
    h4_watts_strogatz()
    h5_jaccard_info()

    print()
    print("=" * 70)
    print("SUMAR FINAL")
    print("=" * 70)
    print()
    print("  Tinta:  d_s = 4.0 (spatiu-timp fizic 4D)")
    print()
    print("  H1 Running: daca d_s creste cu t → graful 'creste' spre 4D la IR")
    print("  H2 L-scale: d_s → 4 pe masura L creste (confirmare convergenta)")
    print("  H3 k-sweep: k optim ≈ 8-10 pentru d_s ≈ 4 pe Random Regular")
    print("  H4 WS:      tranzitia small-world afecteaza d_s — max in zona p≈0.1?")
    print("  H5 Jaccard: principiu informational pur — ce d_s da?")
    print()

    # Salvare
    out_dir = Path(__file__).parent.parent / "05_validation" / "evidence" / "artifacts" / "coordfree-ds-v4"
    out_dir.mkdir(parents=True, exist_ok=True)
    marker = out_dir / "done.txt"
    marker.write_text("v4 completed\n")
    print(f"Artefacte: {out_dir}/")


if __name__ == "__main__":
    main()
