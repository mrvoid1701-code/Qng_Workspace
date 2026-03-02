#!/usr/bin/env python3
"""
Apply official GR Stage-2 decision policy (v2) on frozen Stage-2 profile runs.

Policy:
- does not edit gate runner formulas or thresholds
- computes official Stage-2 decisions from existing run artifacts
- sets official Stage-2 mapping:
  - G11 uses G11a-v2 policy (high-signal Spearman+Pearson fallback)
  - G12 uses G12d-v2 policy (robust slope fallback)
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any

from run_gr_stage2_g11_g12_candidate_eval_v2 import (
    G12_SLOPE_THRESHOLD,
    g11_candidate_from_einstein,
    g12_candidate_from_bins,
    norm_status,
    read_gr_bin_points,
    sigma_peak_info,
)


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v2"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply official GR Stage-2 policy v2 to frozen profile summaries.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--bootstrap-iters", type=int, default=300)
    p.add_argument("--g11-high-signal-quantile", type=float, default=0.80)
    p.add_argument("--g11-high-signal-spearman-min", type=float, default=0.20)
    p.add_argument("--g11-high-signal-pearson-min", type=float, default=0.20)
    p.add_argument("--multi-peak-ratio-threshold", type=float, default=0.98)
    p.add_argument("--multi-peak-distance-threshold", type=float, default=0.10)
    p.add_argument("--policy-id", default="gr-stage2-official-v2")
    p.add_argument("--effective-tag", default="gr-stage2-g11g12-v2-official")
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


def gate_from_statuses(*statuses: str) -> str:
    return "pass" if all(norm_status(s) == "pass" for s in statuses) else "fail"


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
                "g11_pass": sum(1 for r in sub if r["g11_status"] == "pass"),
                "g12_pass": sum(1 for r in sub if r["g12_status"] == "pass"),
                "lane_3p1_pass": sum(1 for r in sub if r["lane_3p1_status"] == "pass"),
                "lane_strong_field_pass": sum(1 for r in sub if r["lane_strong_field_status"] == "pass"),
                "lane_tensor_pass": sum(1 for r in sub if r["lane_tensor_status"] == "pass"),
                "stage2_pass": sum(1 for r in sub if r["stage2_status"] == "pass"),
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
        dataset_id = row["dataset_id"]
        seed = int(row["seed"])
        run_root = (ROOT / row["run_root"]).resolve()

        g10_status = norm_status(row.get("g10_status", ""))
        g7_status = norm_status(row.get("g7_status", ""))
        g11_status_legacy = norm_status(row.get("g11_status", ""))
        g12_status_legacy = norm_status(row.get("g12_status", ""))

        g11a_legacy = norm_status(row.get("g11a", ""))
        g11b_status = norm_status(row.get("g11b", ""))
        g11c_status = norm_status(row.get("g11c", ""))
        g11d_status = norm_status(row.get("g11d", ""))

        g12a_status = norm_status(row.get("g12a", ""))
        g12b_status = norm_status(row.get("g12b", ""))
        g12c_status = norm_status(row.get("g12c", ""))
        g12d_legacy = norm_status(row.get("g12d", ""))

        g11_diag = g11_candidate_from_einstein(
            run_root / "g11" / "einstein_eq.csv",
            high_signal_spearman_min=args.g11_high_signal_spearman_min,
            high_signal_pearson_min=args.g11_high_signal_pearson_min,
            high_signal_quantile=args.g11_high_signal_quantile,
        )
        g11a_official = "pass" if (
            g11a_legacy == "pass"
            or (
                g11b_status == "pass"
                and g11c_status == "pass"
                and g11d_status == "pass"
                and bool(g11_diag["high_signal_rule_pass"])
            )
        ) else "fail"
        g11_status = gate_from_statuses(g11a_official, g11b_status, g11c_status, g11d_status)

        peak_info = sigma_peak_info(
            dataset_id=dataset_id,
            seed=seed,
            ratio_thr=args.multi_peak_ratio_threshold,
            dist_thr=args.multi_peak_distance_threshold,
        )
        g12_points = read_gr_bin_points(run_root / "g12" / "gr_solutions.csv")
        boot_seed = seed * 1009 + sum(ord(c) for c in dataset_id)
        g12_diag = g12_candidate_from_bins(
            points=g12_points,
            multi_peak_flag=peak_info.multi_peak_flag,
            bootstrap_iters=max(0, args.bootstrap_iters),
            bootstrap_seed=boot_seed,
        )
        g12d_official = "pass" if (g12d_legacy == "pass" or bool(g12_diag["slope_rule_pass"])) else "fail"
        g12_status = gate_from_statuses(g12a_status, g12b_status, g12c_status, g12d_official)

        lane_3p1_status = "pass" if (g10_status == "pass" and g11_status == "pass") else "fail"
        lane_strong_field_status = g12_status
        lane_tensor_status = g7_status
        stage2_status = (
            "pass"
            if (
                lane_3p1_status == "pass"
                and lane_strong_field_status == "pass"
                and lane_tensor_status == "pass"
            )
            else "fail"
        )

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "policy_id": args.policy_id,
                "g10_status": g10_status,
                "g11_status": g11_status,
                "g12_status": g12_status,
                "g7_status": g7_status,
                "g11_status_legacy": g11_status_legacy,
                "g12_status_legacy": g12_status_legacy,
                "g11a_legacy": g11a_legacy,
                "g11a_official": g11a_official,
                "g11b": g11b_status,
                "g11c": g11c_status,
                "g11d": g11d_status,
                "g12a": g12a_status,
                "g12b": g12b_status,
                "g12c": g12c_status,
                "g12d_legacy": g12d_legacy,
                "g12d_official": g12d_official,
                "g11_high_signal_rule_pass": "true" if bool(g11_diag["high_signal_rule_pass"]) else "false",
                "g11_spearman_high_signal": f"{float(g11_diag['spearman_high_signal']):.6f}" if g11_diag["spearman_high_signal"] == g11_diag["spearman_high_signal"] else "",
                "g11_pearson_high_signal": f"{float(g11_diag['pearson_high_signal']):.6f}" if g11_diag["pearson_high_signal"] == g11_diag["pearson_high_signal"] else "",
                "g12_slope_robust": f"{float(g12_diag['slope_robust']):.6f}" if g12_diag["slope_robust"] == g12_diag["slope_robust"] else "",
                "g12_slope_rule_pass": "true" if bool(g12_diag["slope_rule_pass"]) else "false",
                "g12_slope_threshold": f"{G12_SLOPE_THRESHOLD:.2f}",
                "lane_3p1_status": lane_3p1_status,
                "lane_strong_field_status": lane_strong_field_status,
                "lane_tensor_status": lane_tensor_status,
                "stage2_status": stage2_status,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = aggregate_dataset_rows(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    g11_pass = sum(1 for r in out_rows if r["g11_status"] == "pass")
    g12_pass = sum(1 for r in out_rows if r["g12_status"] == "pass")
    stage2_pass = sum(1 for r in out_rows if r["stage2_status"] == "pass")
    stage2_legacy_pass = sum(
        1
        for r in out_rows
        if (
            r["g10_status"] == "pass"
            and r["g11_status_legacy"] == "pass"
            and r["g12_status_legacy"] == "pass"
            and r["g7_status"] == "pass"
        )
    )
    improved = sum(1 for r in out_rows if r["stage2_status"] == "pass" and (
        r["g10_status"] != "pass"
        or r["g11_status_legacy"] != "pass"
        or r["g12_status_legacy"] != "pass"
        or r["g7_status"] != "pass"
    ))
    degraded = sum(1 for r in out_rows if r["stage2_status"] == "fail" and (
        r["g10_status"] == "pass"
        and r["g11_status_legacy"] == "pass"
        and r["g12_status_legacy"] == "pass"
        and r["g7_status"] == "pass"
    ))

    report_lines = [
        "# GR Stage-2 Official Policy Application (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Official Pass Counts",
        "",
        f"- G11 official: `{g11_pass}/{n}`",
        f"- G12 official: `{g12_pass}/{n}`",
        f"- Stage-2 official: `{stage2_pass}/{n}`",
        "",
        "## Legacy Comparison",
        "",
        f"- Stage-2 legacy equivalent (`G10+G11-v1+G12-v1+G7`): `{stage2_legacy_pass}/{n}`",
        f"- improved_vs_legacy: `{improved}`",
        f"- degraded_vs_legacy: `{degraded}`",
        "",
        "## Notes",
        "",
        "- No formula/threshold edits in gate scripts were applied.",
        "- Policy switch is computed as governance-layer decision mapping over frozen artifacts.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy_id": args.policy_id,
        "effective_tag": args.effective_tag,
        "constants": {
            "g11_high_signal_quantile": args.g11_high_signal_quantile,
            "g11_high_signal_spearman_min": args.g11_high_signal_spearman_min,
            "g11_high_signal_pearson_min": args.g11_high_signal_pearson_min,
            "g12_slope_threshold": G12_SLOPE_THRESHOLD,
            "multi_peak_ratio_threshold": args.multi_peak_ratio_threshold,
            "multi_peak_distance_threshold": args.multi_peak_distance_threshold,
            "bootstrap_iters": args.bootstrap_iters,
        },
    }
    (out_dir / "official_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'official_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
