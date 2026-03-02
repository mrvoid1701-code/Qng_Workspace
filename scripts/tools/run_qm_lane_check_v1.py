#!/usr/bin/env python3
"""
QM lane check runner (v1).

Runs QM gates G17..G20 in a standalone lane and writes one summary CSV.
This lane is intentionally separate from GR official decision logic.
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
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"


@dataclass(frozen=True)
class GateSpec:
    gate_id: str
    key: str
    script_name: str
    metric_csv: str


QM_GATES: tuple[GateSpec, ...] = (
    GateSpec("G17", "g17", "run_qng_qm_bridge_v1.py", "metric_checks_qm.csv"),
    GateSpec("G18", "g18", "run_qng_qm_info_v1.py", "metric_checks_qm_info.csv"),
    GateSpec("G19", "g19", "run_qng_unruh_thermal_v1.py", "metric_checks_unruh.csv"),
    GateSpec("G20", "g20", "run_qng_semiclassical_v1.py", "metric_checks_semi.csv"),
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run standalone QM lane check (G17..G20).")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default="")
    p.add_argument("--strict-exit", action="store_true")
    return p.parse_args()


def normalize_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def read_metric_status(path: Path) -> str:
    if not path.exists():
        return "fail"
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_gate: dict[str, str] = {}
    for row in rows:
        gid = (row.get("gate_id") or "").strip()
        if gid:
            by_gate[gid] = normalize_status(row.get("status", ""))
    if "FINAL" in by_gate:
        return by_gate["FINAL"]
    non_final = [st for gid, st in by_gate.items() if gid != "FINAL"]
    if non_final and all(st == "pass" for st in non_final):
        return "pass"
    return "fail"


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-8:]) if merged else ""
    return proc.returncode, tail


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    tag = f"{args.dataset_id.lower()}_s{args.seed}"
    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir.strip()
        else (ROOT / "07_exports" / "repro" / "qm_lane_check" / tag)
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        logs.append(msg)

    log("=" * 72)
    log(f"QM lane check v1 | dataset={args.dataset_id} seed={args.seed}")
    log(f"out_dir={out_dir}")
    log("=" * 72)

    row: dict[str, Any] = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
    }

    for spec in QM_GATES:
        gate_dir = out_dir / spec.key
        gate_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(SCRIPTS / spec.script_name),
            "--dataset-id",
            args.dataset_id,
            "--seed",
            str(args.seed),
            "--out-dir",
            str(gate_dir),
        ]
        rc, tail = run_cmd(cmd, ROOT)
        status = read_metric_status(gate_dir / spec.metric_csv)
        row[f"{spec.key}_status"] = status
        row[f"{spec.key}_rc"] = rc
        row[f"{spec.key}_run_root"] = gate_dir.resolve().relative_to(ROOT.resolve()).as_posix()
        log(f"- {spec.gate_id}: rc={rc} status={status}")
        if rc != 0 and tail:
            for line in tail.splitlines():
                log(f"  {line}")

    all_pass = all(row.get(f"{spec.key}_status", "fail") == "pass" for spec in QM_GATES)
    row["all_pass_qm_lane"] = "pass" if all_pass else "fail"

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, [row], list(row.keys()))
    (out_dir / "run-log.txt").write_text("\n".join(logs) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"all_pass_qm_lane={row['all_pass_qm_lane']}")
    if args.strict_exit and not all_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
