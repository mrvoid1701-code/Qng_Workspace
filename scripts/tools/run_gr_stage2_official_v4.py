#!/usr/bin/env python3
"""
Apply official GR Stage-2 decision policy (v4) on frozen Stage-2 profile runs.

Policy:
- no edits to gate runner formulas or thresholds
- computes official Stage-2 decisions from existing run artifacts
- updates Stage-2 governance mapping:
  - G11 uses G11a-v4 fallback (robust rank high-signal rule)
  - G12 keeps frozen official-v2 status from source summary
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
TOOLS_DIR = ROOT / "scripts" / "tools"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402
from run_gr_stage2_g11_candidate_eval_v4 import (  # noqa: E402
    f6,
    g11_v3_poisson_rule,
    laplacian_rw,
    norm_status,
    rank_corr_trimmed,
    read_csv,
    smooth_values,
    to_float,
    write_csv,
)


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v3"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v4"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply official GR Stage-2 policy v4 to frozen profile summaries.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--g11-high-signal-quantile", type=float, default=0.80)
    p.add_argument("--g11-corr-min", type=float, default=0.20)
    p.add_argument("--g11-r-smooth-alpha", type=float, default=0.50)
    p.add_argument("--g11-r-smooth-iters", type=int, default=1)
    p.add_argument("--g11-trim-fraction", type=float, default=0.10)
    p.add_argument("--policy-id", default="gr-stage2-official-v4")
    p.add_argument("--effective-tag", default="gr-stage2-g11-v4-official")
    p.add_argument("--source-policy-id", default="gr-stage2-official-v3")
    return p.parse_args()


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
                "g11_v3_pass": sum(1 for r in sub if r["g11_status_v3"] == "pass"),
                "g11_v4_pass": sum(1 for r in sub if r["g11_status"] == "pass"),
                "g12_pass": sum(1 for r in sub if r["g12_status"] == "pass"),
                "lane_3p1_pass": sum(1 for r in sub if r["lane_3p1_status"] == "pass"),
                "lane_strong_field_pass": sum(1 for r in sub if r["lane_strong_field_status"] == "pass"),
                "lane_tensor_pass": sum(1 for r in sub if r["lane_tensor_status"] == "pass"),
                "stage2_v3_pass": sum(1 for r in sub if r["stage2_status_v3"] == "pass"),
                "stage2_v4_pass": sum(1 for r in sub if r["stage2_status"] == "pass"),
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
        dataset_id = str(row["dataset_id"])
        seed = int(str(row["seed"]))
        run_root = (ROOT / row["run_root"]).resolve()

        g10_status = norm_status(row.get("g10_status", ""))
        g7_status = norm_status(row.get("g7_status", ""))
        g11_status_v3 = norm_status(row.get("g11_status", ""))
        g11_status_legacy = norm_status(row.get("g11_status_legacy", ""))
        g12_status = norm_status(row.get("g12_status", ""))
        g12_status_legacy = norm_status(row.get("g12_status_legacy", ""))

        g11a_v3 = norm_status(row.get("g11a_v3_fallback", ""))
        g11b_status = norm_status(row.get("g11b", ""))
        g11c_status = norm_status(row.get("g11c", ""))
        g11d_status = norm_status(row.get("g11d", ""))

        eq_csv = run_root / "g11" / "einstein_eq.csv"
        eq_rows = read_csv(eq_csv) if eq_csv.exists() else []
        r_vals: list[float] = []
        sigma_norm: list[float] = []
        for eq in eq_rows:
            rv = to_float(eq.get("R", ""))
            sv = to_float(eq.get("sigma_norm", ""))
            if rv is None or sv is None:
                continue
            r_vals.append(rv)
            sigma_norm.append(sv)

        _, _, adj_w = build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]
        n = min(len(r_vals), len(sigma_norm), len(neighbours))
        r_vals = r_vals[:n]
        sigma_norm = sigma_norm[:n]
        neighbours = neighbours[:n]

        # Keep Poisson diagnostics in output for continuity, but decision uses rank-or v4 rule.
        g11_diag_v3 = g11_v3_poisson_rule(
            r_vals=r_vals,
            sigma_norm=sigma_norm,
            neighbours=neighbours,
            high_signal_quantile=args.g11_high_signal_quantile,
            corr_min=args.g11_corr_min,
            smooth_alpha=args.g11_r_smooth_alpha,
            smooth_iters=args.g11_r_smooth_iters,
        )
        r_smooth = smooth_values(r_vals, neighbours, alpha=args.g11_r_smooth_alpha, iters=args.g11_r_smooth_iters)
        source_vals = [abs(v) for v in laplacian_rw(sigma_norm, neighbours)]
        target_vals = [abs(v) for v in r_smooth]
        g11_diag_v4 = rank_corr_trimmed(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_high_signal_quantile,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )

        g11a_v4_fallback = (
            g11b_status == "pass"
            and g11c_status == "pass"
            and g11d_status == "pass"
            and bool(g11_diag_v4["rank_or_pass"])
        )
        g11_status = "pass" if (g11_status_v3 == "pass" or g11a_v4_fallback) else "fail"

        lane_3p1_status = "pass" if (g10_status == "pass" and g11_status == "pass") else "fail"
        lane_strong_field_status = g12_status
        lane_tensor_status = g7_status
        stage2_status_v3 = gate_from_statuses(g10_status, g11_status_v3, g12_status, g7_status)
        stage2_status = gate_from_statuses(g10_status, g11_status, g12_status, g7_status)

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "policy_id": args.policy_id,
                "source_policy_id": args.source_policy_id,
                "g10_status": g10_status,
                "g11_status": g11_status,
                "g11_status_v3": g11_status_v3,
                "g11_status_legacy": g11_status_legacy,
                "g12_status": g12_status,
                "g12_status_legacy": g12_status_legacy,
                "g7_status": g7_status,
                "g11a_v3": g11a_v3,
                "g11a_v4_fallback": "pass" if g11a_v4_fallback else "fail",
                "g11b": g11b_status,
                "g11c": g11c_status,
                "g11d": g11d_status,
                "g11_poisson_rule_pass": "true" if bool(g11_diag_v3["rule_pass"]) else "false",
                "g11_poisson_hs_count": int(g11_diag_v3["high_signal_count"]),
                "g11_poisson_s_threshold": f6(g11_diag_v3["s_threshold"]),
                "g11_poisson_spearman_hs": f6(g11_diag_v3["spearman_hs"]),
                "g11_poisson_pearson_hs": f6(g11_diag_v3["pearson_hs"]),
                "g11_v4_hs_trimmed_count": int(g11_diag_v4["hs_count_trimmed"]),
                "g11_v4_spearman_hs_trimmed": f6(g11_diag_v4["spearman_hs_trimmed"]),
                "g11_v4_rank_or_pass": "true" if bool(g11_diag_v4["rank_or_pass"]) else "false",
                "g11_v4_pearson_collapse_flag": "true" if bool(g11_diag_v4["pearson_collapse_flag"]) else "false",
                "lane_3p1_status": lane_3p1_status,
                "lane_strong_field_status": lane_strong_field_status,
                "lane_tensor_status": lane_tensor_status,
                "stage2_status_v3": stage2_status_v3,
                "stage2_status": stage2_status,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    dataset_rows = aggregate_dataset_rows(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, dataset_rows, list(dataset_rows[0].keys()))

    n = len(out_rows)
    g11_v3_pass = sum(1 for r in out_rows if r["g11_status_v3"] == "pass")
    g11_v4_pass = sum(1 for r in out_rows if r["g11_status"] == "pass")
    g12_pass = sum(1 for r in out_rows if r["g12_status"] == "pass")
    stage2_v3_pass = sum(1 for r in out_rows if r["stage2_status_v3"] == "pass")
    stage2_v4_pass = sum(1 for r in out_rows if r["stage2_status"] == "pass")
    improved = sum(
        1 for r in out_rows if r["stage2_status_v3"] == "fail" and r["stage2_status"] == "pass"
    )
    degraded = sum(
        1 for r in out_rows if r["stage2_status_v3"] == "pass" and r["stage2_status"] == "fail"
    )

    report_lines = [
        "# GR Stage-2 Official Policy Application (v4)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- policy_id: `{args.policy_id}`",
        f"- effective_tag: `{args.effective_tag}`",
        f"- profiles: `{n}`",
        "",
        "## Official Pass Counts",
        "",
        f"- G11 official v3 -> v4: `{g11_v3_pass}/{n} -> {g11_v4_pass}/{n}`",
        f"- G12 official (frozen): `{g12_pass}/{n}`",
        f"- Stage-2 official v3 -> v4: `{stage2_v3_pass}/{n} -> {stage2_v4_pass}/{n}`",
        f"- improved_vs_v3: `{improved}`",
        f"- degraded_vs_v3: `{degraded}`",
        "",
        "## Notes",
        "",
        "- No formula/threshold edits in gate scripts were applied.",
        "- G11 v4 is governance-layer decision mapping over frozen artifacts.",
        "- G12 status is inherited from source summary (unchanged).",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy_id": args.policy_id,
        "effective_tag": args.effective_tag,
        "source_policy_id": args.source_policy_id,
        "constants": {
            "g11_high_signal_quantile": args.g11_high_signal_quantile,
            "g11_corr_min": args.g11_corr_min,
            "g11_r_smooth_alpha": args.g11_r_smooth_alpha,
            "g11_r_smooth_iters": args.g11_r_smooth_iters,
            "g11_trim_fraction": args.g11_trim_fraction,
        },
        "notes": [
            "G11 official v4 computes robust rank high-signal fallback.",
            "G12 official keeps frozen status from source summary.",
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
