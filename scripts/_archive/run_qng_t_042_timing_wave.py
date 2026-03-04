#!/usr/bin/env python3
"""
Executable timing/wave diagnostics for QNG tau/chi-linked residual tests.

Primary target:
- QNG-T-042 (P1 timing/wave)

Also reusable for:
- QNG-T-043, QNG-T-031, QNG-T-032, QNG-T-037

Dependency policy:
- stdlib only
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-042"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"
DEFAULT_CHANNELS = ["GPS-A", "GPS-B", "PSR-B1534", "PSR-J0737", "GW150914", "GW170817"]


@dataclass
class SeriesPoint:
    channel_id: str
    t: float
    driver: float
    residual: float
    sigma: float


@dataclass
class ChannelFit:
    channel_id: str
    n_samples: int
    tau_fit: float
    chi_fit: float
    chi2_baseline: float
    chi2_memory: float
    corr_model: float
    snr_like: float


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
        self.line(x0, y0, x1, y0, color)
        self.line(x1, y0, x1, y1, color)
        self.line(x1, y1, x0, y1, color)
        self.line(x0, y1, x0, y0, color)

    def polyline(self, pts: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            self.line(x0, y0, x1, y1, color)

    def save_png(self, path: Path) -> None:
        row_size = self.width * 3
        raw = bytearray()
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


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


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


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": float("nan"), "std": float("nan"), "cv": float("inf"), "min": float("nan"), "max": float("nan")}
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv = std_v / abs(mean_v) if abs(mean_v) > 1e-18 else float("inf")
    return {
        "count": float(len(values)),
        "mean": mean_v,
        "std": std_v,
        "cv": cv,
        "min": min(values),
        "max": max(values),
    }


def parse_list(text: str, fallback: list[str]) -> list[str]:
    out = [x.strip() for x in text.split(",") if x.strip()]
    return out or fallback


def parse_float_grid(text: str, fallback: list[float]) -> list[float]:
    out: list[float] = []
    for part in text.split(","):
        v = safe_float(part, None)
        if v is None:
            continue
        out.append(float(v))
    return out or fallback


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


def center_values(vals: list[float]) -> list[float]:
    if not vals:
        return []
    m = statistics.fmean(vals)
    return [v - m for v in vals]


def correlation(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    sx = statistics.pstdev(x)
    sy = statistics.pstdev(y)
    if sx <= 1e-18 or sy <= 1e-18:
        return float("nan")
    cov = statistics.fmean((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / (sx * sy)


def build_template(driver: list[float], dt: float, tau: float) -> list[float]:
    alpha = math.exp(-dt / max(tau, 1e-9))
    out: list[float] = []
    mem = 0.0
    for d in driver:
        mem = alpha * mem + d
        out.append(mem)
    return out


def read_input_csv(path: Path) -> tuple[list[SeriesPoint], list[str]]:
    warnings: list[str] = []
    points: list[SeriesPoint] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}
        c_ch = cols.get("channel_id") or cols.get("channel") or cols.get("system_id")
        c_t = cols.get("t") or cols.get("time")
        c_driver = cols.get("driver") or cols.get("x")
        c_resid = cols.get("residual") or cols.get("y")
        c_sigma = cols.get("sigma") or cols.get("err") or cols.get("error")

        if c_ch is None or c_t is None or c_driver is None or c_resid is None:
            raise ValueError("Input CSV needs channel_id, t, driver, residual (sigma optional).")

        for row in reader:
            ch = str(row.get(c_ch, "")).strip() or "unknown"
            t = safe_float(row.get(c_t), None)
            d = safe_float(row.get(c_driver), None)
            y = safe_float(row.get(c_resid), None)
            s = safe_float(row.get(c_sigma), None) if c_sigma else None
            if t is None or d is None or y is None:
                continue
            points.append(
                SeriesPoint(
                    channel_id=ch,
                    t=float(t),
                    driver=float(d),
                    residual=float(y),
                    sigma=float(s) if s and s > 0 else 1.0e-6,
                )
            )
    if not points:
        raise ValueError("No usable rows found in input CSV.")
    return points, warnings


def generate_synthetic_points(
    channels: list[str],
    samples: int,
    dt: float,
    tau_truth: float,
    chi_truth: float,
    noise_sigma: float,
    seed: int,
) -> list[SeriesPoint]:
    rng = random.Random(seed)
    out: list[SeriesPoint] = []
    for idx, ch in enumerate(channels):
        f0 = 0.008 + 0.003 * rng.random()
        phase = rng.uniform(-math.pi, math.pi)
        drift = rng.gauss(0.0, 2.0e-8)
        driver: list[float] = []
        for i in range(samples):
            t = i * dt
            d = (
                math.sin(2.0 * math.pi * f0 * t + phase)
                + 0.35 * math.sin(2.0 * math.pi * 1.8 * f0 * t - 0.4 * phase)
                + 0.14 * math.sin(2.0 * math.pi * 0.5 * f0 * t + idx * 0.3)
            )
            driver.append(d)
        tpl = build_template(driver, dt=dt, tau=tau_truth)
        scale = 0.90 + 0.22 * rng.random()
        for i in range(samples):
            t = i * dt
            signal = chi_truth * scale * tpl[i]
            residual = signal + drift + rng.gauss(0.0, noise_sigma)
            out.append(
                SeriesPoint(
                    channel_id=ch,
                    t=t,
                    driver=driver[i],
                    residual=residual,
                    sigma=noise_sigma,
                )
            )
    return out


def channel_groups(points: list[SeriesPoint]) -> dict[str, list[SeriesPoint]]:
    out: dict[str, list[SeriesPoint]] = {}
    for p in points:
        out.setdefault(p.channel_id, []).append(p)
    for ch in list(out.keys()):
        out[ch] = sorted(out[ch], key=lambda x: x.t)
    return out


def fit_channel(rows: list[SeriesPoint], tau_grid: list[float], dt: float) -> ChannelFit:
    y = [r.residual for r in rows]
    y0 = center_values(y)
    sigma2 = [max(r.sigma * r.sigma, 1e-30) for r in rows]
    chi2_base = sum((yy * yy) / s2 for yy, s2 in zip(y0, sigma2))

    d = [r.driver for r in rows]
    best = None
    for tau in tau_grid:
        tpl = center_values(build_template(d, dt=dt, tau=tau))
        den = sum((tt * tt) / s2 for tt, s2 in zip(tpl, sigma2))
        if den <= 1e-24:
            continue
        num = sum((tt * yy) / s2 for tt, yy, s2 in zip(tpl, y0, sigma2))
        chi = num / den
        chi2 = sum(((yy - chi * tt) ** 2) / s2 for yy, tt, s2 in zip(y0, tpl, sigma2))
        corr = correlation([chi * tt for tt in tpl], y0)
        resid = [yy - chi * tt for yy, tt in zip(y0, tpl)]
        signal_rms = math.sqrt(statistics.fmean((chi * tt) ** 2 for tt in tpl))
        noise_rms = math.sqrt(statistics.fmean(rr * rr for rr in resid))
        snr_like = signal_rms / max(noise_rms, 1e-18)
        if best is None or chi2 < best[0]:
            best = (chi2, tau, chi, corr, snr_like)
    if best is None:
        return ChannelFit(
            channel_id=rows[0].channel_id,
            n_samples=len(rows),
            tau_fit=0.0,
            chi_fit=0.0,
            chi2_baseline=chi2_base,
            chi2_memory=chi2_base,
            corr_model=0.0,
            snr_like=0.0,
        )
    chi2_mem, tau_fit, chi_fit, corr_fit, snr_fit = best
    return ChannelFit(
        channel_id=rows[0].channel_id,
        n_samples=len(rows),
        tau_fit=tau_fit,
        chi_fit=chi_fit,
        chi2_baseline=chi2_base,
        chi2_memory=chi2_mem,
        corr_model=corr_fit if not math.isnan(corr_fit) else 0.0,
        snr_like=snr_fit,
    )


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
        pts = []
        for xi, yi in zip(x, ys):
            sx = left if xmax <= xmin else int(round(left + (xi - xmin) / (xmax - xmin) * (right - left)))
            sy = bottom if ymax <= ymin else int(round(bottom - (yi - ymin) / (ymax - ymin) * (bottom - top)))
            pts.append((sx, sy))
        c.polyline(pts, color)
    c.save_png(path)


def write_csv_dict(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for key, value in payload.items():
            w.writerow([key, value])


def write_channel_fits(path: Path, rows: list[ChannelFit]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel_id", "n_samples", "tau_fit", "chi_fit", "chi2_baseline", "chi2_memory", "delta_chi2", "corr_model", "snr_like"])
        for r in rows:
            w.writerow(
                [
                    r.channel_id,
                    r.n_samples,
                    fmt(r.tau_fit),
                    fmt(r.chi_fit),
                    fmt(r.chi2_baseline),
                    fmt(r.chi2_memory),
                    fmt(r.chi2_memory - r.chi2_baseline),
                    fmt(r.corr_model),
                    fmt(r.snr_like),
                ]
            )


def write_points_csv(path: Path, points: list[SeriesPoint]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["channel_id", "t", "driver", "residual", "sigma"])
        for p in points:
            w.writerow([p.channel_id, fmt(p.t), fmt(p.driver), fmt(p.residual), fmt(p.sigma)])


def write_stability_md(path: Path, tau_stats: dict[str, float], chi_stats: dict[str, float], cv_threshold: float, corr_mean: float, snr_mean: float) -> None:
    status_tau = "pass" if (not math.isinf(tau_stats["cv"]) and tau_stats["cv"] < cv_threshold) else "warn"
    status_chi = "pass" if (not math.isinf(chi_stats["cv"]) and chi_stats["cv"] < cv_threshold) else "warn"
    lines = [
        "# Parameter Stability - QNG Timing/Wave Suite",
        "",
        f"- CV threshold: `{cv_threshold:.2f}`",
        "",
        "| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| tau_fit (per channel) | {int(tau_stats['count'])} | {fmt(tau_stats['mean'])} | {fmt(tau_stats['std'])} | {fmt(tau_stats['cv'])} | {fmt(tau_stats['min'])} | {fmt(tau_stats['max'])} | {status_tau} |",
        f"| chi_fit (per channel) | {int(chi_stats['count'])} | {fmt(chi_stats['mean'])} | {fmt(chi_stats['std'])} | {fmt(chi_stats['cv'])} | {fmt(chi_stats['min'])} | {fmt(chi_stats['max'])} | {status_chi} |",
        "",
        f"- Mean model/residual correlation: `{fmt(corr_mean)}`",
        f"- Mean SNR-like score: `{fmt(snr_mean)}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG timing/wave run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"data_source_mode: {details['data_source_mode']}",
        f"channels: {args.channels}",
        f"samples: {args.samples}",
        f"dt: {args.dt}",
        f"seed: {args.seed}",
        f"tau_truth: {args.tau_truth}",
        f"chi_truth: {args.chi_truth}",
        f"noise_sigma: {args.noise_sigma}",
        f"tau_grid: {args.tau_grid}",
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
    p = argparse.ArgumentParser(description="Run timing/wave tau-chi diagnostics for QNG timing tests.")
    p.add_argument("--dataset-id", default="DS-008", help="Dataset manifest id (default: DS-008).")
    p.add_argument("--input-csv", default="", help="Optional CSV with channel_id,t,driver,residual,sigma.")
    p.add_argument("--channels", default=",".join(DEFAULT_CHANNELS), help="Comma-separated channels in synthetic mode.")
    p.add_argument("--samples", type=int, default=1200, help="Samples per channel in synthetic mode.")
    p.add_argument("--dt", type=float, default=1.0, help="Time-step for synthetic mode.")
    p.add_argument("--seed", type=int, default=9042, help="Random seed.")
    p.add_argument("--tau-truth", type=float, default=36.0, help="Synthetic truth tau.")
    p.add_argument("--chi-truth", type=float, default=3.7e-7, help="Synthetic truth chi.")
    p.add_argument("--noise-sigma", type=float, default=1.8e-7, help="Synthetic residual noise sigma.")
    p.add_argument("--tau-grid", default="12,18,24,30,36,42,48,56", help="Comma-separated tau candidates.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Artifact output directory.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.samples < 300:
        print("Error: --samples should be >= 300", file=sys.stderr)
        return 2
    if args.dt <= 0:
        print("Error: --dt should be > 0", file=sys.stderr)
        return 2
    if args.noise_sigma <= 0:
        print("Error: --noise-sigma should be > 0", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    warnings: list[str] = []
    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"Dataset id '{args.dataset_id}' not found in dataset-manifest.json.")
    else:
        ds_name = str(dataset_meta.get("dataset_name", ""))
        if "timing" not in ds_name.lower() and "wave" not in ds_name.lower():
            warnings.append(
                f"Dataset id '{args.dataset_id}' points to '{ds_name}', expected timing/wave family."
            )

    data_source_mode = "synthetic"
    if args.input_csv.strip():
        points, read_warnings = read_input_csv(Path(args.input_csv))
        warnings.extend(read_warnings)
        data_source_mode = "provided"
    else:
        channels = parse_list(args.channels, DEFAULT_CHANNELS)
        points = generate_synthetic_points(
            channels=channels,
            samples=args.samples,
            dt=args.dt,
            tau_truth=args.tau_truth,
            chi_truth=args.chi_truth,
            noise_sigma=args.noise_sigma,
            seed=args.seed,
        )

    tau_grid = parse_float_grid(args.tau_grid, [12, 18, 24, 30, 36, 42, 48, 56])
    groups = channel_groups(points)
    fits: list[ChannelFit] = [fit_channel(rows, tau_grid=tau_grid, dt=args.dt) for rows in groups.values()]
    fits.sort(key=lambda r: r.channel_id.lower())

    chi2_base = sum(r.chi2_baseline for r in fits)
    chi2_mem = sum(r.chi2_memory for r in fits)
    delta_chi2 = chi2_mem - chi2_base
    aic_base = chi2_base + 2 * 0
    aic_mem = chi2_mem + 2 * 2
    delta_aic = aic_mem - aic_base

    tau_stats = summarize([r.tau_fit for r in fits])
    chi_stats = summarize([r.chi_fit for r in fits])
    corr_mean = statistics.fmean(r.corr_model for r in fits) if fits else 0.0
    snr_mean = statistics.fmean(r.snr_like for r in fits) if fits else 0.0
    sign_consistency = statistics.fmean([1.0 if (r.chi_fit * chi_stats["mean"]) >= 0 else 0.0 for r in fits]) if fits else 0.0

    rule_pass_delta_chi2 = delta_chi2 < 0.0
    rule_pass_delta_aic = delta_aic <= -10.0
    rule_pass_corr = corr_mean >= 0.55
    rule_pass_snr = snr_mean >= 1.50
    rule_pass_stability = tau_stats["cv"] < 0.35 and chi_stats["cv"] < 0.35
    rule_pass_sign = sign_consistency >= 0.80
    recommendation = (
        "pass"
        if all([rule_pass_delta_chi2, rule_pass_delta_aic, rule_pass_corr, rule_pass_snr, rule_pass_stability, rule_pass_sign])
        else "fail"
    )

    write_points_csv(out_dir / "timeseries-sample.csv", points)
    write_channel_fits(out_dir / "channel-fits.csv", fits)
    write_stability_md(out_dir / "parameter-stability.md", tau_stats, chi_stats, cv_threshold=0.35, corr_mean=corr_mean, snr_mean=snr_mean)

    # Representative channel plots.
    rep = groups[sorted(groups.keys())[0]]
    rep_fit = next(r for r in fits if r.channel_id == rep[0].channel_id)
    t = [p.t for p in rep]
    y = center_values([p.residual for p in rep])
    d = [p.driver for p in rep]
    tpl = center_values(build_template(d, dt=args.dt, tau=rep_fit.tau_fit))
    y_mem = [rep_fit.chi_fit * v for v in tpl]
    y_base = [0.0 for _ in y]

    plot_series_png(
        out_dir / "residual-timeseries.png",
        t,
        [
            ("residual", y, (36, 102, 191)),
            ("baseline", y_base, (160, 160, 165)),
            ("memory-fit", y_mem, (24, 148, 112)),
        ],
    )
    plot_series_png(
        out_dir / "echo-template.png",
        t,
        [
            ("driver", center_values(d), (214, 114, 57)),
            ("memory-template", tpl, (42, 130, 98)),
        ],
    )

    duration = time.perf_counter() - started
    details = {
        "duration_seconds": duration,
        "dataset_manifest": dataset_meta,
        "data_source_mode": data_source_mode,
    }
    write_run_log(out_dir / "run-log.txt", args=args, details=details, warnings=warnings)

    summary = {
        "dataset_id": args.dataset_id,
        "data_source_mode": data_source_mode,
        "n_channels": str(len(fits)),
        "n_samples_total": str(len(points)),
        "tau_fit_mean": fmt(tau_stats["mean"]),
        "chi_fit_mean": fmt(chi_stats["mean"]),
        "chi2_baseline": fmt(chi2_base),
        "chi2_memory": fmt(chi2_mem),
        "delta_chi2": fmt(delta_chi2),
        "aic_baseline": fmt(aic_base),
        "aic_memory": fmt(aic_mem),
        "delta_aic": fmt(delta_aic),
        "corr_mean": fmt(corr_mean),
        "snr_mean": fmt(snr_mean),
        "sign_consistency": fmt(sign_consistency),
        "cv_tau": fmt(tau_stats["cv"]),
        "cv_chi": fmt(chi_stats["cv"]),
        "rule_pass_delta_chi2": str(rule_pass_delta_chi2),
        "rule_pass_delta_aic": str(rule_pass_delta_aic),
        "rule_pass_corr": str(rule_pass_corr),
        "rule_pass_snr": str(rule_pass_snr),
        "rule_pass_stability": str(rule_pass_stability),
        "rule_pass_sign_consistency": str(rule_pass_sign),
        "pass_recommendation": recommendation,
        "duration_seconds": fmt(duration),
    }
    write_csv_dict(out_dir / "fit-summary.csv", summary)

    print(f"QNG timing/wave run completed. data_source_mode={data_source_mode}")
    print(
        f"delta_chi2={summary['delta_chi2']} "
        f"delta_aic={summary['delta_aic']} "
        f"tau_fit_mean={summary['tau_fit_mean']} "
        f"pass_recommendation={recommendation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

