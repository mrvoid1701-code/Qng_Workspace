#!/usr/bin/env python3
"""
Run QM-Stage-1 prereg packages (v1) with one-summary outputs.

Purpose:
- execute QM lane gates G17..G20 over a preregistered profile grid
- keep GR and QM decision lanes separated

Inputs:
- dataset list and seed range (or smoke profile set)

Outputs:
- summary.csv (one row per dataset/seed profile)
- dataset_summary.csv
- report.md
- prereg_manifest.json
- run-log.txt

Artifacts written:
- per-profile runs under out_dir/runs/<dataset_seed_tag>/ via run_qm_lane_check_v1.py
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
TOOLS = ROOT / "scripts" / "tools"
DEFAULT_DATASETS = ("DS-002", "DS-003", "DS-006")
DEFAULT_SEED_START = 3401
DEFAULT_SEED_END = 3600


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QM-Stage-1 prereg package (v1).")
    p.add_argument("--mode", choices=("smoke", "prereg"), default="smoke")
    p.add_argument("--datasets", default=",".join(DEFAULT_DATASETS))
    p.add_argument("--seed-start", type=int, default=DEFAULT_SEED_START)
    p.add_argument("--seed-end", type=int, default=DEFAULT_SEED_END)
    p.add_argument("--out-dir", default="")
    p.add_argument("--strict-prereg", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=False)
    return p.parse_args()


def normalize_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-10:]) if merged else ""
    return proc.returncode, tail


def read_summary_row(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"summary row missing: {path}")
    return rows[0]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def make_profiles(args: argparse.Namespace) -> list[Profile]:
    datasets = parse_csv_list(args.datasets)
    if not datasets:
        raise ValueError("datasets list is empty")
    if args.mode == "smoke":
        return [Profile(dataset_id=ds, seed=DEFAULT_SEED_START) for ds in datasets]
    if args.seed_end < args.seed_start:
        raise ValueError("seed-end must be >= seed-start")
    out: list[Profile] = []
    for ds in datasets:
        for seed in range(args.seed_start, args.seed_end + 1):
            out.append(Profile(dataset_id=ds, seed=seed))
    return out


def default_out_dir(mode: str) -> Path:
    root = ROOT / "05_validation" / "evidence" / "artifacts"
    if mode == "smoke":
        return root / "qm-stage1-smoke-v1"
    return root / "qm-stage1-prereg-v1"


def dataset_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    datasets = sorted({str(r["dataset_id"]) for r in rows})
    for ds in datasets:
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g17_pass": sum(1 for r in sub if r["g17_status"] == "pass"),
                "g18_pass": sum(1 for r in sub if r["g18_status"] == "pass"),
                "g19_pass": sum(1 for r in sub if r["g19_status"] == "pass"),
                "g20_pass": sum(1 for r in sub if r["g20_status"] == "pass"),
                "all_pass_qm_lane": sum(1 for r in sub if r["all_pass_qm_lane"] == "pass"),
                "rc_fail_profiles": sum(1 for r in sub if int(r["rc_fail_count"]) > 0),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    datasets = parse_csv_list(args.datasets)
    if args.strict_prereg:
        expected_datasets = list(DEFAULT_DATASETS)
        if args.mode != "prereg":
            raise RuntimeError("strict-prereg requires --mode prereg")
        if datasets != expected_datasets:
            raise RuntimeError(f"strict-prereg datasets must be {expected_datasets}; got {datasets}")
        if args.seed_start != DEFAULT_SEED_START or args.seed_end != DEFAULT_SEED_END:
            raise RuntimeError(
                f"strict-prereg seeds must be {DEFAULT_SEED_START}..{DEFAULT_SEED_END}; "
                f"got {args.seed_start}..{args.seed_end}"
            )

    profiles = make_profiles(args)
    out_dir = Path(args.out_dir).resolve() if args.out_dir.strip() else default_out_dir(args.mode)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 72)
    log(f"QM-Stage-1 prereg v1 | mode={args.mode} | profiles={len(profiles)}")
    log(f"out_dir={out_dir}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    run_root = out_dir / "runs"

    for idx, p in enumerate(profiles, start=1):
        tag = f"{p.dataset_id.lower()}_seed{p.seed}"
        profile_out = run_root / tag
        cmd = [
            sys.executable,
            str(TOOLS / "run_qm_lane_check_v1.py"),
            "--dataset-id",
            p.dataset_id,
            "--seed",
            str(p.seed),
            "--out-dir",
            str(profile_out),
        ]
        log(f"[{idx}/{len(profiles)}] {tag}")
        rc, tail = run_cmd(cmd, ROOT)
        summary_csv = profile_out / "summary.csv"
        if not summary_csv.exists():
            raise RuntimeError(f"profile summary missing: {summary_csv}")

        q = read_summary_row(summary_csv)
        rc_fail_count = sum(
            1
            for key in ("g17_rc", "g18_rc", "g19_rc", "g20_rc")
            if int(str(q.get(key, "1"))) != 0
        )
        row = {
            "dataset_id": p.dataset_id,
            "seed": p.seed,
            "run_root": profile_out.resolve().relative_to(ROOT.resolve()).as_posix(),
            "mode": args.mode,
            "g17_status": normalize_status(q.get("g17_status", "")),
            "g18_status": normalize_status(q.get("g18_status", "")),
            "g19_status": normalize_status(q.get("g19_status", "")),
            "g20_status": normalize_status(q.get("g20_status", "")),
            "g17_rc": int(str(q.get("g17_rc", "1"))),
            "g18_rc": int(str(q.get("g18_rc", "1"))),
            "g19_rc": int(str(q.get("g19_rc", "1"))),
            "g20_rc": int(str(q.get("g20_rc", "1"))),
            "rc_fail_count": rc_fail_count,
            "all_pass_qm_lane": normalize_status(q.get("all_pass_qm_lane", "")),
            "runner_rc": rc,
        }
        rows.append(row)
        log(
            "  - qm_lane:"
            f" rc={rc} all_pass={row['all_pass_qm_lane']}"
            f" g17={row['g17_status']} g18={row['g18_status']}"
            f" g19={row['g19_status']} g20={row['g20_status']}"
        )
        if rc != 0 and tail:
            for line in tail.splitlines():
                log(f"    {line}")

    rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, list(rows[0].keys()))

    ds_rows = dataset_summary(rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(rows)
    g17_pass = sum(1 for r in rows if r["g17_status"] == "pass")
    g18_pass = sum(1 for r in rows if r["g18_status"] == "pass")
    g19_pass = sum(1 for r in rows if r["g19_status"] == "pass")
    g20_pass = sum(1 for r in rows if r["g20_status"] == "pass")
    lane_pass = sum(1 for r in rows if r["all_pass_qm_lane"] == "pass")
    rc_fail_profiles = sum(1 for r in rows if int(r["rc_fail_count"]) > 0)

    report_lines = [
        "# QM-Stage-1 Prereg Report (v1)",
        "",
        f"- mode: `{args.mode}`",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- profiles: `{n}`",
        f"- g17_pass: `{g17_pass}/{n}`",
        f"- g18_pass: `{g18_pass}/{n}`",
        f"- g19_pass: `{g19_pass}/{n}`",
        f"- g20_pass: `{g20_pass}/{n}`",
        f"- all_pass_qm_lane: `{lane_pass}/{n}`",
        f"- rc_fail_profiles: `{rc_fail_profiles}`",
        "",
        "## Notes",
        "",
        "- QM lane remains separated from GR official decision policy.",
        "- No gate formula or threshold edits were applied.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "mode": args.mode,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "datasets": datasets,
        "seed_start": args.seed_start if args.mode == "prereg" else DEFAULT_SEED_START,
        "seed_end": args.seed_end if args.mode == "prereg" else DEFAULT_SEED_START,
        "profiles": n,
        "strict_prereg": bool(args.strict_prereg),
        "runner": "run_qm_stage1_prereg_v1.py",
        "notes": [
            "Runs G17..G20 via run_qm_lane_check_v1.py per dataset/seed profile.",
            "QM lane is separated from GR official pass/fail decisions.",
        ],
    }
    manifest_json = out_dir / "prereg_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run-log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")

    if args.strict_exit and (lane_pass != n or rc_fail_profiles > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
