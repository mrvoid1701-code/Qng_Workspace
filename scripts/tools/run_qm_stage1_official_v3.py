#!/usr/bin/env python3
"""
Apply official QM Stage-1 decision policy (G17-v2 + G18d-v2) on frozen summaries.

Policy:
- no edits to gate runner formulas or thresholds
- computes official QM lane decisions from existing candidate summaries
- official mapping:
  - G17 official status is inherited (already frozen via prior official-v2 governance)
  - G18 official uses candidate-v2 decision status
  - G19/G20 remain inherited from source summary
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
    / "qm-g18-candidate-v2"
    / "primary_ds002_003_006_s3401_3600"
    / "summary.csv"
)
DEFAULT_REFERENCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-stage1-official-v2"
    / "primary_ds002_003_006_s3401_3600"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-stage1-official-v3"
    / "primary_ds002_003_006_s3401_3600"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply official QM Stage-1 policy v3 to frozen profile summaries.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--reference-summary-csv", default=str(DEFAULT_REFERENCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--policy-id", default="qm-stage1-official-v3")
    p.add_argument("--effective-tag", default="qm-stage1-g18-v2-official")
    p.add_argument("--source-policy-id", default="qm-g18-candidate-v2-hybrid-local-ds")
    p.add_argument("--reference-policy-id", default="qm-stage1-official-v2")
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


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


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
                "g17_official_pass": sum(1 for r in sub if r["g17_status"] == "pass"),
                "g18_legacy_pass": sum(1 for r in sub if r["g18_status_legacy"] == "pass"),
                "g18_official_pass": sum(1 for r in sub if r["g18_status"] == "pass"),
                "qm_lane_legacy_pass": sum(1 for r in sub if r["all_pass_qm_lane_legacy"] == "pass"),
                "qm_lane_official_pass": sum(1 for r in sub if r["all_pass_qm_lane"] == "pass"),
                "improved_g18": sum(
                    1 for r in sub if r["g18_status_legacy"] == "fail" and r["g18_status"] == "pass"
                ),
                "degraded_g18": sum(
                    1 for r in sub if r["g18_status_legacy"] == "pass" and r["g18_status"] == "fail"
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
    ref_csv = Path(args.reference_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    ref_map: dict[str, dict[str, str]] = {}
    if ref_csv.exists():
        for rr in read_csv(ref_csv):
            try:
                ds = str(rr.get("dataset_id", "")).strip()
                seed = int(str(rr.get("seed", "0")))
            except Exception:
                continue
            ref_map[key_of(ds, seed)] = rr

    out_rows: list[dict[str, Any]] = []
    for row in src_rows:
        ds = str(row.get("dataset_id", "")).strip()
        seed = int(str(row.get("seed", "0")))
        k = key_of(ds, seed)
        ref = ref_map.get(k, {})

        g17_status = norm_status(row.get("g17_status", ref.get("g17_status", "")))
        g18_legacy = norm_status(row.get("g18_status_v1", ""))
        g18_status = norm_status(row.get("g18_status_v2", ""))
        g19_status = norm_status(row.get("g19_status", ref.get("g19_status", "")))
        g20_status = norm_status(row.get("g20_status", ref.get("g20_status", "")))

        lane_legacy = norm_status(row.get("all_pass_qm_lane_v1", ""))
        lane_official = norm_status(row.get("all_pass_qm_lane_v2", ""))

        out_rows.append(
            {
                "dataset_id": ds,
                "seed": seed,
                "run_root": row.get("run_root", ref.get("run_root", "")),
                "policy_id": args.policy_id,
                "source_policy_id": args.source_policy_id,
                "reference_policy_id": args.reference_policy_id,
                "g17_status": g17_status,
                "g18_status": g18_status,
                "g19_status": g19_status,
                "g20_status": g20_status,
                "all_pass_qm_lane": lane_official,
                "g17_status_legacy": norm_status(ref.get("g17_status_legacy", ref.get("g17_status", ""))),
                "g18_status_legacy": g18_legacy,
                "all_pass_qm_lane_legacy": lane_legacy,
                "g17a_status_v1": norm_status(ref.get("g17a_status_v1", "")),
                "g17a_status_v2": norm_status(ref.get("g17a_status_v2", "")),
                "g17a_v2_rule": ref.get("g17a_v2_rule", ""),
                "g17b_status": norm_status(ref.get("g17b_status", "")),
                "g17c_status": norm_status(ref.get("g17c_status", "")),
                "g17d_status": norm_status(ref.get("g17d_status", "")),
                "g18a_status": norm_status(row.get("g18a_status", "")),
                "g18b_status": norm_status(row.get("g18b_status", "")),
                "g18c_status": norm_status(row.get("g18c_status", "")),
                "g18d_status_v1": norm_status(row.get("g18d_status_v1", "")),
                "g18d_status_v2": norm_status(row.get("g18d_status_v2", "")),
                "g18d_v2_rule": row.get("g18d_v2_rule", ""),
                "multi_peak_mixing": str(row.get("multi_peak_mixing", ref.get("multi_peak_mixing", ""))),
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = aggregate_dataset_rows(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    g17_official_pass = sum(1 for r in out_rows if r["g17_status"] == "pass")
    g18_legacy_pass = sum(1 for r in out_rows if r["g18_status_legacy"] == "pass")
    g18_official_pass = sum(1 for r in out_rows if r["g18_status"] == "pass")
    lane_legacy_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "pass")
    lane_official_pass = sum(1 for r in out_rows if r["all_pass_qm_lane"] == "pass")
    improved_g18 = sum(1 for r in out_rows if r["g18_status_legacy"] == "fail" and r["g18_status"] == "pass")
    degraded_g18 = sum(1 for r in out_rows if r["g18_status_legacy"] == "pass" and r["g18_status"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "fail" and r["all_pass_qm_lane"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_legacy"] == "pass" and r["all_pass_qm_lane"] == "fail"
    )

    report_lines = [
        "# QM Stage-1 Official Policy Application (v3)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- reference_summary_csv: `{ref_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Official Pass Counts",
        "",
        f"- G17 official (inherited): `{g17_official_pass}/{n}`",
        f"- G18 legacy -> official-v3: `{g18_legacy_pass}/{n} -> {g18_official_pass}/{n}`",
        f"- QM lane legacy -> official-v3: `{lane_legacy_pass}/{n} -> {lane_official_pass}/{n}`",
        f"- improved_g18: `{improved_g18}`",
        f"- degraded_g18: `{degraded_g18}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- No formula/threshold edits in gate scripts were applied.",
        "- This is a governance-layer mapping over frozen QM profile runs.",
        "- G17 remains inherited from prior official governance output.",
        "- G18 official status follows candidate-v2 decision outputs.",
        "- G19/G20 statuses are inherited from source summary.",
        "- G18-v1 remains retained as legacy diagnostic status in output columns.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "reference_summary_csv": ref_csv.as_posix(),
        "policy_id": args.policy_id,
        "effective_tag": args.effective_tag,
        "source_policy_id": args.source_policy_id,
        "reference_policy_id": args.reference_policy_id,
        "notes": [
            "QM Stage-1 official v3 uses G18 candidate-v2 decision mapping.",
            "G17 remains inherited from official-v2 governance summaries.",
            "G19/G20 statuses are inherited unchanged from source summary.",
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
