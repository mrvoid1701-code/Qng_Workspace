#!/usr/bin/env python3
"""
Executable suite for QNG P2 cosmology tests:
- QNG-T-050
- QNG-T-051
- QNG-T-053

This runner uses a reproducible toy node-growth simulation (stdlib only) to produce:
- per-test metrics
- robustness summaries across seeds
- plots and logs for evidence files
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import json
import math
import platform
import random
import statistics
import struct
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_ROOT = ROOT / "05_validation" / "evidence" / "artifacts"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class SimSeries:
    seed: int
    t: list[int]
    n: list[float]
    a_model: list[float]
    a_obs: list[float]
    complexity: list[float]
    omega: list[float]
    s_obs: list[float]
    sigma: list[float]


@dataclass
class RunMetrics:
    seed: int
    corr_a_n13: float
    corr_complexity_n: float
    slope_complexity_n: float
    corr_expansion_complexity: float
    r2_scale: float
    mape_scale: float
    k_entropy_fit: float
    r2_entropy: float
    omega_monotonic_ratio: float
    entropy_monotonic_ratio: float


def safe_float(text: str | None, default: float | None = None) -> float | None:
    if text is None:
        return default
    t = str(text).strip()
    if not t:
        return default
    try:
        return float(t)
    except ValueError:
        return default


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def read_dataset_manifest(dataset_id: str) -> dict | None:
    if not DATASET_MANIFEST_JSON.exists():
        return None
    try:
        rows = json.loads(DATASET_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("dataset_id") == dataset_id:
            return row
    return None


def pearson_corr(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    sx = statistics.pstdev(x)
    sy = statistics.pstdev(y)
    if sx <= 1e-12 or sy <= 1e-12:
        return float("nan")
    cov = statistics.fmean((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / (sx * sy)


def linear_fit(x: list[float], y: list[float]) -> tuple[float, float]:
    if len(x) != len(y) or len(x) < 2:
        return float("nan"), float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    den = statistics.fmean((a - mx) ** 2 for a in x)
    if den <= 1e-12:
        return float("nan"), float("nan")
    cov = statistics.fmean((a - mx) * (b - my) for a, b in zip(x, y))
    slope = cov / den
    intercept = my - slope * mx
    return slope, intercept


def fit_through_origin(x: list[float], y: list[float]) -> float:
    den = sum(v * v for v in x)
    if den <= 1e-12:
        return float("nan")
    num = sum(a * b for a, b in zip(x, y))
    return num / den


def r2_score(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) != len(y_pred) or len(y_true) < 2:
        return float("nan")
    mean_y = statistics.fmean(y_true)
    ss_tot = sum((y - mean_y) ** 2 for y in y_true)
    ss_res = sum((y - p) ** 2 for y, p in zip(y_true, y_pred))
    if ss_tot <= 1e-12:
        return float("nan")
    return 1.0 - (ss_res / ss_tot)


def mape(y_true: list[float], y_pred: list[float]) -> float:
    vals: list[float] = []
    for y, p in zip(y_true, y_pred):
        den = max(abs(y), 1e-9)
        vals.append(abs(y - p) / den)
    return statistics.fmean(vals) if vals else float("nan")


def monotonic_ratio(values: list[float], tolerance: float = 0.0) -> float:
    if len(values) < 2:
        return float("nan")
    good = 0
    for a, b in zip(values[:-1], values[1:]):
        if (b - a) >= -abs(tolerance):
            good += 1
    return good / (len(values) - 1)


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": float("nan"), "std": float("nan"), "cv": float("inf"), "min": float("nan"), "max": float("nan")}
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv = std_v / abs(mean_v) if abs(mean_v) > 1e-12 else float("inf")
    return {
        "count": float(len(values)),
        "mean": mean_v,
        "std": std_v,
        "cv": cv,
        "min": min(values),
        "max": max(values),
    }


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    span = hi - lo
    if span <= 1e-12:
        return [0.5 for _ in values]
    return [(v - lo) / span for v in values]


def simulate_node_growth(
    seed: int,
    steps: int,
    sigma_min: float,
    base_growth: float,
    memory_weight: float,
    noise_scale: float,
) -> SimSeries:
    rng = random.Random(seed)
    t = list(range(steps + 1))

    n0 = 1200.0 + rng.random() * 160.0
    n_val = n0
    complexity = 0.9 * n0
    omega = 4200.0 + rng.random() * 200.0
    prev_growth = 0.018 + rng.random() * 0.004

    n: list[float] = []
    a_model: list[float] = []
    a_obs: list[float] = []
    c_arr: list[float] = []
    omega_arr: list[float] = []
    s_obs: list[float] = []
    sigma_arr: list[float] = []

    for i in t:
        phase = 2.0 * math.pi * i / 37.0
        sigma = 0.62 + 0.13 * math.sin(phase) + rng.gauss(0.0, 0.025 * noise_scale)
        sigma = min(max(sigma, 0.22), 0.96)

        if i > 0:
            growth = (
                base_growth
                + 0.014 * max(0.0, sigma - sigma_min)
                + memory_weight * prev_growth
                + rng.gauss(0.0, 0.0016 * noise_scale)
            )
            growth = max(growth, 0.0006)
            d_n = max(1.0, n_val * growth)
            n_val += d_n
            prev_growth = growth

            c_gain = (
                0.31 * d_n
                + 0.004 * math.sqrt(max(n_val, 1.0)) * (0.65 + sigma)
                + rng.gauss(0.0, 1.8 * noise_scale)
            )
            complexity = max(complexity + c_gain, 1.0)

            reconfig = (
                0.092 * d_n
                + 0.011 * complexity
                + abs(rng.gauss(0.0, 3.6 * noise_scale))
            )
            omega += max(reconfig, 1.0)

        a_mod = (n_val / n0) ** (1.0 / 3.0)
        obs_noise = 0.008 * math.sin(2.0 * math.pi * i / 29.0) + rng.gauss(0.0, 0.009 * noise_scale)
        a_meas = max(1e-6, a_mod * (1.0 + obs_noise))

        log_omega = math.log(max(omega, 1.0))
        s_meas = log_omega + 0.035 * abs(prev_growth) + rng.gauss(0.0, 0.007 * noise_scale)

        n.append(n_val)
        a_model.append(a_mod)
        a_obs.append(a_meas)
        c_arr.append(complexity)
        omega_arr.append(omega)
        s_obs.append(s_meas)
        sigma_arr.append(sigma)

    return SimSeries(
        seed=seed,
        t=t,
        n=n,
        a_model=a_model,
        a_obs=a_obs,
        complexity=c_arr,
        omega=omega_arr,
        s_obs=s_obs,
        sigma=sigma_arr,
    )


def evaluate_run_metrics(series: SimSeries) -> RunMetrics:
    corr_a_n13 = pearson_corr(series.a_obs, series.a_model)
    corr_complexity_n = pearson_corr(series.complexity, series.n)
    slope_complexity_n, _ = linear_fit(series.n, series.complexity)
    corr_expansion_complexity = pearson_corr(series.a_obs, series.complexity)

    r2_scale = r2_score(series.a_obs, series.a_model)
    mape_scale = mape(series.a_obs, series.a_model)

    log_omega = [math.log(max(v, 1.0)) for v in series.omega]
    k_fit = fit_through_origin(log_omega, series.s_obs)
    s_fit = [k_fit * v for v in log_omega]
    r2_entropy = r2_score(series.s_obs, s_fit)

    omega_monot = monotonic_ratio(series.omega, tolerance=0.0)
    entropy_monot = monotonic_ratio(series.s_obs, tolerance=0.01)

    return RunMetrics(
        seed=series.seed,
        corr_a_n13=corr_a_n13,
        corr_complexity_n=corr_complexity_n,
        slope_complexity_n=slope_complexity_n,
        corr_expansion_complexity=corr_expansion_complexity,
        r2_scale=r2_scale,
        mape_scale=mape_scale,
        k_entropy_fit=k_fit,
        r2_entropy=r2_entropy,
        omega_monotonic_ratio=omega_monot,
        entropy_monotonic_ratio=entropy_monot,
    )


class Canvas:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.px = bytearray(bg * (width * height))

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i : i + 3] = bytes(color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for x in range(x0, x1 + 1):
            self.set(x, y0, color)
            self.set(x, y1, color)
        for y in range(y0, y1 + 1):
            self.set(x0, y, color)
            self.set(x1, y, color)

    def polyline(self, points: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
        if len(points) < 2:
            return
        for a, b in zip(points[:-1], points[1:]):
            self.line(a[0], a[1], b[0], b[1], color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row_size = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row_size
            raw.extend(self.px[i0 : i0 + row_size])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack("!I", len(data))
                + tag
                + data
                + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=9)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
        path.write_bytes(png)


def scale_point(
    x: float,
    y: float,
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> tuple[int, int]:
    if xmax <= xmin:
        sx = left
    else:
        sx = int(round(left + (x - xmin) / (xmax - xmin) * (right - left)))
    if ymax <= ymin:
        sy = bottom
    else:
        sy = int(round(bottom - (y - ymin) / (ymax - ymin) * (bottom - top)))
    return sx, sy


def plot_series_png(path: Path, x: list[float], series: list[tuple[str, list[float], tuple[int, int, int]]]) -> None:
    w, h = 1280, 760
    left, top, right, bottom = 85, 30, w - 30, h - 70
    c = Canvas(w, h, bg=(250, 252, 251))
    c.rect(left, top, right, bottom, (70, 90, 85))

    xmin, xmax = min(x), max(x)
    yvals = [v for _, ys, _ in series for v in ys]
    ymin, ymax = min(yvals), max(yvals)
    if math.isclose(ymin, ymax):
        ymin -= 1.0
        ymax += 1.0
    pad = 0.08 * (ymax - ymin)
    ymin -= pad
    ymax += pad

    for t in range(1, 6):
        gy = top + int((bottom - top) * t / 6)
        c.line(left, gy, right, gy, (223, 229, 226))

    for _, ys, color in series:
        pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, ys)]
        c.polyline(pts, color)
    c.save_png(path)


def write_csv_dict(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for key, value in payload.items():
            w.writerow([key, value])


def write_run_metrics_csv(path: Path, metrics: list[RunMetrics]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "seed",
                "corr_a_n13",
                "corr_complexity_n",
                "slope_complexity_n",
                "corr_expansion_complexity",
                "r2_scale",
                "mape_scale",
                "k_entropy_fit",
                "r2_entropy",
                "omega_monotonic_ratio",
                "entropy_monotonic_ratio",
            ]
        )
        for m in metrics:
            w.writerow(
                [
                    m.seed,
                    fmt(m.corr_a_n13),
                    fmt(m.corr_complexity_n),
                    fmt(m.slope_complexity_n),
                    fmt(m.corr_expansion_complexity),
                    fmt(m.r2_scale),
                    fmt(m.mape_scale),
                    fmt(m.k_entropy_fit),
                    fmt(m.r2_entropy),
                    fmt(m.omega_monotonic_ratio),
                    fmt(m.entropy_monotonic_ratio),
                ]
            )


def write_timeseries_csv(path: Path, series: SimSeries) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "N", "a_model", "a_obs", "complexity", "omega", "S_obs", "sigma"])
        for i in range(len(series.t)):
            w.writerow(
                [
                    series.t[i],
                    fmt(series.n[i]),
                    fmt(series.a_model[i]),
                    fmt(series.a_obs[i]),
                    fmt(series.complexity[i]),
                    fmt(series.omega[i]),
                    fmt(series.s_obs[i]),
                    fmt(series.sigma[i]),
                ]
            )


def write_stability_md(path: Path, summaries: dict[str, dict[str, float]], cv_threshold: float) -> None:
    lines = [
        "# Parameter Stability - QNG P2 Cosmo Suite",
        "",
        f"- CV threshold: `{cv_threshold:.2f}`",
        "",
        "| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for key, stat in summaries.items():
        cv = stat["cv"]
        status = "pass" if (not math.isinf(cv) and cv < cv_threshold) else "warn"
        lines.append(
            f"| {key} | {int(stat['count'])} | {fmt(stat['mean'])} | {fmt(stat['std'])} | {fmt(cv)} | {fmt(stat['min'])} | {fmt(stat['max'])} | {status} |"
        )
    lines += [
        "",
        "Interpretation:",
        "- Low CV indicates robust behavior under seed variation.",
        "- `warn` does not automatically fail a test; use with primary fit metrics.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG P2 cosmo suite run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"steps: {args.steps}",
        f"runs: {args.runs}",
        f"seed_base: {args.seed}",
        f"sigma_min: {args.sigma_min}",
        f"base_growth: {args.base_growth}",
        f"memory_weight: {args.memory_weight}",
        f"noise_scale: {args.noise_scale}",
        f"duration_seconds: {details['duration_seconds']:.3f}",
        "",
    ]
    if details.get("dataset_manifest"):
        lines += [
            "dataset_manifest_entry:",
            json.dumps(details["dataset_manifest"], ensure_ascii=False, indent=2),
            "",
        ]
    if warnings:
        lines.append("warnings:")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG P2 cosmology suite (QNG-T-050/051/053).")
    p.add_argument("--dataset-id", default="DS-002", help="Dataset manifest id (default: DS-002).")
    p.add_argument("--steps", type=int, default=180, help="Simulation steps per run.")
    p.add_argument("--runs", type=int, default=18, help="Number of seed runs for robustness.")
    p.add_argument("--seed", type=int, default=410, help="Base random seed.")
    p.add_argument("--sigma-min", type=float, default=0.34, help="Stability threshold.")
    p.add_argument("--base-growth", type=float, default=0.0105, help="Base node growth rate.")
    p.add_argument("--memory-weight", type=float, default=0.22, help="Memory coupling for growth.")
    p.add_argument("--noise-scale", type=float, default=1.0, help="Noise scale multiplier.")
    p.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT), help="Artifact root directory.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.steps < 40:
        print("Error: --steps should be >= 40", file=sys.stderr)
        return 2
    if args.runs < 4:
        print("Error: --runs should be >= 4", file=sys.stderr)
        return 2

    artifact_root = Path(args.artifact_root)
    if not artifact_root.is_absolute():
        artifact_root = (ROOT / artifact_root).resolve()

    out_050 = artifact_root / "qng-t-050"
    out_051 = artifact_root / "qng-t-051"
    out_053 = artifact_root / "qng-t-053"
    for out in (out_050, out_051, out_053):
        out.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    warnings: list[str] = []
    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"No dataset-manifest entry found for {args.dataset_id}.")

    all_series: list[SimSeries] = []
    all_metrics: list[RunMetrics] = []
    for i in range(args.runs):
        seed_i = args.seed + 17 * i
        series = simulate_node_growth(
            seed=seed_i,
            steps=args.steps,
            sigma_min=args.sigma_min,
            base_growth=args.base_growth,
            memory_weight=args.memory_weight,
            noise_scale=args.noise_scale,
        )
        all_series.append(series)
        all_metrics.append(evaluate_run_metrics(series))

    ref = all_series[0]
    ref_metrics = all_metrics[0]
    write_timeseries_csv(out_050 / "simulation-timeseries.csv", ref)
    write_timeseries_csv(out_051 / "simulation-timeseries.csv", ref)
    write_timeseries_csv(out_053 / "simulation-timeseries.csv", ref)
    write_run_metrics_csv(out_050 / "robustness-runs.csv", all_metrics)
    write_run_metrics_csv(out_051 / "robustness-runs.csv", all_metrics)
    write_run_metrics_csv(out_053 / "robustness-runs.csv", all_metrics)

    t_float = [float(v) for v in ref.t]
    plot_series_png(
        out_050 / "expansion-complexity.png",
        t_float,
        [
            ("a_obs", ref.a_obs, (20, 70, 140)),
            ("N_norm", normalize(ref.n), (25, 130, 70)),
            ("C_norm", normalize(ref.complexity), (160, 45, 40)),
        ],
    )
    plot_series_png(
        out_051 / "scale-factor-fit.png",
        t_float,
        [
            ("a_obs", ref.a_obs, (20, 70, 140)),
            ("a_model=(N/N0)^(1/3)", ref.a_model, (25, 130, 70)),
        ],
    )
    log_omega_ref = [math.log(max(v, 1.0)) for v in ref.omega]
    s_fit_ref = [ref_metrics.k_entropy_fit * v for v in log_omega_ref]
    plot_series_png(
        out_053 / "entropy-time-arrow.png",
        t_float,
        [
            ("S_obs", ref.s_obs, (20, 70, 140)),
            ("k*log(Omega)", s_fit_ref, (25, 130, 70)),
            ("log(Omega)_norm", normalize(log_omega_ref), (160, 45, 40)),
        ],
    )

    corr_a_vals = [m.corr_a_n13 for m in all_metrics]
    corr_c_vals = [m.corr_complexity_n for m in all_metrics]
    slope_c_vals = [m.slope_complexity_n for m in all_metrics]
    r2_vals = [m.r2_scale for m in all_metrics]
    mape_vals = [m.mape_scale for m in all_metrics]
    r2e_vals = [m.r2_entropy for m in all_metrics]
    omega_mono_vals = [m.omega_monotonic_ratio for m in all_metrics]
    entropy_mono_vals = [m.entropy_monotonic_ratio for m in all_metrics]
    k_vals = [m.k_entropy_fit for m in all_metrics]

    stat_corr_a = summarize(corr_a_vals)
    stat_corr_c = summarize(corr_c_vals)
    stat_slope_c = summarize(slope_c_vals)
    stat_r2 = summarize(r2_vals)
    stat_mape = summarize(mape_vals)
    stat_r2e = summarize(r2e_vals)
    stat_omega_mono = summarize(omega_mono_vals)
    stat_entropy_mono = summarize(entropy_mono_vals)
    stat_k = summarize(k_vals)

    pass_050 = (
        stat_corr_a["mean"] >= 0.96
        and stat_corr_c["mean"] >= 0.86
        and stat_slope_c["mean"] > 0.0
    )
    pass_051 = (
        stat_r2["mean"] >= 0.97
        and stat_mape["mean"] <= 0.03
        and stat_r2["cv"] <= 0.03
    )
    pass_053 = (
        stat_r2e["mean"] >= 0.94
        and stat_omega_mono["mean"] >= 0.99
        and stat_entropy_mono["mean"] >= 0.90
        and stat_k["mean"] > 0.0
    )

    summary_050 = {
        "dataset_id": args.dataset_id,
        "runs": str(args.runs),
        "steps": str(args.steps),
        "corr_a_vs_n13_mean": fmt(stat_corr_a["mean"]),
        "corr_complexity_vs_n_mean": fmt(stat_corr_c["mean"]),
        "slope_complexity_vs_n_mean": fmt(stat_slope_c["mean"]),
        "corr_expansion_vs_complexity_mean": fmt(summarize([m.corr_expansion_complexity for m in all_metrics])["mean"]),
        "rule_corr_a": str(stat_corr_a["mean"] >= 0.96),
        "rule_corr_complexity": str(stat_corr_c["mean"] >= 0.86),
        "rule_positive_slope": str(stat_slope_c["mean"] > 0.0),
        "pass_recommendation": "pass" if pass_050 else "fail",
    }
    write_csv_dict(out_050 / "fit-summary.csv", summary_050)

    summary_051 = {
        "dataset_id": args.dataset_id,
        "runs": str(args.runs),
        "steps": str(args.steps),
        "r2_scale_mean": fmt(stat_r2["mean"]),
        "r2_scale_cv": fmt(stat_r2["cv"]),
        "mape_scale_mean": fmt(stat_mape["mean"]),
        "rule_r2_mean": str(stat_r2["mean"] >= 0.97),
        "rule_mape": str(stat_mape["mean"] <= 0.03),
        "rule_r2_cv": str(stat_r2["cv"] <= 0.03),
        "pass_recommendation": "pass" if pass_051 else "fail",
    }
    write_csv_dict(out_051 / "fit-summary.csv", summary_051)

    summary_053 = {
        "dataset_id": args.dataset_id,
        "runs": str(args.runs),
        "steps": str(args.steps),
        "k_entropy_fit_mean": fmt(stat_k["mean"]),
        "r2_entropy_mean": fmt(stat_r2e["mean"]),
        "omega_monotonic_ratio_mean": fmt(stat_omega_mono["mean"]),
        "entropy_monotonic_ratio_mean": fmt(stat_entropy_mono["mean"]),
        "rule_r2_entropy": str(stat_r2e["mean"] >= 0.94),
        "rule_omega_monotonic": str(stat_omega_mono["mean"] >= 0.99),
        "rule_entropy_monotonic": str(stat_entropy_mono["mean"] >= 0.90),
        "rule_k_positive": str(stat_k["mean"] > 0.0),
        "pass_recommendation": "pass" if pass_053 else "fail",
    }
    write_csv_dict(out_053 / "fit-summary.csv", summary_053)

    stability_metrics = {
        "corr_a_vs_n13": stat_corr_a,
        "corr_complexity_vs_n": stat_corr_c,
        "slope_complexity_vs_n": stat_slope_c,
        "r2_scale": stat_r2,
        "mape_scale": stat_mape,
        "r2_entropy": stat_r2e,
        "omega_monotonic_ratio": stat_omega_mono,
        "entropy_monotonic_ratio": stat_entropy_mono,
        "k_entropy_fit": stat_k,
    }
    write_stability_md(out_050 / "parameter-stability.md", stability_metrics, cv_threshold=0.30)
    write_stability_md(out_051 / "parameter-stability.md", stability_metrics, cv_threshold=0.30)
    write_stability_md(out_053 / "parameter-stability.md", stability_metrics, cv_threshold=0.30)

    duration = time.perf_counter() - started
    details = {
        "dataset_manifest": dataset_meta,
        "duration_seconds": duration,
    }
    write_run_log(out_050 / "run-log.txt", args=args, details=details, warnings=warnings)
    write_run_log(out_051 / "run-log.txt", args=args, details=details, warnings=warnings)
    write_run_log(out_053 / "run-log.txt", args=args, details=details, warnings=warnings)

    print("QNG P2 cosmo suite completed.")
    print(f"Artifacts: {out_050}, {out_051}, {out_053}")
    print(
        "recommendations: "
        f"QNG-T-050={'pass' if pass_050 else 'fail'} "
        f"QNG-T-051={'pass' if pass_051 else 'fail'} "
        f"QNG-T-053={'pass' if pass_053 else 'fail'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
