#!/usr/bin/env python3
"""
QNG G35 — Componenta "Dark" a Propagatorului  (Testul A)

Decomponem propagatorul C_ij in:
  C_dark(r)    = contributia modului constant (phi_0=1/sqrt(n), lambda_0=m²)
               = 1/(n * 2*omega_0)  =  CONSTANTA, identica pentru toate perechile
  C_spatial(r) = C(r) - C_dark  (contributia modurilor spatiale, scade cu r)

Interpretare:
  C_dark este analogul dark matter/dark energy: fond omogen, invizibil in
  structura locala, dar dominant la distante mari.

Masuram:
  f_dark(r) = C_dark / C(r)  [fractia dark la fiecare distanta]
  r*         = distanta la care f_dark = 0.50  [crossover]
  f_dark(r_max) → comparam cu Omega_DM/Omega_total ≈ 0.27 (dark matter)
                                 sau Omega_Lambda/Omega_total ≈ 0.68 (dark energy)

Gates:
  G35a — C_dark > 0:                       modul constant pozitiv
  G35b — f_dark(r_max) > 0.50:             dark domina la distante mari
  G35c — f_dark creste monoton cu r:       dark mai important la scara mare
  G35d — f_dark(r=1) in [0.20, 0.38]:     fractia dark la vecini directi ~ Omega_DM
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G33_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g33-propagator-v1"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g35-dark-ratio-v1"

M_EFF_SQ = 0.014
SEED     = 3401


def fmt(v):
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.5e}"
    return f"{v:.6f}"


def build_jaccard_weighted(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    jaccard_weights = {}
    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter/union if union else 0.0, j))
        scores.sort(reverse=True)
        for s, j in scores[:k_conn]:
            key = (min(i,j), max(i,j))
            jaccard_weights[key] = max(jaccard_weights.get(key, 0.0), s)
    adj_w = [[] for _ in range(n)]
    for (i,j), w in jaccard_weights.items():
        adj_w[i].append((j, w)); adj_w[j].append((i, w))
    return adj_w


def bfs_distances(src, adj_w):
    n = len(adj_w)
    dist = [-1]*n; dist[src] = 0
    q = [src]; head = 0
    while head < len(q):
        u = q[head]; head += 1
        for nb,_ in adj_w[u]:
            if dist[nb] < 0:
                dist[nb] = dist[u]+1; q.append(nb)
    return dist


def pearson(xs, ys):
    n = len(xs)
    if n < 2: return float("nan")
    mx = sum(xs)/n; my = sum(ys)/n
    num   = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    denom = math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return num/denom if denom > 1e-15 else float("nan")


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
    log("QNG G35 — Componenta Dark a Propagatorului")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log("="*70)

    # ── Incarcare profil C(r) din G33 ─────────────────────────────────────────
    g33_json = G33_DIR / "summary.json"
    if not g33_json.exists():
        log("EROARE: G33 summary.json nu exista — ruleaza mai intai G33.")
        return 1

    with g33_json.open() as f:
        g33 = json.load(f)

    n = g33["graph"]["n"]
    omega_0 = g33["constant_mode"]["omega_0"]
    C_profile_raw = g33["C_profile"]

    log(f"\nDate din G33: n={n}, omega_0={fmt(omega_0)}, m²={M_EFF_SQ}")

    # ── Modul dark: contributia constanta ─────────────────────────────────────
    C_dark = 1.0 / (n * 2.0 * omega_0)
    log(f"\n[1] Componenta dark (modul constant phi_0=1/sqrt(n)):")
    log(f"    C_dark = 1/(n * 2*omega_0) = 1/({n} * 2 * {fmt(omega_0)})")
    log(f"    C_dark = {fmt(C_dark)}  [identica pentru TOATE perechile (i,j)]")
    log(f"    E analogul unui fond cosmologic omogen.")

    # ── Profilul C(r) si f_dark(r) ────────────────────────────────────────────
    rs = sorted(int(r) for r in C_profile_raw.keys())
    C_total  = {r: C_profile_raw[str(r)]["mean"] for r in rs}
    C_spatial = {r: max(C_total[r] - C_dark, -C_dark) for r in rs}
    f_dark    = {r: C_dark / C_total[r] if C_total[r] > 1e-15 else float("nan") for r in rs}

    log(f"\n[2] Profil C(r) decomus in dark + spatial:")
    log(f"\n  {'r':>3}  {'C(r)':>12}  {'C_dark':>12}  {'C_spatial':>12}  {'f_dark':>8}")
    log("  " + "-"*55)
    for r in rs:
        log(f"  {r:>3}  {fmt(C_total[r]):>12}  {fmt(C_dark):>12}  "
            f"{fmt(C_spatial[r]):>12}  {fmt(f_dark[r]):>8}")

    # ── Crossover r* ──────────────────────────────────────────────────────────
    r_star = float("nan")
    for i in range(len(rs)-1):
        r1, r2 = rs[i], rs[i+1]
        f1, f2 = f_dark.get(r1, float("nan")), f_dark.get(r2, float("nan"))
        if not (math.isnan(f1) or math.isnan(f2)):
            if f1 <= 0.5 <= f2:
                # interpolare liniara
                r_star = r1 + (0.5 - f1) / (f2 - f1) * (r2 - r1)
                break
            elif f1 >= 0.5 >= f2:
                r_star = r1 + (0.5 - f1) / (f2 - f1) * (r2 - r1)
                break

    f_dark_r1   = f_dark.get(rs[0],   float("nan"))
    f_dark_rmax = f_dark.get(rs[-1],  float("nan"))
    r_max = rs[-1]

    log(f"\n[3] Statistici dark:")
    log(f"    f_dark(r=1)    = {fmt(f_dark_r1)}  (distanta mica, vecini directi)")
    log(f"    f_dark(r={r_max})    = {fmt(f_dark_rmax)}  (distanta maxima)")
    log(f"    Crossover r*   = {fmt(r_star)}  (unde dark = spatial = 50%)")
    log(f"\n    Comparatii cosmologice:")
    log(f"    Omega_DM / Omega_total  ≈ 0.268  (dark matter)")
    log(f"    Omega_Lam / Omega_total ≈ 0.683  (dark energy / Lambda)")
    log(f"    f_dark(r_max) = {fmt(f_dark_rmax)}")
    if 0.20 <= f_dark_rmax <= 0.35:
        log("    -> In intervalul dark matter cosmologic [0.20, 0.35]!")
    elif 0.60 <= f_dark_rmax <= 0.85:
        log("    -> In intervalul dark energy cosmologic [0.60, 0.85]!")
    else:
        log(f"    -> In afara intervalelor standard cosmologice.")

    # Monotonie f_dark(r)
    f_vals = [f_dark[r] for r in rs if not math.isnan(f_dark.get(r, float("nan")))]
    rs_valid = [r for r in rs if not math.isnan(f_dark.get(r, float("nan")))]
    pearson_f_r = pearson(rs_valid, f_vals)
    log(f"\n    Pearson(r, f_dark(r)) = {fmt(pearson_f_r)}  (pozitiv = dark creste cu r)")

    # ── Energia dark vs totala ─────────────────────────────────────────────────
    log(f"\n[4] Energie:")
    E_dark = 0.5 * omega_0
    # Estimam E_total din G33: E_0 (partial) + restul spectrului via Tr(K)
    E_0_partial = g33["propagator_diagonal"]["E_0"]
    K_total_modes = g33["propagator_diagonal"]["K_total"]
    log(f"    E_dark = 0.5 * omega_0 = {fmt(E_dark)}  (modul constant)")
    log(f"    E_0_partial (81 moduri) = {fmt(E_0_partial)}")
    log(f"    f_E_dark_partial = E_dark/E_0_partial = {fmt(E_dark/E_0_partial)}")

    # ── Gates ─────────────────────────────────────────────────────────────────
    log("\n" + "="*70)
    log("GATES G35")
    log("="*70)

    g35a = C_dark > 0.0
    g35b = (not math.isnan(f_dark_rmax)) and f_dark_rmax > 0.50
    # monotonie: f_dark creste cu r (Pearson pozitiv)
    g35c = (not math.isnan(pearson_f_r)) and pearson_f_r > 0.30
    # G35d: la distanta 1 (vecini directi = scala "barionica"),
    # fractia dark trebuie sa fie consistenta cu Omega_DM ≈ 0.268
    g35d = (not math.isnan(f_dark_r1)) and (0.20 <= f_dark_r1 <= 0.38)

    for label, gate, val, cond in [
        ("G35a", g35a, C_dark,        "C_dark > 0"),
        ("G35b", g35b, f_dark_rmax,   "f_dark(r_max) > 0.50  [dark domina la distanta mare]"),
        ("G35c", g35c, pearson_f_r,   "Pearson(r, f_dark) > 0.30  [dark creste cu r]"),
        ("G35d", g35d, f_dark_r1,
         "f_dark(r=1) in [0.20, 0.38]  [~ Omega_DM=0.268 la scala locala]"),
    ]:
        st = "PASS" if gate else "FAIL"
        log(f"\n{label} — {cond}")
        log(f"       Valoare: {fmt(val)}  ->  {st}")

    n_pass = sum([g35a, g35b, g35c, g35d])
    log(f"\nSUMAR: {n_pass}/4 gate-uri trecute")
    log(f"G35a [{'PASS' if g35a else 'FAIL'}]  G35b [{'PASS' if g35b else 'FAIL'}]  "
        f"G35c [{'PASS' if g35c else 'FAIL'}]  G35d [{'PASS' if g35d else 'FAIL'}]")
    log(f"Timp total: {time.time()-t0:.2f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    profile_rows = [
        {"r": r, "C_total": C_total[r], "C_dark": C_dark,
         "C_spatial": C_spatial[r], "f_dark": f_dark[r]}
        for r in rs
    ]
    with (out_dir/"dark_profile.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["r","C_total","C_dark","C_spatial","f_dark"])
        w.writeheader(); w.writerows(profile_rows)

    result = {
        "C_dark": C_dark, "omega_0": omega_0,
        "f_dark_r1": f_dark_r1, "f_dark_rmax": f_dark_rmax,
        "r_star": r_star, "pearson_f_r": pearson_f_r,
        "E_dark": E_dark, "E_0_partial": E_0_partial,
        "gates": {
            "G35a": {"passed": g35a, "value": C_dark},
            "G35b": {"passed": g35b, "value": f_dark_rmax},
            "G35c": {"passed": g35c, "value": pearson_f_r},
            "G35d": {"passed": g35d, "value": f_dark_rmax},
        },
        "summary": {
            "n_pass": n_pass, "n_total": 4, "all_pass": n_pass==4,
            "timestamp": datetime.utcnow().isoformat()+"Z",
            "runtime_s": round(time.time()-t0, 3),
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
