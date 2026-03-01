#!/usr/bin/env python3
"""
Run G15 (PPN) debug diagnostics and compare G15b v1 vs G15b-v2.

Purpose:
- Execute run_qng_ppn_v1.py in debug mode for selected datasets/seeds.
- Collect side-by-side v1/v2 Shapiro ratios without changing thresholds.

Default scope:
- datasets: DS-002, DS-003, DS-006
- seed: 3401

Outputs:
- 05_validation/evidence/artifacts/qng-ppn-debug-v1/summary_v1_vs_v2.csv
- 05_validation/evidence/artifacts/qng-ppn-debug-v1/run-log.txt
- per-run artifacts under:
  05_validation/evidence/artifacts/qng-ppn-debug-v1/runs/

Policy:
- stdlib only
- no threshold tuning
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-ppn-debug-v1"


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(x) for x in parse_csv_list(text)]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G15b diagnostics and compare v1 vs v2.")
    p.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p.add_argument("--seeds", default="3401")
    p.add_argument("--phi-scale", type=float, default=0.08)
    p.add_argument("--debug-topk", type=int, default=10)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def get_metric(rows: list[dict[str, str]], gate_id: str, metric: str) -> str:
    for row in rows:
        if row.get("gate_id") == gate_id and row.get("metric") == metric:
            return row.get("value", "")
    return ""


def get_status(rows: list[dict[str, str]], gate_id: str) -> str:
    for row in rows:
        if row.get("gate_id") == gate_id:
            return row.get("status", "").strip().lower()
    return ""


def run_ppn(
    *,
    dataset_id: str,
    seed: int,
    phi_scale: float,
    debug_topk: int,
    out_dir: Path,
) -> tuple[int, str]:
    script = ROOT / "scripts" / "run_qng_ppn_v1.py"
    cmd = [
        sys.executable,
        str(script),
        "--dataset-id",
        dataset_id,
        "--seed",
        str(seed),
        "--phi-scale",
        f"{phi_scale:.2f}",
        "--out-dir",
        str(out_dir),
        "--debug-mode",
        "--debug-topk",
        str(debug_topk),
        "--no-plots",
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    combined = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(combined.splitlines()[-12:]) if combined else ""
    return proc.returncode, tail


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "dataset_id",
        "seed",
        "phi_scale",
        "g15_final_status",
        "g15a_gamma_dev",
        "g15d_ep_ratio",
        "g15b_v1_ratio",
        "g15b_v1_status",
        "g15b_v2_ratio",
        "g15b_v2_status",
        "run_rc",
        "run_dir",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    runs_root = out_dir / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    datasets = parse_csv_list(args.datasets)
    seeds = parse_int_list(args.seeds)

    log_lines: list[str] = []
    rows: list[dict[str, Any]] = []
    t0 = time.time()

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 72)
    log("QNG G15b debug + v1/v2 comparison")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log(f"Datasets={datasets} Seeds={seeds} phi_scale={args.phi_scale:.2f}")
    log("=" * 72)

    total = len(datasets) * len(seeds)
    i = 0
    for dataset_id in datasets:
        for seed in seeds:
            i += 1
            run_dir = runs_root / f"{dataset_id.lower()}_seed{seed}"
            run_dir.mkdir(parents=True, exist_ok=True)

            log(f"\n[{i}/{total}] dataset={dataset_id} seed={seed}")
            rc, tail = run_ppn(
                dataset_id=dataset_id,
                seed=seed,
                phi_scale=args.phi_scale,
                debug_topk=args.debug_topk,
                out_dir=run_dir,
            )
            if tail:
                log("  run tail:")
                for line in tail.splitlines():
                    log(f"    {line}")

            metric_rows = read_csv_rows(run_dir / "metric_checks_ppn.csv")
            row = {
                "dataset_id": dataset_id,
                "seed": seed,
                "phi_scale": f"{args.phi_scale:.2f}",
                "g15_final_status": get_status(metric_rows, "FINAL"),
                "g15a_gamma_dev": get_metric(metric_rows, "G15a", "gamma_dev"),
                "g15d_ep_ratio": get_metric(metric_rows, "G15d", "EP_ratio"),
                "g15b_v1_ratio": get_metric(metric_rows, "G15b", "shapiro_ratio"),
                "g15b_v1_status": get_status(metric_rows, "G15b"),
                "g15b_v2_ratio": get_metric(metric_rows, "G15b-v2", "shapiro_ratio_v2"),
                "g15b_v2_status": get_status(metric_rows, "G15b-v2"),
                "run_rc": rc,
                "run_dir": str(run_dir),
            }
            rows.append(row)
            log(
                "  summary: "
                f"G15={row['g15_final_status']} "
                f"v1={row['g15b_v1_ratio']}({row['g15b_v1_status']}) "
                f"v2={row['g15b_v2_ratio']}({row['g15b_v2_status']}) "
                f"rc={rc}"
            )

    summary_path = out_dir / "summary_v1_vs_v2.csv"
    write_summary(summary_path, rows)
    elapsed = time.time() - t0

    log(f"\nSummary CSV: {summary_path}")
    log(f"Elapsed: {elapsed:.2f}s")
    (out_dir / "run-log.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
