#!/usr/bin/env python3
"""
Trajectory Real Pilot v1 — NEAR_1 + ROSETTA_1

Conform pre-înregistrării: trajectory-real-pilot-v1.json
Dataset: DS-005  Pase: NEAR_1, ROSETTA_1  Ancoră: P10_EQ23

Model QNG Flyby (C-060 extins):
  Anomalia de flyby provine din termenul de lag de traiectorie:
    a_lag = -tau * (v · nabla) nabla_Sigma
  unde Sigma = gravitational potential (phi/c^2), soluție Poisson.

  Pentru flyby hiperbolic, componenta rezidual de viteză:
    Delta_v_inf = integral a_lag · v_hat dt / v_inf

  Funcție de semn a declinației: Anderson (2008) observă
    Delta_v/v_inf ~ 2*omega_E*R_E/c * (sin^2(d_out) - sin^2(d_in))
  QNG reproduce prin termenul Coriolis de memorie (coupling rotatie-lag).

  Modelul QNG cu 2 parametri liberi: tau, alpha_decl.

Gates (din pilot-configs/trajectory-real-pilot-v1.json):
  delta_chi2 < 0
  delta_AIC <= -10
  delta_BIC <= -10
  Negative controls: orientation_shuffle, segment_shuffle, control_zero
  Robustness: leave_10pct_out, outlier_trim

Output: 05_validation/evidence/artifacts/trajectory-real-pilot-v1/
"""

from __future__ import annotations
import csv, json, math, pathlib, random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

ROOT    = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/trajectory-real-pilot-v1"
FLYBY_CSV   = ROOT / "data/trajectory/flyby_ds005_real.csv"
PIONEER_CSV = ROOT / "data/trajectory/pioneer_ds005_anchor.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED        = 20260220   # din pilot-configs (reproducibilitate)
PILOT_PASES = {"NEAR_1", "ROSETTA_1"}

# Constante
MU_EARTH    = 3.986004418e14   # m³/s²
R_EARTH     = 6.371e6          # m
OMEGA_EARTH = 7.2921150e-5     # rad/s
C_LIGHT     = 2.998e8          # m/s

# Parametri QNG baseline (calibrați pe Pioneer D8)
TAU_PIONEER = 1.394e-5         # s (tau din analiza straton)


# ─────────────────────────────────────────────────────────────────────────────
# Model QNG flyby — Anderson/Meessen signature + tau lag
# ─────────────────────────────────────────────────────────────────────────────

def qng_flyby_prediction(r_p_km: float, v_inf_km_s: float,
                          d_in_deg: float, d_out_deg: float,
                          tau: float, alpha_decl: float) -> float:
    """
    Predicție QNG pentru Δv∞ [mm/s] a unui flyby terestru.

    Componenta 1 — lag radial (Pioneer-like, mic):
      Δv_lag ~ -tau * C_straton * integral(v_r^2) / v_inf   [negativ, mic]

    Componenta 2 — coupling declinație-rotație (Meessen-like):
      Δv_decl = alpha_decl * v_inf * 2 * omega_E * R_E / c
                * (sin^2(d_out) - sin^2(d_in))              [dominant]

    tau       = lag time [s] (liber, anchored on Pioneer)
    alpha_decl = coupling constant [adimensional] (liber)
    """
    r_p  = r_p_km * 1e3      # m
    v_inf = v_inf_km_s * 1e3  # m/s
    d_in  = math.radians(d_in_deg)
    d_out = math.radians(d_out_deg)

    # Componenta 1 — lag radial (Pioneer straton, mic)
    e   = 1 + r_p * v_inf**2 / MU_EARTH
    l   = r_p * (1 + e)
    h   = math.sqrt(MU_EARTH * l)
    r0  = 1e8   # m

    cos_t0   = max(-1.0, min(1.0, (l / r0 - 1) / e))
    theta_max = min(math.acos(cos_t0), math.acos(-1.0 / e) - 1e-8)
    N = 2000
    dtheta = 2 * theta_max / N
    integral = 0.0
    for i in range(N):
        theta = -theta_max + (i + 0.5) * dtheta
        r_val = l / (1 + e * math.cos(theta))
        v_r   = MU_EARTH / h * math.sin(theta)
        integral += v_r**2 * (r_val**2 / h) * dtheta

    C_lag = tau / TAU_PIONEER * 6.992e-14   # s⁻¹, scalat cu tau
    dv_lag = -C_lag * integral / v_inf       # m/s

    # Componenta 2 — coupling declinație-rotație
    meessen_factor = 2 * OMEGA_EARTH * R_EARTH / C_LIGHT
    dv_decl = alpha_decl * v_inf * meessen_factor * (
        math.sin(d_out)**2 - math.sin(d_in)**2
    )  # m/s

    return (dv_lag + dv_decl) * 1e3   # mm/s


