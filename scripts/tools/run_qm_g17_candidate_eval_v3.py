#!/usr/bin/env python3
"""
Run G17 candidate-v3 hybrid evaluation on frozen QM lane summaries.

Policy (diagnostic/governance layer):
- keep G17-v1 unchanged (legacy baseline)
- preserve existing gate formulas/thresholds in runners
- generalize local-gap recovery for all G17a-v1 fail cases (not DS-specific)
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "scripts" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_qm_g17_candidate_eval_v2 as v2  # noqa: E402


DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-g17-candidate-v3"
    / "primary_ds002_003_006_s3401_3600"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G17 candidate-v3 generalized hybrid evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--mix-ratio-threshold", type=float, default=0.90)
    p.add_argument("--mix-distance-threshold", type=float, default=0.25)
    p.add_argument("--basin-quantile", type=float, default=0.15)
    p.add_argument("--local-gap-threshold", type=float, default=0.01)
    p.add_argument("--local-gap-max-modes", type=int, default=12)
    p.add_argument("--local-gap-iters", type=int, default=300)
    return p.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def summarize_by_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g17_v1_pass": sum(1 for r in sub if r["g17_status_v1"] == "pass"),
                "g17_v2_pass": sum(1 for r in sub if r["g17_status_v2"] == "pass"),
                "improved_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass"
                ),
                "degraded_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail"
                ),
                "qm_lane_v1_pass": sum(1 for r in sub if r["all_pass_qm_lane_v1"] == "pass"),
                "qm_lane_v2_pass": sum(1 for r in sub if r["all_pass_qm_lane_v2"] == "pass"),
                "improved_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
                ),
                "degraded_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
                ),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    source_summary = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source_summary.exists():
        raise FileNotFoundError(f"source summary not found: {source_summary}")

    source_rows = v2.read_csv(source_summary)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for srow in source_rows:
        dataset_id = str(srow.get("dataset_id", ""))
        seed = int(str(srow.get("seed", "0")))
        run_root = v2.resolve_run_root(str(srow.get("run_root", "")))
        g17_dir = run_root / "g17"
        mc_csv = g17_dir / "metric_checks_qm.csv"
        if not mc_csv.exists():
            raise FileNotFoundError(f"missing g17 metric file: {mc_csv}")

        base = v2.parse_g17_metric_checks(mc_csv)
        feats = v2.compute_multi_peak_and_local_gap(
            dataset_id=dataset_id,
            seed=seed,
            basin_quantile=args.basin_quantile,
            mix_ratio_threshold=args.mix_ratio_threshold,
            mix_distance_threshold=args.mix_distance_threshold,
            local_gap_max_modes=args.local_gap_max_modes,
            local_gap_iters=args.local_gap_iters,
        )

        g17a_v1 = base["g17a_status_v1"]
        if g17a_v1 == "pass":
            g17a_v2 = "pass"
            g17a_v2_rule = "accept_v1_pass"
        else:
            # v3 generalization: allow local-gap recovery for all fail cases.
            if feats["g17a_gap_local"] > args.local_gap_threshold:
                g17a_v2 = "pass"
                g17a_v2_rule = "local_gap_recovery_generalized"
            else:
                g17a_v2 = "fail"
                g17a_v2_rule = "retain_v1_fail"

        g17_v2 = (
            "pass"
            if g17a_v2 == "pass"
            and base["g17b_status"] == "pass"
            and base["g17c_status"] == "pass"
            and base["g17d_status"] == "pass"
            else "fail"
        )

        g18 = v2.norm_status(srow.get("g18_status", ""))
        g19 = v2.norm_status(srow.get("g19_status", ""))
        g20 = v2.norm_status(srow.get("g20_status", ""))
        lane_v1 = v2.norm_status(srow.get("all_pass_qm_lane", ""))
        lane_v2 = "pass" if (g17_v2 == "pass" and g18 == "pass" and g19 == "pass" and g20 == "pass") else "fail"

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": run_root.resolve().relative_to(ROOT.resolve()).as_posix(),
                "g17_status_v1": base["g17_status_v1"],
                "g17_status_v2": g17_v2,
                "g17a_status_v1": g17a_v1,
                "g17a_status_v2": g17a_v2,
                "g17a_v2_rule": g17a_v2_rule,
                "g17b_status": base["g17b_status"],
                "g17c_status": base["g17c_status"],
                "g17d_status": base["g17d_status"],
                "g17a_gap_global": base["g17a_gap_global"],
                "g17a_gap_local": feats["g17a_gap_local"],
                "sigma_peak2_to_peak1": feats["sigma_peak2_to_peak1"],
                "peak12_distance_norm": feats["peak12_distance_norm"],
                "multi_peak_mixing": feats["multi_peak_mixing"],
                "local_basin_nodes": feats["local_basin_nodes"],
                "g17b_slope": base["g17b_slope"],
                "g17c_e0_per_mode": base["g17c_e0_per_mode"],
                "g17d_heisenberg_dev": base["g17d_heisenberg_dev"],
                "g18_status": g18,
                "g19_status": g19,
                "g20_status": g20,
                "all_pass_qm_lane_v1": lane_v1,
                "all_pass_qm_lane_v2": lane_v2,
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g17_v1_pass = sum(1 for r in out_rows if r["g17_status_v1"] == "pass")
    g17_v2_pass = sum(1 for r in out_rows if r["g17_status_v2"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v2_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v2"] == "pass")
    improved_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass")
    degraded_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
    )

    lines = [
        "# QM G17 Candidate-v3 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G17 v1 -> v3: `{g17_v1_pass}/{n} -> {g17_v2_pass}/{n}`",
        f"- QM lane v1 -> v3: `{lane_v1_pass}/{n} -> {lane_v2_pass}/{n}`",
        f"- improved_g17: `{improved_g17}`",
        f"- degraded_g17: `{degraded_g17}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- Generalized local-gap recovery is applied for all G17a-v1 fail cases.",
        "- No threshold/formula edits in core gate scripts.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g17-candidate-v3-hybrid-generalized",
        "mix_ratio_threshold": args.mix_ratio_threshold,
        "mix_distance_threshold": args.mix_distance_threshold,
        "basin_quantile": args.basin_quantile,
        "local_gap_threshold": args.local_gap_threshold,
        "local_gap_max_modes": args.local_gap_max_modes,
        "local_gap_iters": args.local_gap_iters,
        "notes": [
            "Candidate-only generalized local-gap hardening.",
            "No threshold/formula edits in core gate scripts.",
        ],
    }
    manifest_json = out_dir / "candidate_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

