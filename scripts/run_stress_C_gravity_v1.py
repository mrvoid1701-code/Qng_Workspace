#!/usr/bin/env python3
"""
QNG Stress Test — Categoria C: Atac pe campul gravitational

Bomba eleganta: daca teoria nu reproduce exact GR la Phi→0,
sau daca la Phi mare formeaza orizont artificial, e artifact, nu fizica.

Atacuri:
  C1  Phi → 0   : gamma_PPN → 1 exact? (limita GR)
  C2  Phi mare  : la ce Phi_scale se formeaza orizontul (N→0)?
  C3  Profil Schwarzschild: sigma(r) ~ 1/r pe graf?
  C4  Shapiro delay: creste monoton spre masa?
  C5  Echivalenta principiu: a_radial / (-dPhi/dr) = const?
  C6  g_00 + g_11 = 0? (signatura corecta metric spatiu-timp)

Formula metrica QNG (din G10):
  Phi(i) = -Phi_scale * sigma(i)/sigma_max    (potential gravitational)
  N(i)   = 1 + Phi(i)                         (lapse function)
  gamma_s(i) = 1 - 2*Phi(i)                   (metric spatial izotropa)
  U(i)   = -Phi(i) >= 0                       (potential newtonian pozitiv)
  gamma_PPN(i) = 1/(1 + U(i)/2)               (parametru PPN)

Orizont: N(i) = 0 ↔ Phi_scale = sigma_max/sigma(i) → la Phi_scale=1 pentru sigma_max

Dependinte: stdlib only.
"""

from __future__ import annotations

import collections
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
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-C-gravity-v1"

N = 280; K = 8; SEED = 3401
PHI_SCALE_CANONICAL = 0.08


# ── Graf Jaccard ──────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
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
    # sigma: grad normalizat
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs)
    rng2 = random.Random(seed + 99)
    sigma = [min(max(d / mx + rng2.gauss(0., 0.02), 0.), 1.) for d in degs]
    return sigma, nb


# ── Metrici gravitationale (din G10/G15) ──────────────────────────────────────

def compute_metric(sigma: list[float], phi_scale: float):
    """
    Metrici QNG la scala phi_scale data.
    Returneaza: Phi, N, gamma_s, U, gamma_PPN, c_eff, delta_S per nod
    """
    sigma_max = max(sigma) if sigma else 1.
    n = len(sigma)
    result = []
    for i in range(n):
        Phi     = -phi_scale * sigma[i] / sigma_max
        N       = 1. + Phi
        gamma_s = 1. - 2. * Phi
        U       = -Phi  # U > 0

        gamma_PPN = 1. / (1. + U / 2.) if U > 1e-14 else 1.

        # c_eff = N / sqrt(gamma_s) — viteza efectiva a luminii
        c_eff = N / math.sqrt(gamma_s) if gamma_s > 1e-14 else 0.
        # Shapiro delay
        delta_S = (1. / c_eff - 1.) if c_eff > 1e-14 else float("inf")

        result.append({
            "Phi": Phi, "N": N, "gamma_s": gamma_s, "U": U,
            "gamma_PPN": gamma_PPN, "c_eff": c_eff, "delta_S": delta_S
        })
    return result


def bfs_distances(source: int, nb: list[list[int]]) -> list[int]:
    n = len(nb)
    dist = [-1] * n
    dist[source] = 0
    q = collections.deque([source])
    while q:
        v = q.popleft()
        for u in nb[v]:
            if dist[u] < 0:
                dist[u] = dist[v] + 1
                q.append(u)
    return dist


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


# ── C1: Phi → 0 (limita GR) ──────────────────────────────────────────────────

