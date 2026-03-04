#!/usr/bin/env python3
"""
QNG-T-PIONEER-v1: analytic prediction for Pioneer anomaly using flyby-calibrated tau.

Prereq: 05_validation/pre-registrations/qng-t-pioneer-v1.md
Method: a_QNG = tau_flyby * |∇Σ| with Σ = -GM_sun / r, metric ~ flat (g^{ij} ≈ δ^{ij}).
Gates:
  G1: a_QNG in [6e-10, 1.1e-9] m/s^2 for r in [20,70] AU
  G2: a_QNG < 1e-12 m/s^2 for Mercury/Venus controls
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-pioneer-v1"

AU_M = 1.495978707e11
GM_SUN = 1.32712440018e20  # m^3/s^2


def accel_qng(tau: float, r_m: float) -> float:
    g = GM_SUN / (r_m * r_m)  # |∇Σ| in flat limit
    return tau * g


def main():
    ap = argparse.ArgumentParser(description="QNG-T-PIONEER-v1 analytic prediction")
    ap.add_argument("--tau-flyby", type=float, default=0.002051, help="Tau from T-028 (seconds)")
    ap.add_argument("--r-min-au", type=float, default=20.0)
    ap.add_argument("--r-max-au", type=float, default=70.0)
    ap.add_argument("--n-samples", type=int, default=11)
    ap.add_argument("--out-dir", default=str(ARTIFACTS_ROOT))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    radii = np.linspace(args.r_min_au, args.r_max_au, args.n_samples)
    rows = []
    for r_au in radii:
        a = accel_qng(args.tau_flyby, r_au * AU_M)
        rows.append({"r_AU": r_au, "a_qng": a})

    # controls
    inner = [
        ("Mercury", 0.387),
        ("Venus", 0.723),
    ]
    ctrl_rows = []
    for name, r_au in inner:
        a = accel_qng(args.tau_flyby, r_au * AU_M)
        ctrl_rows.append({"body": name, "r_AU": r_au, "a_qng": a})

    # Gates
    band_lo = 6.0e-10
    band_hi = 1.1e-9
    g1_pass = all(band_lo <= r["a_qng"] <= band_hi for r in rows)
    g2_pass = all(r["a_qng"] < 1.0e-12 for r in ctrl_rows)
    final_pass = g1_pass and g2_pass

    # write outputs
    with (out_dir / "pioneer_prediction.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["r_AU", "a_qng"])
        w.writeheader()
        w.writerows(rows)

    with (out_dir / "inner_control.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["body", "r_AU", "a_qng"])
        w.writeheader()
        w.writerows(ctrl_rows)

    gates = [
        {"gate": "G1", "metric": "Pioneer band", "value": f"{rows[0]['a_qng']:.3e}..{rows[-1]['a_qng']:.3e}", "threshold": "[6e-10,1.1e-9] all r∈[20,70] AU", "status": "pass" if g1_pass else "fail"},
        {"gate": "G2", "metric": "Inner control max", "value": f"{max(r['a_qng'] for r in ctrl_rows):.3e}", "threshold": "<1e-12", "status": "pass" if g2_pass else "fail"},
        {"gate": "FINAL", "metric": "decision", "value": "pass" if final_pass else "fail", "threshold": "G1&G2", "status": "pass" if final_pass else "fail"},
    ]
    with (out_dir / "gate_summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=gates[0].keys())
        w.writeheader()
        w.writerows(gates)

    runlog = {
        "tau_flyby": args.tau_flyby,
        "r_min_au": args.r_min_au,
        "r_max_au": args.r_max_au,
        "n_samples": args.n_samples,
        "band_lo": band_lo,
        "band_hi": band_hi,
        "g1_pass": g1_pass,
        "g2_pass": g2_pass,
        "final": final_pass,
    }
    (out_dir / "run-log.txt").write_text(json.dumps(runlog, indent=2), encoding="utf-8")

    print(json.dumps({"final": final_pass, "g1": g1_pass, "g2": g2_pass}, indent=2))
    return 0 if final_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
