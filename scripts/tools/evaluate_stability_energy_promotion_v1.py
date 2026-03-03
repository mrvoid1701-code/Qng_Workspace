#!/usr/bin/env python3
"""
Evaluate stability energy candidate-v2 promotion checks (anti post-hoc).

Checks:
- no degradation on energy gate pass-cases (v1 pass -> v2 fail)
- non-energy gates unchanged (degraded=0)
- energy uplift on v1 fail-cases (improved > 0)
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-energy-promotion-eval-v1"
NON_ENERGY_GATES = [
    "gate_sigma_bounds",
    "gate_metric_positive",
    "gate_metric_cond",
    "gate_runaway",
    "gate_variational_residual",
    "gate_alpha_drift",
    "gate_no_signalling",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate stability energy candidate-v2 promotion.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="stability-energy-promotion-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-non-energy-stable", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-energy-uplift", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def bool_str(v: bool) -> str:
    return "true" if v else "false"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary csv not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    strict_ds = set(parse_csv_list(args.strict_datasets))
    eval_rows = [r for r in rows if str(r.get("dataset_id", "")) in strict_ds] if strict_ds else rows
    if not eval_rows:
        raise RuntimeError("no rows after dataset filtering")

    n = len(eval_rows)
    energy_v1_pass = sum(1 for r in eval_rows if norm_status(r.get("gate_energy_drift_v1", "")) == "pass")
    energy_v2_pass = sum(1 for r in eval_rows if norm_status(r.get("gate_energy_drift_v2", "")) == "pass")
    energy_improved = sum(
        1
        for r in eval_rows
        if norm_status(r.get("gate_energy_drift_v1", "")) == "fail"
        and norm_status(r.get("gate_energy_drift_v2", "")) == "pass"
    )
    energy_degraded = sum(
        1
        for r in eval_rows
        if norm_status(r.get("gate_energy_drift_v1", "")) == "pass"
        and norm_status(r.get("gate_energy_drift_v2", "")) == "fail"
    )

    all_v1_pass = sum(1 for r in eval_rows if norm_status(r.get("all_pass_v1", "")) == "pass")
    all_v2_pass = sum(1 for r in eval_rows if norm_status(r.get("all_pass_v2", "")) == "pass")
    all_improved = sum(
        1 for r in eval_rows if norm_status(r.get("all_pass_v1", "")) == "fail" and norm_status(r.get("all_pass_v2", "")) == "pass"
    )
    all_degraded = sum(
        1 for r in eval_rows if norm_status(r.get("all_pass_v1", "")) == "pass" and norm_status(r.get("all_pass_v2", "")) == "fail"
    )

    non_energy_degraded: dict[str, int] = {}
    for g in NON_ENERGY_GATES:
        g2 = f"{g}_v2"
        non_energy_degraded[g] = sum(
            1
            for r in eval_rows
            if norm_status(r.get(g, "")) == "pass" and norm_status(r.get(g2, "")) == "fail"
        )
    non_energy_degraded_total = sum(non_energy_degraded.values())

    checks = {
        "zero_degraded_energy": (energy_degraded == 0) if args.require_zero_degraded else True,
        "non_energy_stable": (non_energy_degraded_total == 0) if args.require_non_energy_stable else True,
        "energy_uplift": (energy_improved > 0) if args.require_energy_uplift else True,
    }
    overall = all(checks.values())

    ds_rows: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in eval_rows}):
        sub = [r for r in eval_rows if str(r.get("dataset_id", "")) == ds]
        ds_rows.append(
            {
                "dataset_id": ds,
                "n_profiles": len(sub),
                "energy_v1_pass": sum(1 for r in sub if norm_status(r.get("gate_energy_drift_v1", "")) == "pass"),
                "energy_v2_pass": sum(1 for r in sub if norm_status(r.get("gate_energy_drift_v2", "")) == "pass"),
                "energy_improved": sum(
                    1
                    for r in sub
                    if norm_status(r.get("gate_energy_drift_v1", "")) == "fail"
                    and norm_status(r.get("gate_energy_drift_v2", "")) == "pass"
                ),
                "energy_degraded": sum(
                    1
                    for r in sub
                    if norm_status(r.get("gate_energy_drift_v1", "")) == "pass"
                    and norm_status(r.get("gate_energy_drift_v2", "")) == "fail"
                ),
                "all_v1_pass": sum(1 for r in sub if norm_status(r.get("all_pass_v1", "")) == "pass"),
                "all_v2_pass": sum(1 for r in sub if norm_status(r.get("all_pass_v2", "")) == "pass"),
            }
        )
    write_csv(
        out_dir / "dataset_summary.csv",
        ds_rows,
        ["dataset_id", "n_profiles", "energy_v1_pass", "energy_v2_pass", "energy_improved", "energy_degraded", "all_v1_pass", "all_v2_pass"],
    )

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_summary_csv": summary_csv.as_posix(),
        "strict_datasets": sorted(strict_ds),
        "criteria": {
            "require_zero_degraded": bool(args.require_zero_degraded),
            "require_non_energy_stable": bool(args.require_non_energy_stable),
            "require_energy_uplift": bool(args.require_energy_uplift),
        },
        "totals": {
            "n": n,
            "energy_v1_pass": energy_v1_pass,
            "energy_v2_pass": energy_v2_pass,
            "energy_improved": energy_improved,
            "energy_degraded": energy_degraded,
            "all_v1_pass": all_v1_pass,
            "all_v2_pass": all_v2_pass,
            "all_improved": all_improved,
            "all_degraded": all_degraded,
            "non_energy_degraded_total": non_energy_degraded_total,
            "non_energy_degraded_by_gate": non_energy_degraded,
        },
        "checks": checks,
        "overall_decision": "PASS" if overall else "HOLD",
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Energy Candidate-v2 Promotion Eval",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- source_summary_csv: `{summary_csv.as_posix()}`",
        f"- overall_decision: `{report['overall_decision']}`",
        "",
        "## Totals",
        "",
        f"- energy gate: v1 `{energy_v1_pass}/{n}`, v2 `{energy_v2_pass}/{n}`, improved `{energy_improved}`, degraded `{energy_degraded}`",
        f"- all-pass: v1 `{all_v1_pass}/{n}`, v2 `{all_v2_pass}/{n}`, improved `{all_improved}`, degraded `{all_degraded}`",
        f"- non-energy degraded total: `{non_energy_degraded_total}`",
        "",
        "## Checks",
        "",
        f"- zero_degraded_energy: `{bool_str(checks['zero_degraded_energy'])}`",
        f"- non_energy_stable: `{bool_str(checks['non_energy_stable'])}`",
        f"- energy_uplift: `{bool_str(checks['energy_uplift'])}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {(out_dir / 'dataset_summary.csv').as_posix()}")
    print(f"report_md:           {(out_dir / 'report.md').as_posix()}")
    print(f"report_json:         {(out_dir / 'report.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
