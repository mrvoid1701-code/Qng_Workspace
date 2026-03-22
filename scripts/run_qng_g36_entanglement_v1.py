#!/usr/bin/env python3
"""
QNG G36 — Entropia de Entanglement (Testul C)

Masuram informatia mutuala I(A:B) ca proxy pentru entropia de entanglement:

  I(A:B) = Σ_{i∈A, j∉A} C_ij² / (C_ii * C_jj)

Aceasta cantitate:
  - E zero cand campul nu are corelatie intre A si complementul B
  - Creste cu suprafata frontierei |dA| (area law) — semnatura gravitatiei cuantice
  - Creste cu volumul |A| (volume law) — semnatura unui camp fara structura spatiala

Area law in d_s=4: I ~ |dA| ~ |A|^{3/4}
Volume law:        I ~ |A|

Regiunile A: bile BFS de raza r=1 si r=2 din 25 noduri sursa diferite.
Aceasta da ~50 puncte cu |A| variind de la ~8 la ~80 noduri.

Gates:
  G36a — I(A:B) > 0 pentru toate regiunile:  corelatie exista intre A si B
  G36b — I creste cu |A|:                     Pearson(|A|, I) > 0.70
  G36c — Sublinear (area, nu volume):           exponent < 0.99
  G36d — Exponent area law:                    d(logI)/d(log|A|) in [0.55, 0.95]
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g36-entanglement-v1"

M_EFF_SQ  = 0.014
N_BOTTOM  = 40
N_TOP     = 40
N_ITER    = 200
SEED      = 3401
N_SOURCES = 25


def fmt(v):
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.5e}"
    return f"{v:.6f}"


def build_jaccard_weighted(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init/(n-1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    jw = {}
    for i in range(n):
        Ni = adj0[i]|{i}
        sc = []
        for j in range(n):
            if j==i: continue
            Nj = adj0[j]|{j}
            inter = len(Ni&Nj); union = len(Ni|Nj)
            sc.append((inter/union if union else 0.0, j))
        sc.sort(reverse=True)
        for s,j in sc[:k_conn]:
            key=(min(i,j),max(i,j)); jw[key]=max(jw.get(key,0.0),s)
    adj_w=[[] for _ in range(n)]
    for (i,j),w in jw.items():
        adj_w[i].append((j,w)); adj_w[j].append((i,w))
    return adj_w


def deg_w(adj_w): return [sum(w for _,w in nb) for nb in adj_w]
def apply_K(v, adj_w, deg, m2):
    return [(deg[i]+m2)*v[i]-sum(w*v[j] for j,w in adj_w[i]) for i in range(len(v))]
def dot(u,v): return sum(u[i]*v[i] for i in range(len(u)))
def norm(v): return math.sqrt(dot(v,v))
def deflate(v, basis):
    w=v[:]
    for b in basis:
        c=dot(w,b); w=[w[i]-c*b[i] for i in range(len(w))]
    return w


def compute_top_modes(adj_w, n, n_modes, n_iter, m2, rng, extra_basis=None):
    d=deg_w(adj_w); vecs=[]; lams=[]; eb=list(extra_basis or [])
    for _ in range(n_modes):
        v=[rng.gauss(0,1) for _ in range(n)]
        v=deflate(v,eb+vecs); nm=norm(v)
        if nm<1e-14: continue
        v=[x/nm for x in v]
        for _ in range(n_iter):
            w=apply_K(v,adj_w,d,m2); w=deflate(w,eb+vecs); nm=norm(w)
            if nm<1e-14: break
            v=[x/nm for x in w]
        Kv=apply_K(v,adj_w,d,m2); lam=max(m2,dot(v,Kv))
        vecs.append(v); lams.append(lam)
    order=sorted(range(len(lams)),key=lambda k:-lams[k])
    return [lams[k] for k in order],[vecs[k] for k in order]


def compute_bottom_modes(adj_w, n, n_modes, n_iter, m2, lam_shift, rng, extra_basis=None):
    d=deg_w(adj_w); vecs=[]; lams_K=[]; eb=list(extra_basis or [])
    for _ in range(n_modes):
        v=[rng.gauss(0,1) for _ in range(n)]
        v=deflate(v,eb+vecs); nm=norm(v)
        if nm<1e-14: continue
        v=[x/nm for x in v]
        for _ in range(n_iter):
            Kv=apply_K(v,adj_w,d,m2)
            Av=[lam_shift*v[i]-Kv[i] for i in range(n)]
            Av=deflate(Av,eb+vecs); nm=norm(Av)
            if nm<1e-14: break
            v=[x/nm for x in Av]
        Kv=apply_K(v,adj_w,d,m2); lam=max(m2,dot(v,Kv))
        vecs.append(v); lams_K.append(lam)
    order=sorted(range(len(lams_K)),key=lambda k:lams_K[k])
    return [lams_K[k] for k in order],[vecs[k] for k in order]


def bfs_ball(src, adj_w, radius):
    n=len(adj_w); dist=[-1]*n; dist[src]=0
    q=[src]; head=0
    while head<len(q):
        u=q[head]; head+=1
        for nb,_ in adj_w[u]:
            if dist[nb]<0:
                dist[nb]=dist[u]+1; q.append(nb)
    ball=[i for i in range(n) if 0<=dist[i]<=radius]
    ball_set=set(ball)
    bdry=sum(1 for i in ball for j,_ in adj_w[i] if j not in ball_set)
    return ball, bdry


def compute_C_row(src, all_lambdas, all_vecs, n):
    C_row=[0.0]*n
    for k,lam in enumerate(all_lambdas):
        w2=1.0/(2.0*math.sqrt(lam)); phi_src=all_vecs[k][src]
        if abs(phi_src)<1e-15: continue
        coeff=phi_src*w2; phi=all_vecs[k]
        for j in range(n):
            C_row[j]+=coeff*phi[j]
    return C_row


def compute_mutual_info(region, C_rows, C_diag, n):
    """
    I(A:B) = Σ_{i∈A, j∉A} C_ij^2 / (C_ii * C_jj)
    Proxy pentru entropia de entanglement — masoara corelatie cross-boundary.
    """
    region_set = set(region)
    I = 0.0
    for i in region:
        C_row_i = C_rows[i]
        c_ii = C_diag[i]
        if c_ii < 1e-15: continue
        for j in range(n):
            if j in region_set: continue
            c_jj = C_diag[j]
            if c_jj < 1e-15: continue
            c_ij = C_row_i[j]
            I += c_ij * c_ij / (c_ii * c_jj)
    return I


def pearson(xs, ys):
    n=len(xs)
    if n<2: return float("nan")
    mx=sum(xs)/n; my=sum(ys)/n
    num=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    denom=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return num/denom if denom>1e-15 else float("nan")


def linear_fit(xs, ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    Sxx=sum((x-mx)**2 for x in xs)
    Sxy=sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    b=Sxy/Sxx if Sxx>1e-15 else float("nan")
    a=my-b*mx
    ss_res=sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))
    ss_tot=sum((y-my)**2 for y in ys)
    R2=1-ss_res/ss_tot if ss_tot>1e-15 else float("nan")
    return a,b,R2


def main():
    out_dir = Path(DEFAULT_OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        try: print(msg)
        except UnicodeEncodeError: print(str(msg).encode("ascii","replace").decode())
        lines.append(msg)

    t0 = time.time()
    log("="*70)
    log("QNG G36 — Entropia de Entanglement (Mutual Information proxy)")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log("="*70)
    log("I(A:B) = Σ_{i∈A,j∉A} C_ij² / (C_ii*C_jj)  [proxy entanglement cross-boundary]")

    n = 280
    adj_w = build_jaccard_weighted(n, 8, 8, SEED)

    log(f"\n[1] Eigenmoduri ({N_TOP} top + {N_BOTTOM} bottom + 1 constant)")
    phi0 = [1/math.sqrt(n)]*n
    lambda0 = M_EFF_SQ

    t1 = time.time()
    lams_top, vecs_top = compute_top_modes(
        adj_w, n, N_TOP, N_ITER, M_EFF_SQ, random.Random(SEED+1), extra_basis=[phi0])
    lam_shift = lams_top[0]*1.05+0.5
    lams_bot, vecs_bot = compute_bottom_modes(
        adj_w, n, N_BOTTOM, N_ITER, M_EFF_SQ, lam_shift, random.Random(SEED+2), extra_basis=[phi0])
    log(f"  Calculat in {time.time()-t1:.1f}s  |  lambda_1_K={fmt(lams_bot[0])}")

    all_lambdas = [lambda0] + lams_bot + lams_top
    all_vecs    = [phi0]    + vecs_bot  + vecs_top

    # ── Precomputa C_rows si diagonala ────────────────────────────────────────
    log(f"\n[2] Precomputa propagatorul C_ij pentru toate nodurile...")
    t2 = time.time()
    C_diag = [0.0]*n
    for k,lam in enumerate(all_lambdas):
        w2 = 1.0/(2.0*math.sqrt(lam)); phi = all_vecs[k]
        for i in range(n):
            C_diag[i] += phi[i]*phi[i]*w2

    # Precalculeaza C_rows pentru toate nodurile sursa si cele din regiunile lor
    # (evitam recalcule inutile prin cache)
    C_rows_cache = {}

    def get_C_row(i):
        if i not in C_rows_cache:
            C_rows_cache[i] = compute_C_row(i, all_lambdas, all_vecs, n)
        return C_rows_cache[i]

    log(f"  C_diag calculat in {time.time()-t2:.2f}s  (C_rows: la cerere)")

    # ── Regiuni BFS si I(A:B) ──────────────────────────────────────────────────
    log(f"\n[3] Mutual information I(A:B) pentru bile BFS (r=1,2) din {N_SOURCES} surse")
    log(f"\n  {'src':>4}  {'r':>2}  {'|A|':>5}  {'|dA|':>5}  {'I(A:B)':>12}")
    log("  " + "-"*35)

    data_points = []
    rng_src = random.Random(SEED + 99)
    sources = rng_src.sample(range(n), N_SOURCES)

    for src in sources:
        for r in [1, 2]:
            ball, bdry = bfs_ball(src, adj_w, r)
            if len(ball) < 3 or len(ball) > n//2:
                continue
            # Precomputa C_rows pentru nodurile din regiune
            for i in ball:
                get_C_row(i)
            I_AB = compute_mutual_info(ball, C_rows_cache, C_diag, n)
            data_points.append({
                "src": src, "r": r, "A_size": len(ball),
                "boundary_edges": bdry, "I_AB": I_AB
            })
            log(f"  {src:>4}  {r:>2}  {len(ball):>5}  {bdry:>5}  {fmt(I_AB):>12}")

    log(f"\n  Total puncte: {len(data_points)}")

    # ── Analiza scaling ────────────────────────────────────────────────────────
    log("\n[4] Analiza scaling I(A:B) vs |A| si |dA|")

    valid = [(d["A_size"], d["boundary_edges"], d["I_AB"])
             for d in data_points if d["I_AB"] > 1e-10]

    A_s = [v[0] for v in valid]
    dA_s = [v[1] for v in valid]
    I_s  = [v[2] for v in valid]

    pearson_IA  = pearson(A_s,  I_s) if len(valid) >= 3 else float("nan")
    pearson_IdA = pearson(dA_s, I_s) if len(valid) >= 3 else float("nan")

    # Scaling exponent din log-log
    log_A = [math.log(a) for a in A_s]
    log_I = [math.log(i) for i in I_s]
    _, b_vol, R2_vol = linear_fit(log_A, log_I) if len(valid)>=3 else (float("nan"),float("nan"),float("nan"))
    exponent = b_vol

    _, _, R2_area_lin = linear_fit(dA_s, I_s) if len(valid)>=3 else (float("nan"),float("nan"),float("nan"))
    _, _, R2_vol_lin  = linear_fit(A_s, I_s)  if len(valid)>=3 else (float("nan"),float("nan"),float("nan"))

    log(f"  N puncte valide: {len(valid)}")
    log(f"  Pearson(|A|, I)   = {fmt(pearson_IA)}")
    log(f"  Pearson(|dA|, I)  = {fmt(pearson_IdA)}")
    log(f"  Exponent log(I)/log(|A|) = {fmt(exponent)}  (area law 4D: ~0.75)")
    log(f"  R2(I~|dA|) = {fmt(R2_area_lin)}  vs  R2(I~|A|) = {fmt(R2_vol_lin)}")
    log(f"  Area law mai bun: {not math.isnan(R2_area_lin) and not math.isnan(R2_vol_lin) and R2_area_lin > R2_vol_lin}")

    # Statistici per raza
    for r_val in [1, 2]:
        pts_r = [d for d in valid if d[0] == r_val] if False else \
                [d for d in data_points if d.get("r") == r_val and d["I_AB"] > 1e-10]
        if pts_r:
            I_mean_r = statistics.mean(d["I_AB"] for d in pts_r)
            A_mean_r = statistics.mean(d["A_size"] for d in pts_r)
            log(f"  r={r_val}: N={len(pts_r)}, |A|_mean={A_mean_r:.1f}, I_mean={fmt(I_mean_r)}")

    # ── Gates ─────────────────────────────────────────────────────────────────
    log("\n" + "="*70)
    log("GATES G36")
    log("="*70)

    all_I_positive = all(d["I_AB"] > 0 for d in data_points)
    g36a = all_I_positive and len(data_points) > 0
    g36b = (not math.isnan(pearson_IA)) and pearson_IA > 0.70
    # G36c: exponent sublinear < 0.99 => area law, NU volume law (care ar da 1.0)
    g36c = (not math.isnan(exponent)) and exponent < 0.99
    g36d = (not math.isnan(exponent)) and (0.55 <= exponent <= 0.95)

    for label, gate, val, cond in [
        ("G36a", g36a, float(all_I_positive),
         "I(A:B) > 0 pentru toate regiunile"),
        ("G36b", g36b, pearson_IA,
         "Pearson(|A|, I) > 0.70  [entanglement creste cu marimea regiunii]"),
        ("G36c", g36c, exponent,
         "exponent < 0.99  [sublinear => area law, nu volume law (=1.0)]"),
        ("G36d", g36d, exponent,
         "exponent in [0.55, 0.95]  (area law d_s=4: ~0.75)"),
    ]:
        st = "PASS" if gate else "FAIL"
        log(f"\n{label} — {cond}")
        log(f"       Valoare: {fmt(val)}  ->  {st}")

    n_pass = sum([g36a, g36b, g36c, g36d])
    log(f"\nSUMAR: {n_pass}/4 gate-uri trecute")
    log(f"G36a [{'PASS' if g36a else 'FAIL'}]  G36b [{'PASS' if g36b else 'FAIL'}]  "
        f"G36c [{'PASS' if g36c else 'FAIL'}]  G36d [{'PASS' if g36d else 'FAIL'}]")
    log(f"Timp total: {time.time()-t0:.1f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    with (out_dir/"entanglement.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["src","r","A_size","boundary_edges","I_AB"])
        w.writeheader(); w.writerows(data_points)

    result = {
        "data_points": data_points,
        "scaling": {
            "pearson_IA": pearson_IA, "pearson_IdA": pearson_IdA,
            "exponent_loglog": exponent, "R2_area": R2_area_lin, "R2_vol": R2_vol_lin,
        },
        "gates": {
            "G36a": {"passed": g36a},
            "G36b": {"passed": g36b, "pearson": pearson_IA},
            "G36c": {"passed": g36c, "R2_area": R2_area_lin, "R2_vol": R2_vol_lin},
            "G36d": {"passed": g36d, "exponent": exponent},
        },
        "summary": {
            "n_pass": n_pass, "n_total": 4, "all_pass": n_pass==4,
            "timestamp": datetime.utcnow().isoformat()+"Z",
            "runtime_s": round(time.time()-t0, 2),
        }
    }
    with (out_dir/"summary.json").open("w") as f:
        json.dump(result, f, indent=2)
    with (out_dir/"run.log").open("w") as f:
        f.write("\n".join(lines))
    log(f"\nArtefacte: {out_dir}")
    return 0 if n_pass == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
