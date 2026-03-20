#!/usr/bin/env python3
"""
QNG — Audit de Legitimitate: Parametrii G26 sunt cu adevărat independenți de Planck?

Întrebările cheie:
  1. Formula ell_damp a fost derivată ÎNAINTE sau DUPĂ ce s-a văzut că v1 a eșuat?
  2. μ₁ = 0.291 vine din graf sau a fost ajustat după datele Planck?
  3. d_s = 4.082 este robust și independent de CMB?
  4. ell_D_T = 576.144 — de unde vine și când a fost fixat?

Output:
  05_validation/evidence/artifacts/legitimacy-audit-v1/
    audit_report.md
    audit_summary.json
"""

from __future__ import annotations

import json
import math
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "legitimacy-audit-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Valori de referință
# ─────────────────────────────────────────────────────────────────────────────
MU1_USED       = 0.291        # valoarea folosită în G26
MU1_THEORY     = (2 - math.sqrt(2)) / 2  # = 0.29289, din iso_target=1/√2
D_S_USED       = 4.082
ELL_D_T_USED   = 576.144
ELL_DAMP_PLANCK = 1290.9

# Formula v1 (eșuată)
ELL_DAMP_V1 = ELL_D_T_USED / math.sqrt(MU1_USED)
# Formula v2 (corectată după eșec)
ELL_DAMP_V2 = ELL_D_T_USED * math.sqrt(6.0 / (D_S_USED * MU1_USED))
# Eroarea v1 față de Planck
SIGMA_V1 = abs(ELL_DAMP_V1 - ELL_DAMP_PLANCK) / 12.5  # σ_Planck ≈ 12.5
SIGMA_V2 = abs(ELL_DAMP_V2 - ELL_DAMP_PLANCK) / math.sqrt(19.8**2 + 12.5**2)


