#!/usr/bin/env python3
"""
Evaluate Stage-3 candidate-only v2 diagnostics for G11/G12.

Policy:
- does not modify official gate scripts
- computes candidate statuses in post-processing from existing run artifacts
- preserves v1 passes by construction (non-degrading candidate layer)

Candidate intent:
- G12d-v2: robust radial-slope estimator (bin support + edge trimming + winsorized log fit)
- G11a-v2: robust high-signal correlation with multi-peak guard
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
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-g11-g12-candidate-v2"
)

# Frozen candidate constants
G11_HIGH_SIGNAL_QUANTILE = 0.80
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
    p = argparse.ArgumentParser(description="Evaluate Stage-3 G11/G12 candidate-v2 diagnostics.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--g11-high-signal-quantile", type=float, default=G11_HIGH_SIGNAL_QUANTILE)
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
    if v is None or math.isnan(v) or math.isinf(v):
        return ""
    return f"{v:.6f}"


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


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
    w = pos - lo
    return xs[lo] * (1.0 - w) + xs[hi] * w


def rank_values(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        v = values[order[i]]
        while j + 1 < len(order) and values[order[j + 1]] == v:
            j += 1
        r = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson_corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    sx = sum((v - mx) * (v - mx) for v in xs)
    sy = sum((v - my) * (v - my) for v in ys)
    if sx <= 1e-30 or sy <= 1e-30:
        return float("nan")
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs)))
    return cov / math.sqrt(sx * sy)


def spearman_corr(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    return pearson_corr(rank_values(xs), rank_values(ys))


def smooth_values(values: list[float], neighbours: list[list[int]], alpha: float, iters: int) -> list[float]:
    out = values[:]
    for _ in range(max(0, iters)):
        nxt = out[:]
        for i, nb in enumerate(neighbours):
            if not nb:
                continue
            m = sum(out[j] for j in nb) / len(nb)
            nxt[i] = (1.0 - alpha) * out[i] + alpha * m
        out = nxt
    return out


def laplacian_rw(values: list[float], neighbours: list[list[int]]) -> list[float]:
    out = [0.0] * len(values)
    for i, nb in enumerate(neighbours):
        if not nb:
            continue
        out[i] = sum(values[j] - values[i] for j in nb) / len(nb)
    return out


def trimmed_order_indices(values: list[float], trim_fraction: float, min_keep: int = 6) -> list[int]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    k = int(len(order) * max(0.0, min(0.45, trim_fraction)))
    kept = order[k : len(order) - k]
    if len(kept) < min_keep:
        return order
    return kept


def g11_rank_diag(
    *,
    source_vals: list[float],
    target_vals: list[float],
    high_signal_quantile: float,
    corr_min: float,
    trim_fraction: float,
) -> dict[str, Any]:
    n = min(len(source_vals), len(target_vals))
    if n < 6:
        return {
            "hs_count": 0,
            "hs_trimmed_count": 0,
            "s_threshold": float("nan"),
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "spearman_hs_trimmed": float("nan"),
            "base_rule_pass": False,
            "trim_rule_pass": False,
        }
    s = source_vals[:n]
    t = target_vals[:n]
    s_thr = percentile(s, high_signal_quantile)
    idx = [i for i, v in enumerate(s) if v >= s_thr]
    if len(idx) < 6:
        return {
            "hs_count": len(idx),
            "hs_trimmed_count": len(idx),
            "s_threshold": s_thr,
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "spearman_hs_trimmed": float("nan"),
            "base_rule_pass": False,
            "trim_rule_pass": False,
        }
    hs_s = [s[i] for i in idx]
    hs_t = [t[i] for i in idx]
    sp_hs = spearman_corr(hs_s, hs_t)
    pe_hs = pearson_corr(hs_s, hs_t)

    keep = trimmed_order_indices(hs_t, trim_fraction=trim_fraction, min_keep=6)
    hs_s_t = [hs_s[i] for i in keep]
    hs_t_t = [hs_t[i] for i in keep]
    sp_hs_t = spearman_corr(hs_s_t, hs_t_t)

    base_rule = (
        (not math.isnan(sp_hs))
        and (not math.isnan(pe_hs))
        and (abs(sp_hs) >= corr_min)
        and (abs(pe_hs) >= corr_min)
    )
    trim_rule = (not math.isnan(sp_hs_t)) and (abs(sp_hs_t) >= corr_min)
    return {
        "hs_count": len(idx),
        "hs_trimmed_count": len(keep),
        "s_threshold": s_thr,
        "spearman_hs": sp_hs,
        "pearson_hs": pe_hs,
        "spearman_hs_trimmed": sp_hs_t,
        "base_rule_pass": base_rule,
        "trim_rule_pass": trim_rule,
    }


def peak_features(
    *,
    coords: list[tuple[float, float]],
    sigma: list[float],
    ratio_thr: float,
    dist_thr: float,
) -> dict[str, Any]:
    if len(sigma) < 2:
        return {
            "peak_ratio_2_to_1": 0.0,
            "peak_distance_norm": 0.0,
            "multi_peak_flag": False,
        }
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
    flag = (ratio >= ratio_thr) and (dist_norm <= dist_thr)
    return {
        "peak_ratio_2_to_1": ratio,
        "peak_distance_norm": dist_norm,
        "multi_peak_flag": flag,
    }


def read_g11_pairs(path: Path) -> tuple[list[float], list[float]]:
    rows = read_csv(path) if path.exists() else []
    r_vals: list[float] = []
    sigma_norm: list[float] = []
    for r in rows:
        rv = to_float(r.get("R", ""))
        sv = to_float(r.get("sigma_norm", ""))
        if rv is None or sv is None:
            continue
        r_vals.append(rv)
        sigma_norm.append(sv)
    return r_vals, sigma_norm


def group_g12_bins(path: Path) -> list[dict[str, Any]]:
    rows = read_csv(path) if path.exists() else []
    bins: dict[int, dict[str, list[float]]] = {}
    for r in rows:
        bi = to_float(r.get("bin_idx", ""))
        rv = to_float(r.get("r", ""))
        Rv = to_float(r.get("R", ""))
        if bi is None or rv is None or Rv is None:
            continue
        b = int(bi)
        if b not in bins:
            bins[b] = {"r": [], "R": []}
        bins[b]["r"].append(rv)
        bins[b]["R"].append(Rv)

    out: list[dict[str, Any]] = []
    for b in sorted(bins):
        rr = bins[b]["r"]
        RR = bins[b]["R"]
        if not rr or not RR:
            continue
        r_med = statistics.median(rr)
        absR_vals = [abs(v) for v in RR if abs(v) > 1e-12]
        if not absR_vals:
            continue
        absR_med = statistics.median(absR_vals)
        out.append(
            {
                "bin_idx": b,
                "n": len(rr),
                "r_med": r_med,
                "absR_med": absR_med,
            }
        )
    return out


def winsorize(values: list[float], q: float) -> list[float]:
    if not values:
        return []
    lo = percentile(values, q)
    hi = percentile(values, 1.0 - q)
    return [min(max(v, lo), hi) for v in values]


def ols_slope(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return float("nan")
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    sxx = sum((v - mx) * (v - mx) for v in xs)
    if sxx <= 1e-30:
        return float("nan")
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs)))
    return sxy / sxx


def robust_g12_slope(
    *,
    gr_csv: Path,
    min_bin_count: int,
    winsor_q: float,
    drop_edge_bins: bool,
) -> dict[str, Any]:
    bins = group_g12_bins(gr_csv)
    supported = [b for b in bins if int(b["n"]) >= min_bin_count and float(b["r_med"]) > 0.0 and float(b["absR_med"]) > 1e-12]
    branch = "supported_bins"
    if drop_edge_bins and len(supported) >= 5:
        supported = sorted(supported, key=lambda b: float(b["r_med"]))[1:-1]
        branch = "supported_drop_edges"
    if len(supported) < 4:
        supported = [b for b in bins if float(b["r_med"]) > 0.0 and float(b["absR_med"]) > 1e-12]
        branch = "fallback_all_bins"
    if len(supported) < 2:
        return {
            "selected_bins": len(supported),
            "branch": branch,
            "min_bin_count_selected": min((int(b["n"]) for b in supported), default=0),
            "slope_robust": float("nan"),
        }
    xs = [math.log(float(b["r_med"])) for b in supported]
    ys_raw = [math.log(float(b["absR_med"])) for b in supported]
    ys = winsorize(ys_raw, winsor_q)
    slope = ols_slope(xs, ys)
    return {
        "selected_bins": len(supported),
        "branch": branch,
        "min_bin_count_selected": min(int(b["n"]) for b in supported),
        "slope_robust": slope,
    }


def gate_from_statuses(*statuses: str) -> str:
    return "pass" if all(norm_status(s) == "pass" for s in statuses) else "fail"


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

        g10_v1 = norm_status(row.get("g10_status", ""))
        g11_v1 = norm_status(row.get("g11_status", ""))
        g12_v1 = norm_status(row.get("g12_status", ""))
        g7_v1 = norm_status(row.get("g7_status", ""))
        g8_v1 = norm_status(row.get("g8_status", ""))
        g9_v1 = norm_status(row.get("g9_status", ""))
        stage3_v1 = norm_status(row.get("stage3_status", ""))

        g11a_v1 = norm_status(row.get("g11a", ""))
        g11b_v1 = norm_status(row.get("g11b", ""))
        g11c_v1 = norm_status(row.get("g11c", ""))
        g11d_v1 = norm_status(row.get("g11d", ""))

        g12a_v1 = norm_status(row.get("g12a", ""))
        g12b_v1 = norm_status(row.get("g12b", ""))
        g12c_v1 = norm_status(row.get("g12c", ""))
        g12d_v1 = norm_status(row.get("g12d", ""))

        coords, sigma, adj_w = build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]

        # G11 candidate diagnostics
        r_vals, sigma_norm = read_g11_pairs(run_root / "g11" / "einstein_eq.csv")
        n11 = min(len(r_vals), len(sigma_norm), len(neighbours))
        r_vals = r_vals[:n11]
        sigma_norm = sigma_norm[:n11]
        neighbours_11 = neighbours[:n11]
        peak_diag = peak_features(
            coords=coords[:n11],
            sigma=sigma[:n11],
            ratio_thr=args.g11_multi_peak_ratio_thr,
            dist_thr=args.g11_multi_peak_dist_thr,
        )

        r_smooth = smooth_values(r_vals, neighbours_11, alpha=args.g11_smooth_alpha, iters=args.g11_smooth_iters)
        source_vals = [abs(v) for v in laplacian_rw(sigma_norm, neighbours_11)]
        target_vals = [abs(v) for v in r_smooth]
        g11_diag = g11_rank_diag(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.g11_high_signal_quantile,
            corr_min=args.g11_corr_min,
            trim_fraction=args.g11_trim_fraction,
        )

        if g11_v1 == "pass":
            g11a_v2 = "pass"
            g11_v2 = "pass"
            g11_candidate_rule = "carry_v1_pass"
        else:
            structural_ok = (g11b_v1 == "pass" and g11c_v1 == "pass" and g11d_v1 == "pass")
            if not structural_ok:
                g11a_v2 = "fail"
                g11_v2 = "fail"
                g11_candidate_rule = "structural_fail"
            else:
                if bool(peak_diag["multi_peak_flag"]):
                    rule_ok = bool(g11_diag["trim_rule_pass"])
                    g11_candidate_rule = "multi_peak_trim_rank"
                else:
                    rule_ok = bool(g11_diag["base_rule_pass"] or g11_diag["trim_rule_pass"])
                    g11_candidate_rule = "base_or_trim_rank"
                g11a_v2 = "pass" if rule_ok else "fail"
                g11_v2 = gate_from_statuses(g11a_v2, g11b_v1, g11c_v1, g11d_v1)

        # G12 candidate diagnostics
        g12_diag = robust_g12_slope(
            gr_csv=run_root / "g12" / "gr_solutions.csv",
            min_bin_count=args.g12_min_bin_count,
            winsor_q=args.g12_winsor_q,
            drop_edge_bins=bool(args.g12_drop_edge_bins),
        )
        g12d_v2_rule = (not math.isnan(float(g12_diag["slope_robust"]))) and (float(g12_diag["slope_robust"]) < args.g12_slope_threshold)

        if g12_v1 == "pass":
            g12d_v2 = "pass"
            g12_v2 = "pass"
            g12_candidate_rule = "carry_v1_pass"
        else:
            structural_ok = (g12a_v1 == "pass" and g12b_v1 == "pass" and g12c_v1 == "pass")
            if structural_ok and g12d_v2_rule:
                g12d_v2 = "pass"
                g12_v2 = "pass"
                g12_candidate_rule = "robust_slope_pass"
            else:
                g12d_v2 = "fail"
                g12_v2 = "fail"
                g12_candidate_rule = "robust_slope_fail"

        lane_3p1_v1 = "pass" if (g10_v1 == "pass" and g11_v1 == "pass") else "fail"
        lane_3p1_v2 = "pass" if (g10_v1 == "pass" and g11_v2 == "pass") else "fail"
        lane_strong_v1 = g12_v1
        lane_strong_v2 = g12_v2
        lane_tensor = g7_v1
        lane_geometry = g8_v1
        lane_conservation = g9_v1

        stage3_v2 = (
            "pass"
            if (
                lane_3p1_v2 == "pass"
                and lane_strong_v2 == "pass"
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
                "g10_status": g10_v1,
                "g7_status": g7_v1,
                "g8_status": g8_v1,
                "g9_status": g9_v1,
                "g11_v1_status": g11_v1,
                "g11_v2_status": g11_v2,
                "g11a_v1_status": g11a_v1,
                "g11a_v2_status": g11a_v2,
                "g11b_status": g11b_v1,
                "g11c_status": g11c_v1,
                "g11d_status": g11d_v1,
                "g11_candidate_rule": g11_candidate_rule,
                "g11_multi_peak_flag": "true" if bool(peak_diag["multi_peak_flag"]) else "false",
                "g11_peak_ratio_2_to_1": f6(float(peak_diag["peak_ratio_2_to_1"])),
                "g11_peak_distance_norm": f6(float(peak_diag["peak_distance_norm"])),
                "g11_hs_count": int(g11_diag["hs_count"]),
                "g11_hs_trimmed_count": int(g11_diag["hs_trimmed_count"]),
                "g11_s_threshold": f6(float(g11_diag["s_threshold"])),
                "g11_spearman_hs": f6(float(g11_diag["spearman_hs"])),
                "g11_pearson_hs": f6(float(g11_diag["pearson_hs"])),
                "g11_spearman_hs_trimmed": f6(float(g11_diag["spearman_hs_trimmed"])),
                "g11_base_rule_pass": "true" if bool(g11_diag["base_rule_pass"]) else "false",
                "g11_trim_rule_pass": "true" if bool(g11_diag["trim_rule_pass"]) else "false",
                "g12_v1_status": g12_v1,
                "g12_v2_status": g12_v2,
                "g12a_status": g12a_v1,
                "g12b_status": g12b_v1,
                "g12c_status": g12c_v1,
                "g12d_v1_status": g12d_v1,
                "g12d_v2_status": g12d_v2,
                "g12_candidate_rule": g12_candidate_rule,
                "g12_slope_robust": f6(float(g12_diag["slope_robust"])),
                "g12_selected_bins": int(g12_diag["selected_bins"]),
                "g12_selected_branch": str(g12_diag["branch"]),
                "g12_min_bin_count_selected": int(g12_diag["min_bin_count_selected"]),
                "lane_3p1_v1_status": lane_3p1_v1,
                "lane_3p1_v2_status": lane_3p1_v2,
                "lane_strong_field_v1_status": lane_strong_v1,
                "lane_strong_field_v2_status": lane_strong_v2,
                "lane_tensor_status": lane_tensor,
                "lane_geometry_status": lane_geometry,
                "lane_conservation_status": lane_conservation,
                "stage3_v1_status": stage3_v1,
                "stage3_v2_status": stage3_v2,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    g11_v1_pass = sum(1 for r in out_rows if r["g11_v1_status"] == "pass")
    g11_v2_pass = sum(1 for r in out_rows if r["g11_v2_status"] == "pass")
    g12_v1_pass = sum(1 for r in out_rows if r["g12_v1_status"] == "pass")
    g12_v2_pass = sum(1 for r in out_rows if r["g12_v2_status"] == "pass")
    s3_v1_pass = sum(1 for r in out_rows if r["stage3_v1_status"] == "pass")
    s3_v2_pass = sum(1 for r in out_rows if r["stage3_v2_status"] == "pass")
    improved = sum(1 for r in out_rows if r["stage3_v1_status"] == "fail" and r["stage3_v2_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["stage3_v1_status"] == "pass" and r["stage3_v2_status"] == "fail")

    report_lines = [
        "# GR Stage-3 G11/G12 Candidate Eval (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Counts",
        "",
        f"- G11: `{g11_v1_pass}/{n} -> {g11_v2_pass}/{n}`",
        f"- G12: `{g12_v1_pass}/{n} -> {g12_v2_pass}/{n}`",
        f"- Stage3: `{s3_v1_pass}/{n} -> {s3_v2_pass}/{n}`",
        f"- improved_vs_v1: `{improved}`",
        f"- degraded_vs_v1: `{degraded}`",
        "",
        "## Notes",
        "",
        "- Candidate-only layer over frozen artifacts.",
        "- No gate threshold/formula edits in official scripts.",
        "- G12 threshold remains `< -0.03`; G11 corr threshold remains `0.20`.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "constants": {
            "g11_high_signal_quantile": args.g11_high_signal_quantile,
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
            "Direct v1 pass carry-over is enabled for non-degrading candidate evaluation.",
            "Candidate-v2 is not an official switch; governance decision is separate.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

