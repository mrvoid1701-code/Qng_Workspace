#!/usr/bin/env python3
"""
QNG PHI_SCALE sensitivity sweep (v1) for GR chain G10-G16.

Purpose:
- Verify that changing PHI_SCALE is a regime-control choice, not a post-hoc fit.
- Run gates G10..G16 across datasets and PHI_SCALE grid with fixed seeds.

Inputs:
- dataset ids (default: DS-002,DS-003,DS-006)
- seeds (default: 3401)
- phi-scale grid (default: 0.04,0.06,0.08,0.10,0.12)

Outputs:
- summary CSV:
  05_validation/evidence/artifacts/phi_scale_sweep_v1/summary.csv
- short run log:
  05_validation/evidence/artifacts/phi_scale_sweep_v1/run-log.txt
- per-run gate artifacts under:
  05_validation/evidence/artifacts/phi_scale_sweep_v1/runs/

Artifacts written:
- One row per (dataset, seed, phi_scale), including:
  * G15a gamma_dev
  * G15d EP_ratio
  * G15b shapiro_ratio
  * G13 E_cov drift (from gate row G13b metric E_cov_drift)
  * G14 E_cov drift (from gate row G14b metric E_cov_drift)
  * PASS/FAIL for each gate G10..G16

Policy:
- stdlib only
- no threshold or formula changes
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "phi_scale_sweep_v1"
RUNS_DIR_NAME = "runs"


@dataclass(frozen=True)
class GateSpec:
    gate_id: str
    script: str
    metric_checks_file: str


GATE_SPECS: list[GateSpec] = [
    GateSpec("G10", "run_qng_covariant_metric_v1.py", "metric_checks_covariant.csv"),
    GateSpec("G11", "run_qng_einstein_eq_v1.py", "metric_checks_einstein_eq.csv"),
    GateSpec("G12", "run_qng_gr_solutions_v1.py", "metric_checks_gr_solutions.csv"),
    GateSpec("G13", "run_qng_covariant_wave_v1.py", "metric_checks_covariant_wave.csv"),
    GateSpec("G14", "run_qng_covariant_cons_v1.py", "metric_checks_cov_cons.csv"),
    GateSpec("G15", "run_qng_ppn_v1.py", "metric_checks_ppn.csv"),
    GateSpec("G16", "run_qng_action_v1.py", "metric_checks_action.csv"),
]


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_float_list(text: str) -> list[float]:
    out: list[float] = []
    for token in parse_csv_list(text):
        out.append(float(token))
    return out


def parse_int_list(text: str) -> list[int]:
    out: list[int] = []
    for token in parse_csv_list(text):
        out.append(int(token))
    return out


def phi_tag(phi: float) -> str:
    return f"{phi:.2f}".replace(".", "p")


def read_metric_checks(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def get_metric_value(rows: list[dict[str, str]], gate_id: str, metric: str) -> str:
    for row in rows:
        if row.get("gate_id") == gate_id and row.get("metric") == metric:
            return row.get("value", "")
    return ""


def get_final_status(rows: list[dict[str, str]]) -> str:
    for row in rows:
        if row.get("gate_id") == "FINAL":
            return row.get("status", "").strip().lower()
    return ""


def supports_flag(script_path: Path, flag: str, cache: dict[tuple[str, str], bool]) -> bool:
    key = (str(script_path), flag)
    if key in cache:
        return cache[key]
    try:
        probe = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=ROOT,
            env={**os.environ, **{"PYTHONUTF8": "1"}},
        )
        txt = (probe.stdout or "") + (probe.stderr or "")
        cache[key] = flag in txt
    except Exception:
        cache[key] = False
    return cache[key]


def run_gate(
    gate: GateSpec,
    *,
    dataset_id: str,
    seed: int,
    phi_scale: float,
    out_dir: Path,
    flag_cache: dict[tuple[str, str], bool],
) -> tuple[int, float, str]:
    script_path = ROOT / "scripts" / gate.script
    cmd: list[str] = [
        sys.executable,
        str(script_path),
        "--dataset-id",
        dataset_id,
        "--seed",
        str(seed),
        "--out-dir",
        str(out_dir),
    ]
    if supports_flag(script_path, "--phi-scale", flag_cache):
        cmd.extend(["--phi-scale", f"{phi_scale:.2f}"])
    if supports_flag(script_path, "--plots", flag_cache):
        cmd.append("--no-plots")

    t0 = time.monotonic()
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    elapsed = time.monotonic() - t0
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(combined.splitlines()[-8:]) if combined else ""
    return proc.returncode, elapsed, tail


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
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
        "all_pass",
        "g15a_gamma_dev",
        "g15d_ep_ratio",
        "g15b_shapiro_ratio",
        "g13b_e_cov_drift",
        "g14b_e_cov_drift",
        "g13c_speed_reduction",
        "run_root",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QNG PHI_SCALE sweep v1 across G10-G16.")
    p.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p.add_argument("--seeds", default="3401")
    p.add_argument("--phi-scales", default="0.04,0.06,0.08,0.10,0.12")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root = out_dir / RUNS_DIR_NAME
    runs_root.mkdir(parents=True, exist_ok=True)

    datasets = parse_csv_list(args.datasets)
    seeds = parse_int_list(args.seeds)
    phi_scales = parse_float_list(args.phi_scales)

    summary_rows: list[dict[str, Any]] = []
    log_lines: list[str] = []
    flag_cache: dict[tuple[str, str], bool] = {}
    start = time.time()

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 72)
    log("QNG PHI_SCALE sweep v1")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log(f"Datasets={datasets}  Seeds={seeds}  Phi_scales={phi_scales}")
    log("=" * 72)

    total = len(datasets) * len(seeds) * len(phi_scales)
    idx = 0

    for dataset_id in datasets:
        for seed in seeds:
            for phi in phi_scales:
                idx += 1
                combo_tag = f"{dataset_id.lower()}_seed{seed}_phi{phi_tag(phi)}"
                combo_root = runs_root / combo_tag
                combo_root.mkdir(parents=True, exist_ok=True)
                log(f"\n[{idx}/{total}] {combo_tag}")

                per_gate_status: dict[str, str] = {}
                per_gate_rows: dict[str, list[dict[str, str]]] = {}

                for gate in GATE_SPECS:
                    gate_dir = combo_root / gate.gate_id.lower()
                    gate_dir.mkdir(parents=True, exist_ok=True)
                    rc, elapsed, tail = run_gate(
                        gate,
                        dataset_id=dataset_id,
                        seed=seed,
                        phi_scale=phi,
                        out_dir=gate_dir,
                        flag_cache=flag_cache,
                    )
                    rows = read_metric_checks(gate_dir / gate.metric_checks_file)
                    status = get_final_status(rows)
                    if not status:
                        status = "pass" if rc == 0 else "fail"
                    per_gate_status[gate.gate_id] = status
                    per_gate_rows[gate.gate_id] = rows
                    log(f"  {gate.gate_id}: rc={rc} status={status} elapsed={elapsed:.2f}s")
                    if rc != 0 and tail:
                        log("    tail:")
                        for line in tail.splitlines():
                            log(f"      {line}")

                g15_rows = per_gate_rows.get("G15", [])
                g13_rows = per_gate_rows.get("G13", [])
                g14_rows = per_gate_rows.get("G14", [])
                all_pass = all(per_gate_status.get(f"G{i}", "") == "pass" for i in range(10, 17))

                summary_rows.append(
                    {
                        "dataset_id": dataset_id,
                        "seed": seed,
                        "phi_scale": f"{phi:.2f}",
                        "g10_status": per_gate_status.get("G10", ""),
                        "g11_status": per_gate_status.get("G11", ""),
                        "g12_status": per_gate_status.get("G12", ""),
                        "g13_status": per_gate_status.get("G13", ""),
                        "g14_status": per_gate_status.get("G14", ""),
                        "g15_status": per_gate_status.get("G15", ""),
                        "g16_status": per_gate_status.get("G16", ""),
                        "all_pass": "pass" if all_pass else "fail",
                        "g15a_gamma_dev": get_metric_value(g15_rows, "G15a", "gamma_dev"),
                        "g15d_ep_ratio": get_metric_value(g15_rows, "G15d", "EP_ratio"),
                        "g15b_shapiro_ratio": get_metric_value(g15_rows, "G15b", "shapiro_ratio"),
                        "g13b_e_cov_drift": get_metric_value(g13_rows, "G13b", "E_cov_drift"),
                        "g14b_e_cov_drift": get_metric_value(g14_rows, "G14b", "E_cov_drift"),
                        "g13c_speed_reduction": get_metric_value(g13_rows, "G13c", "speed_reduction"),
                        "run_root": str(combo_root.relative_to(ROOT)).replace("\\", "/"),
                    }
                )

    summary_path = out_dir / "summary.csv"
    write_summary(summary_path, summary_rows)

    pass_count = sum(1 for row in summary_rows if row["all_pass"] == "pass")
    elapsed_total = time.time() - start
    log("\n" + "=" * 72)
    log(f"Rows: {len(summary_rows)}  all_pass={pass_count}/{len(summary_rows)}")
    log(f"summary.csv: {summary_path}")
    log(f"Elapsed: {elapsed_total:.2f}s")
    log("=" * 72)

    (out_dir / "run-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
