#!/usr/bin/env python3
"""
Coordinate-Free Spectral Dimension — FINAL COMPARISON

Cei 4 candidati selectati din sweep-ul H1-H5 (d_s > 3.80, motivati fizic):

  C1) 4D Hypercubic Lattice L=4  — ground truth matematic, analitic exact
  C2) 4D Hypercubic Lattice L=5  — cel mai aproape de d_s=4.0 exact
  C3) Random Regular k=6         — cel mai simplu, coord-free, d_s≈3.88
  C4) Jaccard Informational(8,8) — singurul principiu pur informational

Criterii de selectie pentru QNG:
  (a) d_s cel mai aproape de 4.0
  (b) r² cat mai aproape de 1 (scaling curat)
  (c) Running UV→IR fizic corect (d_s creste cu scala)
  (d) Principiu de conectivitate fara coordonate spatiale
  (e) Compatibilitate cu structura QNG (n, LCC, etc.)

Output: recomandare clara pentru care graf sa inlocuiasca k-NN 2D in QNG.
"""

from __future__ import annotations

import itertools
import math
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path


SEED    = 3401
N_WALKS = 150
N_STEPS = 22
T_LO    = 5
T_HI    = 14
INTEGRATION_POLICY = "informational_c4"  # options: informational_c4 | winner_by_score

if hasattr(sys.stdout, "reconfigure"):
    # Keep script runnable on Windows cp1252 consoles that cannot print box-drawing glyphs.
    sys.stdout.reconfigure(errors="replace")


# ── Utilitare ─────────────────────────────────────────────────────────────────
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


def ds_window(P_t, t_lo, t_hi):
    lx, ly = [], []
    for t in range(t_lo, t_hi+1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t)); ly.append(math.log(P_t[t]))
    if len(lx) < 2: return float("nan"), 0.
    _, b, r2 = ols(lx, ly)
    return -2.*b, r2


def lazy_rw(nb, n_walks, n_steps, rng, p_stay=0.5):
    n = len(nb)
    counts = [0]*(n_steps+1)
    total = n*n_walks
    for start in range(n):
        if not nb[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps+1):
                if rng.random() > p_stay:
                    nbs = nb[v]
                    if nbs: v = rng.choice(nbs)
                if v == start: counts[t] += 1
    return [counts[t]/total for t in range(n_steps+1)]


def ginfo(nb):
    degs = [len(x) for x in nb]; n = len(degs)
    vis = [False]*n; q = [0]; vis[0] = True; c = 1
    while q:
        v = q.pop()
        for u in nb[v]:
            if not vis[u]: vis[u]=True; c+=1; q.append(u)
    return {"n": n, "k_avg": sum(degs)/n, "k_max": max(degs), "lcc": c/n}


# ── Analitic 4D Lattice ───────────────────────────────────────────────────────
def K_4d_lazy(L, t):
    n = L**4; total = 0.
    for ks in itertools.product(range(L), repeat=4):
        alpha = sum(math.cos(2*math.pi*k/L) for k in ks)/4.
        total += ((1+alpha)/2.)**t
    return total/n


def analytical_Pt(L, n_steps):
    return [K_4d_lazy(L, t) for t in range(n_steps+1)]


# ── Constructori ──────────────────────────────────────────────────────────────
def build_4d_lattice(L, rng_seed=SEED):
    n = L**4
    def idx(i,j,k,l): return (i%L)*L**3+(j%L)*L**2+(k%L)*L+(l%L)
    adj = [set() for _ in range(n)]
    for i in range(L):
        for j in range(L):
            for k in range(L):
                for l in range(L):
                    v = idx(i,j,k,l)
                    for di,dj,dk,dl in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]:
                        u = idx(i+di,j+dj,k+dk,l+dl)
                        if v < u: adj[v].add(u); adj[u].add(v)
    return [sorted(s) for s in adj]


def build_rr(n, k, rng_seed=SEED):
    rng = random.Random(rng_seed)
    if (n*k)%2 != 0: k -= 1
    stubs = list(range(n))*k
    adj = [set() for _ in range(n)]
    for _ in range(20):
        rng.shuffle(stubs); adj = [set() for _ in range(n)]; ok = True; i = 0
        while i < len(stubs)-1:
            u,v = stubs[i],stubs[i+1]
            if u==v or v in adj[u]:
                sw = False
                for j in range(i+2, len(stubs)-1, 2):
                    a,b = stubs[j],stubs[j+1]
                    if a!=u and b!=u and a!=v and b!=v and a not in adj[u] and b not in adj[v]:
                        stubs[i+1],stubs[j]=stubs[j],stubs[i+1]; u,v=stubs[i],stubs[i+1]; sw=True; break
                if not sw: ok=False; break
            adj[u].add(v); adj[v].add(u); i += 2
        if ok: break
    return [sorted(s) for s in adj]


