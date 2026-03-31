#!/usr/bin/env python3
"""
Apply official stability decision policy v2 on frozen candidate summaries.

Policy:
- no equation or threshold edits
- official energy decision uses candidate-v2 status
- legacy v1 status is preserved for diagnostics
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SOURCE = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "stability-energy-covariant-v2"
    / "primary_s3401"
    / "summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "stability-official-v2"
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
    p = argparse.ArgumentParser(description="Apply official stability-v2 policy mapping.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--policy-id", default="stability-official-v2")
    p.add_argument("--effective-tag", default="stability-energy-v2-official")
    p.add_argument("--source-policy-id", default="stability-energy-covariant-v2")
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


def summarize_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "energy_legacy_pass": sum(1 for r in sub if r["gate_energy_drift_legacy"] == "pass"),
                "energy_official_pass": sum(1 for r in sub if r["gate_energy_drift"] == "pass"),
                "all_legacy_pass": sum(1 for r in sub if r["all_pass_stability_legacy"] == "pass"),
                "all_official_pass": sum(1 for r in sub if r["all_pass_stability"] == "pass"),
                "energy_improved": sum(
                    1 for r in sub if r["gate_energy_drift_legacy"] == "fail" and r["gate_energy_drift"] == "pass"
                ),
                "energy_degraded": sum(
                    1 for r in sub if r["gate_energy_drift_legacy"] == "pass" and r["gate_energy_drift"] == "fail"
                ),
                "all_improved": sum(
                    1
                    for r in sub
                    if r["all_pass_stability_legacy"] == "fail" and r["all_pass_stability"] == "pass"
                ),
                "all_degraded": sum(
                    1
                    for r in sub
                    if r["all_pass_stability_legacy"] == "pass" and r["all_pass_stability"] == "fail"
                ),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    source_csv = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source_csv.exists():
        raise FileNotFoundError(f"source summary missing: {source_csv}")

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for r in src_rows:
        rec = dict(r)
        for g in NON_ENERGY_GATES:
            rec[g] = norm_status(r.get(g, ""))
        rec["gate_energy_drift_legacy"] = norm_status(r.get("gate_energy_drift_v1", r.get("gate_energy_drift", "")))
        rec["gate_energy_drift"] = norm_status(r.get("gate_energy_drift_v2", ""))
        rec["all_pass_stability_legacy"] = norm_status(r.get("all_pass_v1", r.get("all_pass", "")))
        rec["all_pass_stability"] = norm_status(r.get("all_pass_v2", ""))
        rec["policy_id"] = args.policy_id
        rec["source_policy_id"] = args.source_policy_id
        out_rows.append(rec)

    out_rows.sort(key=lambda x: (str(x.get("dataset_id", "")), str(x.get("combo_id", "")), str(x.get("case_id", ""))))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = summarize_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    legacy_energy_pass = sum(1 for r in out_rows if r["gate_energy_drift_legacy"] == "pass")
    official_energy_pass = sum(1 for r in out_rows if r["gate_energy_drift"] == "pass")
    legacy_all_pass = sum(1 for r in out_rows if r["all_pass_stability_legacy"] == "pass")
    official_all_pass = sum(1 for r in out_rows if r["all_pass_stability"] == "pass")
    energy_improved = sum(1 for r in out_rows if r["gate_energy_drift_legacy"] == "fail" and r["gate_energy_drift"] == "pass")
    energy_degraded = sum(1 for r in out_rows if r["gate_energy_drift_legacy"] == "pass" and r["gate_energy_drift"] == "fail")
    all_improved = sum(
        1 for r in out_rows if r["all_pass_stability_legacy"] == "fail" and r["all_pass_stability"] == "pass"
    )
    all_degraded = sum(
        1 for r in out_rows if r["all_pass_stability_legacy"] == "pass" and r["all_pass_stability"] == "fail"
    )

    report_lines = [
        "# Stability Official Policy Apply (v2)",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Mapping Result",
        "",
        f"- energy gate legacy -> official: `{legacy_energy_pass}/{n} -> {official_energy_pass}/{n}`",
        f"- all-pass legacy -> official: `{legacy_all_pass}/{n} -> {official_all_pass}/{n}`",
        f"- energy improved: `{energy_improved}`",
        f"- energy degraded: `{energy_degraded}`",
        f"- all improved: `{all_improved}`",
        f"- all degraded: `{all_degraded}`",
        "",
        "## Notes",
        "",
        "- No equation/threshold edits.",
        "- Official energy decision uses candidate-v2 status.",
        "- Legacy status is retained for diagnostics.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_summary_csv": source_csv.as_posix(),
        "policy_id": args.policy_id,
        "source_policy_id": args.source_policy_id,
        "effective_tag": args.effective_tag,
        "notes": [
            "Official energy gate = candidate-v2 decision status.",
            "Legacy energy gate retained for diagnostics.",
            "No threshold or formula changes.",
        ],
    }
    (out_dir / "official_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv.as_posix()}")
    print(f"dataset_csv: {dataset_csv.as_posix()}")
    print(f"report_md:   {(out_dir / 'report.md').as_posix()}")
    print(f"manifest:    {(out_dir / 'official_manifest.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
