#!/usr/bin/env python3
"""
GR regression guard for QNG gates G10..G16 (housekeeping only).

Purpose:
- Freeze a reproducible GR baseline profile set.
- Re-run the same profiles and detect regressions in gate statuses and key metrics.

Scope:
- G10, G11, G12, G13, G14, G15, G16
- stdlib only
- no threshold/formula changes inside scientific gate scripts

Outputs:
- observed_summary.csv
- regression_report.json
- regression_report.md
- run-log.txt
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
import time
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE_JSON = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-regression-baseline-v1"
    / "gr_baseline_grid20.json"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-regression-baseline-v1"
    / "latest_check"
)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="QNG GR regression guard (G10..G16) vs frozen baseline."
    )
    parser.add_argument("--baseline-json", default=str(DEFAULT_BASELINE_JSON))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Skip gate execution and compare using --observed-summary.",
    )
    parser.add_argument(
        "--observed-summary",
        default="",
        help="Optional observed summary CSV path (used with --skip-run).",
    )
    parser.add_argument(
        "--plots",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Forward plot flag to gate scripts where supported (default: no plots).",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt_phi(x: Any) -> str:
    return f"{float(x):.2f}"


def profile_key(dataset_id: str, seed: Any, phi_scale: Any) -> str:
    return f"{dataset_id}|{int(seed)}|{fmt_phi(phi_scale)}"


def get_metric(rows: list[dict[str, str]], gate_id: str, metric: str) -> str:
    for row in rows:
        if row.get("gate_id") == gate_id and row.get("metric") == metric:
            return row.get("value", "").strip()
    return ""


def get_status(rows: list[dict[str, str]], gate_id: str) -> str:
    for row in rows:
        if row.get("gate_id") == gate_id:
            return row.get("status", "").strip().lower()
    return ""


def get_final_status(rows: list[dict[str, str]]) -> str:
    return get_status(rows, "FINAL")


def as_repo_relative(path: Path) -> str:
    abs_path = path.resolve()
    try:
        return str(abs_path.relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return abs_path.as_posix()


def supports_flag(
    script_path: Path,
    flag: str,
    cache: dict[tuple[str, str], bool],
) -> bool:
    key = (str(script_path), flag)
    if key in cache:
        return cache[key]
    try:
        proc = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=20,
            cwd=ROOT,
            env={**os.environ, **{"PYTHONUTF8": "1"}},
        )
        txt = (proc.stdout or "") + (proc.stderr or "")
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
    plots: bool,
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
    if supports_flag(script_path, "--plots", flag_cache) and not plots:
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


def collect_observed_for_profile(
    profile: dict[str, Any],
    *,
    runs_root: Path,
    plots: bool,
    flag_cache: dict[tuple[str, str], bool],
    log: list[str],
) -> dict[str, str]:
    dataset_id = str(profile["dataset_id"])
    seed = int(profile["seed"])
    phi_scale = float(profile["phi_scale"])
    phi_tag = fmt_phi(phi_scale).replace(".", "p")
    combo_tag = f"{dataset_id.lower()}_seed{seed}_phi{phi_tag}"
    combo_root = runs_root / combo_tag
    combo_root.mkdir(parents=True, exist_ok=True)

    def add(msg: str) -> None:
        print(msg)
        log.append(msg)

    add(f"profile={combo_tag}")
    gate_rows: dict[str, list[dict[str, str]]] = {}
    gate_status: dict[str, str] = {}

    for gate in GATE_SPECS:
        gate_dir = combo_root / gate.gate_id.lower()
        gate_dir.mkdir(parents=True, exist_ok=True)
        rc, elapsed, tail = run_gate(
            gate,
            dataset_id=dataset_id,
            seed=seed,
            phi_scale=phi_scale,
            out_dir=gate_dir,
            plots=plots,
            flag_cache=flag_cache,
        )
        rows = read_csv(gate_dir / gate.metric_checks_file)
        status = get_final_status(rows)
        if not status:
            status = "pass" if rc == 0 else "fail"
        gate_rows[gate.gate_id] = rows
        gate_status[gate.gate_id] = status
        add(f"  {gate.gate_id}: rc={rc} status={status} elapsed={elapsed:.2f}s")
        if rc != 0 and tail:
            add("    tail:")
            for line in tail.splitlines():
                add(f"      {line}")

    g13_rows = gate_rows.get("G13", [])
    g14_rows = gate_rows.get("G14", [])
    g15_rows = gate_rows.get("G15", [])
    all_pass = all(gate_status.get(f"G{i}", "") == "pass" for i in range(10, 17))

    return {
        "dataset_id": dataset_id,
        "seed": str(seed),
        "phi_scale": fmt_phi(phi_scale),
        "g10_status": gate_status.get("G10", ""),
        "g11_status": gate_status.get("G11", ""),
        "g12_status": gate_status.get("G12", ""),
        "g13_status": gate_status.get("G13", ""),
        "g14_status": gate_status.get("G14", ""),
        "g15_status": gate_status.get("G15", ""),
        "g16_status": gate_status.get("G16", ""),
        "g15b_v2_status": get_status(g15_rows, "G15b-v2"),
        "all_pass": "pass" if all_pass else "fail",
        "g15a_gamma_dev": get_metric(g15_rows, "G15a", "gamma_dev"),
        "g15d_ep_ratio": get_metric(g15_rows, "G15d", "EP_ratio"),
        "g15b_shapiro_ratio": get_metric(g15_rows, "G15b", "shapiro_ratio"),
        "g15b_v2_shapiro_ratio": get_metric(g15_rows, "G15b-v2", "shapiro_ratio_v2"),
        "g13b_e_cov_drift": get_metric(g13_rows, "G13b", "E_cov_drift"),
        "g14b_e_cov_drift": get_metric(g14_rows, "G14b", "E_cov_drift"),
        "g13c_speed_reduction": get_metric(g13_rows, "G13c", "speed_reduction"),
        "run_root": as_repo_relative(combo_root),
    }


def compare_rows(
    expected_rows: list[dict[str, Any]],
    observed_rows: list[dict[str, Any]],
    *,
    status_fields: list[str],
    numeric_fields: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    details: list[dict[str, Any]] = []
    success = True
    obs_map = {
        profile_key(r["dataset_id"], r["seed"], r["phi_scale"]): r
        for r in observed_rows
    }

    for exp in expected_rows:
        key = profile_key(exp["dataset_id"], exp["seed"], exp["phi_scale"])
        obs = obs_map.get(key)
        if obs is None:
            success = False
            details.append(
                {
                    "profile": key,
                    "field": "__row__",
                    "kind": "presence",
                    "status": "fail",
                    "expected": "present",
                    "observed": "missing",
                }
            )
            continue

        for field in status_fields:
            exp_val = str(exp.get(field, "")).strip().lower()
            obs_val = str(obs.get(field, "")).strip().lower()
            ok = exp_val == obs_val
            if not ok:
                success = False
            details.append(
                {
                    "profile": key,
                    "field": field,
                    "kind": "status",
                    "status": "pass" if ok else "fail",
                    "expected": exp_val,
                    "observed": obs_val,
                }
            )

        for field, cfg in numeric_fields.items():
            abs_tol = float(cfg.get("abs_tol", 0.0))
            exp_raw = str(exp.get(field, "")).strip()
            obs_raw = str(obs.get(field, "")).strip()
            ok = True
            abs_diff: float | None = None
            try:
                exp_val = float(exp_raw)
                obs_val = float(obs_raw)
                abs_diff = abs(obs_val - exp_val)
                ok = abs_diff <= abs_tol
            except Exception:
                ok = False
            if not ok:
                success = False
            details.append(
                {
                    "profile": key,
                    "field": field,
                    "kind": "numeric",
                    "status": "pass" if ok else "fail",
                    "expected": exp_raw,
                    "observed": obs_raw,
                    "abs_tol": abs_tol,
                    "abs_diff": abs_diff,
                }
            )

    expected_keys = {
        profile_key(r["dataset_id"], r["seed"], r["phi_scale"]) for r in expected_rows
    }
    for key in sorted(obs_map):
        if key not in expected_keys:
            success = False
            details.append(
                {
                    "profile": key,
                    "field": "__row__",
                    "kind": "presence",
                    "status": "fail",
                    "expected": "not present",
                    "observed": "unexpected row",
                }
            )

    return details, success


def write_markdown_report(
    path: Path,
    *,
    baseline_id: str,
    baseline_tag: str,
    result_ok: bool,
    details: list[dict[str, Any]],
    observed_rows: list[dict[str, Any]],
) -> None:
    fail_rows = [d for d in details if d["status"] != "pass"]
    lines: list[str] = []
    lines.append("# GR Regression Guard Report")
    lines.append("")
    lines.append(f"- baseline_id: `{baseline_id}`")
    lines.append(f"- baseline_tag: `{baseline_tag}`")
    lines.append(f"- overall: `{'PASS' if result_ok else 'FAIL'}`")
    lines.append(f"- profiles_checked: `{len(observed_rows)}`")
    lines.append(f"- checks_total: `{len(details)}`")
    lines.append(f"- checks_failed: `{len(fail_rows)}`")
    lines.append("")
    if fail_rows:
        lines.append("## Failures")
        lines.append("")
        lines.append("| profile | field | kind | expected | observed |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in fail_rows:
            lines.append(
                f"| {row.get('profile','')} | {row.get('field','')} | {row.get('kind','')} "
                f"| {row.get('expected','')} | {row.get('observed','')} |"
            )
    else:
        lines.append("No regressions detected.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    baseline_path = Path(args.baseline_json).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    run_log: list[str] = []

    if not baseline_path.exists():
        print(f"[error] baseline not found: {baseline_path}")
        return 2

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    profiles = list(baseline.get("profiles", []))
    expected_rows = list(baseline.get("expected_rows", []))
    compare_cfg = dict(baseline.get("compare", {}))
    status_fields = list(compare_cfg.get("status_fields", []))
    numeric_fields = dict(compare_cfg.get("numeric_fields", {}))

    observed_rows: list[dict[str, Any]]
    if args.skip_run:
        if not args.observed_summary:
            print("[error] --skip-run requires --observed-summary.")
            return 2
        observed_rows = read_csv(Path(args.observed_summary).resolve())
    else:
        runs_root = out_dir / "runs"
        runs_root.mkdir(parents=True, exist_ok=True)
        flag_cache: dict[tuple[str, str], bool] = {}
        print("=" * 72)
        print("QNG GR regression guard")
        print(f"baseline={baseline_path}")
        print(f"profiles={len(profiles)}")
        print("=" * 72)
        t0 = time.time()
        observed_rows = []
        for profile in profiles:
            observed_rows.append(
                collect_observed_for_profile(
                    profile,
                    runs_root=runs_root,
                    plots=args.plots,
                    flag_cache=flag_cache,
                    log=run_log,
                )
            )
        elapsed = time.time() - t0
        print("=" * 72)
        print(f"run_elapsed={elapsed:.2f}s")
        print("=" * 72)

    summary_fields = [
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
        "all_pass",
        "g15a_gamma_dev",
        "g15d_ep_ratio",
        "g15b_shapiro_ratio",
        "g15b_v2_shapiro_ratio",
        "g13b_e_cov_drift",
        "g14b_e_cov_drift",
        "g13c_speed_reduction",
        "run_root",
    ]
    observed_summary_path = out_dir / "observed_summary.csv"
    write_csv(observed_summary_path, observed_rows, summary_fields)

    details, result_ok = compare_rows(
        expected_rows,
        observed_rows,
        status_fields=status_fields,
        numeric_fields=numeric_fields,
    )

    report_json = {
        "baseline_id": baseline.get("baseline_id", ""),
        "baseline_tag": baseline.get("effective_tag", ""),
        "baseline_commit": baseline.get("effective_commit", ""),
        "checked_utc": datetime.utcnow().isoformat() + "Z",
        "result": "pass" if result_ok else "fail",
        "observed_summary_csv": str(observed_summary_path),
        "details": details,
    }
    report_json_path = out_dir / "regression_report.json"
    report_json_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    report_md_path = out_dir / "regression_report.md"
    write_markdown_report(
        report_md_path,
        baseline_id=str(baseline.get("baseline_id", "")),
        baseline_tag=str(baseline.get("effective_tag", "")),
        result_ok=result_ok,
        details=details,
        observed_rows=observed_rows,
    )

    run_log_path = out_dir / "run-log.txt"
    run_log_path.write_text("\n".join(run_log) + "\n", encoding="utf-8")

    print(f"observed_summary: {observed_summary_path}")
    print(f"report_json:      {report_json_path}")
    print(f"report_md:        {report_md_path}")
    print(f"result:           {'PASS' if result_ok else 'FAIL'}")
    return 0 if result_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
