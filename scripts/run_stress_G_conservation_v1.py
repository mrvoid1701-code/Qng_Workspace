#!/usr/bin/env python3
"""
QNG Stress Test — Categoria G: Atac pe conservarea sub perturbari mari

G14 testa conservarea la AMP_INIT=0.01 (perturbatie mica).
Bomba: ce se intampla la perturbatii 10x, 100x mai mari?
E_cov mai e conservata sau se dezintegreaza?

Atacuri:
  G1  Amplitudine mare (10x, 100x): E_cov tine sau explodeaza?
  G2  Timp lung (N_steps=4000, 10x): drift acumulat pe termen lung
  G3  Unitaritate cuantica: ||psi(t)||^2 = 1 dupa 1000 pasi?
  G4  Phi mare: la Phi=0.5 (camp puternic) mai e conservarea covariant?
  G5  Campuri initiale dezordonate (random, nu wave packet)

Ecuatia undei covariant:
  partial_t^2 h(i) = alpha(i) * c^2 * [L_rw h](i)
  alpha(i) = N(i)^2 / gamma_s(i)   (factor metric)

Energii:
  E_flat(t) = 1/2 * sum_i k_i * v_i^2 + PE   (plata, NON-conservata)
  E_cov(t)  = 1/2 * sum_i (k_i/alpha_i) * v_i^2 + PE  (covariant, conservata)

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
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-G-conservation-v1"

N = 280; K = 8; SEED = 3401
PHI_SCALE_CANONICAL = 0.08
C_WAVE = 0.15
DT     = 0.40


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
    nb = [sorted(s) for s in adj]
    degs = [len(b) for b in nb]
    mx = max(degs)
    rng2 = random.Random(seed + 99)
    sigma = [min(max(d / mx + rng2.gauss(0., 0.02), 0.), 1.) for d in degs]
    return sigma, nb


# ── Ecuatia undei covariant ───────────────────────────────────────────────────

def make_alpha(sigma, nb, phi_scale):
    """alpha(i) = N(i)^2 / gamma_s(i) — factor metric covariat."""
    sigma_max = max(sigma)
    alpha = []
    for i in range(len(sigma)):
        Phi     = -phi_scale * sigma[i] / sigma_max
        N       = 1. + Phi
        gamma_s = 1. - 2. * Phi
        alpha.append(N**2 / gamma_s if gamma_s > 1e-14 else 0.)
    return alpha


def laplacian_rw(h, nb):
    """L_rw h(i) = mean_j h(j) - h(i)"""
    return [(sum(h[j] for j in nb[i]) / len(nb[i]) - h[i]) if nb[i] else 0.
            for i in range(len(h))]


def energy(h, v, nb, alpha, c2):
    """Calculeaza E_flat si E_cov."""
    n = len(h)
    degs = [len(nb[i]) for i in range(n)]
    # Potential energy (identic pentru flat si cov — e scalar)
    PE = 0.
    for i in range(n):
        nb_i = nb[i]
        if nb_i:
            PE += 0.5 * len(nb_i) * sum((h[j] - h[i])**2 for j in nb_i) / len(nb_i)
    PE *= c2 * 0.5
    # Kinetic energy
    E_flat = 0.5 * sum(degs[i] * v[i]**2 for i in range(n)) + PE
    E_cov  = 0.5 * sum((degs[i] / alpha[i]) * v[i]**2
                        for i in range(n) if alpha[i] > 1e-14) + PE
    return E_flat, E_cov


def run_wave(sigma, nb, phi_scale, amp, n_steps, dt, c_wave, seed,
             record_every=40):
    """
    Ruleaza ecuatia undei covariant si returneaza evolutia energiei.
    Conditie initiala: wave packet gaussian centrat pe nodul cu sigma maxima.
    """
    n = len(sigma)
    alpha = make_alpha(sigma, nb, phi_scale)
    c2    = c_wave**2

    # Conditie initiala
    rng   = random.Random(seed + 77)
    center = max(range(n), key=lambda i: sigma[i])
    h = [amp * math.exp(-0.5 * ((i - center) / (n**0.5 * 0.05))**2)
         for i in range(n)]
    v = [0.] * n  # viteza initiala zero

    # Leapfrog step 0 → -dt/2 (initializa v)
    Lh   = laplacian_rw(h, nb)
    accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
    v_half = [v[i] + 0.5 * dt * accel[i] for i in range(n)]

    E0_flat, E0_cov = energy(h, v_half, nb, alpha, c2)
    records = [{"step": 0, "E_flat_ratio": 1., "E_cov_ratio": 1.}]

    for step in range(1, n_steps + 1):
        # Update h
        h = [h[i] + dt * v_half[i] for i in range(n)]
        # Update v
        Lh    = laplacian_rw(h, nb)
        accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
        v_new = [v_half[i] + dt * accel[i] for i in range(n)]
        v_half = v_new

        if step % record_every == 0:
            E_flat, E_cov = energy(h, v_half, nb, alpha, c2)
            r_flat = E_flat / E0_flat if E0_flat > 1e-30 else float("nan")
            r_cov  = E_cov  / E0_cov  if E0_cov  > 1e-30 else float("nan")
            records.append({"step": step, "E_flat_ratio": r_flat,
                             "E_cov_ratio": r_cov})

    final_flat = records[-1]["E_flat_ratio"]
    final_cov  = records[-1]["E_cov_ratio"]
    drift_flat = abs(final_flat - 1.)
    drift_cov  = abs(final_cov  - 1.)
    ratio_drift = drift_flat / drift_cov if drift_cov > 1e-15 else float("inf")

    return {
        "drift_flat": drift_flat,
        "drift_cov":  drift_cov,
        "ratio":      ratio_drift,
        "final_flat": final_flat,
        "final_cov":  final_cov,
        "records":    records,
    }


# ── G1: Amplitudine mare ──────────────────────────────────────────────────────

def test_G1_amplitude(sigma, nb, amplitudes):
    """
    Perturbatie cu amplitudine crescatoare.
    Test: E_cov tine (drift < 2%) la orice amplitudine?
    """
    print("\n── G1: Amplitudine variabila ──────────────────────────────────────")
    print(f"  {'Amp':>8} {'drift_flat':>11} {'drift_cov':>10} {'ratio':>8} "
          f"{'G14b':>5}")
    rows = []
    for amp in amplitudes:
        res = run_wave(sigma, nb, PHI_SCALE_CANONICAL, amp, 400, DT, C_WAVE, SEED)
        gate = res["drift_cov"] < 0.02
        rows.append({"amp": amp, **{k: res[k] for k in
                     ["drift_flat", "drift_cov", "ratio"]}})
        print(f"  {amp:>8.4f} {res['drift_flat']:>11.4f} {res['drift_cov']:>10.6f} "
              f"{res['ratio']:>8.2f} {'PASS' if gate else 'FAIL':>5}")
    return rows


# ── G2: Timp lung ─────────────────────────────────────────────────────────────

def test_G2_long_time(sigma, nb, step_counts):
    """
    Run de durata lunga: drift-ul acumulat creste liniar sau se stabilizeaza?
    """
    print("\n── G2: Timp lung (drift acumulat) ─────────────────────────────────")
    print(f"  {'N_steps':>8} {'drift_flat':>11} {'drift_cov':>10} "
          f"{'drift_cov_per_step':>18} {'G14b':>5}")
    rows = []
    for n_steps in step_counts:
        res = run_wave(sigma, nb, PHI_SCALE_CANONICAL, 0.01, n_steps, DT, C_WAVE, SEED,
                       record_every=max(1, n_steps // 20))
        gate = res["drift_cov"] < 0.02
        dpc  = res["drift_cov"] / n_steps
        rows.append({"n_steps": n_steps, **{k: res[k] for k in
                     ["drift_flat", "drift_cov", "ratio"]},
                     "drift_cov_per_step": dpc})
        print(f"  {n_steps:>8d} {res['drift_flat']:>11.4f} {res['drift_cov']:>10.6f} "
              f"{dpc:>18.2e} {'PASS' if gate else 'FAIL':>5}")

    # Analiza: drift ~ t^alpha (liniar sau subliniar)?
    if len(rows) >= 3:
        log_t = [math.log(r["n_steps"]) for r in rows]
        log_d = [math.log(max(r["drift_cov"], 1e-10)) for r in rows]
        n_pts = len(log_t)
        mx = sum(log_t)/n_pts; my = sum(log_d)/n_pts
        Sxx = sum((x-mx)**2 for x in log_t)
        Sxy = sum((log_t[i]-mx)*(log_d[i]-my) for i in range(n_pts))
        alpha = Sxy/Sxx if abs(Sxx) > 1e-30 else 0.
        print(f"\n  Drift ~ t^{alpha:.3f}  (liniar: 1.0, subliniar: <1, constant: 0)")
    return rows


# ── G3: Unitaritate cuantica ─────────────────────────────────────────────────

def test_G3_unitarity(sigma, nb):
    """
    Testam daca norma cuantica ||psi||^2 e conservata.
    In QNG, 'starea cuantica' e expandata pe eigenvectori Laplacian.
    Evolutia temporala: |psi(t)> = sum_k c_k exp(-i omega_k t) |k>
    ||psi||^2 = sum_k |c_k|^2 = 1 (conservata exact in teoria continua).
    Pe graful discret cu leapfrog, testam ||h||^2 / ||h_0||^2 = const.
    """
    print("\n── G3: Unitaritate (||h||^2 = const) ─────────────────────────────")

    n = len(sigma)
    amp = 0.01
    n_steps = 1000

    alpha = make_alpha(sigma, nb, PHI_SCALE_CANONICAL)
    c2    = C_WAVE**2

    center = max(range(n), key=lambda i: sigma[i])
    h = [amp * math.exp(-0.5 * ((i - center) / (n**0.5 * 0.05))**2)
         for i in range(n)]
    v = [0.] * n

    norm0 = math.sqrt(sum(hi**2 for hi in h))

    Lh    = laplacian_rw(h, nb)
    accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
    v_half = [v[i] + 0.5 * DT * accel[i] for i in range(n)]

    norms = []
    for step in range(1, n_steps + 1):
        h = [h[i] + DT * v_half[i] for i in range(n)]
        Lh    = laplacian_rw(h, nb)
        accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
        v_half = [v_half[i] + DT * accel[i] for i in range(n)]
        if step % 100 == 0:
            norm_t = math.sqrt(sum(hi**2 for hi in h))
            norms.append(norm_t / norm0)
            print(f"  step={step:4d}  ||h(t)||/||h(0)|| = {norm_t/norm0:.8f}")

    max_dev = max(abs(x - 1.) for x in norms)
    unitarity_ok = max_dev < 0.01
    print(f"\n  Max deviation: {max_dev:.6e}  (<0.01: {'PASS' if unitarity_ok else 'FAIL'})")
    return {"norms": norms, "max_dev": max_dev, "unitarity_ok": unitarity_ok}


# ── G4: Camp gravitational puternic ──────────────────────────────────────────

def test_G4_strong_field(sigma, nb, phi_scales):
    """
    La Phi mare (0.5, 0.9): conservarea covariant tine?
    La Phi=0.9: N(i) merge spre 0 pe unele noduri → alpha diverge?
    """
    print("\n── G4: Camp gravitational puternic — conservarea covariant ────────")
    print(f"  {'Phi_scale':>10} {'drift_flat':>11} {'drift_cov':>10} "
          f"{'ratio':>8} {'G14b':>5}")
    rows = []
    for phi_s in phi_scales:
        try:
            res = run_wave(sigma, nb, phi_s, 0.01, 400, DT, C_WAVE, SEED)
            gate = res["drift_cov"] < 0.05  # threshold mai relaxat la camp puternic
            rows.append({"phi_scale": phi_s, **{k: res[k] for k in
                         ["drift_flat", "drift_cov", "ratio"]}})
            print(f"  {phi_s:>10.3f} {res['drift_flat']:>11.4f} "
                  f"{res['drift_cov']:>10.6f} {min(res['ratio'],9999.):>8.2f} "
                  f"{'PASS' if gate else 'FAIL':>5}")
        except Exception as e:
            print(f"  {phi_s:>10.3f} ERROR: {e}")
            rows.append({"phi_scale": phi_s, "error": str(e)})
    return rows


# ── G5: Conditii initiale dezordonate ────────────────────────────────────────

def test_G5_random_initial(sigma, nb, n_configs=5):
    """
    In loc de wave packet gaussian, folosim conditii aleatoare (random noise).
    Test: E_cov mai e conservata pentru conditii initiale generice?
    """
    print("\n── G5: Conditii initiale aleatoare (random noise) ─────────────────")
    n = len(sigma)
    rows = []
    for i in range(n_configs):
        rng = random.Random(SEED + i * 1000)
        # h random, v=0
        h_init = [rng.gauss(0., 0.01) for _ in range(n)]
        amp_actual = math.sqrt(sum(x**2 for x in h_init) / n)

        alpha = make_alpha(sigma, nb, PHI_SCALE_CANONICAL)
        c2    = C_WAVE**2

        h = h_init[:]
        v = [0.] * n
        Lh    = laplacian_rw(h, nb)
        accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
        v_half = [v[i] + 0.5 * DT * accel[i] for i in range(n)]

        E0_flat, E0_cov = energy(h, v_half, nb, alpha, c2)

        for _ in range(400):
            h = [h[i] + DT * v_half[i] for i in range(n)]
            Lh    = laplacian_rw(h, nb)
            accel = [alpha[i] * c2 * Lh[i] for i in range(n)]
            v_half = [v_half[i] + DT * accel[i] for i in range(n)]

        E_flat, E_cov = energy(h, v_half, nb, alpha, c2)
        drift_cov  = abs(E_cov / E0_cov - 1.) if E0_cov > 1e-30 else float("nan")
        drift_flat = abs(E_flat / E0_flat - 1.) if E0_flat > 1e-30 else float("nan")
        gate = drift_cov < 0.02
        rows.append({"config": i, "amp": amp_actual,
                     "drift_flat": drift_flat, "drift_cov": drift_cov,
                     "gate": gate})
        print(f"  config={i}  amp={amp_actual:.4f}  drift_flat={drift_flat:.4f}  "
              f"drift_cov={drift_cov:.6f}  G14b={'PASS' if gate else 'FAIL'}")
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("=" * 70)
    print("QNG STRESS TEST — Categoria G: Atac pe conservarea covariant")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print("Bomba: E_cov tine sub perturbatii extreme si timp lung?")
    print("=" * 70)

    print(f"\n[0] Graf Jaccard N={N}, k={K}...", end=" ", flush=True)
    sigma, nb = build_jaccard_graph(N, K, K, SEED)
    print(f"done")

    r_G1 = test_G1_amplitude(sigma, nb,
        amplitudes=[0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0])

    r_G2 = test_G2_long_time(sigma, nb,
        step_counts=[400, 800, 1600, 3200, 6400])

    r_G3 = test_G3_unitarity(sigma, nb)

    r_G4 = test_G4_strong_field(sigma, nb,
        phi_scales=[0.08, 0.2, 0.4, 0.6, 0.8, 0.95])

    r_G5 = test_G5_random_initial(sigma, nb, n_configs=5)

    # ── Verdict ───────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SUMAR FINAL — Robustete conservare covariant")
    print("=" * 70)

    # G1: la ce amplitudine cade?
    g1_fail = next((r for r in r_G1 if r["drift_cov"] >= 0.02), None)
    print(f"\nG1 Amplitudine: {'FAIL la amp=' + str(g1_fail['amp']) if g1_fail else 'PASS la toate'}")

    # G2: drift crescator?
    g2_last = r_G2[-1]
    g2_linear = (g2_last.get("drift_cov", 0.) / r_G2[0].get("drift_cov", 1.)) / \
                (g2_last["n_steps"] / r_G2[0]["n_steps"])
    print(f"G2 Timp lung: drift la {g2_last['n_steps']} pasi = {g2_last.get('drift_cov',0.):.4f}")

    # G3: unitaritate
    print(f"G3 Unitaritate: max_dev={r_G3['max_dev']:.2e}  {'PASS' if r_G3['unitarity_ok'] else 'FAIL'}")

    # G4: camp puternic
    g4_fail = next((r for r in r_G4 if r.get("drift_cov", 0.) >= 0.05), None)
    print(f"G4 Camp puternic: {'FAIL la phi=' + str(g4_fail['phi_scale']) if g4_fail else 'PASS la toate'}")

    # G5: conditii aleatoare
    g5_fail_count = sum(1 for r in r_G5 if not r["gate"])
    print(f"G5 Conditii aleatoare: {len(r_G5)-g5_fail_count}/{len(r_G5)} PASS")

    checks = {
        "G1_high_amplitude":   g1_fail is None,
        "G2_long_time_stable": g2_last.get("drift_cov", 1.) < 0.05,
        "G3_unitarity":        r_G3["unitarity_ok"],
        "G4_strong_field":     g4_fail is None,
        "G5_random_IC":        g5_fail_count == 0,
    }
    print()
    for check, result in checks.items():
        print(f"  {check:<35} {'PASS' if result else 'FAIL'}")

    n_pass  = sum(checks.values())
    verdict = f"{n_pass}/{len(checks)}_PASS"
    print(f"\nverdict={verdict}")
    print(f"Timp: {time.time()-t0:.1f}s")

    # ── Salvare ───────────────────────────────────────────────────────────────
    json_path = OUT_DIR / "stress_G_results.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "verdict": verdict, "checks": checks,
        "G1_amplitude": r_G1,
        "G2_long_time": r_G2,
        "G3_unitarity": {"max_dev": r_G3["max_dev"], "ok": r_G3["unitarity_ok"]},
        "G4_strong_field": r_G4,
        "G5_random_IC": r_G5,
    }, indent=2, default=str), encoding="utf-8")

    csv_G1 = OUT_DIR / "stress_G1_amplitude.csv"
    with csv_G1.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["amp", "drift_flat", "drift_cov", "ratio"])
        w.writeheader(); w.writerows(r_G1)

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {json_path.name}  {csv_G1.name}")
    print()
    print("=" * 70)
    print(f"STRESS TEST G COMPLET | verdict={verdict}")
    print("=" * 70)

    return 0 if n_pass >= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