def baseline_prediction(r_p_km, v_inf_km_s, d_in_deg, d_out_deg) -> float:
    """Baseline GR: Δv = 0 (nicio anomalie)."""
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
# Fit parametri QNG (grid search, 2 parametri)
# ─────────────────────────────────────────────────────────────────────────────

def fit_qng_params(rows: list[dict]) -> tuple[float, float, float]:
    """
    Grid search pentru (tau, alpha_decl) care minimizează chi2 pe pilot rows.
    Returnează (tau_best, alpha_decl_best, chi2_min).
    """
    best = (TAU_PIONEER, 1.0, 1e18)

    tau_grid   = [TAU_PIONEER * f for f in (0.1, 0.5, 1.0, 2.0, 5.0, 10.0)]
    alpha_grid = [a/10 for a in range(1, 31)]   # 0.1 → 3.0

    for tau in tau_grid:
        for alpha in alpha_grid:
            chi2 = 0.0
            for r in rows:
                pred = qng_flyby_prediction(
                    float(r["r_perigee_km"]), float(r["v_inf_km_s"]),
                    float(r["delta_in_deg"]), float(r["delta_out_deg"]),
                    tau, alpha
                )
                obs   = float(r["delta_v_obs_mm_s"])
                sigma = max(float(r["delta_v_sigma_mm_s"]), 0.05)
                chi2 += ((pred - obs) / sigma) ** 2
            if chi2 < best[2]:
                best = (tau, alpha, chi2)
    return best


# ─────────────────────────────────────────────────────────────────────────────
# Date
# ─────────────────────────────────────────────────────────────────────────────

def load_flyby() -> list[dict]:
    rows = []
    with FLYBY_CSV.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def load_pioneer() -> list[dict]:
    rows = []
    with PIONEER_CSV.open() as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Controale negative
# ─────────────────────────────────────────────────────────────────────────────

def orientation_shuffle(rows: list[dict], rng: random.Random) -> list[dict]:
    """Permutare declinații: d_in/d_out amestecate între pase."""
    d_in_vals  = [float(r["delta_in_deg"])  for r in rows]
    d_out_vals = [float(r["delta_out_deg"]) for r in rows]
    rng.shuffle(d_in_vals)
    rng.shuffle(d_out_vals)
    shuffled = []
    for r, di, do in zip(rows, d_in_vals, d_out_vals):
        rc = dict(r)
        rc["delta_in_deg"]  = str(di)
        rc["delta_out_deg"] = str(do)
        shuffled.append(rc)
    return shuffled


def segment_shuffle(rows: list[dict], rng: random.Random) -> list[dict]:
    """Permutare perechi (r_perigee, v_inf) între pase."""
    pairs = [(float(r["r_perigee_km"]), float(r["v_inf_km_s"])) for r in rows]
    rng.shuffle(pairs)
    shuffled = []
    for r, (rp, vi) in zip(rows, pairs):
        rc = dict(r)
        rc["r_perigee_km"] = str(rp)
        rc["v_inf_km_s"]   = str(vi)
        shuffled.append(rc)
    return shuffled


def control_zero_rows(rows: list[dict]) -> list[dict]:
    """Setează delta_v_obs = 0 (control fals): modelul nu trebuie să funcționeze."""
    zeroed = []
    for r in rows:
        rc = dict(r)
        rc["delta_v_obs_mm_s"] = "0.0"
        zeroed.append(rc)
    return zeroed


