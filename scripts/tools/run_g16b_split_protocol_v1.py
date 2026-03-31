#!/usr/bin/env python3
"""
Evaluate G16b split protocol candidate (v1) on fixed action-run artifacts.

Purpose:
- Keep official G16b-v1 unchanged.
- Diagnose a preregistered split decision policy:
  - low-signal regime: robust rank/linear checks on high-signal subset
  - high-signal regime: correlation + directional alignment + slope-only fit

Inputs:
- Existing run outputs under artifacts/*/runs/*/g16/action.csv (+ metric_checks_action.csv when available)

Outputs:
- summary.csv: per-profile metrics and decisions (v1/v2/split)
- report.md: aggregate comparisons and prereg decision checks
- prereg_manifest.json: frozen protocol metadata
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_SOURCE_RUNS = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-v2-candidate-prereg-v1"
    / "runs"
)
DEFAULT_OUT_SANITY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-split-protocol-sanity-v1"
)
DEFAULT_OUT_PREREG = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-split-protocol-prereg-v1"
)

PREREG_DATASETS = ["DS-002", "DS-003", "DS-006"]
PREREG_SEED_START = 3401
PREREG_SEED_END = 3600
PREREG_PHI_SCALE = 0.08

# Split protocol freeze constants (diagnostic candidate only)
PREREG_SIGNAL_INDEX_NAME = "p90_abs_t11"
PREREG_SIGNAL_THRESHOLD = 0.024
PREREG_HIGH_SIGNAL_QUANTILE = 0.80
PREREG_LOW_CORR_MIN = 0.2
PREREG_LOW_R2_MIN = 0.05
PREREG_HIGH_CORR_MIN = 0.2
PREREG_HIGH_COS_MIN = 0.2
PREREG_HIGH_R2_ORIGIN_MIN = 0.05

# Keep legacy v2 comparator (already used in previous candidate eval)
PREREG_V2_LOW_SIGNAL_RATIO = 10.0
PREREG_V2_CORR_MIN = 0.2
PREREG_V2_R2_MIN = 0.05


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int
    phi_scale: float

    @property
    def tag(self) -> str:
        return f"{self.dataset_id.lower()}_seed{self.seed}_phi{self.phi_scale:.2f}".replace(".", "p")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate G16b split protocol candidate (v1).")
    p.add_argument("--mode", choices=["sanity", "prereg"], default="prereg")
    p.add_argument("--out-dir", default="")
    p.add_argument("--source-runs-dir", default=str(DEFAULT_SOURCE_RUNS))
    p.add_argument("--profiles", default="", help="Comma-separated dataset:seed list for sanity mode.")
    p.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p.add_argument("--seed-start", type=int, default=PREREG_SEED_START)
    p.add_argument("--seed-end", type=int, default=PREREG_SEED_END)
    p.add_argument("--phi-scale", type=float, default=PREREG_PHI_SCALE)

    p.add_argument("--signal-threshold", type=float, default=PREREG_SIGNAL_THRESHOLD)
    p.add_argument("--high-signal-quantile", type=float, default=PREREG_HIGH_SIGNAL_QUANTILE)
    p.add_argument("--low-corr-min", type=float, default=PREREG_LOW_CORR_MIN)
    p.add_argument("--low-r2-min", type=float, default=PREREG_LOW_R2_MIN)
    p.add_argument("--high-corr-min", type=float, default=PREREG_HIGH_CORR_MIN)
    p.add_argument("--high-cos-min", type=float, default=PREREG_HIGH_COS_MIN)
    p.add_argument("--high-r2-origin-min", type=float, default=PREREG_HIGH_R2_ORIGIN_MIN)

    p.add_argument("--v2-low-signal-ratio", type=float, default=PREREG_V2_LOW_SIGNAL_RATIO)
    p.add_argument("--v2-corr-min", type=float, default=PREREG_V2_CORR_MIN)
    p.add_argument("--v2-r2-min", type=float, default=PREREG_V2_R2_MIN)

    p.add_argument(
        "--strict-prereg",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Fail if parameters differ from prereg constants.",
    )
    return p.parse_args()


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def f6(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.6f}"


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.pstdev(values)


def pearson_corr(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    mx, sx = mean_std(x_vals)
    my, sy = mean_std(y_vals)
    if sx <= 1e-30 or sy <= 1e-30:
        return float("nan")
    cov = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(len(x_vals))) / len(x_vals)
    return cov / (sx * sy)


def rank_values(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        v = values[order[i]]
        while j + 1 < len(order) and values[order[j + 1]] == v:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def spearman_corr(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    return pearson_corr(rank_values(x_vals), rank_values(y_vals))


def ols_r2(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    mx = statistics.mean(x_vals)
    my = statistics.mean(y_vals)
    sxx = sum((x - mx) ** 2 for x in x_vals)
    if sxx <= 1e-30:
        return float("nan")
    sxy = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(len(x_vals)))
    b = sxy / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in y_vals)
    if ss_tot <= 1e-30:
        return 1.0
    y_pred = [a + b * x for x in x_vals]
    ss_res = sum((y_vals[i] - y_pred[i]) ** 2 for i in range(len(x_vals)))
    return max(0.0, 1.0 - ss_res / ss_tot)


def r2_origin(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    denom = sum(x * x for x in x_vals)
    if denom <= 1e-30:
        return float("nan")
    b = sum(x_vals[i] * y_vals[i] for i in range(len(x_vals))) / denom
    y_mean = statistics.mean(y_vals)
    ss_tot = sum((y - y_mean) ** 2 for y in y_vals)
    if ss_tot <= 1e-30:
        return 1.0
    ss_res = sum((y_vals[i] - b * x_vals[i]) ** 2 for i in range(len(x_vals)))
    return max(0.0, 1.0 - ss_res / ss_tot)


def cosine_similarity(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or not x_vals:
        return float("nan")
    dot = sum(x_vals[i] * y_vals[i] for i in range(len(x_vals)))
    nx = math.sqrt(sum(x * x for x in x_vals))
    ny = math.sqrt(sum(y * y for y in y_vals))
    if nx <= 1e-30 or ny <= 1e-30:
        return float("nan")
    return dot / (nx * ny)


def read_action_vectors(action_csv: Path) -> tuple[list[float], list[float]]:
    rows = read_csv(action_csv)
    g11_vals: list[float] = []
    t11_vals: list[float] = []
    for row in rows:
        g = to_float(row.get("G11", ""))
        t = to_float(row.get("T11", ""))
        if g is None or t is None:
            continue
        g11_vals.append(g)
        t11_vals.append(t)
    return g11_vals, t11_vals


def parse_metric_checks(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        gid = row.get("gate_id", "").strip()
        if gid:
            out[gid] = row
    return out


def high_signal_subset(g11_vals: list[float], t11_vals: list[float], quantile: float) -> tuple[list[float], list[float], float]:
    abs_t = [abs(v) for v in t11_vals]
    threshold = percentile(abs_t, quantile)
    pairs = [(g11_vals[i], t11_vals[i]) for i in range(len(t11_vals)) if abs_t[i] >= threshold]
    if not pairs:
        return [], [], threshold
    g = [p[0] for p in pairs]
    t = [p[1] for p in pairs]
    return g, t, threshold


def build_profiles(args: argparse.Namespace) -> list[Profile]:
    if args.mode == "sanity":
        if args.profiles.strip():
            out: list[Profile] = []
            for token in parse_csv_list(args.profiles):
                ds, seed_text = token.split(":")
                out.append(Profile(ds.strip().upper(), int(seed_text), float(args.phi_scale)))
            return out
        return [
            Profile("DS-003", 3407, float(args.phi_scale)),
            Profile("DS-002", 3401, float(args.phi_scale)),
            Profile("DS-006", 3401, float(args.phi_scale)),
        ]
    out: list[Profile] = []
    for ds in [d.upper() for d in parse_csv_list(args.datasets)]:
        for seed in range(args.seed_start, args.seed_end + 1):
            out.append(Profile(ds, seed, float(args.phi_scale)))
    return out


def enforce_prereg(args: argparse.Namespace) -> None:
    errors: list[str] = []
    ds = [d.upper() for d in parse_csv_list(args.datasets)]
    if ds != PREREG_DATASETS:
        errors.append(f"datasets must be {PREREG_DATASETS}, got {ds}")
    if args.seed_start != PREREG_SEED_START or args.seed_end != PREREG_SEED_END:
        errors.append(f"seed range must be {PREREG_SEED_START}..{PREREG_SEED_END}")
    if abs(args.phi_scale - PREREG_PHI_SCALE) > 1e-12:
        errors.append(f"phi_scale must be {PREREG_PHI_SCALE}")
    if abs(args.signal_threshold - PREREG_SIGNAL_THRESHOLD) > 1e-12:
        errors.append(f"signal_threshold must be {PREREG_SIGNAL_THRESHOLD}")
    if abs(args.high_signal_quantile - PREREG_HIGH_SIGNAL_QUANTILE) > 1e-12:
        errors.append(f"high_signal_quantile must be {PREREG_HIGH_SIGNAL_QUANTILE}")
    if abs(args.low_corr_min - PREREG_LOW_CORR_MIN) > 1e-12:
        errors.append(f"low_corr_min must be {PREREG_LOW_CORR_MIN}")
    if abs(args.low_r2_min - PREREG_LOW_R2_MIN) > 1e-12:
        errors.append(f"low_r2_min must be {PREREG_LOW_R2_MIN}")
    if abs(args.high_corr_min - PREREG_HIGH_CORR_MIN) > 1e-12:
        errors.append(f"high_corr_min must be {PREREG_HIGH_CORR_MIN}")
    if abs(args.high_cos_min - PREREG_HIGH_COS_MIN) > 1e-12:
        errors.append(f"high_cos_min must be {PREREG_HIGH_COS_MIN}")
    if abs(args.high_r2_origin_min - PREREG_HIGH_R2_ORIGIN_MIN) > 1e-12:
        errors.append(f"high_r2_origin_min must be {PREREG_HIGH_R2_ORIGIN_MIN}")
    if abs(args.v2_low_signal_ratio - PREREG_V2_LOW_SIGNAL_RATIO) > 1e-12:
        errors.append(f"v2_low_signal_ratio must be {PREREG_V2_LOW_SIGNAL_RATIO}")
    if abs(args.v2_corr_min - PREREG_V2_CORR_MIN) > 1e-12:
        errors.append(f"v2_corr_min must be {PREREG_V2_CORR_MIN}")
    if abs(args.v2_r2_min - PREREG_V2_R2_MIN) > 1e-12:
        errors.append(f"v2_r2_min must be {PREREG_V2_R2_MIN}")
    if errors:
        raise ValueError("strict prereg violation: " + "; ".join(errors))


def write_report(path: Path, rows: list[dict[str, Any]], mode: str) -> None:
    def count_fail(key: str) -> int:
        return sum(1 for r in rows if r[key] != "pass")

    total = len(rows)
    fail_v1 = count_fail("g16b_v1_status")
    fail_v2 = count_fail("g16b_v2_status")
    fail_split = count_fail("g16b_split_status")

    pass_v1 = total - fail_v1
    pass_v2 = total - fail_v2
    pass_split = total - fail_split

    lines: list[str] = []
    lines.append("# G16b Split Protocol Candidate (v1)")
    lines.append("")
    lines.append(f"- mode: `{mode}`")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- profiles: `{total}`")
    lines.append(f"- g16b_v1_pass: `{pass_v1}`")
    lines.append(f"- g16b_v2_pass: `{pass_v2}`")
    lines.append(f"- g16b_split_pass: `{pass_split}`")
    lines.append("")

    if mode == "prereg":
        low_rows = [r for r in rows if r["signal_regime"] == "low"]
        high_rows = [r for r in rows if r["signal_regime"] == "high"]
        low_v1_fail = sum(1 for r in low_rows if r["g16b_v1_status"] != "pass")
        low_split_fail = sum(1 for r in low_rows if r["g16b_split_status"] != "pass")
        high_v1_fail = sum(1 for r in high_rows if r["g16b_v1_status"] != "pass")
        high_split_fail = sum(1 for r in high_rows if r["g16b_split_status"] != "pass")
        overall_non_degrade = fail_split <= fail_v1
        low_improve = low_split_fail < low_v1_fail
        high_non_degrade = high_split_fail <= high_v1_fail

        lines.append("## Pre-Registered Split Checks")
        lines.append("")
        lines.append("- criteria:")
        lines.append("  - low-signal fail count improves vs v1")
        lines.append("  - high-signal fail count does not degrade vs v1")
        lines.append("  - overall fail count does not degrade vs v1")
        lines.append(f"- low-signal: v1_fail={low_v1_fail}, split_fail={low_split_fail}, pass={str(low_improve).lower()}")
        lines.append(f"- high-signal: v1_fail={high_v1_fail}, split_fail={high_split_fail}, pass={str(high_non_degrade).lower()}")
        lines.append(f"- overall: v1_fail={fail_v1}, split_fail={fail_split}, pass={str(overall_non_degrade).lower()}")
        if low_improve and high_non_degrade and overall_non_degrade:
            verdict = "candidate acceptable for next promotion grid"
        else:
            verdict = "candidate NOT acceptable yet"
        lines.append(f"- verdict: `{verdict}`")
        lines.append("")

    lines.append("## Dataset Summary")
    lines.append("")
    lines.append("| dataset | n | v1_fail | v2_fail | split_fail |")
    lines.append("| --- | --- | --- | --- | --- |")
    for ds in sorted({r["dataset_id"] for r in rows}):
        sub = [r for r in rows if r["dataset_id"] == ds]
        lines.append(
            f"| {ds} | {len(sub)} | "
            f"{sum(1 for r in sub if r['g16b_v1_status'] != 'pass')} | "
            f"{sum(1 for r in sub if r['g16b_v2_status'] != 'pass')} | "
            f"{sum(1 for r in sub if r['g16b_split_status'] != 'pass')} |"
        )
    lines.append("")

    lines.append("## Regime Summary")
    lines.append("")
    lines.append("| regime | n | v1_fail | v2_fail | split_fail |")
    lines.append("| --- | --- | --- | --- | --- |")
    for reg in ["low", "high"]:
        sub = [r for r in rows if r["signal_regime"] == reg]
        lines.append(
            f"| {reg} | {len(sub)} | "
            f"{sum(1 for r in sub if r['g16b_v1_status'] != 'pass')} | "
            f"{sum(1 for r in sub if r['g16b_v2_status'] != 'pass')} | "
            f"{sum(1 for r in sub if r['g16b_split_status'] != 'pass')} |"
        )
    lines.append("")

    # limit long changed list for readability
    changed_vs_v1 = [r for r in rows if r["g16b_v1_status"] != r["g16b_split_status"]]
    lines.append("## Decision Changes vs v1 (first 40)")
    lines.append("")
    lines.append("| dataset | seed | regime | v1 | split | signal_index | abs_pearson_full | abs_cosine_full | r2_origin_full |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in sorted(changed_vs_v1, key=lambda x: (x["dataset_id"], int(x["seed"])))[:40]:
        lines.append(
            f"| {r['dataset_id']} | {r['seed']} | {r['signal_regime']} | {r['g16b_v1_status']} | {r['g16b_split_status']} | "
            f"{r['signal_index_p90_abs_t11']} | {r['abs_pearson_full']} | {r['abs_cosine_full']} | {r['r2_origin_full']} |"
        )
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    source_runs = Path(args.source_runs_dir).resolve()
    if not source_runs.exists():
        raise FileNotFoundError(f"source runs not found: {source_runs}")

    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir.strip()
        else (DEFAULT_OUT_SANITY if args.mode == "sanity" else DEFAULT_OUT_PREREG).resolve()
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.strict_prereg:
        enforce_prereg(args)

    profiles = build_profiles(args)
    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        logs.append(msg)

    log("=" * 72)
    log(f"G16b split protocol v1 ({args.mode})")
    log(f"start_utc={datetime.utcnow().isoformat()}Z")
    log(f"profiles={len(profiles)}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    for idx, profile in enumerate(profiles, start=1):
        run_dir = source_runs / profile.tag / "g16"
        action_csv = run_dir / "action.csv"
        metric_csv = run_dir / "metric_checks_action.csv"
        if not action_csv.exists():
            log(f"[{idx}/{len(profiles)}] missing action: {run_dir.as_posix()}")
            continue
        g11_vals, t11_vals = read_action_vectors(action_csv)
        if not g11_vals or not t11_vals:
            log(f"[{idx}/{len(profiles)}] empty vectors: {run_dir.as_posix()}")
            continue

        metrics = parse_metric_checks(metric_csv)
        g16a_status = metrics.get("G16a", {}).get("status", "").strip().lower() or "fail"
        g16b_v1_status = metrics.get("G16b", {}).get("status", "").strip().lower()
        g16c_status = metrics.get("G16c", {}).get("status", "").strip().lower() or "fail"
        g16d_status = metrics.get("G16d", {}).get("status", "").strip().lower() or "fail"

        abs_t = [abs(v) for v in t11_vals]
        signal_index = percentile(abs_t, 0.90)
        signal_regime = "low" if signal_index <= args.signal_threshold else "high"

        # shared metrics
        pear_full = pearson_corr(t11_vals, g11_vals)
        spear_full = spearman_corr(t11_vals, g11_vals)
        r2_full = ols_r2(t11_vals, g11_vals)
        cos_full = cosine_similarity(t11_vals, g11_vals)
        r2_origin_full = r2_origin(t11_vals, g11_vals)
        abs_pear_full = abs(pear_full) if not math.isnan(pear_full) else float("nan")
        abs_spear_full = abs(spear_full) if not math.isnan(spear_full) else float("nan")
        abs_cos_full = abs(cos_full) if not math.isnan(cos_full) else float("nan")

        g_hs, t_hs, hs_thr = high_signal_subset(g11_vals, t11_vals, args.high_signal_quantile)
        pear_hs = pearson_corr(t_hs, g_hs)
        spear_hs = spearman_corr(t_hs, g_hs)
        r2_hs = ols_r2(t_hs, g_hs)
        abs_pear_hs = abs(pear_hs) if not math.isnan(pear_hs) else float("nan")
        abs_spear_hs = abs(spear_hs) if not math.isnan(spear_hs) else float("nan")

        # v2 comparator (legacy candidate from prior run)
        t_mean, t_std = mean_std(t11_vals)
        v2_ratio = (t_std / abs(t_mean)) if (not math.isnan(t_std) and not math.isnan(t_mean) and abs(t_mean) > 1e-12) else float("inf")
        v2_low = v2_ratio > args.v2_low_signal_ratio
        if v2_low:
            v2_corr_ok = (abs_pear_hs > args.v2_corr_min) and (abs_spear_hs > args.v2_corr_min)
            v2_r2_ok = r2_hs > args.v2_r2_min
        else:
            v2_corr_ok = (abs_pear_full > args.v2_corr_min) and (abs_spear_full > args.v2_corr_min)
            v2_r2_ok = r2_full > args.v2_r2_min
        g16b_v2_status = "pass" if (v2_corr_ok and v2_r2_ok) else "fail"

        if not g16b_v1_status:
            g16b_v1_status = "pass" if r2_full > 0.05 else "fail"

        # split candidate
        low_pass = (
            (abs_pear_hs > args.low_corr_min)
            and (abs_spear_hs > args.low_corr_min)
            and (r2_hs > args.low_r2_min)
        )
        high_pass = (
            (abs_pear_full > args.high_corr_min)
            and (abs_cos_full > args.high_cos_min)
            and (r2_origin_full > args.high_r2_origin_min)
        )
        g16b_split_status = "pass" if (low_pass if signal_regime == "low" else high_pass) else "fail"

        g16_v1_status = "pass" if all(s == "pass" for s in [g16a_status, g16b_v1_status, g16c_status, g16d_status]) else "fail"
        g16_v2_status = "pass" if all(s == "pass" for s in [g16a_status, g16b_v2_status, g16c_status, g16d_status]) else "fail"
        g16_split_status = "pass" if all(s == "pass" for s in [g16a_status, g16b_split_status, g16c_status, g16d_status]) else "fail"

        rows.append(
            {
                "dataset_id": profile.dataset_id,
                "seed": profile.seed,
                "phi_scale": f"{profile.phi_scale:.2f}",
                "signal_index_name": PREREG_SIGNAL_INDEX_NAME,
                "signal_index_p90_abs_t11": f6(signal_index),
                "signal_threshold": f6(args.signal_threshold),
                "signal_regime": signal_regime,
                "g16a_status": g16a_status,
                "g16b_v1_status": g16b_v1_status,
                "g16b_v2_status": g16b_v2_status,
                "g16b_split_status": g16b_split_status,
                "g16c_status": g16c_status,
                "g16d_status": g16d_status,
                "g16_v1_status": g16_v1_status,
                "g16_v2_status": g16_v2_status,
                "g16_split_status": g16_split_status,
                "t11_mean": f6(t_mean),
                "t11_std": f6(t_std),
                "v2_low_signal_ratio": f6(v2_ratio),
                "v2_low_signal_flag": "true" if v2_low else "false",
                "high_signal_quantile": f6(args.high_signal_quantile),
                "high_signal_count": len(t_hs),
                "high_signal_abs_t11_min": f6(hs_thr),
                "pearson_full": f6(pear_full),
                "spearman_full": f6(spear_full),
                "r2_full": f6(r2_full),
                "abs_pearson_full": f6(abs_pear_full),
                "abs_spearman_full": f6(abs_spear_full),
                "cosine_full": f6(cos_full),
                "abs_cosine_full": f6(abs_cos_full),
                "r2_origin_full": f6(r2_origin_full),
                "pearson_high_signal": f6(pear_hs),
                "spearman_high_signal": f6(spear_hs),
                "r2_high_signal": f6(r2_hs),
                "abs_pearson_high_signal": f6(abs_pear_hs),
                "abs_spearman_high_signal": f6(abs_spear_hs),
                "low_corr_min": f6(args.low_corr_min),
                "low_r2_min": f6(args.low_r2_min),
                "high_corr_min": f6(args.high_corr_min),
                "high_cos_min": f6(args.high_cos_min),
                "high_r2_origin_min": f6(args.high_r2_origin_min),
                "source_run_root": run_dir.resolve().relative_to(ROOT.resolve()).as_posix(),
            }
        )

        if idx % 50 == 0 or idx == len(profiles):
            log(f"[{idx}/{len(profiles)}] processed")

    if not rows:
        raise RuntimeError("no rows produced; check source run directory and profile filters")

    fieldnames = list(rows[0].keys())
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, fieldnames)

    report_md = out_dir / "report.md"
    write_report(report_md, rows, args.mode)

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "strict_prereg": bool(args.strict_prereg),
        "datasets": parse_csv_list(args.datasets),
        "seed_start": args.seed_start,
        "seed_end": args.seed_end,
        "phi_scale": args.phi_scale,
        "signal_index_name": PREREG_SIGNAL_INDEX_NAME,
        "signal_threshold": args.signal_threshold,
        "high_signal_quantile": args.high_signal_quantile,
        "low_gate": {
            "abs_pearson_min": args.low_corr_min,
            "abs_spearman_min": args.low_corr_min,
            "r2_min": args.low_r2_min,
        },
        "high_gate": {
            "abs_pearson_min": args.high_corr_min,
            "abs_cosine_min": args.high_cos_min,
            "r2_origin_min": args.high_r2_origin_min,
        },
        "v2_comparator": {
            "low_signal_ratio_threshold": args.v2_low_signal_ratio,
            "abs_corr_min": args.v2_corr_min,
            "r2_min": args.v2_r2_min,
        },
        "source_runs_dir": source_runs.as_posix(),
        "notes": [
            "Diagnostic candidate only; official G16b remains v1.",
            "No changes to run_qng_action_v1.py formulas or thresholds.",
            "Split-by-regime policy is evaluated post-run from frozen artifacts.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run-log-eval.txt").write_text("\n".join(logs) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    print(f"run_log:     {out_dir / 'run-log-eval.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

