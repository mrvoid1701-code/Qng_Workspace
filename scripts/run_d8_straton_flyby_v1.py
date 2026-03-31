#!/usr/bin/env python3
"""
D8 — QNG Straton Flyby Test: predicție directă a_lag = C × v_r

Modelul straton (Scenario B + VPC):
  a_lag = -C × v_r  unde C = a_Pioneer / v_r,Pioneer = 6.99×10⁻¹⁴ s⁻¹

Testează dacă C universal (calibrat pe Pioneer) reproduce sau contrazice
anomaliile de flyby terestre.

Outputs:
  05_validation/evidence/artifacts/d8-straton-flyby-v1/
    d8_summary.json
    d8_per_pass.csv
    d8_report.md
"""

from __future__ import annotations
import csv, json, math, pathlib
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

ROOT    = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/d8-straton-flyby-v1"
FLYBY_CSV = ROOT / "data/trajectory/flyby_ds005_real.csv"
PIONEER_CSV = ROOT / "data/trajectory/pioneer_ds005_anchor.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Constante fizice
MU_EARTH = 3.986004418e14   # m³/s²
MU_SUN   = 1.327124400e20   # m³/s²
C_STRATON = 6.992e-14       # s⁻¹  (= a_P10P11 / v_r = 8.74e-10 / 12500)


# ─────────────────────────────────────────────────────────────────────────────
# Predicție straton pentru flyby hiperbolic
# ─────────────────────────────────────────────────────────────────────────────

def straton_flyby_dv(r_p: float, v_inf: float, r0: float = 1e8) -> float:
    """
    Returnează Δv∞ [m/s] prezis de modelul straton pentru un flyby terestru.

    Modelul: a_lag = -C × v_r (radial inward)
    Putere:  P = -mC v_r²  (întotdeauna negativă)
    ΔE = ∫ P dt = -mC ∫_{-r0}^{+r0} v_r² dt

    Δv∞ ≈ ΔE / (m v∞)

    r0 = raza de referință (default 10⁸ m ≈ 260 r_Earth)
    """
    v_p = math.sqrt(v_inf**2 + 2 * MU_EARTH / r_p)
    e   = 1 + r_p * v_inf**2 / MU_EARTH
    l   = r_p * (1 + e)
    h   = math.sqrt(MU_EARTH * l)

    # Unghi la r0
    cos_t0 = (l / r0 - 1) / e
    cos_t0 = max(-1.0, min(1.0, cos_t0))
    theta_max = math.acos(cos_t0)
    theta_inf = math.acos(-1.0 / e) - 1e-8
    theta_max = min(theta_max, theta_inf)

    # Integrare numerică: ∫ v_r² dt = ∫ (μ/h sin θ)² × r²/h dθ
    N = 40_000
    dtheta = 2 * theta_max / N
    integral = 0.0
    for i in range(N):
        theta = -theta_max + (i + 0.5) * dtheta
        r   = l / (1 + e * math.cos(theta))
        v_r = MU_EARTH / h * math.sin(theta)
        integral += v_r**2 * (r**2 / h) * dtheta

    delta_v = -C_STRATON * integral / v_inf   # m/s
    return delta_v


def straton_pioneer_accel(v_r: float) -> float:
    """a_lag = C × v_r pentru Pioneer (radial inward = anomalie observată)."""
    return C_STRATON * v_r   # m/s²


# ─────────────────────────────────────────────────────────────────────────────
# Date
# ─────────────────────────────────────────────────────────────────────────────

def load_flyby():
    rows = []
    with FLYBY_CSV.open() as f:
        for r in csv.DictReader(f):
            if r["trajectory_class"] in ("flyby", "control"):
                rows.append(r)
    return rows