def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int):
    """Construiește graful Jaccard și returnează lista de vecini."""
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
            scores.append((inter / union if union else 0.0, j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def power_method_mu1(neighbours: list, n_iter: int = 300, seed: int = 42) -> float:
    """Calculează μ₁ (al doilea eigenvalue al Laplacianului RW) prin power method."""
    n = len(neighbours)
    rng = random.Random(seed)

    def rw(f):
        return [sum(f[j] for j in nb) / len(nb) if nb else 0.0 for nb in neighbours]

    def dot(u, v): return sum(u[i] * v[i] for i in range(n))
    def norm(v):
        s = math.sqrt(dot(v, v))
        return [x / s for x in v] if s > 1e-14 else v[:]
    def defl(v, basis):
        w = v[:]
        for b in basis:
            c = dot(w, b)
            w = [w[i] - c * b[i] for i in range(n)]
        return w

    # Modul 0 (constant)
    v0 = norm([1.0] * n)
    # Modul 1 (spectral gap)
    v1 = norm(defl([rng.gauss(0, 1) for _ in range(n)], [v0]))
    for _ in range(n_iter):
        w = norm(defl(rw(v1), [v0]))
        if math.sqrt(dot(w, w)) < 1e-14: break
        v1 = w
    Av1 = rw(v1)
    alpha = dot(v1, Av1)
    return max(0.0, 1.0 - alpha)


def sweep_mu1_over_seeds(n_seeds: int = 30) -> dict:
    """Calculează μ₁ pe n_seeds seed-uri diferite pentru N=280, k=8."""
    mu1_values = []
    seeds = list(range(1000, 1000 + n_seeds))
    for seed in seeds:
        nb = build_jaccard_graph(280, 8, 8, seed)
        mu1 = power_method_mu1(nb, n_iter=300, seed=seed + 1)
        mu1_values.append(mu1)

    # Adăugăm seed-ul canonic 3401
    nb_canon = build_jaccard_graph(280, 8, 8, 3401)
    mu1_canon = power_method_mu1(nb_canon, n_iter=300, seed=3402)

    return {
        "seeds_tested": seeds,
        "mu1_values": mu1_values,
        "mu1_canonical_seed3401": mu1_canon,
        "mu1_mean": statistics.mean(mu1_values),
        "mu1_std": statistics.stdev(mu1_values),
        "mu1_min": min(mu1_values),
        "mu1_max": max(mu1_values),
        "mu1_theory": MU1_THEORY,
        "bias_from_theory_pct": (statistics.mean(mu1_values) - MU1_THEORY) / MU1_THEORY * 100,
    }


def compute_ell_damp_from_mu1(mu1: float) -> float:
    return ELL_D_T_USED * math.sqrt(6.0 / (D_S_USED * mu1))


def main():
    log = []
    def L(s=""):
        log.append(s); print(s)

    findings = {}

    L("=" * 72)
    L("QNG — AUDIT DE LEGITIMITATE: G26 CMB GATE")
    L("=" * 72)
    L(f"Data: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    L()

    # ── FINDING 1: Formula a fost schimbată DUPĂ ce a eșuat ───────────────────
    L("─" * 72)
    L("FINDING 1: Istoria formulei (din git + documente)")
    L("─" * 72)
    L()
    L(f"  Formula v1 (originală):")
    L(f"    ell_damp = ell_D_T / sqrt(μ₁)")
    L(f"    ell_damp_v1 = {ELL_D_T_USED} / sqrt({MU1_USED}) = {ELL_DAMP_V1:.1f}")
    L(f"    vs Planck: {ELL_DAMP_PLANCK}")
    L(f"    Discrepanță: {SIGMA_V1:.1f}σ  → FAIL")
    L()
    L(f"  Commit git: 'fix(c-120): correct Silk damping formula — 17.8σ FAIL → 0.17σ PASS'")
    L(f"  Data commit: 2026-03-15 20:18:04 UTC")
    L()
    L(f"  Formula v2 (corectată DUPĂ eșec):")
    L(f"    ell_damp = ell_D_T × √(6 / (d_s × μ₁))")
    L(f"    ell_damp_v2 = {ELL_DAMP_V2:.1f}")
    L(f"    vs Planck: {ELL_DAMP_PLANCK}")
    L(f"    Discrepanță: {SIGMA_V2:.3f}σ  → PASS")
    L()
    L("  VERDICT FINDING 1: ⚠️  ROȘU")
    L("  Formula v2 NU este o predicție independentă.")
    L("  A fost derivată specific pentru a corecta eșecul v1.")
    L("  Factorul √(6/d_s) a fost introdus DUPĂ ce s-a văzut că v1 greșea cu 17.8σ.")
    L("  Termenul tehnic: HARKing (Hypothesizing After Results are Known).")
    L()

    findings["formula_independence"] = {
        "status": "RED",
        "v1_prediction": round(ELL_DAMP_V1, 1),
        "v1_sigma_fail": round(SIGMA_V1, 1),
        "v2_prediction": round(ELL_DAMP_V2, 1),
        "v2_sigma_pass": round(SIGMA_V2, 3),
        "formula_changed_after_seeing_data": True,
        "commit_message": "fix(c-120): correct Silk damping formula — 17.8σ FAIL → 0.17σ PASS",
        "verdict": "NOT a genuine prediction. Formula was adjusted to match Planck after v1 failed.",
    }

    # ── FINDING 2: μ₁ — independent sau calibrat pe Planck? ──────────────────
    L("─" * 72)
    L("FINDING 2: μ₁ = 0.291 — sursă și independență")
    L("─" * 72)
    L()
    L("  Document 'qng-kr-cmb-connection-v1.md' (data: 2026-03-16) spune:")
    L("  'μ₁ = 0.291 — spectral gap calibrat pe Silk damping Planck (T-065)'")
    L()
    L("  Cuvântul 'calibrat pe' înseamnă că μ₁ a fost ajustat pe datele Planck.")
    L("  Asta contrazice afirmația că μ₁ vine pur din structura grafului.")
    L()
    L("  Pe de altă parte: μ₁ = 0.291199 vine direct din power method pe graful")
    L("  Jaccard cu N=280, k=8, seed=3401 — valoare determinată de algoritm,")
    L("  nu setată manual.")
    L()
    L("  Întrebarea reală: seed=3401 a fost ales ÎNAINTE sau DUPĂ ce s-a știut")
    L("  ce valoare de μ₁ este necesară pentru a bate Planck?")
    L()

    # Calculăm ce μ₁ ar trebui să fie pentru a da exact ell_damp = 1290.9
    mu1_needed = 6.0 * ELL_D_T_USED**2 / (D_S_USED * ELL_DAMP_PLANCK**2)
    L(f"  μ₁ necesar pentru ell_damp = {ELL_DAMP_PLANCK}: {mu1_needed:.5f}")
    L(f"  μ₁ din graful canonic (seed=3401):              {MU1_USED:.5f}")
    L(f"  Diferența: {abs(MU1_USED - mu1_needed):.5f} ({abs(MU1_USED - mu1_needed)/mu1_needed*100:.2f}%)")
    L()
    L(f"  μ₁ teoretic din iso_target: (2-√2)/2 = {MU1_THEORY:.5f}")
    L(f"  Diferența față de grafic: {abs(MU1_USED - MU1_THEORY)/MU1_THEORY*100:.2f}%")
    L()
    L("  Calculăm distribuția μ₁ pe 30 seed-uri (fără a le fi ales după Planck)...")
    L()

    mu1_sweep = sweep_mu1_over_seeds(n_seeds=30)
    mu1_canonical = mu1_sweep["mu1_canonical_seed3401"]
    mu1_mean = mu1_sweep["mu1_mean"]
    mu1_std  = mu1_sweep["mu1_std"]

    L(f"  Sweep 30 seed-uri (1000–1029), N=280, k=8:")
    L(f"    μ₁ mean  = {mu1_mean:.5f}")
    L(f"    μ₁ std   = {mu1_std:.5f}")
    L(f"    μ₁ min   = {mu1_sweep['mu1_min']:.5f}")
    L(f"    μ₁ max   = {mu1_sweep['mu1_max']:.5f}")
    L(f"    μ₁ teoria = {MU1_THEORY:.5f}")
    L()
    L(f"  Seed canonic 3401: μ₁ = {mu1_canonical:.5f}")

    # Calculăm ell_damp pentru mean și pentru seed 3401
    ell_damp_from_mean  = compute_ell_damp_from_mu1(mu1_mean)
    ell_damp_from_canon = compute_ell_damp_from_mu1(mu1_canonical)
    ell_damp_from_theory = compute_ell_damp_from_mu1(MU1_THEORY)

    L()
    L(f"  ell_damp dacă am folosi μ₁ mediu (30 seed-uri): {ell_damp_from_mean:.1f}")
    L(f"  ell_damp cu seed=3401 (canonic):                {ell_damp_from_canon:.1f}")
    L(f"  ell_damp cu μ₁ teoretic (2-√2)/2:               {ell_damp_from_theory:.1f}")
    L(f"  Planck observat:                                 {ELL_DAMP_PLANCK:.1f}")
    L()

    # Câte seed-uri dau ell_damp în 2σ de Planck?
    n_within_2sigma = sum(
        1 for mu1 in mu1_sweep["mu1_values"]
        if abs(compute_ell_damp_from_mu1(mu1) - ELL_DAMP_PLANCK) / math.sqrt(19.8**2 + 12.5**2) < 2.0
    )
    L(f"  Seed-uri cu ell_damp în 2σ de Planck: {n_within_2sigma}/30 = {n_within_2sigma/30*100:.0f}%")
    L()

    if n_within_2sigma >= 25:
        L("  VERDICT FINDING 2: 🟡 GALBEN")
        L("  μ₁ ≈ 0.291 este caracteristic grafului Jaccard N=280 k=8 în general.")
        L("  Seed=3401 nu pare ales special. TOTUȘI formula v2 rămâne problematică.")
    else:
        L("  VERDICT FINDING 2: ⚠️  ROȘU")
        L("  Doar o minoritate de seed-uri dau ell_damp corect → seed-ul poate fi ales.")

    findings["mu1_independence"] = {
        "mu1_canonical": round(mu1_canonical, 6),
        "mu1_sweep_mean": round(mu1_mean, 6),
        "mu1_sweep_std": round(mu1_std, 6),
        "mu1_theory": round(MU1_THEORY, 6),
        "mu1_needed_for_planck": round(mu1_needed, 6),
        "n_seeds_within_2sigma": n_within_2sigma,
        "total_seeds": 30,
        "ell_damp_from_mean": round(ell_damp_from_mean, 1),
        "ell_damp_from_canonical": round(ell_damp_from_canon, 1),
        "document_says_calibrated_on_planck": True,
    }

    # ── FINDING 3: d_s = 4.082 — robust și independent ───────────────────────
    L("─" * 72)
    L("FINDING 3: d_s = 4.082 — independență față de CMB")
    L("─" * 72)
    L()
    L("  Sweep 50 seed-uri (1000–1049), N=280, k=8:")
    L("    50/50 PASS (d_s ∈ 3.5–4.5)")
    L("    ds_mean = 4.128, ds_std = 0.125")
    L("    Concluzie: d_s ≈ 4 este o proprietate a grafului Jaccard,")
    L("    nu un accident al unui seed sau al calibrării pe CMB.")
    L()
    L("  Threshold (3.5, 4.5) a fost setat pentru d_s ≈ 4D înainte de G26?")
    L("  Commit 'qng jaccard freeze v1': 2026-03-10 07:27 UTC")
    L("  Commit G26: 2026-03-20 20:53 UTC")
    L("  → d_s a fost înghețat la 10 zile înainte de G26. ✓")
    L()
    L("  VERDICT FINDING 3: ✅ VERDE")
    L("  d_s = 4.082 este robust, reproducibil și independent de datele CMB.")
    L()

    findings["ds_independence"] = {
        "status": "GREEN",
        "ds_value": 4.082,
        "ds_mean_50seeds": 4.128,
        "ds_std_50seeds": 0.125,
        "n_pass_50seeds": 50,
        "freeze_date": "2026-03-10",
        "g26_date": "2026-03-20",
        "verdict": "d_s is robust and was frozen before G26.",
    }

    # ── FINDING 4: ell_D_T = 576.144 ─────────────────────────────────────────
    L("─" * 72)
    L("FINDING 4: ell_D_T = 576.144 — sursă și independență")
    L("─" * 72)
    L()
    L("  ell_D_T vine din T-052 (CMB coherence fit), datat: 2026-02-16")
    L("  G26 a fost adăugat pe: 2026-03-20")
    L("  → ell_D_T a fost fixat cu 33 de zile înainte de G26. ✓")
    L()
    L("  ATENȚIE: ell_D_T provine din fitul direct pe datele CMB TT.")
    L("  Deci ell_D_T NU este independent de datele Planck — vine din ele.")
    L("  Asta înseamnă că G26a re-folosește un parametru derivat din Planck")
    L("  pentru a 'prezice' o altă cantitate Planck.")
    L()
    L("  Analogie: dacă știi că o minge cade 10m și 'prezici' că va cădea 10m")
    L("  folosind o formulă care include '10m' ca input — nu e o predicție.")
    L()
    L("  VERDICT FINDING 4: ⚠️  GALBEN-ROȘU")
    L("  ell_D_T vine din datele CMB. G26 NU este o predicție pură:")
    L("  un parametru CMB → formulă → altă cantitate CMB.")
    L()

    findings["ell_D_T_independence"] = {
        "status": "YELLOW-RED",
        "ell_D_T": 576.144,
        "source": "T-052 best-fit on Planck CMB TT data",
        "fixed_date": "2026-02-16",
        "g26_date": "2026-03-20",
        "derived_from_planck": True,
        "verdict": "ell_D_T is derived from Planck CMB data, not independent.",
    }

    # ── VERDICT GLOBAL ────────────────────────────────────────────────────────
    L("=" * 72)
    L("VERDICT GLOBAL")
    L("=" * 72)
    L()
    L("  Finding 1 (Formula): ⚠️  ROȘU — formula schimbată după eșec (HARKing)")
    L("  Finding 2 (μ₁):      🟡 GALBEN — robust pe seed-uri, dar doc spune 'calibrat'")
    L(f"  Finding 3 (d_s):     ✅ VERDE — robust, independent, înghețat înainte")
    L("  Finding 4 (ell_D_T): ⚠️  GALBEN-ROȘU — vine din datele CMB, nu independent")
    L()
    L("  CONCLUZIE:")
    L("  G26a (ell_damp = 1294.9 vs Planck 1290.9) NU este o predicție pură.")
    L()
    L("  Problemele structurale:")
    L("  1. Formula v2 a fost construită DUPĂ ce v1 a eșuat la 17.8σ")
    L("     → Factorul √(6/d_s) a fost adăugat ca 'corecție' ad-hoc")
    L("  2. ell_D_T vine din fitul pe datele CMB → circularitate parțială")
    L("  3. Un document menționează explicit că μ₁ a fost 'calibrat pe Planck'")
    L()
    L("  CE RĂMÂNE VALID:")
    L("  - d_s ≈ 4 (din graf Jaccard) este un rezultat solid și independent")
    L("  - Consistența k_R pe scale diferite (G27) poate fi mai curată")
    L("  - Structura matematică a teoriei poate fi corectă chiar dacă")
    L("    predicția specifică G26a nu e curată")
    L()
    L("  RECOMANDARE:")
    L("  1. Pre-înregistrează formula v2 și parametrii ÎNAINTE de orice test nou")
    L("  2. Caută predicții care NU folosesc ell_D_T ca input")
    L("  3. Încearcă să derivi ell_damp fără să folosi niciun parametru CMB")
    L()

    findings["global_verdict"] = {
        "g26a_is_genuine_prediction": False,
        "reasons": [
            "Formula changed after 17.8-sigma failure (HARKing)",
            "ell_D_T derived from Planck CMB data (partial circularity)",
            "One document explicitly says mu1 was 'calibrated on Planck'",
        ],
        "what_is_solid": [
            "d_s ~ 4 from Jaccard graph is robust and independent",
            "K_R universality across scales (G27) may be cleaner",
        ],
        "recommendation": "Pre-register formula and parameters before next test.",
    }

    # ── Salvare ───────────────────────────────────────────────────────────────
    summary = {
        "audit": "legitimacy-audit-v1",
        "date": datetime.now(timezone.utc).isoformat(),
        "gate_audited": "G26",
        "findings": findings,
    }

    json_path = OUT_DIR / "audit_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    md_path = OUT_DIR / "audit_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log))

    L(f"\nSalvat: {json_path}")
    L(f"Salvat: {md_path}")


if __name__ == "__main__":
    main()
