#!/usr/bin/env python3
"""
Build G16 failure taxonomy from profile summaries (housekeeping only).

Diagnostics focus:
- G16 sub-gate failure signatures
- G16b component diagnostics (signal, linearity, monotonicity)
- Pass/fail taxonomy without changing thresholds/formulas
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_action_v1 import build_adjacency, build_dataset_graph  # noqa: E402


DEFAULT_SUMMARY_CSV = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-regression-baseline-v1"
    / "source_runs_grid20"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16-failure-taxonomy-v1"
)

ACTION_SCRIPT = ROOT / "scripts" / "run_qng_action_v1.py"
ACTION_METRIC_CSV = "metric_checks_action.csv"
ACTION_CONFIG_JSON = "config_action.json"
ACTION_VERTEX_CSV = "action.csv"

SUBGATES = ["G16a", "G16b", "G16c", "G16d"]


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int
    phi_scale: str
    source_row: dict[str, str]

    @property
    def tag(self) -> str:
        return f"{self.dataset_id.lower()}_seed{self.seed}_phi{self.phi_scale.replace('.', 'p')}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run G16 failure taxonomy diagnostics over summary profiles.")
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--reuse-existing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max-profiles", type=int, default=0, help="0 means all profiles.")
    parser.add_argument("--top-patterns", type=int, default=5)
    parser.add_argument("--peak-ratio-threshold", type=float, default=0.98)
    parser.add_argument("--peak-distance-threshold", type=float, default=0.10)
    parser.add_argument(
        "--high-signal-quantile",
        type=float,
        default=0.80,
        help="Quantile q for |T11| high-signal subset (top 1-q fraction).",
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_profiles(rows: list[dict[str, str]]) -> list[Profile]:
    dedup: dict[tuple[str, int, str], Profile] = {}
    for row in rows:
        key = (
            row["dataset_id"].strip(),
            int(row["seed"]),
            f"{float(row['phi_scale']):.2f}",
        )
        if key not in dedup:
            dedup[key] = Profile(
                dataset_id=key[0],
                seed=key[1],
                phi_scale=key[2],
                source_row=row,
            )
    profiles = list(dedup.values())
    profiles.sort(key=lambda p: (p.dataset_id, p.seed, float(p.phi_scale)))
    return profiles


def to_float(text: str) -> float | None:
    try:
        return float(text)
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


def read_metric_checks(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def parse_metric_checks(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        gid = row.get("gate_id", "").strip()
        if gid:
            out[gid] = row
    return out


def read_action_vectors(path: Path) -> tuple[list[float], list[float]]:
    if not path.exists():
        return [], []
    rows = read_csv(path)
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
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman_corr(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    xr = rank_values(x_vals)
    yr = rank_values(y_vals)
    return pearson_corr(xr, yr)


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


def high_signal_subset(
    g11_vals: list[float],
    t11_vals: list[float],
    quantile: float,
) -> tuple[list[float], list[float], float]:
    if not g11_vals or not t11_vals or len(g11_vals) != len(t11_vals):
        return [], [], float("nan")
    abs_t = [abs(v) for v in t11_vals]
    thr = percentile(abs_t, quantile)
    pairs = [(g11_vals[i], t11_vals[i]) for i in range(len(t11_vals)) if abs_t[i] >= thr]
    if not pairs:
        return [], [], thr
    gs = [p[0] for p in pairs]
    ts = [p[1] for p in pairs]
    return gs, ts, thr


def g16b_component_diagnostics(
    g11_vals: list[float],
    t11_vals: list[float],
    *,
    high_signal_quantile: float,
) -> dict[str, Any]:
    g11_mean, g11_std = mean_std(g11_vals)
    t11_mean, t11_std = mean_std(t11_vals)

    eps = max(1e-12, 0.05 * t11_std if not math.isnan(t11_std) else 1e-12)
    n = len(t11_vals)
    t11_pos = sum(1 for v in t11_vals if v > eps)
    t11_neg = sum(1 for v in t11_vals if v < -eps)
    t11_zero = max(0, n - t11_pos - t11_neg)

    std_to_mean = float("nan")
    if not math.isnan(t11_mean) and not math.isnan(t11_std):
        denom = abs(t11_mean)
        std_to_mean = (t11_std / denom) if denom > 1e-12 else float("inf")

    pear = pearson_corr(t11_vals, g11_vals)
    spear = spearman_corr(t11_vals, g11_vals)
    r2_full = ols_r2(t11_vals, g11_vals)

    g_hs, t_hs, abs_t11_hs_min = high_signal_subset(g11_vals, t11_vals, high_signal_quantile)
    pear_hs = pearson_corr(t_hs, g_hs) if t_hs else float("nan")
    spear_hs = spearman_corr(t_hs, g_hs) if t_hs else float("nan")
    r2_hs = ols_r2(t_hs, g_hs) if t_hs else float("nan")

    return {
        "g16b_n_vertices": n,
        "g11_mean": g11_mean,
        "g11_std": g11_std,
        "t11_mean": t11_mean,
        "t11_std": t11_std,
        "t11_pos_frac": (t11_pos / n) if n else float("nan"),
        "t11_neg_frac": (t11_neg / n) if n else float("nan"),
        "t11_near_zero_frac": (t11_zero / n) if n else float("nan"),
        "t11_std_to_abs_mean": std_to_mean,
        "pearson_r": pear,
        "spearman_rho": spear,
        "r2_full_recomputed": r2_full,
        "high_signal_quantile": high_signal_quantile,
        "high_signal_count": len(t_hs),
        "high_signal_abs_t11_min": abs_t11_hs_min,
        "pearson_r_high_signal": pear_hs,
        "spearman_rho_high_signal": spear_hs,
        "r2_high_signal": r2_hs,
    }


def g16b_cause_hint(row: dict[str, Any]) -> str:
    if str(row.get("g16b_status", "")).strip().lower() == "pass":
        return "pass"
    ratio = to_float(str(row.get("t11_std_to_abs_mean", "")))
    r2_full = to_float(str(row.get("r2_G11_T11", "")))
    r2_hs = to_float(str(row.get("r2_high_signal", "")))
    pear = abs(to_float(str(row.get("pearson_r", ""))) or 0.0)
    spear = abs(to_float(str(row.get("spearman_rho", ""))) or 0.0)
    if ratio is not None and ratio >= 8.0:
        return "low_signal_t11"
    if r2_full is not None and r2_full < 0.05 and r2_hs is not None and r2_hs >= 0.05 and spear >= 0.35:
        return "monotonic_nonlinear"
    if pear < 0.2 and spear < 0.2:
        return "weak_coupling"
    return "borderline_linear_fit"


def g16b_issue_axis(cause_hint: str) -> str:
    if cause_hint == "pass":
        return "pass"
    if cause_hint == "low_signal_t11":
        return "A_t11_discretization_noise"
    if cause_hint == "monotonic_nonlinear":
        return "B_operator_mismatch_or_nonlinearity"
    if cause_hint == "weak_coupling":
        return "A_or_B_weak_alignment"
    return "A_or_B_borderline"


def run_action(profile: Profile, out_dir: Path) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(ACTION_SCRIPT),
        "--dataset-id",
        profile.dataset_id,
        "--seed",
        str(profile.seed),
        "--phi-scale",
        profile.phi_scale,
        "--no-plots",
        "--out-dir",
        str(out_dir),
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-8:]) if merged else ""
    return proc.returncode, tail


def euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def sigma_features(
    dataset_id: str,
    seed: int,
    *,
    peak_ratio_threshold: float,
    peak_distance_threshold: float,
) -> dict[str, Any]:
    coords, sigma, adj_list = build_dataset_graph(dataset_id, seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / float(n) if n else float("nan")

    sigma_max = max(sigma) if sigma else 1.0
    sigma_norm = [s / sigma_max for s in sigma]
    sigma_mean = statistics.mean(sigma_norm) if sigma_norm else float("nan")
    sigma_std = statistics.pstdev(sigma_norm) if len(sigma_norm) > 1 else 0.0
    sigma_cv = sigma_std / sigma_mean if sigma_mean and not math.isnan(sigma_mean) else float("nan")

    sorted_idx = sorted(range(n), key=lambda i: sigma_norm[i], reverse=True)
    i1 = sorted_idx[0] if sorted_idx else 0
    i2 = sorted_idx[1] if len(sorted_idx) > 1 else i1
    peak1 = sigma_norm[i1] if sorted_idx else float("nan")
    peak2 = sigma_norm[i2] if len(sorted_idx) > 1 else peak1
    peak_ratio = (peak2 / peak1) if peak1 and not math.isnan(peak1) else float("nan")
    d12 = euclidean(coords[i1], coords[i2]) if len(sorted_idx) > 1 else 0.0

    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    span_diag = math.hypot((max(xs) - min(xs)) if xs else 0.0, (max(ys) - min(ys)) if ys else 0.0)
    d12_norm = d12 / span_diag if span_diag > 1e-12 else 0.0

    is_multi_peak = bool(
        (not math.isnan(peak_ratio))
        and peak_ratio >= peak_ratio_threshold
        and d12_norm >= peak_distance_threshold
    )

    return {
        "n_nodes": n,
        "mean_degree": mean_degree,
        "sigma_mean": sigma_mean,
        "sigma_std": sigma_std,
        "sigma_cv": sigma_cv,
        "sigma_p90": percentile(sigma_norm, 0.90),
        "sigma_p10": percentile(sigma_norm, 0.10),
        "peak1_sigma": peak1,
        "peak2_sigma": peak2,
        "peak2_to_peak1": peak_ratio,
        "peak12_distance": d12,
        "peak12_distance_norm": d12_norm,
        "multi_peak_flag_default": "true" if is_multi_peak else "false",
    }


def fail_signature(sub_status: dict[str, str]) -> str:
    failed = [g for g in SUBGATES if sub_status.get(g, "").lower() != "pass"]
    return "+".join(failed) if failed else "NONE"


def summarize_fail_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {g: 0 for g in SUBGATES}
    for row in rows:
        for g in SUBGATES:
            if str(row.get(f"{g.lower()}_status", "")).strip().lower() != "pass":
                counts[g] += 1
    return counts


def group_count(rows: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    out: dict[str, int] = {}
    for row in rows:
        v = str(row.get(key, "")).strip()
        out[v] = out.get(v, 0) + 1
    return sorted(out.items(), key=lambda kv: (-kv[1], kv[0]))


def mean_of(rows: list[dict[str, Any]], key: str) -> float:
    vals: list[float] = []
    for row in rows:
        value = to_float(str(row.get(key, "")))
        if value is not None:
            vals.append(value)
    return statistics.mean(vals) if vals else float("nan")


def write_report(
    path: Path,
    *,
    all_rows: list[dict[str, Any]],
    fail_rows: list[dict[str, Any]],
    pass_rows: list[dict[str, Any]],
    fail_counts: dict[str, int],
    top_patterns: int,
) -> None:
    lines: list[str] = []
    lines.append("# G16 Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- profiles_total: `{len(all_rows)}`")
    lines.append(f"- g16_fail: `{len(fail_rows)}`")
    lines.append(f"- g16_pass: `{len(pass_rows)}`")
    lines.append("- thresholds/formulas: unchanged (diagnostic-only run)")
    lines.append("")

    lines.append("## Sub-Gate Failure Counts")
    lines.append("")
    lines.append("| subgate | fail_count |")
    lines.append("| --- | --- |")
    for g in SUBGATES:
        lines.append(f"| {g} | {fail_counts[g]} |")
    lines.append("")

    lines.append("## G16b Cause Hints")
    lines.append("")
    lines.append("| cause_hint | count |")
    lines.append("| --- | --- |")
    for cause, cnt in group_count(fail_rows, "g16b_cause_hint"):
        lines.append(f"| {cause} | {cnt} |")
    lines.append("")

    lines.append("## G16b Issue Axes (A/B)")
    lines.append("")
    lines.append("| issue_axis | count |")
    lines.append("| --- | --- |")
    for axis, cnt in group_count(fail_rows, "g16b_issue_axis"):
        lines.append(f"| {axis} | {cnt} |")
    lines.append("")

    lines.append("## Dataset Fail Split")
    lines.append("")
    lines.append("| dataset | fail_count | pass_count | fail_rate |")
    lines.append("| --- | --- | --- | --- |")
    by_ds_fail = dict(group_count(fail_rows, "dataset_id"))
    by_ds_pass = dict(group_count(pass_rows, "dataset_id"))
    for ds in sorted(set(list(by_ds_fail.keys()) + list(by_ds_pass.keys()))):
        fcnt = by_ds_fail.get(ds, 0)
        pcnt = by_ds_pass.get(ds, 0)
        denom = fcnt + pcnt
        rate = (fcnt / float(denom)) if denom else float("nan")
        lines.append(f"| {ds} | {fcnt} | {pcnt} | {f6(rate)} |")
    lines.append("")

    lines.append("## Pass vs Fail Means (G16b Diagnostics)")
    lines.append("")
    lines.append("| feature | fail_mean | pass_mean |")
    lines.append("| --- | --- | --- |")
    for feature in [
        "t11_std_to_abs_mean",
        "pearson_r",
        "spearman_rho",
        "r2_G11_T11",
        "r2_high_signal",
        "mean_degree",
        "sigma_std",
        "peak2_to_peak1",
        "peak12_distance_norm",
    ]:
        lines.append(f"| {feature} | {f6(mean_of(fail_rows, feature))} | {f6(mean_of(pass_rows, feature))} |")
    lines.append("")

    lines.append("## Pattern Notes")
    lines.append("")
    patterns = group_count(fail_rows, "g16b_cause_hint")[:top_patterns]
    if not patterns:
        lines.append("- No G16 failures in analyzed profiles.")
    else:
        for idx, (cause, cnt) in enumerate(patterns, start=1):
            sample = [r for r in fail_rows if r.get("g16b_cause_hint") == cause][:2]
            ex = ", ".join(f"{r['dataset_id']}/seed{r['seed']}" for r in sample) if sample else "n/a"
            lines.append(f"{idx}. `{cause}` appears `{cnt}` times; examples: `{ex}`.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    runs_root = out_dir / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        print(f"[error] summary CSV not found: {summary_csv}")
        return 2

    profiles = parse_profiles(read_csv(summary_csv))
    if args.max_profiles > 0:
        profiles = profiles[: args.max_profiles]

    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        logs.append(msg)

    log("=" * 72)
    log("G16 failure taxonomy v1")
    log(f"start_utc={datetime.utcnow().isoformat()}Z")
    log(f"profiles={len(profiles)}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    for idx, profile in enumerate(profiles, start=1):
        prof_dir = runs_root / profile.tag / "g16"
        prof_dir.mkdir(parents=True, exist_ok=True)
        metric_csv = prof_dir / ACTION_METRIC_CSV
        config_json = prof_dir / ACTION_CONFIG_JSON
        vertex_csv = prof_dir / ACTION_VERTEX_CSV

        log(f"[{idx}/{len(profiles)}] {profile.tag}")
        needs_run = not (args.reuse_existing and metric_csv.exists() and config_json.exists() and vertex_csv.exists())
        if needs_run:
            rc, tail = run_action(profile, prof_dir)
            log(f"  run_action rc={rc}")
            if rc != 0 and tail:
                log("  tail:")
                for line in tail.splitlines():
                    log(f"    {line}")

        metric_rows = read_metric_checks(metric_csv)
        metrics = parse_metric_checks(metric_rows)
        cfg: dict[str, Any] = {}
        if config_json.exists():
            cfg = json.loads(config_json.read_text(encoding="utf-8"))

        g11_vals, t11_vals = read_action_vectors(vertex_csv)
        comp = g16b_component_diagnostics(
            g11_vals,
            t11_vals,
            high_signal_quantile=min(max(args.high_signal_quantile, 0.0), 0.99),
        )

        sub_status = {g: metrics.get(g, {}).get("status", "").strip().lower() for g in SUBGATES}
        final_status = metrics.get("FINAL", {}).get("status", "").strip().lower() or "fail"

        sig = sigma_features(
            profile.dataset_id,
            profile.seed,
            peak_ratio_threshold=args.peak_ratio_threshold,
            peak_distance_threshold=args.peak_distance_threshold,
        )

        g16b_legacy_row = metrics.get("G16b-v1", {}) or metrics.get("G16b", {})

        row: dict[str, Any] = {
            "dataset_id": profile.dataset_id,
            "seed": profile.seed,
            "phi_scale": profile.phi_scale,
            "g16_status": final_status,
            "g16a_status": sub_status["G16a"],
            "g16b_status": sub_status["G16b"],
            "g16c_status": sub_status["G16c"],
            "g16d_status": sub_status["G16d"],
            "fail_signature": fail_signature(sub_status),
            "closure_rel": metrics.get("G16a", {}).get("value", ""),
            "r2_G11_T11": g16b_legacy_row.get("value", ""),
            "m_sq_abs": metrics.get("G16c", {}).get("value", ""),
            "hessian_frac_neg": metrics.get("G16d", {}).get("value", ""),
            "n_nodes": cfg.get("n_nodes", sig["n_nodes"]),
            "mean_degree": f6(to_float(str(cfg.get("mean_degree", ""))) or sig["mean_degree"]),
            "sigma_mean": f6(sig["sigma_mean"]),
            "sigma_std": f6(sig["sigma_std"]),
            "sigma_cv": f6(sig["sigma_cv"]),
            "sigma_p90": f6(sig["sigma_p90"]),
            "sigma_p10": f6(sig["sigma_p10"]),
            "peak1_sigma": f6(sig["peak1_sigma"]),
            "peak2_sigma": f6(sig["peak2_sigma"]),
            "peak2_to_peak1": f6(sig["peak2_to_peak1"]),
            "peak12_distance": f6(sig["peak12_distance"]),
            "peak12_distance_norm": f6(sig["peak12_distance_norm"]),
            "multi_peak_flag_default": sig["multi_peak_flag_default"],
            "g16b_n_vertices": comp["g16b_n_vertices"],
            "g11_mean": f6(comp["g11_mean"]),
            "g11_std": f6(comp["g11_std"]),
            "t11_mean": f6(comp["t11_mean"]),
            "t11_std": f6(comp["t11_std"]),
            "t11_pos_frac": f6(comp["t11_pos_frac"]),
            "t11_neg_frac": f6(comp["t11_neg_frac"]),
            "t11_near_zero_frac": f6(comp["t11_near_zero_frac"]),
            "t11_std_to_abs_mean": f6(comp["t11_std_to_abs_mean"]),
            "pearson_r": f6(comp["pearson_r"]),
            "spearman_rho": f6(comp["spearman_rho"]),
            "r2_full_recomputed": f6(comp["r2_full_recomputed"]),
            "high_signal_quantile": f6(comp["high_signal_quantile"]),
            "high_signal_count": comp["high_signal_count"],
            "high_signal_abs_t11_min": f6(comp["high_signal_abs_t11_min"]),
            "pearson_r_high_signal": f6(comp["pearson_r_high_signal"]),
            "spearman_rho_high_signal": f6(comp["spearman_rho_high_signal"]),
            "r2_high_signal": f6(comp["r2_high_signal"]),
            "g11_status": profile.source_row.get("g11_status", ""),
            "g12_status": profile.source_row.get("g12_status", ""),
            "g13_status": profile.source_row.get("g13_status", ""),
            "g14_status": profile.source_row.get("g14_status", ""),
            "g15_status": profile.source_row.get("g15_status", ""),
            "g15b_v2_status": profile.source_row.get("g15b_v2_status", ""),
            "all_pass_official": profile.source_row.get("all_pass_official", ""),
            "all_pass_diagnostic": profile.source_row.get("all_pass_diagnostic", profile.source_row.get("all_pass", "")),
            "source_run_root": profile.source_row.get("run_root", ""),
            "action_run_root": (prof_dir.resolve().relative_to(ROOT.resolve())).as_posix(),
        }
        row["g16b_cause_hint"] = g16b_cause_hint(row)
        row["g16b_issue_axis"] = g16b_issue_axis(str(row["g16b_cause_hint"]))
        rows.append(row)

    fail_rows = [r for r in rows if str(r.get("g16_status", "")).lower() != "pass"]
    pass_rows = [r for r in rows if str(r.get("g16_status", "")).lower() == "pass"]
    fail_counts = summarize_fail_counts(fail_rows)

    fieldnames = [
        "dataset_id",
        "seed",
        "phi_scale",
        "g16_status",
        "g16a_status",
        "g16b_status",
        "g16c_status",
        "g16d_status",
        "fail_signature",
        "g16b_cause_hint",
        "g16b_issue_axis",
        "closure_rel",
        "r2_G11_T11",
        "m_sq_abs",
        "hessian_frac_neg",
        "n_nodes",
        "mean_degree",
        "sigma_mean",
        "sigma_std",
        "sigma_cv",
        "sigma_p90",
        "sigma_p10",
        "peak1_sigma",
        "peak2_sigma",
        "peak2_to_peak1",
        "peak12_distance",
        "peak12_distance_norm",
        "multi_peak_flag_default",
        "g16b_n_vertices",
        "g11_mean",
        "g11_std",
        "t11_mean",
        "t11_std",
        "t11_pos_frac",
        "t11_neg_frac",
        "t11_near_zero_frac",
        "t11_std_to_abs_mean",
        "pearson_r",
        "spearman_rho",
        "r2_full_recomputed",
        "high_signal_quantile",
        "high_signal_count",
        "high_signal_abs_t11_min",
        "pearson_r_high_signal",
        "spearman_rho_high_signal",
        "r2_high_signal",
        "g11_status",
        "g12_status",
        "g13_status",
        "g14_status",
        "g15_status",
        "g15b_v2_status",
        "all_pass_official",
        "all_pass_diagnostic",
        "source_run_root",
        "action_run_root",
    ]

    fail_csv = out_dir / "g16_fail_cases.csv"
    pass_csv = out_dir / "g16_pass_cases.csv"
    diag_csv = out_dir / "g16b_component_diagnostics.csv"

    write_csv(fail_csv, fail_rows, fieldnames)
    write_csv(pass_csv, pass_rows, fieldnames)
    write_csv(diag_csv, rows, fieldnames)

    report_md = out_dir / "g16_failure_taxonomy.md"
    write_report(
        report_md,
        all_rows=rows,
        fail_rows=fail_rows,
        pass_rows=pass_rows,
        fail_counts=fail_counts,
        top_patterns=max(1, args.top_patterns),
    )

    run_log = out_dir / "run-log-g16-taxonomy.txt"
    run_log.write_text("\n".join(logs) + "\n", encoding="utf-8")

    print(f"g16_fail_cases: {fail_csv}")
    print(f"g16_pass_cases: {pass_csv}")
    print(f"g16b_diag_csv:  {diag_csv}")
    print(f"taxonomy_md:    {report_md}")
    print(f"run_log:        {run_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
