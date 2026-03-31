#!/usr/bin/env python3
"""
Analyze G11 failures from Stage-2 official policy output.

Scope:
- failure taxonomy is reported strictly on rows where `g11_status=fail`
- thresholds for low-signal/sparse/degenerate flags are derived from the
  full official Stage-2 profile grid (dataset-relative quantiles)
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import math
from pathlib import Path
import statistics
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v4"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-g11-failure-taxonomy-v4"
)

MULTI_PEAK_RATIO_THRESHOLD = 0.98
MULTI_PEAK_DISTANCE_THRESHOLD = 0.10
WEAK_CORR_THRESHOLD = 0.20


@dataclass(frozen=True)
class Thresholds:
    low_signal_p90_abs_r_max: float
    sparse_mean_degree_max: float
    degenerate_anisotropy_max: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze Stage-2 official G11 failures.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--low-signal-quantile", type=float, default=0.15)
    p.add_argument("--sparse-quantile", type=float, default=0.10)
    p.add_argument("--degenerate-quantile", type=float, default=0.10)
    p.add_argument("--multi-peak-ratio-threshold", type=float, default=MULTI_PEAK_RATIO_THRESHOLD)
    p.add_argument("--multi-peak-distance-threshold", type=float, default=MULTI_PEAK_DISTANCE_THRESHOLD)
    p.add_argument("--weak-corr-threshold", type=float, default=WEAK_CORR_THRESHOLD)
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


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def f6(v: float | None) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    return f"{float(v):.6f}"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = max(0.0, min(1.0, q)) * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: list[float]) -> float:
    return statistics.median(values) if values else float("nan")


def cov_anisotropy_ratio(coords: list[tuple[float, float]]) -> float:
    n = len(coords)
    if n < 2:
        return 0.0
    mx = sum(x for x, _ in coords) / n
    my = sum(y for _, y in coords) / n
    cxx = sum((x - mx) ** 2 for x, _ in coords) / max(1, n - 1)
    cyy = sum((y - my) ** 2 for _, y in coords) / max(1, n - 1)
    cxy = sum((x - mx) * (y - my) for x, y in coords) / max(1, n - 1)
    tr = cxx + cyy
    det = max(0.0, cxx * cyy - cxy * cxy)
    disc = max(0.0, tr * tr - 4.0 * det)
    lam1 = 0.5 * (tr + math.sqrt(disc))
    lam2 = 0.5 * (tr - math.sqrt(disc))
    if lam1 <= 1e-30:
        return 0.0
    return max(0.0, min(1.0, lam2 / lam1))


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in rows:
        v = str(r.get(key, ""))
        out[v] = out.get(v, 0) + 1
    return out


def g11_metric_map(metric_csv: Path) -> dict[str, tuple[str, float | None, str]]:
    rows = read_csv(metric_csv) if metric_csv.exists() else []
    out: dict[str, tuple[str, float | None, str]] = {}
    for r in rows:
        gid = (r.get("gate_id") or "").strip()
        if not gid:
            continue
        status = (r.get("status") or "").strip().lower()
        value = to_float(r.get("value", ""))
        threshold = (r.get("threshold") or "").strip()
        out[gid] = (status, value, threshold)
    return out


def derive_root_cause(row: dict[str, Any]) -> str:
    if row["g11b_status"] != "pass":
        return "g11b_slope_fail"
    if row["flag_weak_high_signal_corr"] == "true" and row["flag_low_signal"] == "true":
        return "low_signal_weak_corr"
    if row["flag_weak_high_signal_corr"] == "true" and row["flag_multi_peak"] == "true":
        return "multi_peak_weak_corr"
    if row["flag_weak_high_signal_corr"] == "true":
        return "weak_high_signal_corr"
    if row["flag_sparse_graph"] == "true":
        return "sparse_graph"
    if row["flag_degenerate_geometry"] == "true":
        return "degenerate_geometry"
    return "mixed_other"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    src_rows = read_csv(summary_csv)
    if not src_rows:
        raise RuntimeError("summary has zero rows")

    metric_rows: list[dict[str, Any]] = []
    for src in src_rows:
        dataset_id = src["dataset_id"]
        seed = int(src["seed"])
        run_root = (ROOT / src["run_root"]).resolve()

        eq_csv = run_root / "g11" / "einstein_eq.csv"
        eq_rows = read_csv(eq_csv) if eq_csv.exists() else []
        r_vals = [to_float(r.get("R", "")) for r in eq_rows]
        r_vals = [v for v in r_vals if v is not None]
        if not r_vals:
            continue
        p90_abs_r = percentile([abs(v) for v in r_vals], 0.90)
        std_r = statistics.pstdev(r_vals) if len(r_vals) > 1 else 0.0
        mean_r = statistics.mean(r_vals)

        coords, sigma, adj = build_dataset_graph(dataset_id, seed)
        deg = [len(a) for a in adj]
        mean_degree = mean([float(d) for d in deg])
        min_degree = min(deg) if deg else 0
        anis = cov_anisotropy_ratio(coords)

        if len(sigma) >= 2:
            top = sorted(range(len(sigma)), key=lambda i: sigma[i], reverse=True)[:2]
            i1, i2 = top[0], top[1]
            peak1, peak2 = sigma[i1], sigma[i2]
            ratio = peak2 / max(peak1, 1e-12)
            x_min = min(c[0] for c in coords)
            x_max = max(c[0] for c in coords)
            y_min = min(c[1] for c in coords)
            y_max = max(c[1] for c in coords)
            diag = math.hypot(x_max - x_min, y_max - y_min)
            dist = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
            dist_norm = dist / max(diag, 1e-12)
        else:
            peak1 = peak2 = ratio = dist = dist_norm = 0.0

        metric_map = g11_metric_map(run_root / "g11" / "metric_checks_einstein_eq.csv")
        g11a_status, g11a_value, g11a_thr = metric_map.get("G11a", ("", None, ""))
        g11b_status, g11b_value, g11b_thr = metric_map.get("G11b", ("", None, ""))
        g11c_status, g11c_value, _ = metric_map.get("G11c", ("", None, ""))
        g11d_status, g11d_value, _ = metric_map.get("G11d", ("", None, ""))

        sp_hs = abs(to_float(src.get("g11_spearman_high_signal", "")) or float("nan"))
        pe_hs = abs(to_float(src.get("g11_pearson_high_signal", "")) or float("nan"))

        metric_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": src["run_root"],
                "g11_status": (src.get("g11_status") or "").strip().lower(),
                "g11_status_legacy": (src.get("g11_status_legacy") or "").strip().lower(),
                "g11a_legacy_status": (src.get("g11a_legacy") or "").strip().lower(),
                "g11a_official_status": (src.get("g11a_official") or "").strip().lower(),
                "g11b_status": (src.get("g11b") or "").strip().lower(),
                "g11c_status": (src.get("g11c") or "").strip().lower(),
                "g11d_status": (src.get("g11d") or "").strip().lower(),
                "g11a_metric_status": g11a_status,
                "g11a_metric_value": f6(g11a_value),
                "g11a_metric_threshold": g11a_thr,
                "g11b_metric_status": g11b_status,
                "g11b_metric_value": f6(g11b_value),
                "g11b_metric_threshold": g11b_thr,
                "g11c_metric_status": g11c_status,
                "g11c_metric_value": f6(g11c_value),
                "g11d_metric_status": g11d_status,
                "g11d_metric_value": f6(g11d_value),
                "g11_spearman_high_signal_abs": f6(sp_hs),
                "g11_pearson_high_signal_abs": f6(pe_hs),
                "r_mean": f6(mean_r),
                "r_std": f6(std_r),
                "r_p90_abs": f6(p90_abs_r),
                "mean_degree": f6(mean_degree),
                "min_degree": min_degree,
                "geometry_anisotropy": f6(anis),
                "sigma_peak1": f6(peak1),
                "sigma_peak2": f6(peak2),
                "sigma_peak2_to_peak1": f6(ratio),
                "peak12_distance": f6(dist),
                "peak12_distance_norm": f6(dist_norm),
            }
        )

    if not metric_rows:
        raise RuntimeError("no profile metrics derived")

    by_ds: dict[str, Thresholds] = {}
    for ds in sorted({r["dataset_id"] for r in metric_rows}):
        sub = [r for r in metric_rows if r["dataset_id"] == ds]
        p90_vals = [to_float(str(r["r_p90_abs"])) or 0.0 for r in sub]
        deg_vals = [to_float(str(r["mean_degree"])) or 0.0 for r in sub]
        anis_vals = [to_float(str(r["geometry_anisotropy"])) or 0.0 for r in sub]
        by_ds[ds] = Thresholds(
            low_signal_p90_abs_r_max=percentile(p90_vals, args.low_signal_quantile),
            sparse_mean_degree_max=percentile(deg_vals, args.sparse_quantile),
            degenerate_anisotropy_max=percentile(anis_vals, args.degenerate_quantile),
        )

    full_rows: list[dict[str, Any]] = []
    for r in metric_rows:
        ds_thr = by_ds[r["dataset_id"]]
        ratio = to_float(str(r["sigma_peak2_to_peak1"])) or 0.0
        dist_norm = to_float(str(r["peak12_distance_norm"])) or 0.0
        sp_hs = to_float(str(r["g11_spearman_high_signal_abs"])) or 0.0
        pe_hs = to_float(str(r["g11_pearson_high_signal_abs"])) or 0.0
        p90_abs_r = to_float(str(r["r_p90_abs"])) or 0.0
        mean_deg = to_float(str(r["mean_degree"])) or 0.0
        anis = to_float(str(r["geometry_anisotropy"])) or 0.0

        flag_multi_peak = (ratio >= args.multi_peak_ratio_threshold) and (dist_norm <= args.multi_peak_distance_threshold)
        flag_low_signal = p90_abs_r <= ds_thr.low_signal_p90_abs_r_max
        flag_sparse = mean_deg <= ds_thr.sparse_mean_degree_max
        flag_degenerate = anis <= ds_thr.degenerate_anisotropy_max
        flag_weak_corr = (sp_hs < args.weak_corr_threshold) or (pe_hs < args.weak_corr_threshold)

        out = dict(r)
        out["threshold_low_signal_p90_abs_r_max"] = f6(ds_thr.low_signal_p90_abs_r_max)
        out["threshold_sparse_mean_degree_max"] = f6(ds_thr.sparse_mean_degree_max)
        out["threshold_degenerate_anisotropy_max"] = f6(ds_thr.degenerate_anisotropy_max)
        out["flag_multi_peak"] = "true" if flag_multi_peak else "false"
        out["flag_low_signal"] = "true" if flag_low_signal else "false"
        out["flag_sparse_graph"] = "true" if flag_sparse else "false"
        out["flag_degenerate_geometry"] = "true" if flag_degenerate else "false"
        out["flag_weak_high_signal_corr"] = "true" if flag_weak_corr else "false"
        out["root_cause"] = derive_root_cause(out)
        full_rows.append(out)

    fail_rows = [r for r in full_rows if str(r["g11_status"]).lower() != "pass"]

    write_csv(out_dir / "g11_all_profiles_metrics.csv", full_rows, list(full_rows[0].keys()))
    write_csv(out_dir / "g11_fail_cases.csv", fail_rows, list(fail_rows[0].keys()))

    threshold_rows = []
    for ds in sorted(by_ds.keys()):
        t = by_ds[ds]
        threshold_rows.append(
            {
                "dataset_id": ds,
                "low_signal_quantile": f"{args.low_signal_quantile:.3f}",
                "sparse_quantile": f"{args.sparse_quantile:.3f}",
                "degenerate_quantile": f"{args.degenerate_quantile:.3f}",
                "low_signal_p90_abs_r_max": f6(t.low_signal_p90_abs_r_max),
                "sparse_mean_degree_max": f6(t.sparse_mean_degree_max),
                "degenerate_anisotropy_max": f6(t.degenerate_anisotropy_max),
            }
        )
    write_csv(out_dir / "dataset_thresholds.csv", threshold_rows, list(threshold_rows[0].keys()))

    pattern_rows: list[dict[str, Any]] = []
    for key, val in sorted(count_by(fail_rows, "root_cause").items(), key=lambda kv: (-kv[1], kv[0])):
        pattern_rows.append({"kind": "root_cause", "pattern": key, "count": val, "rate_pct": f"{100.0 * val / max(1, len(fail_rows)):.3f}"})

    for key in [
        "flag_weak_high_signal_corr",
        "flag_low_signal",
        "flag_multi_peak",
        "flag_sparse_graph",
        "flag_degenerate_geometry",
    ]:
        c = sum(1 for r in fail_rows if r[key] == "true")
        pattern_rows.append({"kind": "flag_hit_count", "pattern": key, "count": c, "rate_pct": f"{100.0 * c / max(1, len(fail_rows)):.3f}"})

    write_csv(out_dir / "pattern_summary.csv", pattern_rows, list(pattern_rows[0].keys()))

    ds_rows: list[dict[str, Any]] = []
    for ds in sorted({r["dataset_id"] for r in fail_rows}):
        sub = [r for r in fail_rows if r["dataset_id"] == ds]
        ds_rows.append(
            {
                "dataset_id": ds,
                "g11_fail_count": len(sub),
                "weak_corr_count": sum(1 for r in sub if r["flag_weak_high_signal_corr"] == "true"),
                "low_signal_count": sum(1 for r in sub if r["flag_low_signal"] == "true"),
                "multi_peak_count": sum(1 for r in sub if r["flag_multi_peak"] == "true"),
                "sparse_graph_count": sum(1 for r in sub if r["flag_sparse_graph"] == "true"),
                "degenerate_geometry_count": sum(1 for r in sub if r["flag_degenerate_geometry"] == "true"),
                "r_std_median": f6(median([to_float(str(r["r_std"])) or 0.0 for r in sub])),
                "r_p90_abs_median": f6(median([to_float(str(r["r_p90_abs"])) or 0.0 for r in sub])),
            }
        )
    write_csv(out_dir / "dataset_fail_summary.csv", ds_rows, list(ds_rows[0].keys()))

    report_lines: list[str] = []
    report_lines.append("# GR Stage-2 Official G11 Failure Taxonomy (v1)")
    report_lines.append("")
    report_lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    report_lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    report_lines.append(f"- total_profiles_scanned: `{len(full_rows)}`")
    report_lines.append(f"- g11_fail_profiles_analyzed: `{len(fail_rows)}`")
    report_lines.append("- taxonomy scope: `strictly g11_status=fail rows`")
    report_lines.append("")
    report_lines.append("## Freeze Constants")
    report_lines.append("")
    report_lines.append(f"- weak_corr_threshold: `{args.weak_corr_threshold:.2f}`")
    report_lines.append(f"- multi_peak_ratio_threshold: `{args.multi_peak_ratio_threshold:.2f}`")
    report_lines.append(f"- multi_peak_distance_norm_threshold: `{args.multi_peak_distance_threshold:.2f}`")
    report_lines.append(f"- low_signal_quantile (dataset-relative): `{args.low_signal_quantile:.2f}`")
    report_lines.append(f"- sparse_quantile (dataset-relative): `{args.sparse_quantile:.2f}`")
    report_lines.append(f"- degenerate_quantile (dataset-relative): `{args.degenerate_quantile:.2f}`")
    report_lines.append("")
    report_lines.append("## Primary Findings")
    report_lines.append("")
    for key in [
        "flag_weak_high_signal_corr",
        "flag_low_signal",
        "flag_multi_peak",
        "flag_sparse_graph",
        "flag_degenerate_geometry",
    ]:
        c = sum(1 for r in fail_rows if r[key] == "true")
        report_lines.append(f"- {key}: `{c}/{len(fail_rows)}`")
    report_lines.append("")
    report_lines.append("Top root-cause labels:")
    for key, val in sorted(count_by(fail_rows, "root_cause").items(), key=lambda kv: (-kv[1], kv[0])):
        report_lines.append(f"- `{key}`: `{val}`")
    report_lines.append("")
    report_lines.append("## Dataset Breakdown")
    report_lines.append("")
    report_lines.append("| dataset | g11_fails | weak_corr | low_signal | multi_peak | sparse_graph | degenerate_geometry |")
    report_lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in ds_rows:
        report_lines.append(
            f"| {r['dataset_id']} | {r['g11_fail_count']} | {r['weak_corr_count']} | "
            f"{r['low_signal_count']} | {r['multi_peak_count']} | {r['sparse_graph_count']} | {r['degenerate_geometry_count']} |"
        )
    report_lines.append("")
    report_lines.append("## Outputs")
    report_lines.append("")
    report_lines.append("- `g11_fail_cases.csv`")
    report_lines.append("- `dataset_fail_summary.csv`")
    report_lines.append("- `pattern_summary.csv`")
    report_lines.append("- `dataset_thresholds.csv`")
    report_lines.append("- `g11_all_profiles_metrics.csv`")
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"g11_fail_cases:         {out_dir / 'g11_fail_cases.csv'}")
    print(f"dataset_fail_summary:   {out_dir / 'dataset_fail_summary.csv'}")
    print(f"pattern_summary:        {out_dir / 'pattern_summary.csv'}")
    print(f"dataset_thresholds:     {out_dir / 'dataset_thresholds.csv'}")
    print(f"all_profiles_metrics:   {out_dir / 'g11_all_profiles_metrics.csv'}")
    print(f"report_md:              {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
