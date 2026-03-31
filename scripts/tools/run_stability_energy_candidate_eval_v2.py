#!/usr/bin/env python3
"""
Run stability energy-gate candidate-v2 evaluation from frozen v1 summary.

Candidate rule (anti post-hoc, no threshold tuning):
- keep v1 energy pass as pass
- for v1 energy fail, evaluate covariant/Noether-like energy drift against
  the same frozen threshold used by v1 (`energy_rel_max`)
- keep all non-energy gates unchanged
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "stability-energy-covariant-v2"
    / "primary_s3401"
)

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
    p = argparse.ArgumentParser(description="Run stability energy candidate-v2 evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--energy-threshold", type=float, default=0.90)
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--eval-id", default="stability-energy-covariant-v2")
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(str(v).strip())
    except Exception:
        return default


def summarize_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in rows}):
        sub = [r for r in rows if str(r.get("dataset_id", "")) == ds]
        n = len(sub)
        energy_v1_pass = sum(1 for r in sub if r["gate_energy_drift_v1"] == "pass")
        energy_v2_pass = sum(1 for r in sub if r["gate_energy_drift_v2"] == "pass")
        lane_v1_pass = sum(1 for r in sub if r["all_pass_v1"] == "pass")
        lane_v2_pass = sum(1 for r in sub if r["all_pass_v2"] == "pass")
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "energy_v1_pass": energy_v1_pass,
                "energy_v2_pass": energy_v2_pass,
                "energy_improved": sum(
                    1 for r in sub if r["gate_energy_drift_v1"] == "fail" and r["gate_energy_drift_v2"] == "pass"
                ),
                "energy_degraded": sum(
                    1 for r in sub if r["gate_energy_drift_v1"] == "pass" and r["gate_energy_drift_v2"] == "fail"
                ),
                "all_v1_pass": lane_v1_pass,
                "all_v2_pass": lane_v2_pass,
                "all_improved": sum(1 for r in sub if r["all_pass_v1"] == "fail" and r["all_pass_v2"] == "pass"),
                "all_degraded": sum(1 for r in sub if r["all_pass_v1"] == "pass" and r["all_pass_v2"] == "fail"),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    source_csv = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")

    source_rows = read_csv(source_csv)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    strict_ds = set(parse_csv_list(args.strict_datasets))
    if strict_ds:
        source_rows = [r for r in source_rows if str(r.get("dataset_id", "")) in strict_ds]
    if not source_rows:
        raise RuntimeError("no rows after strict dataset filter")

    out_rows: list[dict[str, Any]] = []
    for r in source_rows:
        rec = dict(r)
        gate_energy_v1 = norm_status(r.get("gate_energy_drift", ""))
        noether_rel = to_float(r.get("energy_noether_rel", "nan"), float("nan"))
        if gate_energy_v1 == "pass":
            gate_energy_v2 = "pass"
            path = "keep_v1_pass"
        elif noether_rel <= args.energy_threshold:
            gate_energy_v2 = "pass"
            path = "covariant_pass"
        else:
            gate_energy_v2 = "fail"
            path = "covariant_fail"

        non_energy_status = [norm_status(r.get(g, "")) for g in NON_ENERGY_GATES]
        all_v2 = "pass" if (all(s == "pass" for s in non_energy_status) and gate_energy_v2 == "pass") else "fail"
        all_v1 = norm_status(r.get("all_pass", ""))

        rec["gate_energy_drift_v1"] = gate_energy_v1
        rec["gate_energy_drift_v2"] = gate_energy_v2
        rec["energy_v2_path"] = path
        rec["all_pass_v1"] = all_v1
        rec["all_pass_v2"] = all_v2
        for g in NON_ENERGY_GATES:
            rec[f"{g}_v2"] = norm_status(r.get(g, ""))
        out_rows.append(rec)

    summary_path = out_dir / "summary.csv"
    fieldnames = list(out_rows[0].keys())
    write_csv(summary_path, out_rows, fieldnames)

    ds_rows = summarize_dataset(out_rows)
    dataset_summary_path = out_dir / "dataset_summary.csv"
    write_csv(
        dataset_summary_path,
        ds_rows,
        [
            "dataset_id",
            "n_profiles",
            "energy_v1_pass",
            "energy_v2_pass",
            "energy_improved",
            "energy_degraded",
            "all_v1_pass",
            "all_v2_pass",
            "all_improved",
            "all_degraded",
        ],
    )

    total = len(out_rows)
    energy_v1_pass = sum(1 for r in out_rows if r["gate_energy_drift_v1"] == "pass")
    energy_v2_pass = sum(1 for r in out_rows if r["gate_energy_drift_v2"] == "pass")
    energy_improved = sum(1 for r in out_rows if r["gate_energy_drift_v1"] == "fail" and r["gate_energy_drift_v2"] == "pass")
    energy_degraded = sum(1 for r in out_rows if r["gate_energy_drift_v1"] == "pass" and r["gate_energy_drift_v2"] == "fail")
    all_v1_pass = sum(1 for r in out_rows if r["all_pass_v1"] == "pass")
    all_v2_pass = sum(1 for r in out_rows if r["all_pass_v2"] == "pass")
    all_improved = sum(1 for r in out_rows if r["all_pass_v1"] == "fail" and r["all_pass_v2"] == "pass")
    all_degraded = sum(1 for r in out_rows if r["all_pass_v1"] == "pass" and r["all_pass_v2"] == "fail")

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_summary_csv": source_csv.as_posix(),
        "strict_datasets": sorted(strict_ds),
        "energy_threshold": args.energy_threshold,
        "totals": {
            "n": total,
            "energy_v1_pass": energy_v1_pass,
            "energy_v2_pass": energy_v2_pass,
            "energy_improved": energy_improved,
            "energy_degraded": energy_degraded,
            "all_v1_pass": all_v1_pass,
            "all_v2_pass": all_v2_pass,
            "all_improved": all_improved,
            "all_degraded": all_degraded,
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Energy Candidate-v2 Eval",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- energy_threshold (unchanged): `{args.energy_threshold}`",
        "",
        "## Totals",
        "",
        f"- energy gate: v1 `{energy_v1_pass}/{total}`, v2 `{energy_v2_pass}/{total}`, improved `{energy_improved}`, degraded `{energy_degraded}`",
        f"- all-pass: v1 `{all_v1_pass}/{total}`, v2 `{all_v2_pass}/{total}`, improved `{all_improved}`, degraded `{all_degraded}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"summary_csv:         {summary_path.as_posix()}")
    print(f"dataset_summary_csv: {dataset_summary_path.as_posix()}")
    print(f"report_md:           {(out_dir / 'report.md').as_posix()}")
    print(f"report_json:         {(out_dir / 'report.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