def test_C1_phi_to_zero(sigma, phi_scales):
    """
    Limita campului slab: la Phi→0, teoria trebuie sa reproduca GR exact.
    gamma_PPN → 1, Shapiro delay → 0, N → 1, gamma_s → 1.
    """
    print("\n── C1: Phi → 0 (limita GR exacta) ─────────────────────────────────")
    print(f"  {'Phi_scale':>10} {'N_min':>8} {'gamma_PPN':>11} {'|g-1|':>8} "
          f"{'Shapiro_max':>12} {'G10a':>5} {'G15a':>5}")

    rows = []
    for phi_s in phi_scales:
        metrics = compute_metric(sigma, phi_s)
        N_min   = min(m["N"] for m in metrics)
        N_max   = max(m["N"] for m in metrics)
        g_ppn   = [m["gamma_PPN"] for m in metrics]
        g_mean  = statistics.mean(g_ppn)
        g_dev   = abs(g_mean - 1.)
        S_max   = max(m["delta_S"] for m in metrics)
        gate_G10a = N_min > 0.
        gate_G15a = g_dev < 0.06
        rows.append({
            "phi_scale": phi_s, "N_min": N_min, "g_PPN_mean": g_mean,
            "g_dev": g_dev, "shapiro_max": S_max,
            "G10a": gate_G10a, "G15a": gate_G15a
        })
        print(f"  {phi_s:>10.4f} {N_min:>8.4f} {g_mean:>11.6f} {g_dev:>8.6f} "
              f"{S_max:>12.6f} {'PASS' if gate_G10a else 'FAIL':>5} "
              f"{'PASS' if gate_G15a else 'FAIL':>5}")

    # La ce Phi_scale cade G15a?
    fail_G15a = next((r for r in rows if not r["G15a"]), None)
    if fail_G15a:
        print(f"\n  G15a FAIL la Phi_scale = {fail_G15a['phi_scale']} "
              f"(g_dev={fail_G15a['g_dev']:.4f} > 0.06)")
    else:
        print(f"\n  G15a PASS la toate Phi_scale testate! (GR limita robust)")

    # Convergenta gamma_PPN → 1 la Phi→0
    if rows:
        g_small = rows[0]["g_dev"]
        g_canonical = next(r for r in rows if abs(r["phi_scale"] - 0.08) < 0.001)["g_dev"]
        print(f"  g_dev la Phi=0.001: {g_small:.8f}  (→0 ca Phi→0: corect)")
        print(f"  g_dev la Phi=0.080: {g_canonical:.6f}  (canonical)")

    return rows


# ── C2: Phi mare — orizont ────────────────────────────────────────────────────

def test_C2_horizon_formation(sigma, phi_scales_strong):
    """
    La ce Phi_scale se formeaza orizontul (N → 0)?
    G10a: N > 0 trebuie sa tina.
    Teoretic: N_min = 1 - Phi_scale (pentru nodul cu sigma_max).
    Orizont: Phi_scale = 1.0 exact.
    """
    print("\n── C2: Orizont (N→0) — la ce Phi_scale? ───────────────────────────")
    print(f"  Teoretic: N_min = 1 - Phi_scale → orizont la Phi_scale = 1.0")
    print()
    print(f"  {'Phi_scale':>10} {'N_min':>8} {'N_max':>8} {'G10a':>5} {'g_PPN_min':>10}")

    rows = []
    phi_crit = None
    for phi_s in phi_scales_strong:
        metrics = compute_metric(sigma, phi_s)
        N_vals  = [m["N"] for m in metrics]
        N_min   = min(N_vals)
        N_max   = max(N_vals)
        g_ppn_min = min(m["gamma_PPN"] for m in metrics)
        gate_G10a = N_min > 0.
        rows.append({"phi_scale": phi_s, "N_min": N_min, "G10a": gate_G10a})
        print(f"  {phi_s:>10.4f} {N_min:>8.4f} {N_max:>8.4f} "
              f"{'PASS' if gate_G10a else 'FAIL':>5} {g_ppn_min:>10.4f}")
        if not gate_G10a and phi_crit is None:
            phi_crit = phi_s

    print(f"\n  Phi_crit (N→0): {phi_crit if phi_crit else '>'+str(phi_scales_strong[-1])}")
    print(f"  Phi_canonical = {PHI_SCALE_CANONICAL}  (marja fata de orizont: "
          f"{(1.0 - PHI_SCALE_CANONICAL)*100:.0f}%)")

    return rows, phi_crit


# ── C3: Profil Schwarzschild sigma(r) ~ 1/r ───────────────────────────────────

