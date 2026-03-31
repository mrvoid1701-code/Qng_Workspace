#!/usr/bin/env python3
"""
Apply official GR Stage-3 decision policy (v2) on frozen Stage-3 profile runs.

Policy:
- no edits to gate runner formulas or thresholds
- computes official Stage-3 decisions from existing candidate-v2 summaries
- updates Stage-3 governance mapping:
  - G11 uses candidate-v2 decision status
  - G12 uses candidate-v2 decision status
  - G7/G8/G9 remain frozen from source summary
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-g11-g12-candidate-v2"
    / "primary_ds002_003_006_s3401_3600"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-official-v2"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply official GR Stage-3 policy v2 to frozen profile summaries.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--policy-id", default="gr-stage3-official-v2")
    p.add_argument("--effective-tag", default="gr-stage3-g11g12-v2-official")
    p.add_argument("--source-policy-id", default="gr-stage3-g11-g12-candidate-v2")
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


def aggregate_dataset_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    datasets = sorted({str(r["dataset_id"]) for r in rows})
    out: list[dict[str, Any]] = []
    for ds in datasets:
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g11_v1_pass": sum(1 for r in sub if r["g11_status_v1"] == "pass"),
                "g11_official_v2_pass": sum(1 for r in sub if r["g11_status"] == "pass"),
                "g12_v1_pass": sum(1 for r in sub if r["g12_status_v1"] == "pass"),
                "g12_official_v2_pass": sum(1 for r in sub if r["g12_status"] == "pass"),
                "stage3_v1_pass": sum(1 for r in sub if r["stage3_status_v1"] == "pass"),
                "stage3_official_v2_pass": sum(1 for r in sub if r["stage3_status"] == "pass"),
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

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for row in src_rows:
        g10_status = norm_status(row.get("g10_status", ""))
        g7_status = norm_status(row.get("g7_status", ""))
        g8_status = norm_status(row.get("g8_status", ""))
        g9_status = norm_status(row.get("g9_status", ""))

        g11_v1 = norm_status(row.get("g11_v1_status", ""))
        g11_v2 = norm_status(row.get("g11_v2_status", ""))
        g12_v1 = norm_status(row.get("g12_v1_status", ""))
        g12_v2 = norm_status(row.get("g12_v2_status", ""))

        lane_3p1_v1 = norm_status(row.get("lane_3p1_v1_status", ""))
        lane_3p1_v2 = norm_status(row.get("lane_3p1_v2_status", ""))
        lane_sf_v1 = norm_status(row.get("lane_strong_field_v1_status", ""))
        lane_sf_v2 = norm_status(row.get("lane_strong_field_v2_status", ""))
        lane_tensor = norm_status(row.get("lane_tensor_status", ""))
        lane_geometry = norm_status(row.get("lane_geometry_status", ""))
        lane_conservation = norm_status(row.get("lane_conservation_status", ""))
        stage3_v1 = norm_status(row.get("stage3_v1_status", ""))
        stage3_v2 = norm_status(row.get("stage3_v2_status", ""))

        out_rows.append(
            {
                "dataset_id": row.get("dataset_id", ""),
                "seed": int(str(row.get("seed", "0"))),
                "run_root": row.get("run_root", ""),
                "policy_id": args.policy_id,
                "source_policy_id": args.source_policy_id,
                "g10_status": g10_status,
                "g11_status": g11_v2,
                "g12_status": g12_v2,
                "g7_status": g7_status,
                "g8_status": g8_status,
                "g9_status": g9_status,
                "g11_status_v1": g11_v1,
                "g12_status_v1": g12_v1,
                "g11a_v1_status": norm_status(row.get("g11a_v1_status", "")),
                "g11a_v2_status": norm_status(row.get("g11a_v2_status", "")),
                "g11b_status": norm_status(row.get("g11b_status", "")),
                "g11c_status": norm_status(row.get("g11c_status", "")),
                "g11d_status": norm_status(row.get("g11d_status", "")),
                "g12a_status": norm_status(row.get("g12a_status", "")),
                "g12b_status": norm_status(row.get("g12b_status", "")),
                "g12c_status": norm_status(row.get("g12c_status", "")),
                "g12d_v1_status": norm_status(row.get("g12d_v1_status", "")),
                "g12d_v2_status": norm_status(row.get("g12d_v2_status", "")),
                "lane_3p1_status": lane_3p1_v2,
                "lane_strong_field_status": lane_sf_v2,
                "lane_tensor_status": lane_tensor,
                "lane_geometry_status": lane_geometry,
                "lane_conservation_status": lane_conservation,
                "lane_3p1_status_v1": lane_3p1_v1,
                "lane_strong_field_status_v1": lane_sf_v1,
                "stage3_status": stage3_v2,
                "stage3_status_v1": stage3_v1,
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = aggregate_dataset_rows(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    g11_v1_pass = sum(1 for r in out_rows if r["g11_status_v1"] == "pass")
    g11_v2_pass = sum(1 for r in out_rows if r["g11_status"] == "pass")
    g12_v1_pass = sum(1 for r in out_rows if r["g12_status_v1"] == "pass")
    g12_v2_pass = sum(1 for r in out_rows if r["g12_status"] == "pass")
    stage3_v1_pass = sum(1 for r in out_rows if r["stage3_status_v1"] == "pass")
    stage3_v2_pass = sum(1 for r in out_rows if r["stage3_status"] == "pass")
    improved = sum(1 for r in out_rows if r["stage3_status_v1"] == "fail" and r["stage3_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["stage3_status_v1"] == "pass" and r["stage3_status"] == "fail")

    report_lines = [
        "# GR Stage-3 Official Policy Application (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Official Pass Counts",
        "",
        f"- G11 v1 -> official-v2: `{g11_v1_pass}/{n} -> {g11_v2_pass}/{n}`",
        f"- G12 v1 -> official-v2: `{g12_v1_pass}/{n} -> {g12_v2_pass}/{n}`",
        f"- Stage-3 v1 -> official-v2: `{stage3_v1_pass}/{n} -> {stage3_v2_pass}/{n}`",
        f"- improved_vs_v1: `{improved}`",
        f"- degraded_vs_v1: `{degraded}`",
        "",
        "## Notes",
        "",
        "- No formula/threshold edits in gate scripts were applied.",
        "- This is a governance-layer mapping over frozen Stage-3 profile runs.",
        "- G11/G12 official status follows candidate-v2 decision outputs.",
        "- G7/G8/G9 statuses are inherited from source summary.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy_id": args.policy_id,
        "effective_tag": args.effective_tag,
        "source_policy_id": args.source_policy_id,
        "notes": [
            "Stage-3 official v2 uses candidate-v2 decision mapping for G11/G12.",
            "G7/G8/G9 statuses are inherited unchanged from source summary.",
            "No gate formulas or thresholds are modified.",
        ],
    }
    (out_dir / "official_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'official_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