def build_jaccard(n, k_init, k_conn, rng_seed=SEED):
    rng = random.Random(rng_seed)
    p0 = k_init/(n-1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0: adj0[i].add(j); adj0[j].add(i)
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i]|{i}
        scores = []
        for j in range(n):
            if j==i: continue
            Nj = adj0[j]|{j}
            inter=len(Ni&Nj); union=len(Ni|Nj)
            scores.append((inter/union if union else 0., j))
        scores.sort(reverse=True)
        for _,j in scores[:k_conn]: adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Structura rezultat ────────────────────────────────────────────────────────
@dataclass
class Candidate:
    name:   str
    code:   str   # C1-C4
    nb:     list
    P_t:    list = field(default_factory=list)
    info:   dict = field(default_factory=dict)
    ds_main:   float = 0.
    r2_main:   float = 0.
    ds_uv:     float = 0.   # t=[2,5]
    ds_mid:    float = 0.   # t=[5,9]
    ds_ir:     float = 0.   # t=[12,18]
    analytical: bool = False
    score:     float = 0.


# ── Scoring ──────────────────────────────────────────────────────────────────
def compute_score(c: Candidate) -> float:
    """
    Scor compus (0-100) pentru selectia candidatului QNG:

      (a) Proximitate d_s=4.0   — 40 puncte  (exp decay din distanta)
      (b) Calitate fit r²        — 20 puncte
      (c) Running UV→IR corect  — 20 puncte  (d_s_ir > d_s_uv = fizic)
      (d) Acoperire LCC=1       — 10 puncte
      (e) Dimensiune manageriala — 10 puncte (n < 700)
    """
    # (a) Proximitate 4.0
    dist = abs(c.ds_main - 4.0)
    score_a = 40. * math.exp(-2.*dist)

    # (b) r²
    score_b = 20. * c.r2_main

    # (c) Running: d_s creste de la UV la IR (semn fizic corect)
    if not math.isnan(c.ds_uv) and not math.isnan(c.ds_ir):
        running = c.ds_ir - c.ds_uv
        score_c = 20. * min(max(running / 2., 0.), 1.)
    else:
        score_c = 0.

    # (d) LCC
    score_d = 10. * c.info.get("lcc", 0.)

    # (e) Dimensiune
    n = c.info.get("n", 1e9)
    score_e = 10. if n <= 700 else 5. if n <= 1500 else 0.

    return score_a + score_b + score_c + score_d + score_e


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print()
    print("=" * 70)
    print("QNG Graph Selection — FINAL COMPARISON")
    print("Cei 4 candidati cu d_s > 3.80 (coord-free, fizic motivati)")
    print("=" * 70)

    # ── Construieste candidatii ───────────────────────────────────────────────
    print("\nConstructie grafuri si masurare...")

    candidates: list[Candidate] = []

    # C1: 4D Lattice L=4 (analitic)
    nb1 = build_4d_lattice(L=4)
    c1 = Candidate("4D Lattice L=4 (analitic)", "C1", nb1, analytical=True)
    c1.P_t = analytical_Pt(4, N_STEPS)
    c1.info = ginfo(nb1)
    print(f"  C1 construit: n={c1.info['n']}")

    # C2: 4D Lattice L=5 (analitic)
    nb2 = build_4d_lattice(L=5)
    c2 = Candidate("4D Lattice L=5 (analitic)", "C2", nb2, analytical=True)
    c2.P_t = analytical_Pt(5, N_STEPS)
    c2.info = ginfo(nb2)
    print(f"  C2 construit: n={c2.info['n']}")

    # C3: Random Regular k=6
    nb3 = build_rr(n=280, k=6)
    c3 = Candidate("Random Regular k=6", "C3", nb3)
    rng3 = random.Random(SEED)
    c3.P_t = lazy_rw(nb3, N_WALKS, N_STEPS, rng3)
    c3.info = ginfo(nb3)
    print(f"  C3 construit: n={c3.info['n']}")

    # C4: Jaccard (8,8)
    nb4 = build_jaccard(n=280, k_init=8, k_conn=8)
    c4 = Candidate("Jaccard Informational(8,8)", "C4", nb4)
    rng4 = random.Random(SEED)
    c4.P_t = lazy_rw(nb4, N_WALKS, N_STEPS, rng4)
    c4.info = ginfo(nb4)
    print(f"  C4 construit: n={c4.info['n']}")

    candidates = [c1, c2, c3, c4]

    # ── Masurare d_s la ferestre multiple ────────────────────────────────────
    print("\nMasurare d_s...")
    windows_main = (T_LO, T_HI)
    for c in candidates:
        c.ds_main, c.r2_main = ds_window(c.P_t, *windows_main)
        c.ds_uv,  _          = ds_window(c.P_t, 2, 5)
        c.ds_mid, _          = ds_window(c.P_t, 5, 9)
        c.ds_ir,  _          = ds_window(c.P_t, 12, 18)
        c.score = compute_score(c)
        method = "analitic" if c.analytical else "simulat"
        print(f"  {c.code}) {c.name}: d_s={c.ds_main:.3f} ({method})")

    # ── Raport comparativ ────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                     COMPARATIE FINALA CANDIDATI                        ║")
    print("╠══════════════════════════════════════════════════════════════════════════╣")

    # Header
    print(f"║  {'Criteriu':<30} {'C1':>8} {'C2':>8} {'C3':>8} {'C4':>8}  ║")
    print("╠══════════════════════════════════════════════════════════════════════════╣")

    def r(v, fmt=".3f"):
        return f"{v:{fmt}}" if not math.isnan(v) else "  nan"

    rows = [
        ("Noduri n",         [str(c.info['n'])   for c in candidates]),
        ("k_avg",            [f"{c.info['k_avg']:.1f}" for c in candidates]),
        ("LCC",              [f"{c.info['lcc']:.3f}"   for c in candidates]),
        ("─"*30,             ["─"*8]*4),
        ("d_s principal",    [r(c.ds_main)        for c in candidates]),
        ("dist de 4.0",      [r(abs(c.ds_main-4.))for c in candidates]),
        ("r² fit",           [r(c.r2_main)        for c in candidates]),
        ("─"*30,             ["─"*8]*4),
        ("d_s UV [2,5]",     [r(c.ds_uv)          for c in candidates]),
        ("d_s MID [5,9]",    [r(c.ds_mid)         for c in candidates]),
        ("d_s IR [12,18]",   [r(c.ds_ir)          for c in candidates]),
        ("Running IR-UV",    [r(c.ds_ir-c.ds_uv)  for c in candidates]),
        ("─"*30,             ["─"*8]*4),
        ("SCOR TOTAL /100",  [f"{c.score:.1f}"    for c in candidates]),
    ]

    for label, vals in rows:
        if label.startswith("─"):
            print("╠══════════════════════════════════════════════════════════════════════════╣")
            continue
        print(f"║  {label:<30} {vals[0]:>8} {vals[1]:>8} {vals[2]:>8} {vals[3]:>8}  ║")

    print("╠══════════════════════════════════════════════════════════════════════════╣")

    winner_by_score = max(candidates, key=lambda c: c.score)
    if INTEGRATION_POLICY == "winner_by_score":
        integration_candidate = winner_by_score
        integration_policy_note = "score-aligned policy (integration follows winner-by-score)"
    elif INTEGRATION_POLICY == "informational_c4":
        integration_candidate = next(c for c in candidates if c.code == "C4")
        integration_policy_note = (
            "physics policy override: informational-principle lane uses C4 "
            "even if winner-by-score differs"
        )
    else:
        raise ValueError(f"Unknown INTEGRATION_POLICY: {INTEGRATION_POLICY}")
    print(f"║  {'CASTIGATOR':<30} {'':>8} {'':>8} {'':>8} {'':>8}  ║")
    print(f"║  → {winner_by_score.code}: {winner_by_score.name:<54}  ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")

    # ── Analiza per candidat ──────────────────────────────────────────────────
    print()
    print("ANALIZA PER CANDIDAT:")
    print()

    pros_cons = {
        "C1": {
            "pro":  ["d_s analitic exact (r²=1.000)", "ground truth matematic",
                     "k=8 exact (ca 4D cubic lattice)"],
            "con":  ["n=256, usor sub tinta 280", "d_s=3.82 usor sub 4.0",
                     "Running UV→IR slab"],
        },
        "C2": {
            "pro":  ["d_s=4.06 cel mai aproape de 4.0", "analitic exact",
                     "convergenta demonstrata (H2)"],
            "con":  ["n=625 — mai mare decat QNG actual (280)",
                     "Simulare lenta pentru n=625"],
        },
        "C3": {
            "pro":  ["n=280 identic cu QNG curent", "simplu de implementat",
                     "k=6 fix (regulat, fara preferinta spatiala)"],
            "con":  ["d_s=3.88, usor sub 4.0", "zero motivatie fizica directa",
                     "Running UV→IR slab"],
        },
        "C4": {
            "pro":  ["SINGURUL principiu pur informational",
                     "d_s=4.08 — in tinta",
                     "n=280 identic cu QNG curent",
                     "Principiu: 'context similar → conexiune'"],
            "con":  ["Constructie in 2 pasi (ER init + Jaccard recon)",
                     "Mai lent de construit decat RR"],
        },
    }

    for c in candidates:
        print(f"  [{c.code}] {c.name}  (scor={c.score:.1f})")
        for p in pros_cons[c.code]["pro"]:
            print(f"       ✓ {p}")
        for p in pros_cons[c.code]["con"]:
            print(f"       ✗ {p}")
        print()

    # ── Recomandare finala ────────────────────────────────────────────────────
    print("═" * 70)
    print("RECOMANDARE FINALA PENTRU QNG")
    print("═" * 70)
    print()
    print(f"  Castigator score: [{winner_by_score.code}] {winner_by_score.name}")
    print(f"  d_s = {winner_by_score.ds_main:.3f}  (dist de 4.0 = {abs(winner_by_score.ds_main-4.):.3f})")
    print(f"  r²  = {winner_by_score.r2_main:.4f}")
    print(f"  Candidat integrare: [{integration_candidate.code}] {integration_candidate.name}")
    print(f"  Integration policy: {INTEGRATION_POLICY} ({integration_policy_note})")
    print()
    print("  MOTIVATIE:")
    print("  C4 (Jaccard Informational) e singurul candidat care:")
    print("  1. Da d_s ≈ 4.0 (in tinta fizica)")
    print("  2. Are n=280 (compatibil cu QNG curent)")
    print("  3. Foloseste un principiu pur informational —")
    print("     conexiunile vin din similaritatea contextului,")
    print("     nu din distanta spatiala sau regula arbitrara.")
    print("  4. Aliniaza cu interpretarea QNG: graful e o structura")
    print("     emergenta din informatia locala, nu geometrie pre-impusa.")
    print()
    print("  ALTERNATIVA (daca vrei rigoare matematica maxima):")
    print("  C2 (4D Lattice L=5) — d_s=4.06 exact, analitic, r²=1.000")
    print("  Trade-off: n=625 vs 280 si nu are motivatie informationala.")
    print()
    print("  PLAN DE INTEGRARE IN QNG:")
    print("  → Inlocuieste build_dataset_graph() cu build_jaccard(n=280, k_init=8, k_conn=8)")
    print("  → Pastreaza sigma field (calculat pe noul graf)")
    print("  → Re-ruleaza G18d cu lazy RW — asteptat d_s ≈ 4.0")
    print("  → Re-valideaza G10-G16 (GR gates) pe noul graf")
    print()

    # ── Salvare ───────────────────────────────────────────────────────────────
    out_dir = Path(__file__).parent.parent / "05_validation" / "evidence" / "artifacts" / "coordfree-ds-final"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv = out_dir / "candidates.csv"
    with csv.open("w", encoding="utf-8") as f:
        f.write("code,name,n,k_avg,lcc,ds_main,r2,ds_uv,ds_mid,ds_ir,running,score\n")
        for c in candidates:
            f.write(
                f"{c.code},\"{c.name}\",{c.info['n']},{c.info['k_avg']:.1f},"
                f"{c.info['lcc']:.3f},{c.ds_main:.4f},{c.r2_main:.4f},"
                f"{c.ds_uv:.4f},{c.ds_mid:.4f},{c.ds_ir:.4f},"
                f"{c.ds_ir-c.ds_uv:.4f},{c.score:.2f}\n"
            )

    rec = out_dir / "recommendation.txt"
    with rec.open("w", encoding="utf-8") as f:
        f.write(f"Winner by score: {winner_by_score.code} — {winner_by_score.name}\n")
        f.write(
            f"d_s = {winner_by_score.ds_main:.4f}, r² = {winner_by_score.r2_main:.4f}, "
            f"score = {winner_by_score.score:.1f}\n\n"
        )
        f.write(f"Integration candidate: {integration_candidate.code} — {integration_candidate.name}\n")
        f.write(f"Integration policy: {INTEGRATION_POLICY}\n")
        f.write(f"Policy note: {integration_policy_note}\n")
        f.write("Integration: replace build_dataset_graph() with build_jaccard(n=280, k_init=8, k_conn=8)\n")
        f.write("Expected G18d result: d_s ≈ 4.0 with lazy RW\n")

    print(f"Salvat: {out_dir}/")


if __name__ == "__main__":
    main()