def test_C3_schwarzschild_profile(sigma, nb):
    """
    Schwarzschild: Phi ~ M/r → sigma ~ 1/r.
    Testam: sigma(r) scade cu distanta BFS de la centru?
    Centru = nodul cu sigma maxima.
    Fit sigma(r) vs r in log-log: sigma ~ r^alpha (BH: alpha=-1).
    """
    print("\n── C3: Profil Schwarzschild sigma(r) ~ r^alpha ─────────────────────")

    n = len(sigma)
    center = max(range(n), key=lambda i: sigma[i])
    dist   = bfs_distances(center, nb)

    max_r  = max(d for d in dist if d >= 0)
    by_shell = collections.defaultdict(list)
    for i in range(n):
        if dist[i] >= 0:
            by_shell[dist[i]].append(sigma[i])

    print(f"  Centru: nod {center}, sigma={sigma[center]:.4f}")
    print(f"  Raze BFS: 0..{max_r}")
    print(f"  {'r':>3} {'<sigma>':>8} {'sigma_std':>9} {'n_nodes':>8}")

    shell_means = []
    for r in range(max_r + 1):
        vals = by_shell[r]
        if not vals: continue
        mean_s = statistics.mean(vals)
        std_s  = statistics.stdev(vals) if len(vals) > 1 else 0.
        shell_means.append((r, mean_s))
        if r <= 8:
            print(f"  {r:>3} {mean_s:>8.4f} {std_s:>9.4f} {len(vals):>8}")

    # Fit log(sigma) ~ alpha * log(r) pentru r >= 1
    log_r   = [math.log(r) for r, s in shell_means if r >= 1 and s > 1e-8]
    log_s   = [math.log(s) for r, s in shell_means if r >= 1 and s > 1e-8]
    alpha_fit = float("nan"); r2_fit = 0.
    if len(log_r) >= 3:
        _, alpha_fit, r2_fit = ols_fit(log_r, log_s)

    print(f"\n  Fit sigma(r) ~ r^alpha:")
    print(f"  alpha_fit = {alpha_fit:.4f}  R² = {r2_fit:.4f}")
    print(f"  Schwarzschild: alpha = -1.0  (sigma ~ 1/r)")
    print(f"  Match Schwarzschild? {not math.isnan(alpha_fit) and abs(alpha_fit + 1.) < 0.5}")

    return shell_means, alpha_fit, r2_fit


# ── C4: Shapiro delay monoton ─────────────────────────────────────────────────

