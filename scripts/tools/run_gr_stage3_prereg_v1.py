#!/usr/bin/env python3
"""
GR Stage-3 prereg runner (v1).

Purpose:
- Freeze and execute a Stage-3 GR expansion protocol with one summary CSV.
- Extend Stage-2 lane coverage with geometry + conservation checks.

Scope in Stage-3:
- 3+1 core lane: G10 + G11
- strong-field lane: G12
- tensor lane: G7
- geometry lane: G8
- conservation lane: G9

Policy:
- stdlib only
- no threshold/formula edits in gate scripts
- thresholds are inherited from existing gate implementations
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"

DEFAULT_OUT_SMOKE = ROOT / "05_validation" / "evidence" / "artifacts" / "gr-stage3-smoke-v1"
DEFAULT_OUT_PREREG = ROOT / "05_validation" / "evidence" / "artifacts" / "gr-stage3-prereg-v1"

PREREG_DATASETS = ["DS-002", "DS-003", "DS-006"]
PREREG_SEED_START = 3401
PREREG_SEED_END = 3600
PREREG_PHI_SCALE = 0.08

PREREG_TENSOR_N_STEPS = 80
PREREG_TENSOR_DT = 0.40
PREREG_TENSOR_C_WAVE = 0.15

PREREG_CONSERVATION_N_STEPS = 200
PREREG_CONSERVATION_DT = 0.40
PREREG_CONSERVATION_C_WAVE = 0.15


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int

    @property
    def tag(self) -> str:
        return f"{self.dataset_id.lower()}_seed{self.seed}"


@dataclass(frozen=True)
class GateRunSpec:
    key: str
    script_name: str
    metric_csv: str
    subgates: tuple[str, ...]


GATE_SPECS: tuple[GateRunSpec, ...] = (
    GateRunSpec(
        key="g10",
        script_name="run_qng_covariant_metric_v1.py",
        metric_csv="metric_checks_covariant.csv",
        subgates=("G10a", "G10b", "G10c", "G10d"),
    ),
    GateRunSpec(
        key="g11",
        script_name="run_qng_einstein_eq_v1.py",
        metric_csv="metric_checks_einstein_eq.csv",
        subgates=("G11a", "G11b", "G11c", "G11d"),
    ),
    GateRunSpec(
        key="g12",
        script_name="run_qng_gr_solutions_v1.py",
        metric_csv="metric_checks_gr_solutions.csv",
        subgates=("G12a", "G12b", "G12c", "G12d"),
    ),
    GateRunSpec(
        key="g7",
        script_name="run_qng_metric_dynamics_v1.py",
        metric_csv="metric_checks_tensor.csv",
        subgates=("G7a", "G7b", "G7c", "G7d"),
    ),
    GateRunSpec(
        key="g8",
        script_name="run_qng_einstein_v1.py",
        metric_csv="metric_checks_einstein.csv",
        subgates=("G8a", "G8b", "G8c", "G8d"),
    ),
    GateRunSpec(
        key="g9",
        script_name="run_qng_conservation_v1.py",
        metric_csv="metric_checks_conservation.csv",
        subgates=("G9a", "G9b", "G9c", "G9d"),
    ),
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run GR Stage-3 prereg protocol (v1).")
    p.add_argument("--mode", choices=["smoke", "prereg"], default="smoke")
    p.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p.add_argument("--seed-start", type=int, default=PREREG_SEED_START)
    p.add_argument("--seed-end", type=int, default=PREREG_SEED_START)
    p.add_argument("--out-dir", default="")
    p.add_argument("--reuse-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--phi-scale", type=float, default=PREREG_PHI_SCALE)
    p.add_argument("--tensor-n-steps", type=int, default=PREREG_TENSOR_N_STEPS)
    p.add_argument("--tensor-dt", type=float, default=PREREG_TENSOR_DT)
    p.add_argument("--tensor-c-wave", type=float, default=PREREG_TENSOR_C_WAVE)
    p.add_argument("--conservation-n-steps", type=int, default=PREREG_CONSERVATION_N_STEPS)
    p.add_argument("--conservation-dt", type=float, default=PREREG_CONSERVATION_DT)
    p.add_argument("--conservation-c-wave", type=float, default=PREREG_CONSERVATION_C_WAVE)
    p.add_argument(
        "--strict-prereg",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enforce frozen prereg datasets/seeds/config for mode=prereg.",
    )
    return p.parse_args()


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def normalize_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def gate_status_map(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    out: dict[str, str] = {}
    for row in rows:
        gid = (row.get("gate_id") or "").strip()
        if gid:
            out[gid] = normalize_status(row.get("status", ""))
    return out


def final_gate_status(statuses: dict[str, str], subgates: tuple[str, ...]) -> str:
    if "FINAL" in statuses:
        return statuses["FINAL"]
    if all(statuses.get(g, "fail") == "pass" for g in subgates):
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


def build_profiles(args: argparse.Namespace) -> list[Profile]:
    if args.mode == "smoke":
        return [
            Profile("DS-002", PREREG_SEED_START),
            Profile("DS-003", PREREG_SEED_START),
            Profile("DS-006", PREREG_SEED_START),
        ]
    datasets = [d.upper() for d in parse_csv_list(args.datasets)]
    out: list[Profile] = []
    for ds in datasets:
        for seed in range(args.seed_start, args.seed_end + 1):
            out.append(Profile(ds, seed))
    return out


def enforce_prereg(args: argparse.Namespace) -> None:
    errors: list[str] = []
    datasets = [d.upper() for d in parse_csv_list(args.datasets)]
    if datasets != PREREG_DATASETS:
        errors.append(f"datasets must be {PREREG_DATASETS}, got {datasets}")
    if args.seed_start != PREREG_SEED_START or args.seed_end != PREREG_SEED_END:
        errors.append(f"seed range must be {PREREG_SEED_START}..{PREREG_SEED_END}")
    if abs(args.phi_scale - PREREG_PHI_SCALE) > 1e-12:
        errors.append(f"phi-scale must be {PREREG_PHI_SCALE}")
    if (
        args.tensor_n_steps != PREREG_TENSOR_N_STEPS
        or abs(args.tensor_dt - PREREG_TENSOR_DT) > 1e-12
        or abs(args.tensor_c_wave - PREREG_TENSOR_C_WAVE) > 1e-12
    ):
        errors.append("tensor config must match frozen prereg values")
    if (
        args.conservation_n_steps != PREREG_CONSERVATION_N_STEPS
        or abs(args.conservation_dt - PREREG_CONSERVATION_DT) > 1e-12
        or abs(args.conservation_c_wave - PREREG_CONSERVATION_C_WAVE) > 1e-12
    ):
        errors.append("conservation config must match frozen prereg values")
    if errors:
        raise ValueError("strict prereg violation: " + "; ".join(errors))


def choose_out_dir(args: argparse.Namespace) -> Path:
    if args.out_dir.strip():
        return Path(args.out_dir).resolve()
    return (DEFAULT_OUT_SMOKE if args.mode == "smoke" else DEFAULT_OUT_PREREG).resolve()


def gate_extra_args(spec_key: str, args: argparse.Namespace) -> list[str]:
    if spec_key == "g10":
        return ["--phi-scale", f"{args.phi_scale:.2f}"]
    if spec_key == "g7":
        return [
            "--n-steps",
            str(args.tensor_n_steps),
            "--dt",
            f"{args.tensor_dt:.2f}",
            "--c-wave",
            f"{args.tensor_c_wave:.2f}",
        ]
    if spec_key == "g9":
        return [
            "--n-steps",
            str(args.conservation_n_steps),
            "--dt",
            f"{args.conservation_dt:.2f}",
            "--c-wave",
            f"{args.conservation_c_wave:.2f}",
        ]
    return []


def aggregate_dataset_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    datasets = sorted({r["dataset_id"] for r in rows})
    out: list[dict[str, Any]] = []
    for ds in datasets:
        sub = [r for r in rows if r["dataset_id"] == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "lane_3p1_core_pass": sum(1 for r in sub if r["lane_3p1_core_status"] == "pass"),
                "lane_strong_field_pass": sum(1 for r in sub if r["lane_strong_field_status"] == "pass"),
                "lane_tensor_pass": sum(1 for r in sub if r["lane_tensor_status"] == "pass"),
                "lane_geometry_pass": sum(1 for r in sub if r["lane_geometry_status"] == "pass"),
                "lane_conservation_pass": sum(1 for r in sub if r["lane_conservation_status"] == "pass"),
                "stage3_pass": sum(1 for r in sub if r["stage3_status"] == "pass"),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    if args.mode == "prereg" and args.strict_prereg:
        enforce_prereg(args)

    out_dir = choose_out_dir(args)
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root = out_dir / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    profiles = build_profiles(args)
    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        logs.append(msg)

    log("=" * 72)
    log(f"GR Stage-3 prereg v1 | mode={args.mode} | profiles={len(profiles)}")
    log(f"out_dir={out_dir}")
    log("=" * 72)

    summary_rows: list[dict[str, Any]] = []

    for idx, profile in enumerate(profiles, start=1):
        log(f"[{idx}/{len(profiles)}] {profile.tag}")
        profile_dir = runs_root / profile.tag
        profile_dir.mkdir(parents=True, exist_ok=True)

        gate_data: dict[str, dict[str, Any]] = {}
        for spec in GATE_SPECS:
            gate_dir = profile_dir / spec.key
            gate_dir.mkdir(parents=True, exist_ok=True)
            metric_path = gate_dir / spec.metric_csv
            rc = 0
            tail = ""
            ran = False

            if not (args.reuse_existing and metric_path.exists()):
                cmd = [
                    sys.executable,
                    str(SCRIPTS / spec.script_name),
                    "--dataset-id",
                    profile.dataset_id,
                    "--seed",
                    str(profile.seed),
                    "--out-dir",
                    str(gate_dir),
                ]
                cmd.extend(gate_extra_args(spec.key, args))
                rc, tail = run_cmd(cmd, ROOT)
                ran = True

            statuses = gate_status_map(metric_path)
            final = final_gate_status(statuses, spec.subgates)
            gate_data[spec.key] = {
                "rc": rc,
                "status_map": statuses,
                "final": final,
                "ran": ran,
                "tail": tail,
            }
            run_state = "run" if ran else "reuse"
            log(f"  - {spec.key}: {run_state} final={final}")
            if tail and rc != 0:
                for line in tail.splitlines():
                    log(f"    {line}")

        g10 = gate_data["g10"]
        g11 = gate_data["g11"]
        g12 = gate_data["g12"]
        g7 = gate_data["g7"]
        g8 = gate_data["g8"]
        g9 = gate_data["g9"]

        lane_3p1_core = "pass" if (g10["final"] == "pass" and g11["final"] == "pass") else "fail"
        lane_strong_field = g12["final"]
        lane_tensor = g7["final"]
        lane_geometry = g8["final"]
        lane_conservation = g9["final"]
        stage3_status = (
            "pass"
            if (
                lane_3p1_core == "pass"
                and lane_strong_field == "pass"
                and lane_tensor == "pass"
                and lane_geometry == "pass"
                and lane_conservation == "pass"
            )
            else "fail"
        )

        row: dict[str, Any] = {
            "dataset_id": profile.dataset_id,
            "seed": profile.seed,
            "phi_scale_where_applicable": f"{args.phi_scale:.2f}",
            "g10_status": g10["final"],
            "g10a": g10["status_map"].get("G10a", "fail"),
            "g10b": g10["status_map"].get("G10b", "fail"),
            "g10c": g10["status_map"].get("G10c", "fail"),
            "g10d": g10["status_map"].get("G10d", "fail"),
            "g11_status": g11["final"],
            "g11a": g11["status_map"].get("G11a", "fail"),
            "g11b": g11["status_map"].get("G11b", "fail"),
            "g11c": g11["status_map"].get("G11c", "fail"),
            "g11d": g11["status_map"].get("G11d", "fail"),
            "g12_status": g12["final"],
            "g12a": g12["status_map"].get("G12a", "fail"),
            "g12b": g12["status_map"].get("G12b", "fail"),
            "g12c": g12["status_map"].get("G12c", "fail"),
            "g12d": g12["status_map"].get("G12d", "fail"),
            "g7_status": g7["final"],
            "g7a": g7["status_map"].get("G7a", "fail"),
            "g7b": g7["status_map"].get("G7b", "fail"),
            "g7c": g7["status_map"].get("G7c", "fail"),
            "g7d": g7["status_map"].get("G7d", "fail"),
            "g8_status": g8["final"],
            "g8a": g8["status_map"].get("G8a", "fail"),
            "g8b": g8["status_map"].get("G8b", "fail"),
            "g8c": g8["status_map"].get("G8c", "fail"),
            "g8d": g8["status_map"].get("G8d", "fail"),
            "g9_status": g9["final"],
            "g9a": g9["status_map"].get("G9a", "fail"),
            "g9b": g9["status_map"].get("G9b", "fail"),
            "g9c": g9["status_map"].get("G9c", "fail"),
            "g9d": g9["status_map"].get("G9d", "fail"),
            "lane_3p1_core_status": lane_3p1_core,
            "lane_strong_field_status": lane_strong_field,
            "lane_tensor_status": lane_tensor,
            "lane_geometry_status": lane_geometry,
            "lane_conservation_status": lane_conservation,
            "stage3_status": stage3_status,
            "run_root": profile_dir.resolve().relative_to(ROOT.resolve()).as_posix(),
        }
        summary_rows.append(row)

    if not summary_rows:
        raise RuntimeError("No profiles executed.")

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, summary_rows, list(summary_rows[0].keys()))

    ds_rows = aggregate_dataset_rows(summary_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    stage3_pass = sum(1 for r in summary_rows if r["stage3_status"] == "pass")
    stage3_total = len(summary_rows)

    report_lines = [
        "# GR Stage-3 Prereg Report (v1)",
        "",
        f"- mode: `{args.mode}`",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- profiles: `{stage3_total}`",
        f"- stage3_pass: `{stage3_pass}/{stage3_total}`",
        f"- lane_3p1_core_pass: `{sum(1 for r in summary_rows if r['lane_3p1_core_status'] == 'pass')}/{stage3_total}`",
        f"- lane_strong_field_pass: `{sum(1 for r in summary_rows if r['lane_strong_field_status'] == 'pass')}/{stage3_total}`",
        f"- lane_tensor_pass: `{sum(1 for r in summary_rows if r['lane_tensor_status'] == 'pass')}/{stage3_total}`",
        f"- lane_geometry_pass: `{sum(1 for r in summary_rows if r['lane_geometry_status'] == 'pass')}/{stage3_total}`",
        f"- lane_conservation_pass: `{sum(1 for r in summary_rows if r['lane_conservation_status'] == 'pass')}/{stage3_total}`",
        "",
        "## Notes",
        "",
        "- Stage-3 is prereg/candidate lane and does not overwrite Stage-1/Stage-2 official policies.",
        "- No threshold or formula changes were applied in gate runner scripts.",
        "- All thresholds are inherited from gate scripts G10, G11, G12, G7, G8, G9.",
        "",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "datasets": sorted({r["dataset_id"] for r in summary_rows}),
        "seed_start": min(int(r["seed"]) for r in summary_rows),
        "seed_end": max(int(r["seed"]) for r in summary_rows),
        "phi_scale_where_applicable": args.phi_scale,
        "tensor_config": {
            "n_steps": args.tensor_n_steps,
            "dt": args.tensor_dt,
            "c_wave": args.tensor_c_wave,
        },
        "conservation_config": {
            "n_steps": args.conservation_n_steps,
            "dt": args.conservation_dt,
            "c_wave": args.conservation_c_wave,
        },
        "stage3_lanes": {
            "lane_3p1_core": ["G10", "G11"],
            "lane_strong_field": ["G12"],
            "lane_tensor": ["G7"],
            "lane_geometry": ["G8"],
            "lane_conservation": ["G9"],
        },
        "notes": [
            "Stage-3 remains prereg/candidate until promotion criteria are explicitly closed.",
            "QM lane is tracked separately and excluded from Stage-3 decision CSV.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run-log.txt").write_text("\n".join(logs) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

