#!/usr/bin/env python3
"""
QNG-T-CURL-004: curl of residual (non-conservative) acceleration with stronger controls.

Changes vs CURL-003:
- Uses a_res = a_total - proj_grad(a_total, grad_sigma).
- Computes curl_abs and curl_rel on residual field.
- Stronger controls: rewire_strong (30%) and block_shuffle (Sigma proxy shuffle).
- Gates: C1' smallness, C2' lag_factor_res >=1.5, C3' rewire_factor_res >=2.0.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import csv
import json
import math
import random

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_OUT_DIR = ARTIFACTS_ROOT / "qng-t-curl-003"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(np.median(values))


def parse_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_metric_dataset(dataset_id: str) -> dict:
    # Use v4 artifacts by default
    ds_norm = dataset_id.lower().replace("-", "").replace("_", "")
    path = ARTIFACTS_ROOT / f"qng-metric-hardening-v4-{ds_norm}"
    eigs = parse_csv(path / "eigs.csv")
    vac = parse_csv(path / "vacuum_gate.csv")
    return {"eigs": eigs, "vac": vac}


def sample_anchor_rows(eigs: list[dict[str, str]], scale: str, n: int, seed: int) -> list[dict[str, str]]:
    rows = [r for r in eigs if str(r.get("scale", "")) == scale]
    rng = random.Random(seed)
    if len(rows) <= n:
        return rows
    return [rows[i] for i in rng.sample(range(len(rows)), n)]


@dataclass
class GateThresholds:
    c1_static_max: float = 1e-8
    c2_lag_factor_min: float = 1.5
    c3_rewire_factor_min: float = 2.0
    c4_mono_factor_min: float = 1.5
    tau_test: float = 1.0
    a_epsilon: float = 1e-12
    rewire_fraction: float = 0.5


def project_on_vec(vec: np.ndarray, base: np.ndarray, eps: float) -> np.ndarray:
    norm2 = float(np.dot(base, base))
    if norm2 < eps:
        return np.zeros_like(vec)
    return (np.dot(vec, base) / norm2) * base


def compute_curl_residual(beta: float, g: np.ndarray, chart_pts: np.ndarray, v_vec: np.ndarray, tau: float, grad_sigma: np.ndarray, a_epsilon: float) -> dict:
    x = chart_pts[:, 0]
    y = chart_pts[:, 1]
    A = np.stack([np.ones_like(x), x, y], axis=1)

    # base acceleration linear in coordinates
    ax_base = beta * (g[0, 0] * x + g[0, 1] * y)
    ay_base = beta * (g[1, 0] * x + g[1, 1] * y)

    # Newton term from grad_sigma
    g_inv = np.linalg.inv(g)
    a_newton = -g_inv @ grad_sigma
    ax_newton = a_newton[0] * np.ones_like(x)
    ay_newton = a_newton[1] * np.ones_like(y)

    # lag component
    lag_term = tau * (v_vec[0] * x + v_vec[1] * y)
    ax_lag = lag_term
    ay_lag = lag_term

    ax_tot = ax_base + ax_newton + ax_lag
    ay_tot = ay_base + ay_newton + ay_lag

    # project out grad direction per point
    grad_unit = grad_sigma / max(np.linalg.norm(grad_sigma), a_epsilon)
    ax_res = []
    ay_res = []
    for axp, ayp in zip(ax_tot, ay_tot):
        a_vec = np.array([axp, ayp])
        proj = project_on_vec(a_vec, grad_unit, a_epsilon)
        res = a_vec - proj
        ax_res.append(res[0])
        ay_res.append(res[1])

    ax_res = np.array(ax_res)
    ay_res = np.array(ay_res)

    coeff_ax, *_ = np.linalg.lstsq(A, ax_res, rcond=None)
    coeff_ay, *_ = np.linalg.lstsq(A, ay_res, rcond=None)

    def curl_from_coeff(cax, cay) -> float:
        return cay[1] - cax[2]

    curl_abs = abs(curl_from_coeff(coeff_ax, coeff_ay))
    a_mag = math.sqrt(coeff_ax[0] ** 2 + coeff_ay[0] ** 2)
    denom = max(a_mag, a_epsilon)
    return {
        "curl_abs": curl_abs,
        "curl_rel": curl_abs / denom,
        "a_mag": a_mag,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="QNG-T-CURL-004: residual curl with stronger controls.")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=20260224)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = p.parse_args()

    thresholds = GateThresholds()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_metric_dataset(args.dataset_id)
    eigs = data["eigs"]
    anchor_rows = [r for r in eigs if str(r.get("scale", "")) == "1s0"]
    if not anchor_rows:
        raise RuntimeError("No anchors for scale 1s0.")
    beta_candidates = []
    for r in anchor_rows:
        if "beta" in r and r["beta"] not in ("", None):
            beta_candidates.append(float(r["beta"]))
        elif "frob" in r and r["frob"] not in ("", None):
            beta_candidates.append(float(r["frob"]))
    beta = float(np.median(beta_candidates)) if beta_candidates else 1.0

    rng = np.random.default_rng(args.seed)
    charts = sample_anchor_rows(eigs, "1s0", args.samples, args.seed)

    curl_abs_static = []
    curl_abs_lag_iso = []
    curl_abs_lag_grad = []
    curl_abs_rewire = []
    curl_abs_block = []
    curl_rel_static = []
    curl_rel_lag_iso = []
    curl_rel_lag_grad = []
    curl_rel_rewire = []
    curl_rel_block = []
    tau_sweep = {0.0: [], thresholds.tau_test: [], 2 * thresholds.tau_test: [], 4 * thresholds.tau_test: []}

    for row in charts:
        g11 = float(row["g11"])
        g12 = float(row["g12"])
        g22 = float(row["g22"])
        g = np.array([[g11, g12], [g12, g22]])
        grad_sigma = np.array([g11 + g12, g12 + g22])
        v_iso = np.array([1.0, 1.0])
        v_grad = np.array([1.0, 0.5])

        pts = rng.standard_normal((12, 2)) * 0.1

        r_static = compute_curl_residual(beta, g, pts, v_iso, tau=0.0, grad_sigma=grad_sigma, a_epsilon=thresholds.a_epsilon)
        r_lag_iso = compute_curl_residual(beta, g, pts, v_iso, tau=thresholds.tau_test, grad_sigma=grad_sigma, a_epsilon=thresholds.a_epsilon)
        r_lag_grad = compute_curl_residual(beta, g, pts, v_grad, tau=thresholds.tau_test, grad_sigma=grad_sigma, a_epsilon=thresholds.a_epsilon)

        curl_abs_static.append(r_static["curl_abs"])
        curl_abs_lag_iso.append(r_lag_iso["curl_abs"])
        curl_abs_lag_grad.append(r_lag_grad["curl_abs"])
        curl_rel_static.append(r_static["curl_rel"])
        curl_rel_lag_iso.append(r_lag_iso["curl_rel"])
        curl_rel_lag_grad.append(r_lag_grad["curl_rel"])

        for tau_val in tau_sweep:
            r_tau = compute_curl_residual(beta, g, pts, v_iso, tau=tau_val, grad_sigma=grad_sigma, a_epsilon=thresholds.a_epsilon)
            tau_sweep[tau_val].append(r_tau["curl_rel"])

        # control: rewired strong (flip off-diagonal and scale by (1+0.3))
        g_rew = g.copy()
        g_rew[0, 1] = g_rew[1, 0] = -g[1, 0] * 1.3
        r_rew = compute_curl_residual(beta, g_rew, pts, v_iso, tau=0.0, grad_sigma=grad_sigma, a_epsilon=thresholds.a_epsilon)
        curl_abs_rewire.append(r_rew["curl_abs"])
        curl_rel_rewire.append(r_rew["curl_rel"])

        # control: block shuffle grad proxy (swap grad_sigma with another anchor in block)
        grad_block = grad_sigma.copy()
        if len(anchor_rows) >= 4:
            j = rng.integers(low=0, high=len(anchor_rows))
            other = anchor_rows[j]
            grad_block = np.array([float(other["g11"]) + float(other["g12"]), float(other["g12"]) + float(other["g22"])])
        r_block = compute_curl_residual(beta, g, pts, v_iso, tau=0.0, grad_sigma=grad_block, a_epsilon=thresholds.a_epsilon)
        curl_abs_block.append(r_block["curl_abs"])
        curl_rel_block.append(r_block["curl_rel"])

    med_abs_static = median(curl_abs_static)
    med_abs_lag_iso = median(curl_abs_lag_iso)
    med_abs_lag_grad = median(curl_abs_lag_grad)
    med_abs_rewire = median(curl_abs_rewire)
    med_abs_block = median(curl_abs_block)

    med_static = median(curl_rel_static)
    med_lag_iso = median(curl_rel_lag_iso)
    med_lag_grad = median(curl_rel_lag_grad)
    med_rewire = median(curl_rel_rewire)
    med_block = median(curl_rel_block)

    med_tau0 = median(tau_sweep[0.0])
    med_tau1 = median(tau_sweep[thresholds.tau_test])
    med_tau2 = median(tau_sweep[2 * thresholds.tau_test])
    med_tau4 = median(tau_sweep[4 * thresholds.tau_test])

    lag_factor = max(med_lag_iso, med_lag_grad) / med_static if med_static > 0 else float("inf")
    rew_factor = med_rewire / med_static if med_static > 0 else float("inf")
    block_factor = med_block / med_static if med_static > 0 else float("inf")

    gate_c1 = med_static < thresholds.c1_static_max
    gate_c2 = lag_factor >= thresholds.c2_lag_factor_min
    gate_c3 = rew_factor >= thresholds.c3_rewire_factor_min
    mono_ok = (med_tau0 <= med_tau1 + 1e-12 <= med_tau2 + 1e-12 <= med_tau4 + 1e-12) and (med_tau4 >= thresholds.c4_mono_factor_min * med_tau0)
    gate_c4 = mono_ok

    info_rows = [
        {"gate_id": "M1", "metric": "median_rel_static", "value": fmt(med_static), "threshold": "-", "status": "info"},
        {"gate_id": "M2", "metric": "median_rel_lag_iso", "value": fmt(med_lag_iso), "threshold": "-", "status": "info"},
        {"gate_id": "M3", "metric": "median_rel_lag_grad", "value": fmt(med_lag_grad), "threshold": "-", "status": "info"},
        {"gate_id": "M4", "metric": "median_rel_rewire", "value": fmt(med_rewire), "threshold": "-", "status": "info"},
        {"gate_id": "M5", "metric": "median_rel_blockshuffle", "value": fmt(med_block), "threshold": "-", "status": "info"},
        {"gate_id": "M6", "metric": "median_abs_static", "value": fmt(med_abs_static), "threshold": "-", "status": "info"},
        {"gate_id": "M7", "metric": "median_abs_lag_iso", "value": fmt(med_abs_lag_iso), "threshold": "-", "status": "info"},
        {"gate_id": "M8", "metric": "median_abs_lag_grad", "value": fmt(med_abs_lag_grad), "threshold": "-", "status": "info"},
        {"gate_id": "M9", "metric": "median_abs_rewire", "value": fmt(med_abs_rewire), "threshold": "-", "status": "info"},
        {"gate_id": "M10", "metric": "median_abs_blockshuffle", "value": fmt(med_abs_block), "threshold": "-", "status": "info"},
        {"gate_id": "M11", "metric": "lag_factor", "value": fmt(lag_factor), "threshold": "-", "status": "info"},
        {"gate_id": "M12", "metric": "rewire_factor", "value": fmt(rew_factor), "threshold": "-", "status": "info"},
        {"gate_id": "M13", "metric": "block_factor", "value": fmt(block_factor), "threshold": "-", "status": "info"},
    ]

    gate_rows = [
        {"gate_id": "C1", "metric": "median_curl_rel_static", "value": fmt(med_static), "threshold": f"<{fmt(thresholds.c1_static_max)}", "status": "pass" if gate_c1 else "fail"},
        {"gate_id": "C2", "metric": "lag_factor", "value": fmt(lag_factor), "threshold": f">={fmt(thresholds.c2_lag_factor_min)}", "status": "pass" if gate_c2 else "fail"},
        {"gate_id": "C3", "metric": "rewire_factor", "value": fmt(rew_factor), "threshold": f">={fmt(thresholds.c3_rewire_factor_min)}", "status": "pass" if gate_c3 else "fail"},
        {"gate_id": "C4", "metric": "tau sweep monotonicity", "value": f"{fmt(med_tau0)}->{fmt(med_tau1)}->{fmt(med_tau2)}->{fmt(med_tau4)}", "threshold": "nondecreasing & tau4>=1.5x tau0", "status": "pass" if gate_c4 else "fail"},
    ]

    final_pass = all(r["status"] == "pass" for r in gate_rows)
    gate_rows.append({"gate_id": "FINAL", "metric": "decision", "value": "pass" if final_pass else "fail", "threshold": "C1&C2&C3&C4", "status": "pass" if final_pass else "fail"})
    gate_rows = info_rows + gate_rows

    def write_csv(path: Path, rows: list[dict]):
        if not rows:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        cols = list(rows[0].keys())
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for row in rows:
                w.writerow(row)

    write_csv(out_dir / "gate_summary.csv", gate_rows)
    write_csv(out_dir / "curl_rel_values.csv", [
        {
            "anchor_id": i,
            "curl_rel_static": fmt(s),
            "curl_rel_lag_iso": fmt(li),
            "curl_rel_lag_grad": fmt(lg),
            "curl_rel_rewire": fmt(rw),
            "curl_rel_block": fmt(rb),
        }
        for i, (s, li, lg, rw, rb) in enumerate(zip(curl_rel_static, curl_rel_lag_iso, curl_rel_lag_grad, curl_rel_rewire, curl_rel_block))
    ])
    write_csv(out_dir / "curl_abs_values.csv", [
        {
            "anchor_id": i,
            "curl_abs_static": fmt(s),
            "curl_abs_lag_iso": fmt(li),
            "curl_abs_lag_grad": fmt(lg),
            "curl_abs_rewire": fmt(rw),
            "curl_abs_block": fmt(rb),
        }
        for i, (s, li, lg, rw, rb) in enumerate(zip(curl_abs_static, curl_abs_lag_iso, curl_abs_lag_grad, curl_abs_rewire, curl_abs_block))
    ])

    run_log = {
        "dataset_id": args.dataset_id,
        "samples": args.samples,
        "seed": args.seed,
        "tau_test": thresholds.tau_test,
        "c1_static_max": thresholds.c1_static_max,
        "c2_lag_factor_min": thresholds.c2_lag_factor_min,
        "c3_rewire_factor_min": thresholds.c3_rewire_factor_min,
        "c4_mono_factor_min": thresholds.c4_mono_factor_min,
    }
    (out_dir / "run-log.txt").write_text(json.dumps(run_log, indent=2), encoding="utf-8")

    print(json.dumps({
        "decision": final_pass,
        "med_rel_static": med_static,
        "med_rel_lag_iso": med_lag_iso,
        "med_rel_lag_grad": med_lag_grad,
        "med_rel_rewire": med_rewire,
        "med_rel_block": med_block,
        "med_abs_static": med_abs_static,
        "med_abs_lag_iso": med_abs_lag_iso,
        "med_abs_lag_grad": med_abs_lag_grad,
        "med_abs_rewire": med_abs_rewire,
        "med_abs_block": med_abs_block,
        "lag_factor": lag_factor,
        "rewire_factor": rew_factor,
        "block_factor": block_factor,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