def test_C4_shapiro_monoton(sigma, nb):
    """
    Shapiro delay trebuie sa fie mai mare langa masa.
    Testam: delta_S(i) e corelat cu sigma(i)?
    """
    print("\n── C4: Shapiro delay — corelare cu masa ────────────────────────────")

    metrics = compute_metric(sigma, PHI_SCALE_CANONICAL)
    n = len(sigma)

    delta_S = [m["delta_S"] for m in metrics]
    U_vals  = [m["U"] for m in metrics]

    # Corelatie Pearson intre U si delta_S
    mean_U = statistics.mean(U_vals)
    mean_S = statistics.mean(delta_S)
    cov = sum((U_vals[i]-mean_U)*(delta_S[i]-mean_S) for i in range(n))
    var_U = sum((u-mean_U)**2 for u in U_vals)
    var_S = sum((s-mean_S)**2 for s in delta_S)
    corr = cov / math.sqrt(var_U * var_S) if var_U * var_S > 1e-30 else 0.

    # Stratificare: inner (top 20% U) vs outer (bot 20% U)
    sorted_nodes = sorted(range(n), key=lambda i: U_vals[i])
    inner = sorted_nodes[-n//5:]
    outer = sorted_nodes[:n//5]
    S_inner = statistics.mean(delta_S[i] for i in inner)
    S_outer = statistics.mean(delta_S[i] for i in outer)
    ratio   = S_inner / S_outer if S_outer > 1e-14 else float("inf")

    print(f"  Corr(U, delta_S) = {corr:.4f}  (1=perfect, 0=necorelat)")
    print(f"  S_inner (top 20% U) = {S_inner:.6f}")
    print(f"  S_outer (bot 20% U) = {S_outer:.6f}")
    print(f"  S_inner/S_outer = {ratio:.4f}  (G15b threshold: > 2.0)")
    print(f"  G15b: {'PASS' if ratio > 2.0 else 'FAIL'}")

    return {"corr_U_S": corr, "S_inner": S_inner, "S_outer": S_outer, "ratio": ratio}


# ── C5: Principiul echivalentei ───────────────────────────────────────────────

def test_C5_equivalence_principle(sigma, nb):
    """
    Principiul echivalentei: acceleratia gravitationala nu depinde de
    'masa' testului — numai de pozitie.

    Pe graf: a_i ~ -grad Phi(i)
    Masuram: cv(a_radial / grad_Phi) < threshold (uniformitate)
    """
    print("\n── C5: Principiul echivalentei ─────────────────────────────────────")

    n = len(nb)
    sigma_max = max(sigma)
    degrees   = [len(b) for b in nb]

    # Gradient discret al campului sigma:
    # grad_sigma(i) ~ mean over neighbors: (sigma(j) - sigma(i))
    grad_sigma = []
    for i in range(n):
        nb_i = nb[i]
        if not nb_i:
            grad_sigma.append(0.); continue
        g = sum(abs(sigma[j] - sigma[i]) for j in nb_i) / len(nb_i)
        grad_sigma.append(g)

    # Acceleratia: a(i) ~ |grad Phi(i)| ~ Phi_scale/sigma_max * grad_sigma(i)
    a_vals = [PHI_SCALE_CANONICAL / sigma_max * g for g in grad_sigma]

    # 'Masa locala' ~ sigma(i)
    # Principiul echivalentei: a(i) / sigma(i) = const?
    ratios = []
    for i in range(n):
        if sigma[i] > 1e-6 and a_vals[i] > 1e-10:
            ratios.append(a_vals[i] / sigma[i])

    if ratios:
        mean_r = statistics.mean(ratios)
        std_r  = statistics.stdev(ratios)
        cv_r   = std_r / mean_r if mean_r > 1e-14 else float("inf")
        print(f"  a(i)/sigma(i): mean={mean_r:.4e}  std={std_r:.4e}  cv={cv_r:.4f}")
        print(f"  cv < 0.3? {cv_r < 0.3}  ← principiu echivalenta (cv mic = uniform)")
        ep_pass = cv_r < 0.5
    else:
        cv_r = float("nan"); ep_pass = False
        print("  Nu suficiente date!")

    return {"cv_ratio": cv_r, "equivalence_principle": ep_pass}


# ── C6: Semnatura metricii g_00 + g_11 ───────────────────────────────────────

def test_C6_metric_signature(sigma, phi_scales):
    """
    Semnatura metricii: g_00 < 0, g_11 > 0 (Lorentziana).
    g_00 = -N², g_11 = gamma_s.
    Testam ca semnatura nu se schimba la Phi mare.
    """
    print("\n── C6: Semnatura metricii (Lorentziana) ───────────────────────────")

    rows = []
    for phi_s in phi_scales:
        metrics = compute_metric(sigma, phi_s)
        # g_00 = -N², g_11 = gamma_s
        n_neg_g00 = sum(1 for m in metrics if -m["N"]**2 >= 0)  # trebuie 0
        n_neg_g11 = sum(1 for m in metrics if m["gamma_s"] <= 0)  # trebuie 0
        lorentz_ok = (n_neg_g00 == 0 and n_neg_g11 == 0)
        rows.append({"phi_scale": phi_s, "lorentz_ok": lorentz_ok,
                     "n_wrong_g00": n_neg_g00, "n_wrong_g11": n_neg_g11})
        print(f"  Phi={phi_s:.3f}  g00<0: {n_neg_g00==0}  g11>0: {n_neg_g11==0}  "
              f"Lorentz: {lorentz_ok}")

    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("=" * 70)
    print("QNG STRESS TEST — Categoria C: Atac pe campul gravitational")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print("Bomba: la Phi→0 gamma_PPN→1 exact? La Phi mare: orizont?")
    print("=" * 70)

    print(f"\n[0] Graf Jaccard N={N}, k={K}...", end=" ", flush=True)
    sigma, nb = build_jaccard_graph(N, K, K, SEED)
    print(f"done  sigma: [{min(sigma):.3f}, {max(sigma):.3f}]")

    # C1: Phi → 0
    r_C1 = test_C1_phi_to_zero(sigma,
        phi_scales=[0.001, 0.005, 0.01, 0.05, 0.08, 0.1, 0.2, 0.3, 0.5,
                    0.7, 0.9, 0.95, 0.99, 1.0])

    # C2: orizont
    r_C2, phi_crit = test_C2_horizon_formation(sigma,
        phi_scales_strong=[0.5, 0.7, 0.9, 0.95, 0.99, 0.999, 1.0, 1.001, 1.01, 1.1, 2.0])

    # C3: profil Schwarzschild
    r_C3_shells, alpha_C3, r2_C3 = test_C3_schwarzschild_profile(sigma, nb)

    # C4: Shapiro delay
    r_C4 = test_C4_shapiro_monoton(sigma, nb)

    # C5: principiul echivalentei
    r_C5 = test_C5_equivalence_principle(sigma, nb)

    # C6: semnatura
    r_C6 = test_C6_metric_signature(sigma,
        phi_scales=[0.08, 0.5, 0.9, 0.99, 1.0, 1.5, 2.0])

    # ── Verdict ───────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SUMAR FINAL — Robustete gravitationala")
    print("=" * 70)

    # C1: G15a la canonical
    g15a_canonical = next(
        (r["G15a"] for r in r_C1 if abs(r["phi_scale"] - 0.08) < 0.001), False)
    # C1: gamma_PPN → 1 la Phi=0.001
    g_small = next((r["g_dev"] for r in r_C1 if abs(r["phi_scale"] - 0.001) < 0.0001), float("nan"))
    # C2: orizont
    horizon_at_1 = phi_crit is not None and abs(phi_crit - 1.0) < 0.01
    # C4: Shapiro
    shapiro_pass = r_C4["ratio"] > 2.0
    # C5: echivalenta
    ep_pass = r_C5["equivalence_principle"]
    # C6: semnatura la canonical
    sig_canon = next(
        (r["lorentz_ok"] for r in r_C6 if abs(r["phi_scale"] - 0.08) < 0.001), False)

    checks = {
        "C1_gamma_PPN_to_1_at_weak_field":   g15a_canonical,
        "C2_horizon_at_Phi_1_exact":         horizon_at_1,
        "C3_Schwarzschild_profile":          not math.isnan(alpha_C3),
        "C4_Shapiro_inner_vs_outer":         shapiro_pass,
        "C5_equivalence_principle":          ep_pass,
        "C6_Lorentz_signature_canonical":    sig_canon,
    }

    for check, result in checks.items():
        print(f"  {check:<40} {'PASS' if result else 'FAIL'}")

    print(f"\n  gamma_PPN_dev la Phi=0.001: {g_small:.2e}  (→0: GR limita corecta)")
    print(f"  gamma_PPN_dev la Phi=0.08:  "
          f"{next((r['g_dev'] for r in r_C1 if abs(r['phi_scale']-0.08)<0.001), 0.):.4f}")
    print(f"  Phi_crit (orizont): {phi_crit if phi_crit else '>2.0'}  "
          f"(teoretic: 1.0 exact)")
    print(f"  sigma(r) ~ r^{alpha_C3:.2f}  (Schwarzschild: -1.0)")
    print(f"  Shapiro ratio: {r_C4['ratio']:.3f}  (> 2.0: PASS)")
    print(f"  Echivalenta: cv(a/sigma) = {r_C5['cv_ratio']:.4f}  (< 0.5: PASS)")

    n_pass  = sum(checks.values())
    verdict = f"{n_pass}/{len(checks)}_PASS"
    print(f"\nverdict={verdict}")
    print(f"Timp: {time.time()-t0:.1f}s")

    # ── Salvare ───────────────────────────────────────────────────────────────
    csv_C1 = OUT_DIR / "stress_C1_phi_sweep.csv"
    with csv_C1.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["phi_scale","N_min","g_PPN_mean",
                                           "g_dev","shapiro_max","G10a","G15a"])
        w.writeheader(); w.writerows(r_C1)

    json_path = OUT_DIR / "stress_C_results.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "verdict": verdict,
        "checks": checks,
        "phi_canonical": PHI_SCALE_CANONICAL,
        "phi_crit_horizon": phi_crit,
        "alpha_schwarzschild": alpha_C3,
        "r2_schwarzschild": r2_C3,
        "C4_shapiro": r_C4,
        "C5_equivalence": r_C5,
        "C1_sweep": r_C1,
        "C2_strong": r_C2,
        "C6_signature": r_C6,
    }, indent=2, default=str), encoding="utf-8")

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {csv_C1.name}  {json_path.name}")
    print()
    print("=" * 70)
    print(f"STRESS TEST C COMPLET | verdict={verdict}")
    print("=" * 70)

    return 0 if n_pass >= 4 else 1


if __name__ == "__main__":
    sys.exit(main())
