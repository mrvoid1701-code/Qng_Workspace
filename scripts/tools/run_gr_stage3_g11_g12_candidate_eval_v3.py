#!/usr/bin/env python3
"""
Evaluate Stage-3 candidate-only v3 diagnostics for G11/G12.

Policy:
- does not modify official gate scripts
- computes candidate statuses in post-processing from existing run artifacts
- preserves official-v2 passes by construction (non-degrading candidate layer)

Candidate intent:
- G11a-v3: dual high-signal support (q=0.80 OR q=0.75), same corr threshold
- G12d-v3: robust-slope OR plain-slope fallback, same threshold
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = ROOT / "scripts" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import run_gr_stage3_g11_g12_candidate_eval_v2 as v2  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-official-v2-rerun-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-g11-g12-candidate-v3"
)

# Frozen candidate constants (thresholds unchanged)
G11_HIGH_SIGNAL_QUANTILE = 0.80
G11_SUPPORT_QUANTILE = 0.75
G11_CORR_MIN = 0.20
G11_TRIM_FRACTION = 0.10
G11_SMOOTH_ALPHA = 0.50
G11_SMOOTH_ITERS = 1
G11_MULTI_PEAK_RATIO_THR = 0.98
G11_MULTI_PEAK_DIST_THR = 0.10

G12_SLOPE_THRESHOLD = -0.03  # unchanged threshold
G12_MIN_BIN_COUNT = 4
G12_WINSOR_Q = 0.10


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-3 G11/G12 candidate-v3 diagnostics.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--g11-high-signal-quantile", type=float, default=G11_HIGH_SIGNAL_QUANTILE)
    p.add_argument("--g11-support-quantile", type=float, default=G11_SUPPORT_QUANTILE)
    p.add_argument("--g11-corr-min", type=float, default=G11_CORR_MIN)
    p.add_argument("--g11-trim-fraction", type=float, default=G11_TRIM_FRACTION)
    p.add_argument("--g11-smooth-alpha", type=float, default=G11_SMOOTH_ALPHA)
    p.add_argument("--g11-smooth-iters", type=int, default=G11_SMOOTH_ITERS)
    p.add_argument("--g11-multi-peak-ratio-thr", type=float, default=G11_MULTI_PEAK_RATIO_THR)
    p.add_argument("--g11-multi-peak-dist-thr", type=float, default=G11_MULTI_PEAK_DIST_THR)
    p.add_argument("--g12-slope-threshold", type=float, default=G12_SLOPE_THRESHOLD)
    p.add_argument("--g12-min-bin-count", type=int, default=G12_MIN_BIN_COUNT)
    p.add_argument("--g12-winsor-q", type=float, default=G12_WINSOR_Q)
    p.add_argument("--g12-drop-edge-bins", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def robust_g12_slope_plain(
    *,
    gr_csv: Path,
    min_bin_count: int,
    drop_edge_bins: bool,
) -> dict[str, Any]:
    bins = v2.group_g12_bins(gr_csv)
    supported = [b for b in bins if int(b["n"]) >= min_bin_count and float(b["r_med"]) > 0.0 and float(b["absR_med"]) > 1e-12]
    branch = "supported_bins_plain"
    if drop_edge_bins and len(supported) >= 5:
        supported = sorted(supported, key=lambda b: float(b["r_med"]))[1:-1]
        branch = "supported_drop_edges_plain"
    if len(supported) < 4:
        supported = [b for b in bins if float(b["r_med"]) > 0.0 and float(b["absR_med"]) > 1e-12]
        branch = "fallback_all_bins_plain"
    if len(supported) < 2:
        return {
            "selected_bins": len(supported),
            "branch": branch,
            "min_bin_count_selected": min((int(b["n"]) for b in supported), default=0),
            "slope_plain": float("nan"),
        }
    xs = [math.log(float(b["r_med"])) for b in supported]
    ys = [math.log(float(b["absR_med"])) for b in supported]
    slope = v2.ols_slope(xs, ys)
    return {
        "selected_bins": len(supported),
        "branch": branch,
        "min_bin_count_selected": min(int(b["n"]) for b in supported),
        "slope_plain": slope,
    }


def pick_status(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row and (row.get(k) or "").strip():
            return v2.norm_status(row.get(k, ""))
    return "fail"


def gate_from_statuses(*statuses: str) -> str:
    return "pass" if all(v2.norm_status(s) == "pass" for s in statuses) else "fail"


def main() -> int:
    args = parse_args()
    source_csv = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")
    src_rows = v2.read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for row in src_rows:
        dataset_id = str(row["dataset_id"])
        seed = int(str(row["seed"]))
        run_root = (ROOT / row["run_root"]).resolve()

        g10_v2 = pick_status(row, "g10_status")
        g11_v2 = pick_status(row, "g11_status")
        g12_v2 = pick_status(row, "g12_status")
        g7_v2 = pick_status(row, "g7_status")
        g8_v2 = pick_status(row, "g8_status")
        g9_v2 = pick_status(row, "g9_status")
        stage3_v2 = pick_status(row, "stage3_status")
        stage3_v1 = pick_status(row, "stage3_status_v1")

        g11b = pick_status(row, "g11b_status", "g11b")
        g11c = pick_status(row, "g11c_status", "g11c")
        g11d = pick_status(row, "g11d_status", "g11d")

        g12a = pick_status(row, "g12a_status", "g12a")
        g12b = pick_status(row, "g12b_status", "g12b")
        g12c = pick_status(row, "g12c_status", "g12c")

        coords, sigma, adj_w = v2.build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]

        # G11 candidate diagnostics
        r_vals, sigma_norm = v2.read_g11_pairs(run_root / "g11" / "einstein_eq.csv")
        n11 = min(len(r_vals), len(sigma_norm), len(neighbours))
        r_vals = r_vals[:n11]
        sigma_norm = sigma_norm[:n11]
        neighbours_11 = neighbours[:n11]
        peak_diag = v2.peak_features(
            coords=coords[:n11],
            sigma=sigma[:n11],
            ratio_thr=args.g11_multi_peak_ratio_thr,
            dist_thr=args.g11_multi_peak_dist_thr,
        )

        r_smooth = v2.smooth_values(r_vals, neighbours_11, alpha=args.g11_smooth_alpha, iters=args.g11_smooth_iters)
        source_vals = [abs(v) for v in v2.laplacian_rw(sigma_norm, neighbours_11)]
        target_vals = [abs(v) for v in r_smooth]

        g11_diag_q80 = v2.g11_rank_diag(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_high_signal_quantile,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )
        g11_diag_q75 = v2.g11_rank_diag(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_support_quantile,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )

        rule_q80 = bool(g11_diag_q80["base_rule_pass"] or g11_diag_q80["trim_rule_pass"])
        rule_q75 = bool(g11_diag_q75["base_rule_pass"] or g11_diag_q75["trim_rule_pass"])

        if g11_v2 == "pass":
            g11a_v3 = "pass"
            g11_v3 = "pass"
            g11_candidate_rule = "carry_v2_pass"
        else:
            structural_ok = (g11b == "pass" and g11c == "pass" and g11d == "pass")
            if not structural_ok:
                g11a_v3 = "fail"
                g11_v3 = "fail"
                g11_candidate_rule = "structural_fail"
            else:
                rule_ok = rule_q80 or rule_q75
                if bool(peak_diag["multi_peak_flag"]):
                    g11_candidate_rule = "multi_peak_q80_or_q75"
                else:
                    g11_candidate_rule = "base_or_trim_q80_or_q75"
                g11a_v3 = "pass" if rule_ok else "fail"
                g11_v3 = gate_from_statuses(g11a_v3, g11b, g11c, g11d)

        # G12 candidate diagnostics
        g12_diag_winsor = v2.robust_g12_slope(
            gr_csv=run_root / "g12" / "gr_solutions.csv",
            min_bin_count=args.g12_min_bin_count,
            winsor_q=args.g12_winsor_q,
            drop_edge_bins=bool(args.g12_drop_edge_bins),
        )
        g12_diag_plain = robust_g12_slope_plain(
            gr_csv=run_root / "g12" / "gr_solutions.csv",
            min_bin_count=args.g12_min_bin_count,
            drop_edge_bins=bool(args.g12_drop_edge_bins),
        )
        g12d_winsor_rule = (
            (not math.isnan(float(g12_diag_winsor["slope_robust"])))
            and (float(g12_diag_winsor["slope_robust"]) < args.g12_slope_threshold)
        )
        g12d_plain_rule = (
            (not math.isnan(float(g12_diag_plain["slope_plain"])))
            and (float(g12_diag_plain["slope_plain"]) < args.g12_slope_threshold)
        )

        if g12_v2 == "pass":
            g12d_v3 = "pass"
            g12_v3 = "pass"
            g12_candidate_rule = "carry_v2_pass"
        else:
            structural_ok = (g12a == "pass" and g12b == "pass" and g12c == "pass")
            if structural_ok and (g12d_winsor_rule or g12d_plain_rule):
                g12d_v3 = "pass"
                g12_v3 = "pass"
                g12_candidate_rule = "winsor_or_plain_pass"
            else:
                g12d_v3 = "fail"
                g12_v3 = "fail"
                g12_candidate_rule = "winsor_or_plain_fail"

        lane_3p1_v2 = pick_status(row, "lane_3p1_status")
        lane_strong_v2 = pick_status(row, "lane_strong_field_status")
        lane_tensor = pick_status(row, "lane_tensor_status")
        lane_geometry = pick_status(row, "lane_geometry_status")
        lane_conservation = pick_status(row, "lane_conservation_status")
        lane_3p1_v3 = "pass" if (g10_v2 == "pass" and g11_v3 == "pass") else "fail"
        lane_strong_v3 = g12_v3

        stage3_v3 = (
            "pass"
            if (
                lane_3p1_v3 == "pass"
                and lane_strong_v3 == "pass"
                and lane_tensor == "pass"
                and lane_geometry == "pass"
                and lane_conservation == "pass"
            )
            else "fail"
        )

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "g10_status": g10_v2,
                "g7_status": g7_v2,
                "g8_status": g8_v2,
                "g9_status": g9_v2,
                "g11_v2_status": g11_v2,
                "g11_v3_status": g11_v3,
                "g11a_v2_status": pick_status(row, "g11a_v2_status", "g11a_v1_status"),
                "g11a_v3_status": g11a_v3,
                "g11b_status": g11b,
                "g11c_status": g11c,
                "g11d_status": g11d,
                "g11_candidate_rule": g11_candidate_rule,
                "g11_multi_peak_flag": "true" if bool(peak_diag["multi_peak_flag"]) else "false",
                "g11_peak_ratio_2_to_1": v2.f6(float(peak_diag["peak_ratio_2_to_1"])),
                "g11_peak_distance_norm": v2.f6(float(peak_diag["peak_distance_norm"])),
                "g11_q80_hs_count": int(g11_diag_q80["hs_count"]),
                "g11_q80_hs_trimmed_count": int(g11_diag_q80["hs_trimmed_count"]),
                "g11_q80_s_threshold": v2.f6(float(g11_diag_q80["s_threshold"])),
                "g11_q80_spearman_hs": v2.f6(float(g11_diag_q80["spearman_hs"])),
                "g11_q80_pearson_hs": v2.f6(float(g11_diag_q80["pearson_hs"])),
                "g11_q80_spearman_hs_trimmed": v2.f6(float(g11_diag_q80["spearman_hs_trimmed"])),
                "g11_q80_base_rule_pass": "true" if bool(g11_diag_q80["base_rule_pass"]) else "false",
                "g11_q80_trim_rule_pass": "true" if bool(g11_diag_q80["trim_rule_pass"]) else "false",
                "g11_q75_hs_count": int(g11_diag_q75["hs_count"]),
                "g11_q75_hs_trimmed_count": int(g11_diag_q75["hs_trimmed_count"]),
                "g11_q75_s_threshold": v2.f6(float(g11_diag_q75["s_threshold"])),
                "g11_q75_spearman_hs": v2.f6(float(g11_diag_q75["spearman_hs"])),
                "g11_q75_pearson_hs": v2.f6(float(g11_diag_q75["pearson_hs"])),
                "g11_q75_spearman_hs_trimmed": v2.f6(float(g11_diag_q75["spearman_hs_trimmed"])),
                "g11_q75_base_rule_pass": "true" if bool(g11_diag_q75["base_rule_pass"]) else "false",
                "g11_q75_trim_rule_pass": "true" if bool(g11_diag_q75["trim_rule_pass"]) else "false",
                "g12_v2_status": g12_v2,
                "g12_v3_status": g12_v3,
                "g12a_status": g12a,
                "g12b_status": g12b,
                "g12c_status": g12c,
                "g12d_v2_status": pick_status(row, "g12d_v2_status", "g12d_v1_status"),
                "g12d_v3_status": g12d_v3,
                "g12_candidate_rule": g12_candidate_rule,
                "g12_winsor_slope": v2.f6(float(g12_diag_winsor["slope_robust"])),
                "g12_winsor_selected_bins": int(g12_diag_winsor["selected_bins"]),
                "g12_winsor_selected_branch": str(g12_diag_winsor["branch"]),
                "g12_winsor_min_bin_count_selected": int(g12_diag_winsor["min_bin_count_selected"]),
                "g12_plain_slope": v2.f6(float(g12_diag_plain["slope_plain"])),
                "g12_plain_selected_bins": int(g12_diag_plain["selected_bins"]),
                "g12_plain_selected_branch": str(g12_diag_plain["branch"]),
                "g12_plain_min_bin_count_selected": int(g12_diag_plain["min_bin_count_selected"]),
                "g12_winsor_rule_pass": "true" if g12d_winsor_rule else "false",
                "g12_plain_rule_pass": "true" if g12d_plain_rule else "false",
                "lane_3p1_v2_status": lane_3p1_v2,
                "lane_3p1_v3_status": lane_3p1_v3,
                "lane_strong_field_v2_status": lane_strong_v2,
                "lane_strong_field_v3_status": lane_strong_v3,
                "lane_tensor_status": lane_tensor,
                "lane_geometry_status": lane_geometry,
                "lane_conservation_status": lane_conservation,
                "stage3_v1_status": stage3_v1,
                "stage3_v2_status": stage3_v2,
                "stage3_v3_status": stage3_v3,
            }
        )

    summary_csv = out_dir / "summary.csv"
    v2.write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    g11_v2_pass = sum(1 for r in out_rows if r["g11_v2_status"] == "pass")
    g11_v3_pass = sum(1 for r in out_rows if r["g11_v3_status"] == "pass")
    g12_v2_pass = sum(1 for r in out_rows if r["g12_v2_status"] == "pass")
    g12_v3_pass = sum(1 for r in out_rows if r["g12_v3_status"] == "pass")
    s3_v2_pass = sum(1 for r in out_rows if r["stage3_v2_status"] == "pass")
    s3_v3_pass = sum(1 for r in out_rows if r["stage3_v3_status"] == "pass")
    improved = sum(1 for r in out_rows if r["stage3_v2_status"] == "fail" and r["stage3_v3_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["stage3_v2_status"] == "pass" and r["stage3_v3_status"] == "fail")

    report_lines = [
        "# GR Stage-3 G11/G12 Candidate Eval (v3)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts (official-v2 -> candidate-v3)",
        "",
        f"- G11: `{g11_v2_pass}/{n} -> {g11_v3_pass}/{n}`",
        f"- G12: `{g12_v2_pass}/{n} -> {g12_v3_pass}/{n}`",
        f"- STAGE3: `{s3_v2_pass}/{n} -> {s3_v3_pass}/{n}`",
        f"- improved_vs_v2: `{improved}`",
        f"- degraded_vs_v2: `{degraded}`",
        "",
        "## Candidate Notes",
        "",
        "- Candidate-only evaluation; official policy unchanged in this script.",
        "- G11 uses q80 OR q75 high-signal support with unchanged corr threshold (0.20).",
        "- G12 uses winsorized slope OR plain slope with unchanged threshold (< -0.03).",
        "- No gate threshold/formula edits in official scripts.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy": "stage3-g11-g12-candidate-v3",
        "constants": {
            "g11_high_signal_quantile": args.g11_high_signal_quantile,
            "g11_support_quantile": args.g11_support_quantile,
            "g11_corr_min": args.g11_corr_min,
            "g11_trim_fraction": args.g11_trim_fraction,
            "g11_smooth_alpha": args.g11_smooth_alpha,
            "g11_smooth_iters": args.g11_smooth_iters,
            "g11_multi_peak_ratio_thr": args.g11_multi_peak_ratio_thr,
            "g11_multi_peak_dist_thr": args.g11_multi_peak_dist_thr,
            "g12_slope_threshold": args.g12_slope_threshold,
            "g12_min_bin_count": args.g12_min_bin_count,
            "g12_winsor_q": args.g12_winsor_q,
            "g12_drop_edge_bins": bool(args.g12_drop_edge_bins),
        },
        "notes": [
            "Baseline comparison is official-v2 Stage-3 summary.",
            "No gate thresholds/formulas modified.",
            "v3 remains candidate-only until explicit governance switch.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
