#!/usr/bin/env python3
"""
Apply official QM Stage-1 decision policy (G17-v2) on frozen QM summaries.

Policy:
- no edits to gate runner formulas or thresholds
- computes official QM lane decisions from existing candidate-v2 summaries
- official mapping:
  - G17 official uses candidate-v2 decision status
  - G18/G19/G20 stay inherited from source summary
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
    / "qm-g17-candidate-v2"
    / "primary_ds002_003_006_s3401_3600"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-stage1-official-v2"
    / "primary_ds002_003_006_s3401_3600"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply official QM Stage-1 policy v2 to frozen profile summaries.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--policy-id", default="qm-stage1-official-v2")
    p.add_argument("--effective-tag", default="qm-stage1-g17-v2-official")
    p.add_argument("--source-policy-id", default="qm-g17-candidate-v2-hybrid")
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
                "g17_legacy_pass": sum(1 for r in sub if r["g17_status_legacy"] == "pass"),
                "g17_official_pass": sum(1 for r in sub if r["g17_status"] == "pass"),
                "qm_lane_legacy_pass": sum(1 for r in sub if r["all_pass_qm_lane_legacy"] == "pass"),
                "qm_lane_official_pass": sum(1 for r in sub if r["all_pass_qm_lane"] == "pass"),
                "improved_g17": sum(
                    1 for r in sub if r["g17_status_legacy"] == "fail" and r["g17_status"] == "pass"
                ),
                "degraded_g17": sum(
                    1 for r in sub if r["g17_status_legacy"] == "pass" and r["g17_status"] == "fail"
                ),
                "improved_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_legacy"] == "fail" and r["all_pass_qm_lane"] == "pass"
                ),
                "degraded_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_legacy"] == "pass" and r["all_pass_qm_lane"] == "fail"
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
        raise FileNotFoundError(f"source summary not found: {source_csv}")

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for row in src_rows:
        g17_legacy = norm_status(row.get("g17_status_v1", ""))
        g17_official = norm_status(row.get("g17_status_v2", ""))
        g18_status = norm_status(row.get("g18_status", ""))
        g19_status = norm_status(row.get("g19_status", ""))
        g20_status = norm_status(row.get("g20_status", ""))

        lane_legacy = norm_status(row.get("all_pass_qm_lane_v1", ""))
        lane_official = norm_status(row.get("all_pass_qm_lane_v2", ""))

        out_rows.append(
            {
                "dataset_id": row.get("dataset_id", ""),
                "seed": int(str(row.get("seed", "0"))),
                "run_root": row.get("run_root", ""),
                "policy_id": args.policy_id,
                "source_policy_id": args.source_policy_id,
                "g17_status": g17_official,
                "g18_status": g18_status,
                "g19_status": g19_status,
                "g20_status": g20_status,
                "all_pass_qm_lane": lane_official,
                "g17_status_legacy": g17_legacy,
                "all_pass_qm_lane_legacy": lane_legacy,
                "g17a_status_v1": norm_status(row.get("g17a_status_v1", "")),
                "g17a_status_v2": norm_status(row.get("g17a_status_v2", "")),
                "g17a_v2_rule": row.get("g17a_v2_rule", ""),
                "g17b_status": norm_status(row.get("g17b_status", "")),
                "g17c_status": norm_status(row.get("g17c_status", "")),
                "g17d_status": norm_status(row.get("g17d_status", "")),
                "multi_peak_mixing": str(row.get("multi_peak_mixing", "")),
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = aggregate_dataset_rows(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    g17_legacy_pass = sum(1 for r in out_rows if r["g17_status_legacy"] == "pass")
    g17_official_pass = sum(1 for r in out_rows if r["g17_status"] == "pass")
    lane_legacy_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "pass")
    lane_official_pass = sum(1 for r in out_rows if r["all_pass_qm_lane"] == "pass")
    improved_g17 = sum(1 for r in out_rows if r["g17_status_legacy"] == "fail" and r["g17_status"] == "pass")
    degraded_g17 = sum(1 for r in out_rows if r["g17_status_legacy"] == "pass" and r["g17_status"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "fail" and r["all_pass_qm_lane"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "pass" and r["all_pass_qm_lane"] == "fail"
    )

    report_lines = [
        "# QM Stage-1 Official Policy Application (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Official Pass Counts",
        "",
        f"- G17 legacy -> official-v2: `{g17_legacy_pass}/{n} -> {g17_official_pass}/{n}`",
        f"- QM lane legacy -> official-v2: `{lane_legacy_pass}/{n} -> {lane_official_pass}/{n}`",
        f"- improved_g17: `{improved_g17}`",
        f"- degraded_g17: `{degraded_g17}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- No formula/threshold edits in gate scripts were applied.",
        "- This is a governance-layer mapping over frozen QM profile runs.",
        "- G17 official status follows candidate-v2 decision outputs.",
        "- G18/G19/G20 statuses are inherited from source summary.",
        "- G17-v1 remains retained as legacy diagnostic status in output columns.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy_id": args.policy_id,
        "effective_tag": args.effective_tag,
        "source_policy_id": args.source_policy_id,
        "notes": [
            "QM Stage-1 official v2 uses G17 candidate-v2 decision mapping.",
            "G18/G19/G20 statuses are inherited unchanged from source summary.",
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