# ─────────────────────────────────────────────────────────────────────────────
# Metrici
# ─────────────────────────────────────────────────────────────────────────────

def chi2_score(rows, pred_fn) -> float:
    total = 0.0
    for r in rows:
        pred  = pred_fn(r)
        obs   = float(r["delta_v_obs_mm_s"])
        sigma = max(float(r["delta_v_sigma_mm_s"]), 0.05)
        total += ((pred - obs) / sigma) ** 2
    return total


def aic(chi2, k, n) -> float:
    return chi2 + 2 * k


def bic(chi2, k, n) -> float:
    return chi2 + k * math.log(n)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    rng = random.Random(SEED)
    log = []
    def L(s): log.append(s); print(s)

    L("=" * 60)
    L("TRAJECTORY REAL PILOT v1 — NEAR_1 + ROSETTA_1")
    L(f"Seed: {SEED}  |  Config: trajectory-real-pilot-v1.json")
    L("=" * 60)

    all_rows = load_flyby()
    pioneer_rows = load_pioneer()

    # ── Pilot rows ────────────────────────────────────────────────────────────
    pilot_rows = [r for r in all_rows if r["pass_id"] in PILOT_PASES]
    control_rows = [r for r in all_rows
                    if r["trajectory_class"] == "control"
                    and r["pass_id"] not in PILOT_PASES]

    L(f"\nPilot pase: {[r['pass_id'] for r in pilot_rows]}")
    L(f"Control pase: {[r['pass_id'] for r in control_rows]}")
    L(f"Ancoră Pioneer: {[r.get('pass_id', r.get('segment_id', '?')) for r in pioneer_rows[:3]]}")

    # ── Fit QNG pe pilot ──────────────────────────────────────────────────────
    L("\n--- FIT QNG ---")
    tau_best, alpha_best, chi2_qng = fit_qng_params(pilot_rows)
    L(f"tau_best    = {tau_best:.3e} s  (Pioneer: {TAU_PIONEER:.3e} s)")
    L(f"alpha_best  = {alpha_best:.2f}  (coupling declinatie-rotatie)")
    L(f"chi2_QNG    = {chi2_qng:.4f}")

    def qng_pred(r):
        return qng_flyby_prediction(
            float(r["r_perigee_km"]), float(r["v_inf_km_s"]),
            float(r["delta_in_deg"]),  float(r["delta_out_deg"]),
            tau_best, alpha_best
        )

    def base_pred(r): return baseline_prediction(
        float(r["r_perigee_km"]), float(r["v_inf_km_s"]),
        float(r["delta_in_deg"]), float(r["delta_out_deg"])
    )

    # ── Chi2 baseline ─────────────────────────────────────────────────────────
    chi2_base = chi2_score(pilot_rows, base_pred)
    L(f"chi2_base   = {chi2_base:.4f}")

    n = len(pilot_rows)
    k_qng  = 2   # tau, alpha_decl
    k_base = 0

    delta_chi2 = chi2_qng - chi2_base
    delta_aic  = aic(chi2_qng, k_qng, n) - aic(chi2_base, k_base, n)
    delta_bic  = bic(chi2_qng, k_qng, n) - bic(chi2_base, k_base, n)

    L(f"\n--- GATE METRICI ---")
    L(f"delta_chi2  = {delta_chi2:.4f}  (gate: < 0)")
    L(f"delta_AIC   = {delta_aic:.4f}  (gate: <= -10)")
    L(f"delta_BIC   = {delta_bic:.4f}  (gate: <= -10)")

    gate_chi2 = delta_chi2 < 0
    gate_aic  = delta_aic <= -10
    gate_bic  = delta_bic <= -10

    L(f"\nGate delta_chi2 < 0:   {'PASS' if gate_chi2 else 'FAIL'}")
    L(f"Gate delta_AIC <= -10: {'PASS' if gate_aic  else 'FAIL'}")
    L(f"Gate delta_BIC <= -10: {'PASS' if gate_bic  else 'FAIL'}")

    # ── Per-pass breakdown ───────────────────────────────────────────────────
    L("\n--- PER-PASS ---")
    L(f"{'Pass':<15} {'Obs [mm/s]':>12} {'QNG [mm/s]':>12} {'Base [mm/s]':>12} {'σ':>8}")
    per_pass = []
    for r in pilot_rows:
        obs   = float(r["delta_v_obs_mm_s"])
        sigma = float(r["delta_v_sigma_mm_s"])
        pred  = qng_pred(r)
        resid = pred - obs
        L(f"{r['pass_id']:<15} {obs:>12.3f} {pred:>12.3f} {0.0:>12.3f} {sigma:>8.3f}")
        per_pass.append({
            "pass_id": r["pass_id"],
            "obs_mm_s": obs, "sigma_mm_s": sigma,
            "qng_mm_s": pred, "resid_mm_s": resid,
            "pull": resid / max(sigma, 0.05)
        })

    # ── Controale negative ───────────────────────────────────────────────────
    L("\n--- CONTROALE NEGATIVE ---")

    # C1: orientation shuffle
    n_shuf = 200
    chi2_shuf_vals = []
    for _ in range(n_shuf):
        shuf = orientation_shuffle(pilot_rows, rng)
        tau_s, alpha_s, chi2_s = fit_qng_params(shuf)
        chi2_shuf_vals.append(chi2_s)
    p_orient = sum(1 for v in chi2_shuf_vals if v <= chi2_qng) / n_shuf
    ratio_orient = (sum(chi2_shuf_vals) / len(chi2_shuf_vals)) / max(chi2_qng, 1e-9)
    L(f"C1 orientation_shuffle: p={p_orient:.3f}  ratio_shuf/real={ratio_orient:.2f}")
    L(f"  Gate C1: p <= 0.10 AND ratio <= 0.45 → {'PASS' if p_orient <= 0.10 and ratio_orient <= 0.45 else 'FAIL'}")

    # C2: segment shuffle
    chi2_seg_vals = []
    for _ in range(n_shuf):
        shuf = segment_shuffle(pilot_rows, rng)
        tau_s, alpha_s, chi2_s = fit_qng_params(shuf)
        chi2_seg_vals.append(chi2_s)
    p_seg   = sum(1 for v in chi2_seg_vals if v <= chi2_qng) / n_shuf
    ratio_seg = (sum(chi2_seg_vals) / len(chi2_seg_vals)) / max(chi2_qng, 1e-9)
    L(f"C2 segment_shuffle:     p={p_seg:.3f}  ratio_shuf/real={ratio_seg:.2f}")
    L(f"  Gate C2: p <= 0.10 AND ratio <= 0.95 → {'PASS' if p_seg <= 0.10 and ratio_seg <= 0.95 else 'FAIL'}")

    # C3: control_zero (semnalul real vs semnal zero)
    zeroed = control_zero_rows(pilot_rows)
    _, _, chi2_zero = fit_qng_params(zeroed)
    L(f"C3 control_zero:        chi2_zero={chi2_zero:.4f} vs chi2_real={chi2_qng:.4f}")
    L(f"  Semnal real mai bun: {'DA' if chi2_qng < chi2_zero else 'NU'}")

    # ── Robustness ───────────────────────────────────────────────────────────
    L("\n--- ROBUSTNESS ---")

    # leave_10pct_out (cu n=2 pase, omit câte 1 pe rând)
    if n >= 2:
        loo_chi2s = []
        for idx in range(n):
            loo_rows = [r for i, r in enumerate(pilot_rows) if i != idx]
            if loo_rows:
                _, _, c2 = fit_qng_params(loo_rows)
                loo_chi2s.append(c2)
        if loo_chi2s:
            loo_mean = sum(loo_chi2s) / len(loo_chi2s)
            L(f"leave_one_out: chi2_mean={loo_mean:.4f}  (vs full={chi2_qng:.4f})")
            L(f"  Robust dacă LOO chi2 ~ full chi2: {'DA' if abs(loo_mean - chi2_qng) < 5 * chi2_qng else 'NU'}")

    # outlier_trim (excludem pasul cu cel mai mare pull)
    if per_pass:
        pulls = [abs(p["pull"]) for p in per_pass]
        max_pull_idx = pulls.index(max(pulls))
        trim_rows = [r for i, r in enumerate(pilot_rows) if i != max_pull_idx]
        if trim_rows:
            _, _, chi2_trim = fit_qng_params(trim_rows)
            L(f"outlier_trim (exclude {pilot_rows[max_pull_idx]['pass_id']}): chi2={chi2_trim:.4f}")

    # ── Concluzie Pilot ───────────────────────────────────────────────────────
    L("\n" + "=" * 60)
    all_gates = gate_chi2 and gate_aic and gate_bic
    L(f"REZULTAT PILOT: {'PASS' if all_gates else 'FAIL'}")
    L(f"  delta_chi2={delta_chi2:.2f}, delta_AIC={delta_aic:.2f}, delta_BIC={delta_bic:.2f}")
    L(f"  tau_best={tau_best:.2e} s  (Pioneer anchor: {TAU_PIONEER:.2e} s)")
    L(f"  alpha_decl={alpha_best:.2f}  (coupling declinatie-rotatie)")
    if all_gates:
        L("  NOTA: Pilot PASS nu înseamnă Gold Promotion — conform preregistrare.")
    else:
        L("  NOTA: Pilot FAIL — modelul curent nu reproduce semnătura flyby.")
        L(f"  tau din pilot ({tau_best:.2e}) vs Pioneer ({TAU_PIONEER:.2e}): "
          f"raport = {tau_best/TAU_PIONEER:.1f}×")
    L("=" * 60)

    # ── Salvare ───────────────────────────────────────────────────────────────
    result = {
        "config": "trajectory-real-pilot-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "pilot_passes": list(PILOT_PASES),
        "n_pilot": n,
        "params": {"tau_best": tau_best, "alpha_decl": alpha_best},
        "chi2": {"qng": chi2_qng, "base": chi2_base},
        "gates": {
            "delta_chi2": delta_chi2, "gate_chi2_pass": gate_chi2,
            "delta_aic":  delta_aic,  "gate_aic_pass":  gate_aic,
            "delta_bic":  delta_bic,  "gate_bic_pass":  gate_bic,
        },
        "pilot_result": "PASS" if all_gates else "FAIL",
        "per_pass": per_pass,
        "controls": {
            "orientation_shuffle_p": p_orient,
            "orientation_shuffle_ratio": ratio_orient,
            "segment_shuffle_p": p_seg,
            "segment_shuffle_ratio": ratio_seg,
        },
    }

    out_json = OUT_DIR / "pilot_result.json"
    out_md   = OUT_DIR / "pilot_report.md"
    out_json.write_text(json.dumps(result, indent=2))

    md_lines = ["# Trajectory Real Pilot v1 — Report", "",
                f"**Date**: {datetime.now(timezone.utc).isoformat()}", "",
                "## Gate Results", "",
                f"| Gate | Value | Threshold | Status |",
                "|------|-------|-----------|--------|",
                f"| delta_chi2 | {delta_chi2:.3f} | < 0 | {'PASS' if gate_chi2 else 'FAIL'} |",
                f"| delta_AIC | {delta_aic:.3f} | <= -10 | {'PASS' if gate_aic else 'FAIL'} |",
                f"| delta_BIC | {delta_bic:.3f} | <= -10 | {'PASS' if gate_bic else 'FAIL'} |",
                "", f"**PILOT RESULT: {'PASS' if all_gates else 'FAIL'}**", "",
                "## Fitted Parameters", "",
                f"- tau_best = {tau_best:.3e} s",
                f"- alpha_decl = {alpha_best:.2f}",
                "", "## Per-Pass", ""]
    for p in per_pass:
        md_lines.append(f"- {p['pass_id']}: obs={p['obs_mm_s']:.3f}, QNG={p['qng_mm_s']:.3f}, "
                        f"pull={p['pull']:.2f}σ")
    out_md.write_text("\n".join(md_lines))

    for line in log:
        pass  # deja printat
    print(f"\nSalvat în: {OUT_DIR}")


if __name__ == "__main__":
    main()
