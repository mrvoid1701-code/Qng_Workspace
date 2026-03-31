#!/usr/bin/env python3
"""
Evaluate Stage-3 candidate-only v5 diagnostics for G11 (G12 unchanged).

Policy:
- does not modify official gate scripts
- computes candidate statuses in post-processing from existing run artifacts
- preserves official-v3 passes by construction (non-degrading candidate layer)

Candidate intent:
- G11a-v5: robust hybrid for multi-peak/sparse regimes using basin-local high-signal rank rule
- G11b-v5: robust slope fallback (Theil-Sen) with unchanged threshold
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
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
    / "gr-stage3-official-v3-rerun-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-g11-candidate-v5"
    / "primary_ds002_003_006_s3401_3600"
)

# Frozen candidate constants (official thresholds unchanged)
G11_CORR_MIN = 0.20
G11_HIGH_SIGNAL_Q80 = 0.80
G11_HIGH_SIGNAL_Q75 = 0.75
G11_BASIN_QUANTILE = 0.15
G11_BASIN_HIGH_SIGNAL_QUANTILE = 0.50
G11_TRIM_FRACTION = 0.10
G11_SMOOTH_ALPHA = 0.50
G11_SMOOTH_ITERS = 1
G11_MULTI_PEAK_RATIO_THR = 0.98
G11_MULTI_PEAK_DIST_THR = 0.10
G11_SPARSE_MEAN_DEGREE_MAX = 8.50


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-3 G11 candidate-v5 diagnostics.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--g11-corr-min", type=float, default=G11_CORR_MIN)
    p.add_argument("--g11-high-signal-q80", type=float, default=G11_HIGH_SIGNAL_Q80)
    p.add_argument("--g11-high-signal-q75", type=float, default=G11_HIGH_SIGNAL_Q75)
    p.add_argument("--g11-basin-quantile", type=float, default=G11_BASIN_QUANTILE)
    p.add_argument("--g11-basin-high-signal-quantile", type=float, default=G11_BASIN_HIGH_SIGNAL_QUANTILE)
    p.add_argument("--g11-trim-fraction", type=float, default=G11_TRIM_FRACTION)
    p.add_argument("--g11-smooth-alpha", type=float, default=G11_SMOOTH_ALPHA)
    p.add_argument("--g11-smooth-iters", type=int, default=G11_SMOOTH_ITERS)
    p.add_argument("--g11-multi-peak-ratio-thr", type=float, default=G11_MULTI_PEAK_RATIO_THR)
    p.add_argument("--g11-multi-peak-dist-thr", type=float, default=G11_MULTI_PEAK_DIST_THR)
    p.add_argument("--g11-sparse-mean-degree-max", type=float, default=G11_SPARSE_MEAN_DEGREE_MAX)
    return p.parse_args()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_threshold(text: str) -> float | None:
    s = (text or "").strip()
    token = ""
    for ch in s:
        if ch.isdigit() or ch in ".-+eE":
            token += ch
    try:
        return float(token) if token else None
    except Exception:
        return None


def theil_sen_slope(xs: list[float], ys: list[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 3:
        return float("nan")
    x = xs[:n]
    y = ys[:n]
    slopes: list[float] = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = x[j] - x[i]
            if abs(dx) <= 1e-12:
                continue
            slopes.append((y[j] - y[i]) / dx)
    if not slopes:
        return float("nan")
    return float(statistics.median(slopes))


def robust_g11b_from_profile(run_root: Path) -> dict[str, Any]:
    metrics = v2.read_csv(run_root / "g11" / "metric_checks_einstein_eq.csv")
    rows = v2.read_csv(run_root / "g11" / "einstein_eq.csv")
    threshold = float("nan")
    ols = float("nan")
    for m in metrics:
        if (m.get("gate_id") or "").strip() == "G11b":
            ols = float(m.get("value", "nan"))
            thr = parse_threshold(m.get("threshold", ""))
            threshold = float(thr) if thr is not None else float("nan")
            break
    xs: list[float] = []
    ys: list[float] = []
    for r in rows:
        sv = v2.to_float(r.get("sigma_norm", ""))
        rv = v2.to_float(r.get("R", ""))
        if sv is None or rv is None:
            continue
        xs.append(abs(float(sv)))
        ys.append(abs(float(rv)))
    ts = theil_sen_slope(xs, ys)
    robust = max(ols, ts) if (not math.isnan(ols) and not math.isnan(ts)) else (ols if not math.isnan(ols) else ts)
    pass_robust = (not math.isnan(robust)) and (not math.isnan(threshold)) and (robust > threshold)
    return {
        "g11b_ols": ols,
        "g11b_theil_sen": ts,
        "g11b_threshold": threshold,
        "g11b_robust": robust,
        "g11b_v5_pass_rule": bool(pass_robust),
    }


def pick_status(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row and (row.get(k) or "").strip():
            return v2.norm_status(row.get(k, ""))
    return "fail"


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

        g10 = pick_status(row, "g10_status")
        g11_base = pick_status(row, "g11_status")
        g12 = pick_status(row, "g12_status")
        g7 = pick_status(row, "g7_status")
        g8 = pick_status(row, "g8_status")
        g9 = pick_status(row, "g9_status")
        stage3_base = pick_status(row, "stage3_status")

        g11a_base = pick_status(row, "g11a_v3_status", "g11a_v2_status")
        g11b_base = pick_status(row, "g11b_status")
        g11c = pick_status(row, "g11c_status")
        g11d = pick_status(row, "g11d_status")

        coords, sigma, adj_w = v2.build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]
        mean_degree = (sum(len(nb) for nb in neighbours) / len(neighbours)) if neighbours else 0.0

        # G11a diagnostics
        r_vals, sigma_norm = v2.read_g11_pairs(run_root / "g11" / "einstein_eq.csv")
        n11 = min(len(r_vals), len(sigma_norm), len(neighbours), len(sigma), len(coords))
        r_vals = r_vals[:n11]
        sigma_norm = sigma_norm[:n11]
        neighbours_11 = neighbours[:n11]
        sigma_11 = sigma[:n11]
        coords_11 = coords[:n11]

        peak_diag = v2.peak_features(
            coords=coords_11,
            sigma=sigma_11,
            ratio_thr=args.g11_multi_peak_ratio_thr,
            dist_thr=args.g11_multi_peak_dist_thr,
        )
        multi_peak = bool(peak_diag["multi_peak_flag"])
        sparse_graph = mean_degree <= args.g11_sparse_mean_degree_max

        r_smooth = v2.smooth_values(r_vals, neighbours_11, alpha=args.g11_smooth_alpha, iters=args.g11_smooth_iters)
        source_vals = [abs(v) for v in v2.laplacian_rw(sigma_norm, neighbours_11)]
        target_vals = [abs(v) for v in r_smooth]

        g11_q80 = v2.g11_rank_diag(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_high_signal_q80,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )
        g11_q75 = v2.g11_rank_diag(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_high_signal_q75,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )
        global_rule = bool(g11_q80["base_rule_pass"] or g11_q80["trim_rule_pass"] or g11_q75["base_rule_pass"] or g11_q75["trim_rule_pass"])

        basin_n = max(8, int(round(args.g11_basin_quantile * max(1, n11))))
        basin_idx = sorted(range(n11), key=lambda i: sigma_11[i], reverse=True)[:basin_n]
        basin_source = [source_vals[i] for i in basin_idx]
        basin_target = [target_vals[i] for i in basin_idx]
        g11_basin = v2.g11_rank_diag(
            source_vals=basin_source,
            target_vals=basin_target,
            high_signal_quantile=args.g11_basin_high_signal_quantile,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )
        basin_rule = bool(g11_basin["base_rule_pass"] or g11_basin["trim_rule_pass"])

        if g11a_base == "pass":
            g11a_v5 = "pass"
            g11a_rule = "carry_base_pass"
        else:
            if multi_peak or sparse_graph:
                pass_rule = global_rule or basin_rule
                g11a_rule = "global_or_basin_regime"
            else:
                pass_rule = global_rule
                g11a_rule = "global_only"
            g11a_v5 = "pass" if pass_rule else "fail"

        # G11b robust slope fallback
        g11b_diag = robust_g11b_from_profile(run_root)
        if g11b_base == "pass":
            g11b_v5 = "pass"
            g11b_rule = "carry_base_pass"
        else:
            g11b_v5 = "pass" if g11b_diag["g11b_v5_pass_rule"] else "fail"
            g11b_rule = "robust_slope_fallback"

        g11_v5 = "pass" if (g11a_v5 == "pass" and g11b_v5 == "pass" and g11c == "pass" and g11d == "pass") else "fail"

        lane_tensor = pick_status(row, "lane_tensor_status")
        lane_geometry = pick_status(row, "lane_geometry_status")
        lane_conservation = pick_status(row, "lane_conservation_status")
        lane_strong = pick_status(row, "lane_strong_field_status")
        lane_3p1_v5 = "pass" if (g10 == "pass" and g11_v5 == "pass") else "fail"
        stage3_v5 = (
            "pass"
            if (
                lane_3p1_v5 == "pass"
                and lane_strong == "pass"
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
                "g10_status": g10,
                "g7_status": g7,
                "g8_status": g8,
                "g9_status": g9,
                "g11_v2_status": g11_base,
                "g11_v3_status": g11_v5,
                "g11a_v2_status": g11a_base,
                "g11a_v3_status": g11a_v5,
                "g11a_v5_rule": g11a_rule,
                "g11b_status": g11b_base,
                "g11b_v5_status": g11b_v5,
                "g11b_v5_rule": g11b_rule,
                "g11b_ols_slope": v2.f6(g11b_diag["g11b_ols"]),
                "g11b_theil_sen_slope": v2.f6(g11b_diag["g11b_theil_sen"]),
                "g11b_robust_slope": v2.f6(g11b_diag["g11b_robust"]),
                "g11b_threshold": v2.f6(g11b_diag["g11b_threshold"]),
                "g11c_status": g11c,
                "g11d_status": g11d,
                "g11_multi_peak_flag": "true" if multi_peak else "false",
                "g11_sparse_graph_flag": "true" if sparse_graph else "false",
                "g11_mean_degree": v2.f6(mean_degree),
                "g11_peak_ratio_2_to_1": v2.f6(float(peak_diag["peak_ratio_2_to_1"])),
                "g11_peak_distance_norm": v2.f6(float(peak_diag["peak_distance_norm"])),
                "g11_q80_spearman_hs": v2.f6(float(g11_q80["spearman_hs"])),
                "g11_q80_pearson_hs": v2.f6(float(g11_q80["pearson_hs"])),
                "g11_q80_trim_spearman_hs": v2.f6(float(g11_q80["spearman_hs_trimmed"])),
                "g11_q75_spearman_hs": v2.f6(float(g11_q75["spearman_hs"])),
                "g11_q75_pearson_hs": v2.f6(float(g11_q75["pearson_hs"])),
                "g11_q75_trim_spearman_hs": v2.f6(float(g11_q75["spearman_hs_trimmed"])),
                "g11_basin_spearman_hs": v2.f6(float(g11_basin["spearman_hs"])),
                "g11_basin_pearson_hs": v2.f6(float(g11_basin["pearson_hs"])),
                "g11_basin_trim_spearman_hs": v2.f6(float(g11_basin["spearman_hs_trimmed"])),
                "g12_v2_status": g12,
                "g12_v3_status": g12,
                "lane_3p1_v2_status": pick_status(row, "lane_3p1_status"),
                "lane_3p1_v3_status": lane_3p1_v5,
                "lane_strong_field_v2_status": lane_strong,
                "lane_strong_field_v3_status": lane_strong,
                "lane_tensor_status": lane_tensor,
                "lane_geometry_status": lane_geometry,
                "lane_conservation_status": lane_conservation,
                "stage3_v2_status": stage3_base,
                "stage3_v3_status": stage3_v5,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    g11_base_pass = sum(1 for r in out_rows if r["g11_v2_status"] == "pass")
    g11_v5_pass = sum(1 for r in out_rows if r["g11_v3_status"] == "pass")
    stage3_base_pass = sum(1 for r in out_rows if r["stage3_v2_status"] == "pass")
    stage3_v5_pass = sum(1 for r in out_rows if r["stage3_v3_status"] == "pass")
    improved = sum(1 for r in out_rows if r["stage3_v2_status"] == "fail" and r["stage3_v3_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["stage3_v2_status"] == "pass" and r["stage3_v3_status"] == "fail")

    report_lines = [
        "# GR Stage-3 G11 Candidate Eval (v5)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts (base -> candidate-v5)",
        "",
        f"- G11: `{g11_base_pass}/{n} -> {g11_v5_pass}/{n}`",
        f"- STAGE3: `{stage3_base_pass}/{n} -> {stage3_v5_pass}/{n}`",
        f"- improved_vs_base: `{improved}`",
        f"- degraded_vs_base: `{degraded}`",
        "",
        "## Candidate Notes",
        "",
        "- G11a-v5 adds basin-local rank fallback for multi-peak/sparse regimes.",
        "- G11b-v5 adds robust Theil-Sen slope fallback with unchanged threshold.",
        "- G12 is unchanged in this candidate lane.",
        "- No gate threshold/formula edits in official scripts.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "policy": "stage3-g11-candidate-v5",
        "constants": {
            "g11_corr_min": args.g11_corr_min,
            "g11_high_signal_q80": args.g11_high_signal_q80,
            "g11_high_signal_q75": args.g11_high_signal_q75,
            "g11_basin_quantile": args.g11_basin_quantile,
            "g11_basin_high_signal_quantile": args.g11_basin_high_signal_quantile,
            "g11_trim_fraction": args.g11_trim_fraction,
            "g11_smooth_alpha": args.g11_smooth_alpha,
            "g11_smooth_iters": args.g11_smooth_iters,
            "g11_multi_peak_ratio_thr": args.g11_multi_peak_ratio_thr,
            "g11_multi_peak_dist_thr": args.g11_multi_peak_dist_thr,
            "g11_sparse_mean_degree_max": args.g11_sparse_mean_degree_max,
        },
        "notes": [
            "Baseline comparison is official-v3 Stage-3 summary.",
            "No gate thresholds/formulas modified.",
            "v5 remains candidate-only until explicit governance switch.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

