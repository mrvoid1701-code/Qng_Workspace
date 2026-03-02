#!/usr/bin/env python3
"""
Run QM-GR coupling audit package (v1).

Audit scope:
- execute G20 (semiclassical backreaction) on a profile grid
- verify frozen GR Stage-3 guard remains PASS before and after audit run

No GR thresholds/formulas are changed. This is a stability/audit wrapper.
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
SCRIPTS = ROOT / "scripts"
DEFAULT_DATASETS = ("DS-002", "DS-003", "DS-006")
DEFAULT_SEED_START = 3401
DEFAULT_SEED_END = 3600
DEFAULT_GR_BASELINE = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-regression-baseline-v1"
    / "gr_stage3_baseline_official.json"
)
DEFAULT_GR_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-official-v3-rerun-v1"
    / "summary.csv"
)


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QM-GR coupling audit (v1).")
    p.add_argument("--mode", choices=("smoke", "audit"), default="smoke")
    p.add_argument("--datasets", default=",".join(DEFAULT_DATASETS))
    p.add_argument("--seed-start", type=int, default=DEFAULT_SEED_START)
    p.add_argument("--seed-end", type=int, default=DEFAULT_SEED_END)
    p.add_argument("--out-dir", default="")
    p.add_argument("--gr-baseline-json", default=str(DEFAULT_GR_BASELINE))
    p.add_argument("--gr-summary-csv", default=str(DEFAULT_GR_SUMMARY))
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def read_metric_final_status(path: Path) -> str:
    if not path.exists():
        return "fail"
    rows = read_csv(path)
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
        return root / "qm-gr-coupling-audit-smoke-v1"
    return root / "qm-gr-coupling-audit-v1"


def run_gr_guard(baseline_json: Path, summary_csv: Path, out_dir: Path) -> tuple[int, str, Path]:
    cmd = [
        sys.executable,
        str(TOOLS / "run_gr_stage3_regression_guard_v1.py"),
        "--baseline-json",
        str(baseline_json),
        "--summary-csv",
        str(summary_csv),
        "--out-dir",
        str(out_dir),
        "--no-strict-exit",
    ]
    rc, tail = run_cmd(cmd, ROOT)
    report_json = out_dir / "regression_report.json"
    if not report_json.exists():
        return rc, "missing_report", report_json
    report = json.loads(report_json.read_text(encoding="utf-8"))
    return rc, str(report.get("decision", "FAIL")), report_json


def dataset_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g20_pass": sum(1 for r in sub if r["g20_status"] == "pass"),
                "g20_rc_fail_profiles": sum(1 for r in sub if int(r["g20_rc"]) != 0),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    profiles = make_profiles(args)
    out_dir = Path(args.out_dir).resolve() if args.out_dir.strip() else default_out_dir(args.mode)
    out_dir.mkdir(parents=True, exist_ok=True)

    gr_baseline = Path(args.gr_baseline_json).resolve()
    gr_summary = Path(args.gr_summary_csv).resolve()
    if not gr_baseline.exists():
        raise FileNotFoundError(f"gr baseline missing: {gr_baseline}")
    if not gr_summary.exists():
        raise FileNotFoundError(f"gr summary missing: {gr_summary}")

    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 72)
    log(f"QM-GR coupling audit v1 | mode={args.mode} | profiles={len(profiles)}")
    log(f"out_dir={out_dir}")
    log("=" * 72)

    pre_guard_dir = out_dir / "gr_guard_pre"
    pre_rc, pre_decision, _ = run_gr_guard(gr_baseline, gr_summary, pre_guard_dir)
    log(f"[guard-pre] rc={pre_rc} decision={pre_decision}")

    rows: list[dict[str, Any]] = []
    run_root = out_dir / "runs"
    for idx, p in enumerate(profiles, start=1):
        tag = f"{p.dataset_id.lower()}_seed{p.seed}"
        profile_root = run_root / tag / "g20"
        cmd = [
            sys.executable,
            str(SCRIPTS / "run_qng_semiclassical_v1.py"),
            "--dataset-id",
            p.dataset_id,
            "--seed",
            str(p.seed),
            "--out-dir",
            str(profile_root),
        ]
        rc, tail = run_cmd(cmd, ROOT)
        status = read_metric_final_status(profile_root / "metric_checks_semi.csv")
        rows.append(
            {
                "dataset_id": p.dataset_id,
                "seed": p.seed,
                "run_root": profile_root.resolve().relative_to(ROOT.resolve()).as_posix(),
                "g20_status": status,
                "g20_rc": rc,
            }
        )
        log(f"[{idx}/{len(profiles)}] {tag} - g20: rc={rc} status={status}")
        if rc != 0 and tail:
            for line in tail.splitlines():
                log(f"    {line}")

    post_guard_dir = out_dir / "gr_guard_post"
    post_rc, post_decision, _ = run_gr_guard(gr_baseline, gr_summary, post_guard_dir)
    log(f"[guard-post] rc={post_rc} decision={post_decision}")

    rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, list(rows[0].keys()))

    ds_rows = dataset_summary(rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(rows)
    g20_pass = sum(1 for r in rows if r["g20_status"] == "pass")
    g20_rc_fail = sum(1 for r in rows if int(r["g20_rc"]) != 0)
    guard_unchanged = (pre_decision == "PASS" and post_decision == "PASS")

    report_lines = [
        "# QM-GR Coupling Audit Report (v1)",
        "",
        f"- mode: `{args.mode}`",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- profiles: `{n}`",
        f"- g20_pass: `{g20_pass}/{n}`",
        f"- g20_rc_fail_profiles: `{g20_rc_fail}`",
        f"- gr_guard_pre: `{pre_decision}` (rc={pre_rc})",
        f"- gr_guard_post: `{post_decision}` (rc={post_rc})",
        f"- gr_guard_unchanged_pass: `{'true' if guard_unchanged else 'false'}`",
        "",
        "## Notes",
        "",
        "- Audit checks GR guard stability while running semiclassical G20 profiles.",
        "- This runner does not change GR summaries or gate thresholds.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "mode": args.mode,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "datasets": parse_csv_list(args.datasets),
        "seed_start": args.seed_start if args.mode == "audit" else DEFAULT_SEED_START,
        "seed_end": args.seed_end if args.mode == "audit" else DEFAULT_SEED_START,
        "profiles": n,
        "gr_baseline_json": gr_baseline.as_posix(),
        "gr_summary_csv": gr_summary.as_posix(),
        "gr_guard_pre": pre_decision,
        "gr_guard_post": post_decision,
        "notes": [
            "Runs G20 only for coupling audit readout.",
            "Verifies Stage-3 GR baseline guard remains PASS pre/post audit.",
        ],
    }
    manifest_json = out_dir / "audit_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run-log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")

    if args.strict_exit and (not guard_unchanged or g20_rc_fail > 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
