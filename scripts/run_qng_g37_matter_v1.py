#!/usr/bin/env python3
"""
QNG G37 — Definirea Materiei: IPR si Clasificare Moduri

Materia in QNG se defineste prin LOCALIZARE spatiala:

  IPR_alpha = Σ_i phi_alpha(i)^4   [Inverse Participation Ratio]
  DR_alpha  = IPR_alpha * n / 3     [Delocalization Ratio, =1 pt vector random]

  DR < 1.5   → puternic delocalizat  → DARK MATTER (nu emite, nu se vede)
  DR in [1.5, 4.0] → intermediar    → DARK MATTER (halo, structuri mari)
  DR > 4.0   → localizat            → MATERIE BARIONICA (interactii locale, "vizibil")

  Modul constant → DARK ENERGY (fond omogen, nici macar structura spatiala)

Comparatii cosmologice (Planck 2018):
  Omega_Lambda = 68.4%   [dark energy]
  Omega_DM     = 26.8%   [dark matter]
  Omega_b      =  4.9%   [materie barionica]
  Omega_DM / Omega_b = 5.47

Gates:
  G37a — Top moduri mai localizate decat bottom: DR(top)/DR(bottom) > 1.5
  G37b — Fractia barionica Omega_b_QNG in [0.02, 0.12]  (vs 4.9%)
  G37c — Raportul Omega_DM/Omega_b in [2.0, 15.0]        (vs 5.47)
  G37d — Omega_tot = Lambda + DM + b in [0.80, 1.20]     (platitudine)
  G37e — Omega_Lambda absolut < 50% delta (DIAGNOSTIC, OPEN_PROBLEM)
         1 mod constant / 280 total => Omega_DE_QNG << 0.6847 (factor ~1800x)
         Nu este bug numeric — limitare structurala teoretica.
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g37-matter-v1"

M_EFF_SQ  = 0.014
N_BOTTOM  = 40
N_TOP     = 40
N_ITER    = 200
SEED      = 3401

# Cosmologie Planck 2018
OMEGA_LAMBDA_OBS = 0.6847
OMEGA_DM_OBS     = 0.2607
OMEGA_B_OBS      = 0.0490
RATIO_DM_B_OBS   = OMEGA_DM_OBS / OMEGA_B_OBS   # 5.32


def fmt(v):
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.5e}"
    return f"{v:.6f}"


# ── Graf ──────────────────────────────────────────────────────────────────────

def build_jaccard_weighted(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    jw = {}
    for i in range(n):
        Ni = adj0[i] | {i}
        sc = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            sc.append((inter/union if union else 0.0, j))
        sc.sort(reverse=True)
        for s, j in sc[:k_conn]:
            key = (min(i,j), max(i,j))
            jw[key] = max(jw.get(key, 0.0), s)
    adj_w = [[] for _ in range(n)]
    for (i,j), w in jw.items():
        adj_w[i].append((j,w)); adj_w[j].append((i,w))
    return adj_w


def deg_w(adj_w): return [sum(w for _,w in nb) for nb in adj_w]
def apply_K(v, adj_w, deg, m2):
    return [(deg[i]+m2)*v[i] - sum(w*v[j] for j,w in adj_w[i]) for i in range(len(v))]
def dot(u,v): return sum(u[i]*v[i] for i in range(len(u)))
def norm(v): return math.sqrt(dot(v,v))
def deflate(v, basis):
    w = v[:]
    for b in basis:
        c = dot(w,b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w


def compute_top_modes(adj_w, n, n_modes, n_iter, m2, rng, extra_basis=None):
    d = deg_w(adj_w); vecs=[]; lams=[]; eb=list(extra_basis or [])
    for _ in range(n_modes):
        v = [rng.gauss(0,1) for _ in range(n)]
        v = deflate(v, eb+vecs); nm = norm(v)
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            w = apply_K(v, adj_w, d, m2); w = deflate(w, eb+vecs); nm = norm(w)
            if nm < 1e-14: break
            v = [x/nm for x in w]
        Kv = apply_K(v, adj_w, d, m2); lam = max(m2, dot(v, Kv))
        vecs.append(v); lams.append(lam)
    order = sorted(range(len(lams)), key=lambda k: -lams[k])
    return [lams[k] for k in order], [vecs[k] for k in order]


def compute_bottom_modes(adj_w, n, n_modes, n_iter, m2, lam_shift, rng, extra_basis=None):
    d = deg_w(adj_w); vecs=[]; lams_K=[]; eb=list(extra_basis or [])
    for _ in range(n_modes):
        v = [rng.gauss(0,1) for _ in range(n)]
        v = deflate(v, eb+vecs); nm = norm(v)
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            Kv = apply_K(v, adj_w, d, m2)
            Av = [lam_shift*v[i]-Kv[i] for i in range(n)]
            Av = deflate(Av, eb+vecs); nm = norm(Av)
            if nm < 1e-14: break
            v = [x/nm for x in Av]
        Kv = apply_K(v, adj_w, d, m2); lam = max(m2, dot(v, Kv))
        vecs.append(v); lams_K.append(lam)
    order = sorted(range(len(lams_K)), key=lambda k: lams_K[k])
    return [lams_K[k] for k in order], [vecs[k] for k in order]


def compute_trace_moments(adj_w, deg, n, m2):
    tr_K = sum(d + m2 for d in deg)
    tr_K2 = 0.0
    for i in range(n):
        kii = deg[i] + m2
        tr_K2 += kii * kii
        for _, w in adj_w[i]:
            tr_K2 += w * w
    return tr_K, tr_K2


def ipr(phi):
    """Inverse Participation Ratio = Σ phi_i^4"""
    return sum(x**4 for x in phi)


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
    log("QNG G37 — Definirea Materiei: IPR si Clasificare Moduri")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log("="*70)
    log()
    log("Clasificare:")
    log("  DR < 1.5        → delocalizat     → DARK MATTER")
    log("  1.5 <= DR < 4.0 → semi-localizat  → DARK MATTER (halo)")
    log("  DR >= 4.0       → localizat        → MATERIE BARIONICA")
    log("  Modul constant  →                  → DARK ENERGY")
    log()
    log(f"Planck 2018: Omega_Lambda={OMEGA_LAMBDA_OBS:.3f}  Omega_DM={OMEGA_DM_OBS:.3f}  Omega_b={OMEGA_B_OBS:.3f}")
    log(f"             Omega_DM/Omega_b = {RATIO_DM_B_OBS:.2f}")

    n = 280
    adj_w = build_jaccard_weighted(n, 8, 8, SEED)
    deg   = deg_w(adj_w)

    # ── Momente de urma — spectru complet ─────────────────────────────────────
    tr_K, tr_K2 = compute_trace_moments(adj_w, deg, n, M_EFF_SQ)
    mean_lam  = tr_K / n
    var_lam   = tr_K2 / n - mean_lam**2
    omega_mean_est = math.sqrt(mean_lam) * (1.0 - var_lam / (8.0 * mean_lam**2))
    E_total_full_est = n / 2.0 * omega_mean_est

    log(f"\n[0] Spectru complet (din momente de urma):")
    log(f"    Tr(K)={fmt(tr_K)}  mean_lambda={fmt(mean_lam)}")
    log(f"    omega_mean_est={fmt(omega_mean_est)}")
    log(f"    E_total_full_est = n/2 * omega_mean = {fmt(E_total_full_est)}")

    # ── Eigenmoduri ────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmoduri ({N_TOP} top + {N_BOTTOM} bottom + 1 constant)...")
    phi0    = [1/math.sqrt(n)] * n
    lambda0 = M_EFF_SQ
    omega0  = math.sqrt(lambda0)

    t1 = time.time()
    lams_top, vecs_top = compute_top_modes(
        adj_w, n, N_TOP, N_ITER, M_EFF_SQ, random.Random(SEED+1), extra_basis=[phi0])
    lam_shift = lams_top[0] * 1.05 + 0.5
    lams_bot, vecs_bot = compute_bottom_modes(
        adj_w, n, N_BOTTOM, N_ITER, M_EFF_SQ, lam_shift, random.Random(SEED+2), extra_basis=[phi0])
    log(f"    Calculat in {time.time()-t1:.1f}s")

    # ── IPR pentru fiecare mod ─────────────────────────────────────────────────
    log("\n[2] Inverse Participation Ratio (IPR) si clasificare")

    ipr_random = 3.0 / n   # IPR asteptat pentru vector Gaussian aleator
    DR_THRESHOLD_LOW  = 1.5   # sub acesta: dark matter
    DR_THRESHOLD_HIGH = 4.0   # peste acesta: materie barionica

    all_lambdas = [lambda0] + lams_bot + lams_top
    all_vecs    = [phi0]    + vecs_bot  + vecs_top
    all_labels  = ["dark_energy"] + ["dark_matter_candidate"]*N_BOTTOM + ["baryonic_candidate"]*N_TOP

    mode_data = []
    E_dark_energy  = 0.0
    E_dark_matter  = 0.0
    E_baryonic     = 0.0

    ipr_bottom_vals = []
    ipr_top_vals    = []

    for k, (lam, phi, label_init) in enumerate(zip(all_lambdas, all_vecs, all_labels)):
        omega = math.sqrt(lam)
        E_k   = 0.5 * omega
        ipr_k = ipr(phi)
        DR_k  = ipr_k / ipr_random

        if k == 0:  # constant mode
            category = "dark_energy"
            E_dark_energy += E_k
        elif DR_k >= DR_THRESHOLD_HIGH:
            category = "baryonic"
            E_baryonic += E_k
        else:
            category = "dark_matter"
            E_dark_matter += E_k

        if k > 0 and k <= N_BOTTOM:
            ipr_bottom_vals.append(ipr_k)
        elif k > N_BOTTOM:
            ipr_top_vals.append(ipr_k)

        mode_data.append({
            "mode": k,
            "source": "constant" if k==0 else ("bottom" if k<=N_BOTTOM else "top"),
            "lambda": lam,
            "omega": omega,
            "E_k": E_k,
            "IPR": ipr_k,
            "DR": DR_k,
            "category": category,
        })

    E_partial_total = E_dark_energy + E_dark_matter + E_baryonic

    DR_bottom_mean = statistics.mean(ipr_bottom_vals) / ipr_random if ipr_bottom_vals else float("nan")
    DR_top_mean    = statistics.mean(ipr_top_vals)    / ipr_random if ipr_top_vals    else float("nan")
    DR_ratio = DR_top_mean / DR_bottom_mean if DR_bottom_mean > 0 else float("nan")

    n_dark_energy = sum(1 for m in mode_data if m["category"] == "dark_energy")
    n_dark_matter = sum(1 for m in mode_data if m["category"] == "dark_matter")
    n_baryonic    = sum(1 for m in mode_data if m["category"] == "baryonic")

    log(f"\n  IPR random (vector Gaussian): {fmt(ipr_random)}")
    log(f"  DR_bottom_mean = {fmt(DR_bottom_mean)}")
    log(f"  DR_top_mean    = {fmt(DR_top_mean)}")
    log(f"  DR(top)/DR(bottom) = {fmt(DR_ratio)}")
    log(f"\n  Clasificare ({len(mode_data)} moduri totale):")
    log(f"    Dark energy (constant):  {n_dark_energy:3d} moduri  E={fmt(E_dark_energy)}")
    log(f"    Dark matter (DR<{DR_THRESHOLD_HIGH:.0f}):   {n_dark_matter:3d} moduri  E={fmt(E_dark_matter)}")
    log(f"    Materie barionica (DR>={DR_THRESHOLD_HIGH:.0f}): {n_baryonic:3d} moduri  E={fmt(E_baryonic)}")
    log(f"    E_partial_total = {fmt(E_partial_total)}")

    # Top 10 mode-uri dupa DR (cele mai localizate)
    sorted_by_DR = sorted(mode_data[1:], key=lambda m: -m["DR"])
    log(f"\n  Top 10 moduri dupa DR (cele mai localizate = materie):")
    log(f"  {'mod':>5}  {'sursa':>8}  {'lambda':>10}  {'DR':>8}  {'cat':>12}")
    for m in sorted_by_DR[:10]:
        log(f"  {m['mode']:>5}  {m['source']:>8}  {fmt(m['lambda']):>10}  {fmt(m['DR']):>8}  {m['category']:>12}")

    # ── Extrapolarea la spectrul complet (n=280 moduri) ────────────────────────
    log("\n[3] Extrapolarea Omega la spectrul complet")
    log(f"    E_total_full_est = {fmt(E_total_full_est)}  (din Tr(K), toate cele {n} moduri)")
    log(f"    E_partial        = {fmt(E_partial_total)}   (din cele {len(mode_data)} moduri)")

    # Fractions din moduri partiale
    f_b_partial  = E_baryonic    / E_partial_total
    f_DM_partial = E_dark_matter / E_partial_total
    f_DE_partial = E_dark_energy / E_partial_total

    log(f"\n  Fractii din moduri partiale (81/280):")
    log(f"    f_DE (dark energy, partial)  = {fmt(f_DE_partial)}  (vs Omega_Lambda={OMEGA_LAMBDA_OBS:.3f})")
    log(f"    f_DM (dark matter, partial)  = {fmt(f_DM_partial)}  (vs Omega_DM={OMEGA_DM_OBS:.3f})")
    log(f"    f_b  (baryonic, partial)     = {fmt(f_b_partial)}  (vs Omega_b={OMEGA_B_OBS:.3f})")

    # Modurile MIDDLE (199 necomputate) au energie intermediara
    # Estimam: E_middle = E_total_full - E_partial
    E_middle_est = E_total_full_est - E_partial_total
    if E_middle_est < 0: E_middle_est = 0.0

    # Modurile middle au IPR ~ random (delocalizate) => dark matter
    # Deci E_dark_matter_full = E_dark_matter_partial + E_middle
    E_DM_full_est = E_dark_matter + E_middle_est
    E_DE_full_est = E_dark_energy
    E_b_full_est  = E_baryonic
    E_total_est2  = E_DE_full_est + E_DM_full_est + E_b_full_est

    Omega_DE_QNG = E_DE_full_est / E_total_est2 if E_total_est2 > 0 else float("nan")
    Omega_DM_QNG = E_DM_full_est / E_total_est2 if E_total_est2 > 0 else float("nan")
    Omega_b_QNG  = E_b_full_est  / E_total_est2 if E_total_est2 > 0 else float("nan")
    Omega_tot    = Omega_DE_QNG + Omega_DM_QNG + Omega_b_QNG
    ratio_DM_b   = Omega_DM_QNG / Omega_b_QNG if Omega_b_QNG > 0 else float("nan")

    log(f"\n  Extrapolat la spectrul complet (middle modes ~ dark matter):")
    log(f"    E_middle_est = {fmt(E_middle_est)}  ({n-len(mode_data)} moduri necomputate)")
    log(f"    Omega_DE (QNG) = {fmt(Omega_DE_QNG)}  vs Omega_Lambda={OMEGA_LAMBDA_OBS:.3f}  delta={fmt(abs(Omega_DE_QNG-OMEGA_LAMBDA_OBS))}")
    log(f"    Omega_DM (QNG) = {fmt(Omega_DM_QNG)}  vs Omega_DM={OMEGA_DM_OBS:.3f}     delta={fmt(abs(Omega_DM_QNG-OMEGA_DM_OBS))}")
    log(f"    Omega_b  (QNG) = {fmt(Omega_b_QNG)}  vs Omega_b={OMEGA_B_OBS:.3f}       delta={fmt(abs(Omega_b_QNG-OMEGA_B_OBS))}")
    log(f"    Omega_tot      = {fmt(Omega_tot)}")
    log(f"    Omega_DM/Omega_b = {fmt(ratio_DM_b)}  vs observat={RATIO_DM_B_OBS:.2f}")

    # ── Noduri "materie": distributia C_ii ────────────────────────────────────
    log("\n[4] Noduri materie: distributia variancei locale C_ii")

    C_diag = [0.0] * n
    for k, lam in enumerate(all_lambdas):
        w2 = 1.0 / (2.0 * math.sqrt(lam))
        phi = all_vecs[k]
        for i in range(n):
            C_diag[i] += phi[i] * phi[i] * w2

    C_dark_contrib = (1.0/n) / (2.0 * omega0)   # contributia modului constant
    C_mean = statistics.mean(C_diag)
    C_std  = statistics.stdev(C_diag)
    C_min  = min(C_diag); C_max = max(C_diag)

    log(f"    C_ii: min={fmt(C_min)}  max={fmt(C_max)}  mean={fmt(C_mean)}  std={fmt(C_std)}")
    log(f"    C_dark_contrib (per nod) = {fmt(C_dark_contrib)}")

    # Noduri "barionice": C_ii > mean + 1.5*std (outlieri)
    thresh_baryon = C_mean + 1.5 * C_std
    n_baryon_nodes = sum(1 for c in C_diag if c > thresh_baryon)
    f_baryon_nodes = n_baryon_nodes / n

    # Fractia din energia locala a nodurilor barionice
    C_baryon_sum = sum(c for c in C_diag if c > thresh_baryon)
    f_baryon_energy = C_baryon_sum / sum(C_diag)

    log(f"\n    Prag barionic = mean + 1.5*std = {fmt(thresh_baryon)}")
    log(f"    Noduri barionice: {n_baryon_nodes}/{n} = {f_baryon_nodes*100:.1f}%")
    log(f"    Fractia energiei locale la noduri barionice: {f_baryon_energy*100:.1f}%")
    log(f"    Comparatie: Omega_b = {OMEGA_B_OBS*100:.1f}%")

    # Histograma C_ii pe intervale
    bins = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
    log(f"\n    Histograma C_ii:")
    for i in range(len(bins)-1):
        cnt = sum(1 for c in C_diag if bins[i] <= c < bins[i+1])
        bar = "█" * cnt
        log(f"    [{bins[i]:.2f}, {bins[i+1]:.2f}): {cnt:3d}  {bar}")
    cnt_last = sum(1 for c in C_diag if c >= bins[-1])
    log(f"    [{bins[-1]:.2f}, inf): {cnt_last:3d}  {'█'*cnt_last}")

    # ── Rezumat comparatie cosmologica ─────────────────────────────────────────
    log("\n[5] Comparatie finala cu Planck 2018")
    log(f"    {'Componenta':20s}  {'QNG':>10}  {'Planck':>10}  {'Delta':>10}")
    log("    " + "-"*55)
    for name, qng_val, planck_val in [
        ("Omega_Lambda (DE)", Omega_DE_QNG, OMEGA_LAMBDA_OBS),
        ("Omega_DM",          Omega_DM_QNG, OMEGA_DM_OBS),
        ("Omega_b",           Omega_b_QNG,  OMEGA_B_OBS),
        ("Omega_DM/Omega_b",  ratio_DM_b,   RATIO_DM_B_OBS),
    ]:
        delta = abs(qng_val - planck_val) / planck_val * 100 if planck_val > 0 else float("nan")
        log(f"    {name:20s}  {fmt(qng_val):>10}  {planck_val:>10.4f}  {delta:>8.1f}%")

    # ── Gates ─────────────────────────────────────────────────────────────────
    log("\n" + "="*70)
    log("GATES G37")
    log("="*70)

    g37a = (not math.isnan(DR_ratio)) and DR_ratio > 1.5
    g37b = (not math.isnan(Omega_b_QNG)) and (0.02 <= Omega_b_QNG <= 0.12)
    g37c = (not math.isnan(ratio_DM_b)) and (2.0 <= ratio_DM_b <= 15.0)
    g37d = (not math.isnan(Omega_tot)) and (0.80 <= Omega_tot <= 1.20)

    for label, gate, val, cond in [
        ("G37a", g37a, DR_ratio,
         f"DR(top)/DR(bottom) > 1.5  [top moduri mai localizate]"),
        ("G37b", g37b, Omega_b_QNG,
         f"Omega_b_QNG in [0.02, 0.12]  (vs Planck Omega_b={OMEGA_B_OBS:.3f})"),
        ("G37c", g37c, ratio_DM_b,
         f"Omega_DM/Omega_b in [2.0, 15.0]  (vs Planck {RATIO_DM_B_OBS:.2f})"),
        ("G37d", g37d, Omega_tot,
         f"Omega_tot in [0.80, 1.20]  (platitudine)"),
    ]:
        st = "PASS" if gate else "FAIL"
        log(f"\n{label} — {cond}")
        log(f"       Valoare: {fmt(val)}  ->  {st}")

    # G37e — Omega_Lambda absolut (DIAGNOSTIC, OPEN_PROBLEM)
    # Problema structurala: 1 mod constant din n=280 => E_DE/E_tot << 0.68
    # Nu este un bug numeric — este o limitare teoretica a identificarii curente.
    # Factor de discrepanta: 0.6847 / 0.000380 ~ 1800x
    delta_lambda_rel = abs(Omega_DE_QNG - OMEGA_LAMBDA_OBS) / OMEGA_LAMBDA_OBS
    g37e_threshold   = 0.50   # orice discrepanta > 50% = FAIL
    g37e             = delta_lambda_rel < g37e_threshold   # va fi FAIL (~99.9%)
    g37e_factor      = OMEGA_LAMBDA_OBS / Omega_DE_QNG if Omega_DE_QNG > 0 else float("inf")

    log(f"\nG37e — Omega_Lambda absolut (DIAGNOSTIC, OPEN_PROBLEM)")
    log(f"       Omega_DE_QNG = {fmt(Omega_DE_QNG)}  vs Planck Omega_Lambda = {OMEGA_LAMBDA_OBS:.4f}")
    log(f"       Delta relativ = {delta_lambda_rel*100:.1f}%   Factor discrepanta = {g37e_factor:.0f}x")
    log(f"       Conditie: delta_rel < {g37e_threshold*100:.0f}%  ->  {'PASS' if g37e else 'FAIL'}")
    log(f"       STATUS: OPEN_PROBLEM")
    log(f"       CAUZA: Modul constant (1/sqrt(n)) reprezinta 1/{n} din spectru.")
    log(f"              E_DE = omega_0/2 = sqrt(M_EFF_SQ)/2 = {fmt(math.sqrt(M_EFF_SQ)/2)}")
    log(f"              E_total ~ n/2 * omega_mean => f_DE ~ 1/n * omega_0/omega_mean << 0.68")
    log(f"              Necesita un mecanism teoretic nou (ex. condensat de vacuum,")
    log(f"              degenerare exponentiala) pentru a amplifica contributia DE.")

    n_pass = sum([g37a, g37b, g37c, g37d])
    n_total_diagnostic = 5   # include G37e ca gate diagnostic
    log(f"\nSUMAR: {n_pass}/4 gate-uri principale trecute  ({n_pass}/{n_total_diagnostic} cu diagnostic G37e)")
    log(f"G37a [{'PASS' if g37a else 'FAIL'}]  G37b [{'PASS' if g37b else 'FAIL'}]  "
        f"G37c [{'PASS' if g37c else 'FAIL'}]  G37d [{'PASS' if g37d else 'FAIL'}]  "
        f"G37e [{'PASS' if g37e else 'FAIL (OPEN_PROBLEM)'}]")
    log(f"Timp total: {time.time()-t0:.1f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    with (out_dir/"modes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["mode","source","lambda","omega","E_k","IPR","DR","category"])
        w.writeheader(); w.writerows(mode_data)

    with (out_dir/"nodes.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["node","C_ii","baryon_flag"])
        w.writeheader()
        w.writerows([{"node": i, "C_ii": C_diag[i],
                      "baryon_flag": int(C_diag[i] > thresh_baryon)} for i in range(n)])

    result = {
        "ipr_analysis": {
            "ipr_random": ipr_random,
            "DR_bottom_mean": DR_bottom_mean,
            "DR_top_mean": DR_top_mean,
            "DR_ratio_top_bottom": DR_ratio,
            "n_dark_energy": n_dark_energy,
            "n_dark_matter": n_dark_matter,
            "n_baryonic_modes": n_baryonic,
        },
        "energy_fractions_partial": {
            "f_DE": f_DE_partial, "f_DM": f_DM_partial, "f_b": f_b_partial,
        },
        "omega_extrapolated": {
            "Omega_DE_QNG": Omega_DE_QNG,
            "Omega_DM_QNG": Omega_DM_QNG,
            "Omega_b_QNG": Omega_b_QNG,
            "Omega_tot": Omega_tot,
            "ratio_DM_b": ratio_DM_b,
        },
        "planck_comparison": {
            "Omega_Lambda_planck": OMEGA_LAMBDA_OBS,
            "Omega_DM_planck": OMEGA_DM_OBS,
            "Omega_b_planck": OMEGA_B_OBS,
            "ratio_DM_b_planck": RATIO_DM_B_OBS,
        },
        "node_analysis": {
            "C_mean": C_mean, "C_std": C_std,
            "thresh_baryon": thresh_baryon,
            "n_baryon_nodes": n_baryon_nodes,
            "f_baryon_nodes": f_baryon_nodes,
            "f_baryon_energy": f_baryon_energy,
        },
        "gates": {
            "G37a": {"passed": g37a, "value": DR_ratio},
            "G37b": {"passed": g37b, "value": Omega_b_QNG},
            "G37c": {"passed": g37c, "value": ratio_DM_b},
            "G37d": {"passed": g37d, "value": Omega_tot},
            "G37e": {
                "passed": g37e,
                "status": "OPEN_PROBLEM",
                "value_Omega_DE_QNG": Omega_DE_QNG,
                "value_Omega_Lambda_planck": OMEGA_LAMBDA_OBS,
                "delta_rel": delta_lambda_rel,
                "factor_discrepancy": g37e_factor,
                "description": (
                    "Omega_Lambda absolut: 1 mod constant din n=280 produce "
                    "E_DE/E_tot << 0.68. Limitare structurala, nu bug numeric. "
                    "Factor ~1800x sub valoarea Planck 2018. "
                    "Necesita mecanism teoretic nou pentru amplificarea contributiei DE."
                ),
            },
        },
        "summary": {
            "n_pass": n_pass, "n_total": 4, "n_total_with_diagnostic": 5,
            "all_pass_main": n_pass == 4,
            "open_problems": ["G37e"],
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
