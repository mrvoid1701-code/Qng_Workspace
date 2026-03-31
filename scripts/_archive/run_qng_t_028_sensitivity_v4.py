#!/usr/bin/env python3
"""
QNG-T-028 sensitivity scan (metric v4) over anisotropy_keep and tau_universal.

Prereq: 05_validation/pre-registrations/qng-t-028-sensitivity-v4.md
Runner: wraps scripts/run_qng_t_028_trajectory_real.py without modifying it.
If the underlying script ignores the hyperparameters, results will be identical
across combos; this is recorded in outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_RUNNER = ROOT / "scripts" / "run_qng_t_028_trajectory_real.py"
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-028-sens-v4"

COMB_ANIS = [0.2, 0.3, 0.4, 0.5, 0.6]
COMB_TAU = [0.25, 0.40, 0.55]


def parse_delta_chi2(model_md: Path) -> float | None:
    if not model_md.exists():
        return None
    for line in model_md.read_text(encoding="utf-8").splitlines():
        if "chi2_total" in line:
            parts = [p.strip() for p in line.strip().strip("|").split("|")]
            # expected: ["chi2_total", "Baseline", "Memory", "Delta"]
            if len(parts) >= 4:
                try:
                    return float(parts[3])
                except Exception:
                    try:
                        # sometimes columns are Baseline, Memory, Delta
                        return float(parts[-1])
                    except Exception:
                        return None
    return None


def run_combo(ani: float, tau: float, seed: int, base_args: list[str]) -> dict:
    combo_dir = ARTIFACTS_ROOT / f"comb_ani{ani:.2f}_tau{tau:.2f}"
    combo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["QNG_ANISOTROPY_KEEP"] = str(ani)
    env["QNG_TAU_UNIVERSAL"] = str(tau)
    cmd = ["python", str(BASE_RUNNER), "--out-dir", str(combo_dir)] + base_args + ["--seed", str(seed)]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    success = res.returncode == 0
    delta = parse_delta_chi2(combo_dir / "model-comparison.md")
    return {
        "anisotropy_keep": ani,
        "tau_universal": tau,
        "returncode": res.returncode,
        "delta_chi2": delta,
        "stdout": res.stdout[-500:],
        "stderr": res.stderr[-500:],
        "success": success,
        "out_dir": str(combo_dir),
    }


def main():
    ap = argparse.ArgumentParser(description="QNG-T-028 sensitivity scan v4")
    ap.add_argument("--seed", type=int, default=20260225)
    ap.add_argument("--flyby-csv", default=None, help="Optional override flyby CSV")
    ap.add_argument("--pioneer-csv", default=None, help="Optional override pioneer CSV")
    args = ap.parse_args()

    base_args = []
    if args.flyby_csv:
        base_args += ["--flyby-csv", args.flyby_csv]
    if args.pioneer_csv:
        base_args += ["--pioneer-csv", args.pioneer_csv, "--use-pioneer-anchor"]
    else:
        base_args += ["--use-pioneer-anchor"]

    ARTIFACTS_ROOT.mkdir(parents=True, exist_ok=True)
    results = []
    for ani in COMB_ANIS:
        for tau in COMB_TAU:
            results.append(run_combo(ani, tau, args.seed, base_args))

    # evaluate gate
    valid = [r for r in results if r["delta_chi2"] is not None and r["returncode"] == 0]
    pass_count = sum(1 for r in valid if r["delta_chi2"] < 0)
    gate_g1 = pass_count >= 12
    final_pass = gate_g1

    # write summary csv
    import csv

    summary_path = ARTIFACTS_ROOT / "sens_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        cols = ["anisotropy_keep", "tau_universal", "delta_chi2", "returncode", "success", "out_dir"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k) for k in cols})

    gate_rows = [
        {"gate": "G1", "metric": "passes_with_delta_chi2<0", "value": pass_count, "threshold": ">=12 of 15", "status": "pass" if gate_g1 else "fail"},
        {"gate": "FINAL", "metric": "decision", "value": "pass" if final_pass else "fail", "threshold": "G1", "status": "pass" if final_pass else "fail"},
    ]
    gate_path = ARTIFACTS_ROOT / "gate_summary.csv"
    with gate_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=gate_rows[0].keys())
        w.writeheader()
        w.writerows(gate_rows)

    log = {
        "seed": args.seed,
        "flyby_csv": args.flyby_csv,
        "pioneer_csv": args.pioneer_csv,
        "combos": len(results),
        "pass_count": pass_count,
        "gate_g1": gate_g1,
        "final": final_pass,
        "note": "Underlying runner currently does not consume QNG_ANISOTROPY_KEEP / QNG_TAU_UNIVERSAL; results are expected identical across combos unless runner adds support.",
    }
    (ARTIFACTS_ROOT / "run-log.txt").write_text(json.dumps(log, indent=2), encoding="utf-8")

    print(json.dumps({"final": final_pass, "pass_count": pass_count, "gate_g1": gate_g1}, indent=2))
    return 0 if final_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
