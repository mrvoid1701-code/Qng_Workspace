#!/usr/bin/env python3
"""
One-command helpers for reproducible GR checks.

Subcommands:
- official-check: run G10..G16 for one dataset/seed and print pass summary
- baseline-guard: run the frozen GR regression guard
- sweep-phi: run PHI_SCALE sweep on DS-002/003/006

Policy:
- stdlib only
- no threshold or formula edits
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"


def read_metric_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def get_status(rows: list[dict[str, str]], gate_id: str) -> str:
    for row in rows:
        if row.get("gate_id", "").strip() == gate_id:
            return row.get("status", "").strip().lower()
    return ""


def get_final_status(rows: list[dict[str, str]]) -> str:
    return get_status(rows, "FINAL")


def supports_flag(script_path: Path, flag: str) -> bool:
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
            env={**os.environ, **{"PYTHONUTF8": "1"}},
        )
        return flag in ((proc.stdout or "") + (proc.stderr or ""))
    except Exception:
        return False


def run_cmd(cmd: list[str], cwd: Path) -> int:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=False,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    return proc.returncode


def official_check(args: argparse.Namespace) -> int:
    gate_specs = [
        ("G10", "run_qng_covariant_metric_v1.py", "metric_checks_covariant.csv"),
        ("G11", "run_qng_einstein_eq_v1.py", "metric_checks_einstein_eq.csv"),
        ("G12", "run_qng_gr_solutions_v1.py", "metric_checks_gr_solutions.csv"),
        ("G13", "run_qng_covariant_wave_v1.py", "metric_checks_covariant_wave.csv"),
        ("G14", "run_qng_covariant_cons_v1.py", "metric_checks_cov_cons.csv"),
        ("G15", "run_qng_ppn_v1.py", "metric_checks_ppn.csv"),
        ("G16", "run_qng_action_v1.py", "metric_checks_action.csv"),
    ]

    tag = f"{args.dataset_id.lower()}_s{args.seed}_phi{args.phi_scale:.2f}".replace(".", "p")
    out_root = Path(args.out_dir).resolve() if args.out_dir else (ROOT / "07_exports" / "repro" / "gr_official_check" / tag)
    out_root.mkdir(parents=True, exist_ok=True)

    gate_status: dict[str, str] = {}
    print("=" * 72)
    print(f"GR official check: dataset={args.dataset_id} seed={args.seed} phi_scale={args.phi_scale:.2f}")
    print(f"out_dir={out_root}")
    print("=" * 72)

    t0 = time.time()
    for gate_id, script_name, metric_name in gate_specs:
        script = SCRIPTS / script_name
        gate_dir = out_root / gate_id.lower()
        gate_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(script),
            "--dataset-id",
            args.dataset_id,
            "--seed",
            str(args.seed),
            "--out-dir",
            str(gate_dir),
        ]
        if supports_flag(script, "--phi-scale"):
            cmd += ["--phi-scale", f"{args.phi_scale:.2f}"]
        if supports_flag(script, "--plots"):
            cmd += ["--no-plots"]
        rc = run_cmd(cmd, ROOT)
        rows = read_metric_csv(gate_dir / metric_name)
        final = get_final_status(rows) or ("pass" if rc == 0 else "fail")
        gate_status[gate_id] = final
        print(f"{gate_id}: rc={rc} status={final}")

    g15_rows = read_metric_csv(out_root / "g15" / "metric_checks_ppn.csv")
    g15b_v2_status = get_status(g15_rows, "G15b-v2")
    all_pass_official = all(
        gate_status.get(k, "") == "pass"
        for k in ["G10", "G11", "G12", "G13", "G14", "G16"]
    ) and g15b_v2_status == "pass"
    all_pass_diagnostic = all(v == "pass" for v in gate_status.values())

    summary_path = out_root / "summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "dataset_id",
            "seed",
            "phi_scale",
            "g10_status",
            "g11_status",
            "g12_status",
            "g13_status",
            "g14_status",
            "g15_status",
            "g16_status",
            "g15b_v2_status",
            "all_pass_official",
            "all_pass_diagnostic",
            "elapsed_s",
        ]
        row = {
            "dataset_id": args.dataset_id,
            "seed": str(args.seed),
            "phi_scale": f"{args.phi_scale:.2f}",
            "g10_status": gate_status.get("G10", ""),
            "g11_status": gate_status.get("G11", ""),
            "g12_status": gate_status.get("G12", ""),
            "g13_status": gate_status.get("G13", ""),
            "g14_status": gate_status.get("G14", ""),
            "g15_status": gate_status.get("G15", ""),
            "g16_status": gate_status.get("G16", ""),
            "g15b_v2_status": g15b_v2_status,
            "all_pass_official": "pass" if all_pass_official else "fail",
            "all_pass_diagnostic": "pass" if all_pass_diagnostic else "fail",
            "elapsed_s": f"{time.time() - t0:.2f}",
        }
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerow(row)

    print("-" * 72)
    print(f"all_pass_official={'pass' if all_pass_official else 'fail'}")
    print(f"all_pass_diagnostic={'pass' if all_pass_diagnostic else 'fail'}")
    print(f"summary={summary_path}")
    if args.strict_exit and not all_pass_official:
        return 1
    return 0


def baseline_guard(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).resolve() if args.out_dir else (
        ROOT / "07_exports" / "repro" / "gr_baseline_guard"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCRIPTS / "run_qng_gr_regression_guard_v1.py"),
        "--out-dir",
        str(out_dir),
    ]
    print("=" * 72)
    print(f"GR baseline guard -> {out_dir}")
    print("=" * 72)
    return run_cmd(cmd, ROOT)


def sweep_phi(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir).resolve() if args.out_dir else (
        ROOT / "07_exports" / "repro" / "gr_sweep_phi"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(SCRIPTS / "run_qng_phi_scale_sweep_v1.py"),
        "--datasets",
        args.datasets,
        "--seeds",
        args.seeds,
        "--phi-scales",
        args.phi_scales,
        "--out-dir",
        str(out_dir),
    ]
    print("=" * 72)
    print(f"GR phi sweep -> {out_dir}")
    print("=" * 72)
    return run_cmd(cmd, ROOT)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="One-command GR reproducibility helpers.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_off = sub.add_parser("official-check", help="Run G10..G16 for one dataset/seed.")
    p_off.add_argument("--dataset-id", default="DS-003")
    p_off.add_argument("--seed", type=int, default=3520)
    p_off.add_argument("--phi-scale", type=float, default=0.08)
    p_off.add_argument("--out-dir", default="")
    p_off.add_argument("--strict-exit", action="store_true")
    p_off.set_defaults(fn=official_check)

    p_guard = sub.add_parser("baseline-guard", help="Run frozen GR regression guard.")
    p_guard.add_argument("--out-dir", default="")
    p_guard.set_defaults(fn=baseline_guard)

    p_sweep = sub.add_parser("sweep-phi", help="Run PHI_SCALE sweep.")
    p_sweep.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p_sweep.add_argument("--seeds", default="3401")
    p_sweep.add_argument("--phi-scales", default="0.04,0.06,0.08,0.10,0.12")
    p_sweep.add_argument("--out-dir", default="")
    p_sweep.set_defaults(fn=sweep_phi)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.fn(args))


if __name__ == "__main__":
    raise SystemExit(main())