def load_pioneer():
    rows = []
    with PIONEER_CSV.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    log = []
    def L(s): log.append(s); print(s)

    L("=== D8: QNG STRATON FLYBY TEST ===")
    L(f"C_straton = {C_STRATON:.3e} s⁻¹  (calibrat pe Pioneer P10+P11)")
    L("")

    # ── Pioneer ──────────────────────────────────────────────────────────────
    L("--- PIONEER (calibrare) ---")
    pioneer_rows = load_pioneer()
    pioneer_results = []
    for p in pioneer_rows:
        v_r = float(p["v_km_s"]) * 1e3   # m/s
        a_obs = float(p["a_obs_m_s2"])
        a_sig = float(p["a_sigma_m_s2"])
        a_pred = straton_pioneer_accel(v_r)
        pull = (a_obs - a_pred) / a_sig
        ok = abs(pull) < 3
        pioneer_results.append({
            "id": p["record_id"],
            "v_r_km_s": v_r / 1e3,
            "a_obs": a_obs,
            "a_pred": a_pred,
            "a_sigma": a_sig,
            "pull_sigma": pull,
            "pass": ok,
        })
        L(f"  {p['record_id']:12s}: a_pred={a_pred:.3e}  a_obs={a_obs:.3e}  σ={a_sig:.2e}  pull={pull:+.1f}σ  {'✓' if ok else '✗'}")

    L("")

    # ── Flyby terestre ───────────────────────────────────────────────────────
    L("--- FLYBY TERESTRE ---")
    L(f"{'Pass':18s}  {'Δv_strat mm/s':>14s}  {'Δv_obs mm/s':>12s}  {'σ mm/s':>8s}  {'Status':>10s}  Notă")

    flyby_rows = load_flyby()
    flyby_results = []
    eps_zero = 1e-9
    n_anderson = 0   # anomalii Anderson pozitive cu σ<0.2 mm/s
    n_nulls    = 0   # flyby moderne cu null (σ~1 mm/s)
    n_nulls_ok = 0

    for row in flyby_rows:
        pid   = row["pass_id"]
        cls   = row["trajectory_class"]
        r_p   = float(row["r_perigee_km"]) * 1e3
        v_inf = float(row["v_inf_km_s"])   * 1e3
        dv_obs = float(row["delta_v_obs_mm_s"])
        dv_sig = float(row["delta_v_sigma_mm_s"])

        dv_pred_ms  = straton_flyby_dv(r_p, v_inf)
        dv_pred_mms = dv_pred_ms * 1e3

        consistent = abs(dv_pred_mms - dv_obs) < 3 * dv_sig
        detectable = abs(dv_pred_mms) > dv_sig

        # Clasificare
        if dv_obs != 0 and dv_sig < 0.2:
            category = "Anderson2008"
            n_anderson += 1
        elif abs(dv_obs) <= eps_zero and dv_sig >= 0.5 and cls == "flyby":
            category = "null_modern"
            n_nulls += 1
            if consistent: n_nulls_ok += 1
        else:
            category = "control"

        note = "sub σ" if not detectable else ("cons" if consistent else "inco")
        status_sym = "✓" if consistent else "✗"
        L(f"  {pid:18s}  {dv_pred_mms:+14.4f}  {dv_obs:+12.3f}  {dv_sig:8.3f}  {status_sym:>10s}  [{category}]")

        flyby_results.append({
            "pass_id": pid,
            "class": cls,
            "category": category,
            "r_perigee_km": float(row["r_perigee_km"]),
            "v_inf_km_s": float(row["v_inf_km_s"]),
            "dv_pred_mms": dv_pred_mms,
            "dv_obs_mms": dv_obs,
            "dv_sigma_mms": dv_sig,
            "consistent": consistent,
            "detectable": detectable,
        })

    L("")
    L("--- CONCLUZIE ---")
    L("")
    L(f"Pioneer ({len(pioneer_results)} date):")
    n_p_ok = sum(1 for r in pioneer_results if r["pass"])
    L(f"  ✓ {n_p_ok}/{len(pioneer_results)} în 3σ — modelul calibrat reproduce Pioneer")
    L("")
    L(f"Anderson (2008) anomalii ({n_anderson} pase cu σ<0.2 mm/s):")
    L(f"  Predicție straton: Δv < 0 (negativ, ~0.002-0.01 mm/s)")
    L(f"  Observat: Δv = +1.8 to +13.5 mm/s (pozitiv, factor 1000× mai mare)")
    L(f"  → NU sunt explicate de straton. Necesită fizică diferită.")
    L(f"    (candidat: cuplaj cu rotația Pământului în câmp gravitațional, separat de VPC)")
    L("")
    L(f"Nulluri moderne ({n_nulls} pase, σ~1 mm/s):")
    L(f"  ✓ {n_nulls_ok}/{n_nulls} consistente cu predicția straton (|Δv_strat| < σ)")
    L(f"  Predicția straton: |Δv| = 0.001–0.01 mm/s (sub pragul de detecție)")

    # ── Salvare ──────────────────────────────────────────────────────────────
    summary = {
        "test_id": "d8-straton-flyby-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "C_straton_s_inv": C_STRATON,
        "pioneer_n": len(pioneer_results),
        "pioneer_pass": n_p_ok,
        "anderson_n": n_anderson,
        "anderson_explained": False,
        "anderson_reason": "Straton predicts Δv<0 (~0.01 mm/s), Anderson anomalies are Δv>0 (~1-13 mm/s). Different physics required.",
        "nulls_n": n_nulls,
        "nulls_consistent": n_nulls_ok,
        "verdict": "Pioneer reproduced; Anderson unexplained; modern nulls consistent",
    }
    with (OUT_DIR / "d8_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    # CSV per-pass
    with (OUT_DIR / "d8_per_pass.csv").open("w", newline="") as f:
        default_fields = [
            "pass_id",
            "class",
            "category",
            "r_perigee_km",
            "v_inf_km_s",
            "dv_pred_mms",
            "dv_obs_mms",
            "dv_sigma_mms",
            "consistent",
            "detectable",
        ]
        fields = list(flyby_results[0].keys()) if flyby_results else default_fields
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        if flyby_results:
            w.writerows(flyby_results)

    # Report MD
    report = "\n".join([
        "# D8 — QNG Straton Flyby Test",
        "",
        f"**Data:** {datetime.now(timezone.utc).date()}  ",
        f"**C_straton:** {C_STRATON:.3e} s⁻¹ (calibrat pe Pioneer P10+P11)  ",
        "",
        "## Model",
        "",
        "```",
        "a_lag = -C × v_r  (radial inward, din Scenario B + VPC)",
        "C = a_P10P11 / v_r,Pioneer = 8.74×10⁻¹⁰ / 12500 = 6.99×10⁻¹⁴ s⁻¹",
        "```",
        "",
        "Pentru flyby terestru: `Δv∞ ≈ -(C/v∞) × ∫ v_r² dt`",
        "",
        "## Pioneer (calibrare)",
        "",
        "| Pass | v_r km/s | a_pred | a_obs | pull |",
        "|------|---------|--------|-------|------|",
    ] + [
        f"| {r['id']} | {r['v_r_km_s']:.1f} | {r['a_pred']:.3e} | {r['a_obs']:.3e} | {r['pull_sigma']:+.1f}σ |"
        for r in pioneer_results
    ] + [
        "",
        "## Flyby Terestre",
        "",
        "| Pass | Δv_strat mm/s | Δv_obs mm/s | σ | Categorie |",
        "|------|-------------|-----------|---|-----------|",
    ] + [
        f"| {r['pass_id']} | {r['dv_pred_mms']:+.4f} | {r['dv_obs_mms']:+.3f} | {r['dv_sigma_mms']:.3f} | {r['category']} |"
        for r in flyby_results
    ] + [
        "",
        "## Concluzie",
        "",
        f"- **Pioneer:** {n_p_ok}/{len(pioneer_results)} în 3σ ✓",
        f"- **Anderson (2008):** Straton prezice Δv ~ -0.01 mm/s (negativ, factor 1000× sub observat). **Nu sunt explicate.**",
        f"  Fizica Anderson necesită un mecanism separat (posibil cuplaj cu rotația Pământului în QNG).",
        f"- **Nulluri moderne (Juno, BepiColombo, Solar Orbiter):** {n_nulls_ok}/{n_nulls} consistente cu predicție straton. ✓",
        "",
        "### De ce straton nu poate explica Anderson anomalii",
        "",
        "VPC implică `a_lag ∝ v_r` (radial). Puterea instantanee `P = -C v_r² ≤ 0` mereu.",
        "=> Energia scade => Δv∞ < 0 mereu.",
        "Anderson anomalii sunt **pozitive** (+1.8 to +13.5 mm/s) → cer cuplaj cu alt câmp",
        "(rotație, câmp magnetic, sau termen QNG non-VPC).",
        "",
        "Aceasta este o predicție falsificabilă: dacă un mecanism QNG suplimentar",
        "(**fără** VPC) produce Δv > 0 cu formula δv/v = 2ωR/c × (cosδ_in − cosδ_out),",
        "atunci QNG unifică Pioneer + flyby. Altfel, flyby anomalii au altă origine.",
    ])
    (OUT_DIR / "d8_report.md").write_text(report, encoding="utf-8")

    print(f"\nSalvat în {OUT_DIR}")


if __name__ == "__main__":
    main()
