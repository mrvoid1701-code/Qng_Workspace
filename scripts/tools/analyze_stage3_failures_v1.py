#!/usr/bin/env python3
"""
Analyze GR Stage-3 failures (strict fail scope) and build taxonomy outputs.

Scope:
- read Stage-3 prereg summary.csv
- classify only profiles with stage3_status=fail
- compute fail-vs-feature correlations for diagnostics

Policy:
- no gate threshold/formula edits
- reporting/diagnostics only
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
import math
import re
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_gr_solutions_v1 import build_dataset_graph


DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-failure-taxonomy-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze GR Stage-3 failures and feature correlations.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--multi-peak-ratio-thr", type=float, default=0.98)
    p.add_argument("--multi-peak-dist-thr", type=float, default=0.10)
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


def pick(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row and (row.get(k) or "").strip():
            return str(row.get(k, ""))
    return ""


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def f6(v: float | None) -> str:
    if v is None:
        return ""
    if math.isnan(v) or math.isinf(v):
        return ""
    return f"{v:.6f}"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = max(0.0, min(1.0, q)) * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    w = pos - lo
    return xs[lo] * (1.0 - w) + xs[hi] * w


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    return sum((v - m) * (v - m) for v in values) / len(values)


def pearson_corr(xs: list[float], ys: list[float]) -> float | None:
    n = min(len(xs), len(ys))
    if n < 3:
        return None
    x = xs[:n]
    y = ys[:n]
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) * (v - mx) for v in x)
    syy = sum((v - my) * (v - my) for v in y)
    if sxx <= 1e-18 or syy <= 1e-18:
        return None
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def parse_threshold(text: str) -> tuple[str, float | None]:
    s = (text or "").strip()
    if not s:
        return "", None
    op = ""
    if s.startswith(">="):
        op = ">="
    elif s.startswith("<="):
        op = "<="
    elif s.startswith(">"):
        op = ">"
    elif s.startswith("<"):
        op = "<"
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not m:
        return op, None
    return op, float(m.group(0))


def compute_margin(value: float | None, op: str, thr: float | None) -> float | None:
    if value is None or thr is None:
        return None
    if op in (">", ">="):
        return value - thr
    if op in ("<", "<="):
        return thr - value
    return None


def metric_map(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    rows = read_csv(path)
    for r in rows:
        gid = (r.get("gate_id") or "").strip()
        if gid:
            out[gid] = r
    return out


def top2_peak_features(
    coords: list[tuple[float, float]],
    sigma: list[float],
    ratio_thr: float,
    dist_thr: float,
) -> tuple[float, float, bool, bool]:
    if len(sigma) < 2:
        return 0.0, 0.0, False, False
    top = sorted(range(len(sigma)), key=lambda i: sigma[i], reverse=True)[:2]
    i1, i2 = top[0], top[1]
    ratio = sigma[i2] / max(sigma[i1], 1e-12)
    x_min = min(c[0] for c in coords)
    x_max = max(c[0] for c in coords)
    y_min = min(c[1] for c in coords)
    y_max = max(c[1] for c in coords)
    diag = math.hypot(x_max - x_min, y_max - y_min)
    dist = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
    dist_norm = dist / max(diag, 1e-12)
    multi_peak = (ratio >= ratio_thr) and (dist_norm <= dist_thr)
    degenerate_peak = (ratio >= 0.99) and (dist_norm <= 0.05)
    return ratio, dist_norm, multi_peak, degenerate_peak


def classify_cause(
    *,
    g11_fail: bool,
    g12_fail: bool,
    g11a_fail: bool,
    g11b_fail: bool,
    g12d_fail: bool,
    multi_peak: bool,
    low_signal: bool,
    sparse_graph: bool,
    binning_edge: bool,
) -> str:
    if g11_fail and g12_fail:
        if g11a_fail and g12d_fail:
            return "coupled_weakcorr_slope"
        return "coupled_g11_g12"
    if g11_fail:
        if g11b_fail:
            return "g11b_slope_instability"
        if g11a_fail and multi_peak:
            return "weak_corr_multi_peak"
        if g11a_fail and low_signal:
            return "weak_corr_low_signal"
        if g11a_fail and sparse_graph:
            return "weak_corr_sparse_graph"
        if g11a_fail:
            return "weak_corr_high_signal"
        return "g11_other"
    if g12_fail:
        if g12d_fail and binning_edge:
            return "slope_instability_binning_edge"
        if g12d_fail and low_signal:
            return "slope_instability_low_signal"
        if g12d_fail:
            return "slope_instability"
        return "g12_other"
    return "none"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary has zero rows")

    enriched: list[dict[str, Any]] = []
    for row in rows:
        dataset_id = str(row["dataset_id"])
        seed = int(str(row["seed"]))
        run_root = (ROOT / row["run_root"]).resolve()

        g11_metrics = metric_map(run_root / "g11" / "metric_checks_einstein_eq.csv")
        g12_metrics = metric_map(run_root / "g12" / "metric_checks_gr_solutions.csv")
        g12_profile = read_csv(run_root / "g12" / "gr_solutions.csv") if (run_root / "g12" / "gr_solutions.csv").exists() else []

        coords, sigma, adj = build_dataset_graph(dataset_id, seed)
        n = len(coords)
        mean_degree = sum(len(nb) for nb in adj) / max(1, n)
        n_edges = sum(len(nb) for nb in adj) / 2.0
        graph_density = (2.0 * n_edges) / max(1.0, n * (n - 1))

        sigma_max = max(sigma) if sigma else 1.0
        phi_scale = to_float(row.get("phi_scale_where_applicable", "")) or 0.08
        U_vals = [(phi_scale * s / sigma_max) for s in sigma] if sigma else [0.0]
        mean_abs_u = sum(abs(v) for v in U_vals) / max(1, len(U_vals))
        var_u = variance(U_vals)

        peak_ratio, peak_dist_norm, multi_peak, degenerate_peak = top2_peak_features(
            coords=coords,
            sigma=sigma,
            ratio_thr=args.multi_peak_ratio_thr,
            dist_thr=args.multi_peak_dist_thr,
        )

        bin_counts: Counter[str] = Counter()
        for pr in g12_profile:
            b = (pr.get("bin_idx") or "").strip()
            if b:
                bin_counts[b] += 1
        radial_nonempty_bins = len(bin_counts)
        radial_min_bin_count = min(bin_counts.values()) if bin_counts else 0

        g11a_val = to_float(g11_metrics.get("G11a", {}).get("value", ""))
        g11a_thr_txt = g11_metrics.get("G11a", {}).get("threshold", "")
        g11a_op, g11a_thr = parse_threshold(g11a_thr_txt)
        g11a_margin = compute_margin(g11a_val, g11a_op, g11a_thr)

        g11b_val = to_float(g11_metrics.get("G11b", {}).get("value", ""))
        g11b_thr_txt = g11_metrics.get("G11b", {}).get("threshold", "")
        g11b_op, g11b_thr = parse_threshold(g11b_thr_txt)
        g11b_margin = compute_margin(g11b_val, g11b_op, g11b_thr)

        g12d_val = to_float(g12_metrics.get("G12d", {}).get("value", ""))
        g12d_thr_txt = g12_metrics.get("G12d", {}).get("threshold", "")
        g12d_op, g12d_thr = parse_threshold(g12d_thr_txt)
        g12d_margin = compute_margin(g12d_val, g12d_op, g12d_thr)

        g12c_val = to_float(g12_metrics.get("G12c", {}).get("value", ""))

        enriched.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "g10_status": norm_status(pick(row, "g10_status")),
                "g11_status": norm_status(pick(row, "g11_status", "g11_v2_status")),
                "g12_status": norm_status(pick(row, "g12_status", "g12_v2_status")),
                "g7_status": norm_status(pick(row, "g7_status")),
                "g8_status": norm_status(pick(row, "g8_status")),
                "g9_status": norm_status(pick(row, "g9_status")),
                "stage3_status": norm_status(pick(row, "stage3_status", "stage3_v2_status")),
                "g11a_status": norm_status(pick(row, "g11a", "g11a_v2_status", "g11a_v1_status")),
                "g11b_status": norm_status(pick(row, "g11b", "g11b_status")),
                "g12d_status": norm_status(pick(row, "g12d", "g12d_v2_status", "g12d_v1_status")),
                "g11a_value": g11a_val,
                "g11a_margin": g11a_margin,
                "g11b_value": g11b_val,
                "g11b_margin": g11b_margin,
                "g12d_value": g12d_val,
                "g12d_margin": g12d_margin,
                "g12c_value": g12c_val,
                "sigma_peak2_to_peak1": peak_ratio,
                "peak12_distance_norm": peak_dist_norm,
                "multi_peak_flag": multi_peak,
                "degenerate_peak_flag": degenerate_peak,
                "mean_abs_u": mean_abs_u,
                "var_u": var_u,
                "mean_degree": mean_degree,
                "graph_density": graph_density,
                "radial_nonempty_bins": radial_nonempty_bins,
                "radial_min_bin_count": radial_min_bin_count,
            }
        )

    # global thresholds for regime labels (diagnostic-only)
    p25_u = percentile([float(r["mean_abs_u"]) for r in enriched], 0.25)
    p25_deg = percentile([float(r["mean_degree"]) for r in enriched], 0.25)

    fail_rows: list[dict[str, Any]] = []
    for r in enriched:
        stage3_fail = r["stage3_status"] != "pass"
        g11_fail = r["g11_status"] != "pass"
        g12_fail = r["g12_status"] != "pass"
        g11a_fail = r["g11a_status"] != "pass"
        g11b_fail = r["g11b_status"] != "pass"
        g12d_fail = r["g12d_status"] != "pass"
        low_signal = float(r["mean_abs_u"]) <= p25_u
        sparse_graph = float(r["mean_degree"]) <= p25_deg
        binning_edge = (int(r["radial_nonempty_bins"]) < 8) or (int(r["radial_min_bin_count"]) <= 3)
        cause = classify_cause(
            g11_fail=g11_fail,
            g12_fail=g12_fail,
            g11a_fail=g11a_fail,
            g11b_fail=g11b_fail,
            g12d_fail=g12d_fail,
            multi_peak=bool(r["multi_peak_flag"]),
            low_signal=low_signal,
            sparse_graph=sparse_graph,
            binning_edge=binning_edge,
        )
        fail_pattern_parts: list[str] = []
        if g11_fail:
            fail_pattern_parts.append("G11")
        if g12_fail:
            fail_pattern_parts.append("G12")
        if r["g10_status"] != "pass":
            fail_pattern_parts.append("G10")
        if r["g7_status"] != "pass":
            fail_pattern_parts.append("G7")
        if r["g8_status"] != "pass":
            fail_pattern_parts.append("G8")
        if r["g9_status"] != "pass":
            fail_pattern_parts.append("G9")
        fail_pattern = "+".join(fail_pattern_parts) if fail_pattern_parts else "none"

        if stage3_fail:
            fail_rows.append(
                {
                    "dataset_id": r["dataset_id"],
                    "seed": r["seed"],
                    "fail_pattern": fail_pattern,
                    "cause_class": cause,
                    "g11_status": r["g11_status"],
                    "g12_status": r["g12_status"],
                    "g11a_status": r["g11a_status"],
                    "g11b_status": r["g11b_status"],
                    "g12d_status": r["g12d_status"],
                    "multi_peak_flag": "true" if r["multi_peak_flag"] else "false",
                    "degenerate_peak_flag": "true" if r["degenerate_peak_flag"] else "false",
                    "low_signal_flag": "true" if low_signal else "false",
                    "sparse_graph_flag": "true" if sparse_graph else "false",
                    "binning_edge_flag": "true" if binning_edge else "false",
                    "sigma_peak2_to_peak1": f6(float(r["sigma_peak2_to_peak1"])),
                    "peak12_distance_norm": f6(float(r["peak12_distance_norm"])),
                    "mean_abs_u": f6(float(r["mean_abs_u"])),
                    "var_u": f6(float(r["var_u"])),
                    "mean_degree": f6(float(r["mean_degree"])),
                    "graph_density": f6(float(r["graph_density"])),
                    "radial_nonempty_bins": int(r["radial_nonempty_bins"]),
                    "radial_min_bin_count": int(r["radial_min_bin_count"]),
                    "g11a_value": f6(r["g11a_value"]),
                    "g11a_margin": f6(r["g11a_margin"]),
                    "g11b_value": f6(r["g11b_value"]),
                    "g11b_margin": f6(r["g11b_margin"]),
                    "g12d_value": f6(r["g12d_value"]),
                    "g12d_margin": f6(r["g12d_margin"]),
                    "run_root": r["run_root"],
                }
            )

    if not fail_rows:
        raise RuntimeError("no stage3 fail rows found")

    write_csv(out_dir / "fail_profiles.csv", fail_rows, list(fail_rows[0].keys()))

    class_counts = Counter(str(r["cause_class"]) for r in fail_rows)
    class_rows = [
        {
            "cause_class": k,
            "count": v,
            "rate_pct": f"{(100.0 * v / len(fail_rows)):.3f}",
        }
        for (k, v) in sorted(class_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    write_csv(out_dir / "class_summary.csv", class_rows, ["cause_class", "count", "rate_pct"])

    pattern_counts = Counter(str(r["fail_pattern"]) for r in fail_rows)
    pattern_rows = [
        {"fail_pattern": k, "count": v, "rate_pct": f"{(100.0 * v / len(fail_rows)):.3f}"}
        for (k, v) in sorted(pattern_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    write_csv(out_dir / "pattern_summary.csv", pattern_rows, ["fail_pattern", "count", "rate_pct"])

    # feature correlations (all profiles; fail indicator in y)
    feature_names = [
        "sigma_peak2_to_peak1",
        "peak12_distance_norm",
        "mean_abs_u",
        "var_u",
        "mean_degree",
        "graph_density",
        "radial_nonempty_bins",
        "radial_min_bin_count",
        "g11a_value",
        "g11b_value",
        "g12c_value",
        "g12d_value",
    ]
    corr_rows: list[dict[str, Any]] = []
    for feat in feature_names:
        x_all: list[float] = []
        y_stage3: list[float] = []
        y_g11: list[float] = []
        y_g12: list[float] = []
        x_fail: list[float] = []
        x_pass: list[float] = []
        for r in enriched:
            xv = r.get(feat, None)
            if xv is None:
                continue
            xv_f = float(xv)
            x_all.append(xv_f)
            stage3_fail = 1.0 if r["stage3_status"] != "pass" else 0.0
            g11_fail = 1.0 if r["g11_status"] != "pass" else 0.0
            g12_fail = 1.0 if r["g12_status"] != "pass" else 0.0
            y_stage3.append(stage3_fail)
            y_g11.append(g11_fail)
            y_g12.append(g12_fail)
            if stage3_fail > 0.5:
                x_fail.append(xv_f)
            else:
                x_pass.append(xv_f)
        corr_rows.append(
            {
                "feature": feat,
                "n": len(x_all),
                "mean_fail_stage3": f6(mean(x_fail)),
                "mean_pass_stage3": f6(mean(x_pass)),
                "delta_fail_minus_pass": f6((mean(x_fail) or 0.0) - (mean(x_pass) or 0.0)),
                "corr_stage3_fail": f6(pearson_corr(x_all, y_stage3)),
                "corr_g11_fail": f6(pearson_corr(x_all, y_g11)),
                "corr_g12_fail": f6(pearson_corr(x_all, y_g12)),
            }
        )
    write_csv(
        out_dir / "feature_correlations.csv",
        corr_rows,
        [
            "feature",
            "n",
            "mean_fail_stage3",
            "mean_pass_stage3",
            "delta_fail_minus_pass",
            "corr_stage3_fail",
            "corr_g11_fail",
            "corr_g12_fail",
        ],
    )

    # lightweight comparative summary by dataset
    ds_rows: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in enriched}):
        sub = [r for r in enriched if str(r["dataset_id"]) == ds]
        ds_rows.append(
            {
                "dataset_id": ds,
                "n_profiles": len(sub),
                "stage3_fail": sum(1 for r in sub if r["stage3_status"] != "pass"),
                "g11_fail": sum(1 for r in sub if r["g11_status"] != "pass"),
                "g12_fail": sum(1 for r in sub if r["g12_status"] != "pass"),
                "multi_peak_count": sum(1 for r in sub if r["multi_peak_flag"]),
                "low_signal_count": sum(1 for r in sub if float(r["mean_abs_u"]) <= p25_u),
                "sparse_graph_count": sum(1 for r in sub if float(r["mean_degree"]) <= p25_deg),
            }
        )
    write_csv(out_dir / "dataset_fail_summary.csv", ds_rows, list(ds_rows[0].keys()))

    # report
    top_corr = sorted(
        corr_rows,
        key=lambda r: abs(to_float(str(r["corr_stage3_fail"])) or 0.0),
        reverse=True,
    )

    lines: list[str] = []
    lines.append("# GR Stage-3 Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    lines.append(f"- profiles_total: `{len(enriched)}`")
    lines.append(f"- strict_fail_scope: `{len(fail_rows)}` (only `stage3_status=fail` rows classified)")
    lines.append("")
    lines.append("## Fail Pattern Counts")
    lines.append("")
    for r in pattern_rows[: max(1, args.top_k)]:
        lines.append(f"- `{r['fail_pattern']}`: `{r['count']}`")
    lines.append("")
    lines.append("## Cause Classes")
    lines.append("")
    for r in class_rows[: max(1, args.top_k)]:
        lines.append(f"- `{r['cause_class']}`: `{r['count']}`")
    lines.append("")
    lines.append("## Top Feature Correlations (Stage3 Fail)")
    lines.append("")
    for r in top_corr[: max(1, args.top_k)]:
        lines.append(
            f"- `{r['feature']}`: corr_stage3_fail=`{r['corr_stage3_fail']}`, "
            f"delta_fail_minus_pass=`{r['delta_fail_minus_pass']}`"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This is diagnostic-only; no thresholds/formulas were changed.")
    lines.append("- `low_signal` and `sparse_graph` are percentile labels (P25) for comparative taxonomy only.")
    lines.append("- Any further estimator-policy updates should be preregistered before rerun/promotion.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"fail_profiles_csv:      {out_dir / 'fail_profiles.csv'}")
    print(f"class_summary_csv:      {out_dir / 'class_summary.csv'}")
    print(f"pattern_summary_csv:    {out_dir / 'pattern_summary.csv'}")
    print(f"feature_correlations:   {out_dir / 'feature_correlations.csv'}")
    print(f"dataset_fail_summary:   {out_dir / 'dataset_fail_summary.csv'}")
    print(f"report_md:              {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
