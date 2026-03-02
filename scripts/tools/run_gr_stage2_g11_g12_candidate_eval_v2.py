#!/usr/bin/env python3
"""
Evaluate candidate-only v2 diagnostics for GR Stage-2 weak points (G11/G12).

Policy:
- does not modify official v1 gate scripts
- computes candidate statuses in post-processing from existing run artifacts
- writes one summary CSV for promotion evaluation

G11a-v2 candidate rule (frozen):
- keep v1 pass as-is
- otherwise require:
  - v1 G11b/G11c/G11d are pass
  - |Spearman(rho, R)| on high-signal subset >= 0.20
  - |Pearson(rho, R)| on high-signal subset >= 0.20
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
from pathlib import Path
import random
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
    / "gr-stage2-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-g11-g12-candidate-eval-v2"
)

# Frozen candidate constants
G11_HIGH_SIGNAL_SPEARMAN_MIN = 0.20
G11_HIGH_SIGNAL_PEARSON_MIN = 0.20
G11_HIGH_SIGNAL_QUANTILE = 0.80
G12_SLOPE_THRESHOLD = -0.03  # same as v1 threshold
G12_BOOTSTRAP_ITERS = 300
MULTI_PEAK_RATIO_THRESHOLD = 0.98
MULTI_PEAK_DISTANCE_THRESHOLD = 0.10
MULTI_PEAK_R_Q_LOW = 0.25
MULTI_PEAK_R_Q_HIGH = 0.90


@dataclass(frozen=True)
class SigmaPeakInfo:
    peak1: float
    peak2: float
    ratio_2_to_1: float
    dist: float
    dist_norm: float
    multi_peak_flag: bool


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate GR Stage-2 G11/G12 candidate v2 diagnostics.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--bootstrap-iters", type=int, default=G12_BOOTSTRAP_ITERS)
    p.add_argument("--g11-high-signal-spearman-min", type=float, default=G11_HIGH_SIGNAL_SPEARMAN_MIN)
    p.add_argument("--g11-high-signal-pearson-min", type=float, default=G11_HIGH_SIGNAL_PEARSON_MIN)
    p.add_argument("--g11-high-signal-quantile", type=float, default=G11_HIGH_SIGNAL_QUANTILE)
    p.add_argument("--multi-peak-ratio-threshold", type=float, default=MULTI_PEAK_RATIO_THRESHOLD)
    p.add_argument("--multi-peak-distance-threshold", type=float, default=MULTI_PEAK_DISTANCE_THRESHOLD)
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
    if v is None or math.isnan(v):
        return ""
    return f"{v:.6f}"


def norm_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


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


def pearson_corr(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = statistics.mean(x)
    my = statistics.mean(y)
    sx = sum((v - mx) ** 2 for v in x)
    sy = sum((v - my) ** 2 for v in y)
    if sx <= 1e-30 or sy <= 1e-30:
        return float("nan")
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(len(x)))
    return cov / math.sqrt(sx * sy)


def spearman_corr(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    return pearson_corr(rank_values(x), rank_values(y))


def read_einstein_eq_pairs(path: Path) -> tuple[list[float], list[float]]:
    rows = read_csv(path) if path.exists() else []
    r_vals: list[float] = []
    rho_vals: list[float] = []
    for row in rows:
        r = to_float(row.get("R", ""))
        rho = to_float(row.get("sigma_norm", ""))
        if r is None or rho is None:
            continue
        r_vals.append(r)
        rho_vals.append(rho)
    return r_vals, rho_vals


def g11_candidate_from_einstein(
    einstein_csv: Path,
    high_signal_spearman_min: float,
    high_signal_pearson_min: float,
    high_signal_quantile: float,
) -> dict[str, Any]:
    r_vals, rho_vals = read_einstein_eq_pairs(einstein_csv)
    n = len(r_vals)
    if n == 0:
        return {
            "n_points": 0,
            "spearman_full": float("nan"),
            "pearson_full": float("nan"),
            "spearman_high_signal": float("nan"),
            "pearson_high_signal": float("nan"),
            "high_signal_count": 0,
            "high_signal_rho_min": float("nan"),
            "high_signal_rule_pass": False,
        }

    sp_full = spearman_corr(rho_vals, r_vals)
    pe_full = pearson_corr(rho_vals, r_vals)
    rho_thr = percentile(rho_vals, high_signal_quantile)
    hs_pairs = [(rho_vals[i], r_vals[i]) for i in range(n) if rho_vals[i] >= rho_thr]
    hs_rho = [p[0] for p in hs_pairs]
    hs_r = [p[1] for p in hs_pairs]
    sp_hs = spearman_corr(hs_rho, hs_r) if len(hs_pairs) >= 2 else float("nan")
    pe_hs = pearson_corr(hs_rho, hs_r) if len(hs_pairs) >= 2 else float("nan")

    pass_rule = (
        (not math.isnan(sp_hs))
        and (not math.isnan(pe_hs))
        and (abs(sp_hs) >= high_signal_spearman_min)
        and (abs(pe_hs) >= high_signal_pearson_min)
    )
    return {
        "n_points": n,
        "spearman_full": sp_full,
        "pearson_full": pe_full,
        "spearman_high_signal": sp_hs,
        "pearson_high_signal": pe_hs,
        "high_signal_count": len(hs_pairs),
        "high_signal_rho_min": rho_thr,
        "high_signal_rule_pass": pass_rule,
    }


def read_gr_bin_points(gr_csv: Path) -> list[tuple[int, float, float]]:
    rows = read_csv(gr_csv) if gr_csv.exists() else []
    by_bin: dict[int, tuple[float, float]] = {}
    for row in rows:
        bin_idx = int(float(row.get("bin_idx", "0")))
        r = to_float(row.get("bin_r_mean", ""))
        R = to_float(row.get("bin_R_mean", ""))
        if r is None or R is None:
            continue
        by_bin[bin_idx] = (r, R)
    pts: list[tuple[int, float, float]] = []
    for b, (r, R) in sorted(by_bin.items()):
        if r > 0.0 and abs(R) > 1e-12:
            pts.append((b, r, R))
    return pts


def theil_sen_slope(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    slopes: list[float] = []
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            dx = x[j] - x[i]
            if abs(dx) <= 1e-30:
                continue
            slopes.append((y[j] - y[i]) / dx)
    if not slopes:
        return float("nan")
    slopes.sort()
    m = len(slopes)
    if m % 2 == 1:
        return slopes[m // 2]
    return 0.5 * (slopes[m // 2 - 1] + slopes[m // 2])


def sigma_peak_info(
    dataset_id: str,
    seed: int,
    ratio_thr: float,
    dist_thr: float,
) -> SigmaPeakInfo:
    coords, sigma, _ = build_dataset_graph(dataset_id, seed)
    if len(sigma) < 2:
        return SigmaPeakInfo(
            peak1=0.0,
            peak2=0.0,
            ratio_2_to_1=0.0,
            dist=0.0,
            dist_norm=0.0,
            multi_peak_flag=False,
        )
    top = sorted(range(len(sigma)), key=lambda i: sigma[i], reverse=True)[:2]
    i1, i2 = top[0], top[1]
    p1, p2 = sigma[i1], sigma[i2]
    ratio = p2 / max(p1, 1e-12)
    x_min = min(c[0] for c in coords)
    x_max = max(c[0] for c in coords)
    y_min = min(c[1] for c in coords)
    y_max = max(c[1] for c in coords)
    diag = math.hypot(x_max - x_min, y_max - y_min)
    dist = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
    dist_norm = dist / max(diag, 1e-12)
    flag = (ratio >= ratio_thr) and (dist_norm <= dist_thr)
    return SigmaPeakInfo(
        peak1=p1,
        peak2=p2,
        ratio_2_to_1=ratio,
        dist=dist,
        dist_norm=dist_norm,
        multi_peak_flag=flag,
    )


def select_g12_bins(
    points: list[tuple[int, float, float]],
    multi_peak_flag: bool,
) -> tuple[list[tuple[int, float, float]], str]:
    if len(points) <= 2:
        return points, "fallback_all"

    if multi_peak_flag:
        r_values = [p[1] for p in points]
        q_lo = percentile(r_values, MULTI_PEAK_R_Q_LOW)
        q_hi = percentile(r_values, MULTI_PEAK_R_Q_HIGH)
        sel = [p for p in points if p[1] >= q_lo and p[1] <= q_hi]
        if len(sel) >= 4:
            return sel, "multi_peak_mid_quantile"

    trimmed = points[1:-1]
    if len(trimmed) >= 4:
        return trimmed, "trim_edge_bins"

    return points, "fallback_all"


def g12_candidate_from_bins(
    points: list[tuple[int, float, float]],
    multi_peak_flag: bool,
    bootstrap_iters: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    selected, branch = select_g12_bins(points, multi_peak_flag)
    x = [math.log(p[1]) for p in selected]
    y = [math.log(abs(p[2])) for p in selected]
    slope = theil_sen_slope(x, y)

    rng = random.Random(bootstrap_seed)
    boot: list[float] = []
    n = len(selected)
    if n >= 3 and bootstrap_iters > 0:
        for _ in range(bootstrap_iters):
            sample = [selected[rng.randrange(0, n)] for _ in range(n)]
            xs = [math.log(p[1]) for p in sample]
            ys = [math.log(abs(p[2])) for p in sample]
            s = theil_sen_slope(xs, ys)
            if not math.isnan(s):
                boot.append(s)
    ci_low = percentile(boot, 0.025) if boot else float("nan")
    ci_high = percentile(boot, 0.975) if boot else float("nan")
    rule_pass = (not math.isnan(slope)) and (slope < G12_SLOPE_THRESHOLD)
    return {
        "selected_count": len(selected),
        "selected_branch": branch,
        "slope_robust": slope,
        "bootstrap_n": len(boot),
        "bootstrap_ci_low": ci_low,
        "bootstrap_ci_high": ci_high,
        "slope_rule_pass": rule_pass,
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
        dataset_id = row["dataset_id"]
        seed = int(row["seed"])
        run_root = (ROOT / row["run_root"]).resolve()

        g11_v1 = norm_status(row.get("g11_status", ""))
        g11a_v1 = norm_status(row.get("g11a", ""))
        g11b_v1 = norm_status(row.get("g11b", ""))
        g11c_v1 = norm_status(row.get("g11c", ""))
        g11d_v1 = norm_status(row.get("g11d", ""))

        g12_v1 = norm_status(row.get("g12_status", ""))
        g12a_v1 = norm_status(row.get("g12a", ""))
        g12b_v1 = norm_status(row.get("g12b", ""))
        g12c_v1 = norm_status(row.get("g12c", ""))
        g12d_v1 = norm_status(row.get("g12d", ""))

        g10_v1 = norm_status(row.get("g10_status", ""))
        g7_v1 = norm_status(row.get("g7_status", ""))
        stage2_v1 = norm_status(row.get("stage2_status", ""))

        g11_diag = g11_candidate_from_einstein(
            run_root / "g11" / "einstein_eq.csv",
            high_signal_spearman_min=args.g11_high_signal_spearman_min,
            high_signal_pearson_min=args.g11_high_signal_pearson_min,
            high_signal_quantile=args.g11_high_signal_quantile,
        )
        g11a_v2 = "pass" if (
            g11a_v1 == "pass"
            or (
                g11b_v1 == "pass"
                and g11c_v1 == "pass"
                and g11d_v1 == "pass"
                and bool(g11_diag["high_signal_rule_pass"])
            )
        ) else "fail"
        g11_v2 = gate_from_statuses(g11a_v2, g11b_v1, g11c_v1, g11d_v1)

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
        g12d_v2 = "pass" if (g12d_v1 == "pass" or bool(g12_diag["slope_rule_pass"])) else "fail"
        g12_v2 = gate_from_statuses(g12a_v1, g12b_v1, g12c_v1, g12d_v2)

        stage2_v2 = gate_from_statuses(g10_v1, g11_v2, g12_v2, g7_v1)

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "g10_v1_status": g10_v1,
                "g7_v1_status": g7_v1,
                "g11_v1_status": g11_v1,
                "g11a_v1_status": g11a_v1,
                "g11b_v1_status": g11b_v1,
                "g11c_v1_status": g11c_v1,
                "g11d_v1_status": g11d_v1,
                "g11a_v2_status": g11a_v2,
                "g11_v2_status": g11_v2,
                "g11_spearman_full": f6(g11_diag["spearman_full"]),
                "g11_pearson_full": f6(g11_diag["pearson_full"]),
                "g11_spearman_high_signal": f6(g11_diag["spearman_high_signal"]),
                "g11_pearson_high_signal": f6(g11_diag["pearson_high_signal"]),
                "g11_high_signal_count": g11_diag["high_signal_count"],
                "g11_high_signal_rho_min": f6(g11_diag["high_signal_rho_min"]),
                "g11_high_signal_rule_pass": "true" if bool(g11_diag["high_signal_rule_pass"]) else "false",
                "g12_v1_status": g12_v1,
                "g12a_v1_status": g12a_v1,
                "g12b_v1_status": g12b_v1,
                "g12c_v1_status": g12c_v1,
                "g12d_v1_status": g12d_v1,
                "g12d_v2_status": g12d_v2,
                "g12_v2_status": g12_v2,
                "g12_points_total": len(g12_points),
                "g12_points_selected": g12_diag["selected_count"],
                "g12_selected_branch": g12_diag["selected_branch"],
                "g12_slope_robust": f6(g12_diag["slope_robust"]),
                "g12_bootstrap_n": g12_diag["bootstrap_n"],
                "g12_bootstrap_ci_low": f6(g12_diag["bootstrap_ci_low"]),
                "g12_bootstrap_ci_high": f6(g12_diag["bootstrap_ci_high"]),
                "g12_slope_rule_pass": "true" if bool(g12_diag["slope_rule_pass"]) else "false",
                "peak1_sigma": f6(peak_info.peak1),
                "peak2_sigma": f6(peak_info.peak2),
                "peak2_to_peak1": f6(peak_info.ratio_2_to_1),
                "peak12_distance": f6(peak_info.dist),
                "peak12_distance_norm": f6(peak_info.dist_norm),
                "multi_peak_flag": "true" if peak_info.multi_peak_flag else "false",
                "stage2_v1_status": stage2_v1,
                "stage2_v2_status": stage2_v2,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    def count_pass(k: str) -> int:
        return sum(1 for r in out_rows if norm_status(str(r[k])) == "pass")
    g11_v1_pass = count_pass("g11_v1_status")
    g11_v2_pass = count_pass("g11_v2_status")
    g12_v1_pass = count_pass("g12_v1_status")
    g12_v2_pass = count_pass("g12_v2_status")
    st_v1_pass = count_pass("stage2_v1_status")
    st_v2_pass = count_pass("stage2_v2_status")

    report_lines = [
        "# GR Stage-2 G11/G12 Candidate Evaluation (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G11 v1: `{g11_v1_pass}/{n}`",
        f"- G11 v2: `{g11_v2_pass}/{n}`",
        f"- G12 v1: `{g12_v1_pass}/{n}`",
        f"- G12 v2: `{g12_v2_pass}/{n}`",
        f"- Stage2 v1: `{st_v1_pass}/{n}`",
        f"- Stage2 v2: `{st_v2_pass}/{n}`",
        "",
        "## Notes",
        "",
        "- v1 official gates remain unchanged.",
        "- v2 is candidate-only evaluation layer.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "constants": {
            "g11_high_signal_spearman_min": args.g11_high_signal_spearman_min,
            "g11_high_signal_pearson_min": args.g11_high_signal_pearson_min,
            "g11_high_signal_quantile": args.g11_high_signal_quantile,
            "g12_slope_threshold": G12_SLOPE_THRESHOLD,
            "bootstrap_iters": args.bootstrap_iters,
            "multi_peak_ratio_threshold": args.multi_peak_ratio_threshold,
            "multi_peak_distance_threshold": args.multi_peak_distance_threshold,
        },
        "notes": [
            "No edits to official gate scripts.",
            "Candidate rules are computed in post-processing only.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
