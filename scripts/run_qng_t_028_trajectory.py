#!/usr/bin/env python3
"""
Executable trajectory diagnostics for QNG lag-law tests.

Primary target:
- QNG-T-028 (P1 trajectory)

Also reusable for:
- QNG-T-041, QNG-T-010, QNG-T-011, QNG-T-025

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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-028"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"
DEFAULT_MISSIONS = ["Galileo", "NEAR", "Rosetta", "Cassini", "Juno", "Pioneer"]


@dataclass
class TelemetryPoint:
    mission_id: str
    feature: float
    residual: float
    sigma: float
    phase: float


@dataclass
class MissionFit:
    mission_id: str
    n_points: int
    tau_hat: float
    directionality: float
    amp_median: float


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


def read_input_csv(path: Path) -> tuple[list[TelemetryPoint], list[str]]:
    warnings: list[str] = []
    points: list[TelemetryPoint] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}
        c_mission = cols.get("mission_id") or cols.get("mission") or cols.get("system_id")
        c_feature = cols.get("feature") or cols.get("driver") or cols.get("x")
        c_resid = cols.get("residual") or cols.get("a_residual") or cols.get("y")
        c_sigma = cols.get("sigma") or cols.get("err") or cols.get("error")
        c_phase = cols.get("phase") or cols.get("t")

        if c_mission is None or c_feature is None or c_resid is None:
            raise ValueError("Input CSV needs columns for mission_id, feature, residual (sigma optional).")

        for row in reader:
            mission = str(row.get(c_mission, "")).strip() or "unknown"
            feature = safe_float(row.get(c_feature), None)
            resid = safe_float(row.get(c_resid), None)
            sigma = safe_float(row.get(c_sigma), None) if c_sigma else None
            phase = safe_float(row.get(c_phase), None) if c_phase else None
            if feature is None or resid is None:
                continue
            points.append(
                TelemetryPoint(
                    mission_id=mission,
                    feature=float(feature),
                    residual=float(resid),
                    sigma=float(sigma) if sigma and sigma > 0 else 5.0e-10,
                    phase=float(phase) if phase is not None else 0.0,
                )
            )

    if not points:
        raise ValueError("No usable rows found in input CSV.")
    return points, warnings


def generate_synthetic_points(
    missions: list[str],
    points_per_mission: int,
    tau_truth: float,
    noise_sigma: float,
    seed: int,
) -> list[TelemetryPoint]:
    rng = random.Random(seed)
    out: list[TelemetryPoint] = []
    for idx, mission in enumerate(missions):
        phase_shift = rng.uniform(-0.9, 0.9)
        mission_gain = 0.75 + 0.50 * rng.random()
        mission_bias = rng.gauss(0.0, noise_sigma * 0.65)
        for j in range(points_per_mission):
            u = -1.0 + 2.0 * j / max(1, points_per_mission - 1)
            phi = math.pi * u
            feature = mission_gain * (
                math.sin(phi + phase_shift)
                + 0.30 * math.sin(2.0 * phi - 0.6 * phase_shift)
                + 0.10 * math.sin(3.0 * phi + idx * 0.25)
            )
            # Slightly stronger near perigee.
            perigee_boost = 1.0 + 0.25 * math.exp(-5.0 * (u * u))
            feature *= perigee_boost
            residual = tau_truth * feature + mission_bias + rng.gauss(0.0, noise_sigma)
            out.append(
                TelemetryPoint(
                    mission_id=mission,
                    feature=feature,
                    residual=residual,
                    sigma=noise_sigma,
                    phase=u,
                )
            )
    return out


def mission_groups(points: list[TelemetryPoint]) -> dict[str, list[TelemetryPoint]]:
    groups: dict[str, list[TelemetryPoint]] = {}
    for p in points:
        groups.setdefault(p.mission_id, []).append(p)
    return groups


def center_values(vals: list[float]) -> list[float]:
    if not vals:
        return []
    m = statistics.fmean(vals)
    return [v - m for v in vals]


def fit_tau_global(points: list[TelemetryPoint]) -> tuple[float, float, float]:
    groups = mission_groups(points)
    num = 0.0
    den = 0.0
    chi2_base = 0.0
    for rows in groups.values():
        x = center_values([r.feature for r in rows])
        y = center_values([r.residual for r in rows])
        for xi, yi, r in zip(x, y, rows):
            w = 1.0 / max(r.sigma * r.sigma, 1e-30)
            num += w * xi * yi
            den += w * xi * xi
            chi2_base += w * yi * yi
    tau_hat = num / den if den > 1e-30 else 0.0
    chi2_mem = 0.0
    for rows in groups.values():
        x = center_values([r.feature for r in rows])
        y = center_values([r.residual for r in rows])
        for xi, yi, r in zip(x, y, rows):
            w = 1.0 / max(r.sigma * r.sigma, 1e-30)
            chi2_mem += w * (yi - tau_hat * xi) ** 2
    return tau_hat, chi2_base, chi2_mem


def fit_per_mission(points: list[TelemetryPoint], tau_global: float) -> list[MissionFit]:
    out: list[MissionFit] = []
    for mission, rows in mission_groups(points).items():
        x = center_values([r.feature for r in rows])
        y = center_values([r.residual for r in rows])
        den = sum(v * v for v in x)
        tau_hat = sum(a * b for a, b in zip(x, y)) / den if den > 1e-24 else 0.0
        agree = [1.0 if (a * b) >= 0.0 else 0.0 for a, b in zip(x, y) if abs(a) > 1e-16 and abs(b) > 1e-16]
        directionality = statistics.fmean(agree) if agree else 0.0
        pred_amp = [abs(tau_global * xi) for xi in x]
        amp_median = statistics.median(pred_amp) if pred_amp else 0.0
        out.append(
            MissionFit(
                mission_id=mission,
                n_points=len(rows),
                tau_hat=tau_hat,
                directionality=directionality,
                amp_median=amp_median,
            )
        )
    out.sort(key=lambda r: r.mission_id.lower())
    return out


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
            if xmax <= xmin:
                sx = left
            else:
                sx = int(round(left + (xi - xmin) / (xmax - xmin) * (right - left)))
            if ymax <= ymin:
                sy = bottom
            else:
                sy = int(round(bottom - (yi - ymin) / (ymax - ymin) * (bottom - top)))
            pts.append((sx, sy))
        c.polyline(pts, color)
    c.save_png(path)


def write_csv_dict(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for key, value in payload.items():
            w.writerow([key, value])


def write_points_csv(path: Path, points: list[TelemetryPoint], tau_fit: float) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mission_id", "phase", "feature", "residual", "sigma", "residual_centered", "pred_memory_centered"])
        for mission, rows in mission_groups(points).items():
            x = center_values([r.feature for r in rows])
            y = center_values([r.residual for r in rows])
            for r, xi, yi in zip(rows, x, y):
                w.writerow(
                    [
                        mission,
                        fmt(r.phase),
                        fmt(r.feature),
                        fmt(r.residual),
                        fmt(r.sigma),
                        fmt(yi),
                        fmt(tau_fit * xi),
                    ]
                )


def write_mission_fits_csv(path: Path, rows: list[MissionFit]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mission_id", "n_points", "tau_hat", "directionality", "amp_median"])
        for r in rows:
            w.writerow([r.mission_id, r.n_points, fmt(r.tau_hat), fmt(r.directionality), fmt(r.amp_median)])


def write_stability_md(path: Path, tau_stats: dict[str, float], cv_threshold: float, directionality_mean: float, sign_consistency: float) -> None:
    status = "pass" if (not math.isinf(tau_stats["cv"]) and tau_stats["cv"] < cv_threshold) else "warn"
    lines = [
        "# Parameter Stability - QNG Trajectory Suite",
        "",
        f"- CV threshold: `{cv_threshold:.2f}`",
        "",
        "| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| tau_fit (per mission) | {int(tau_stats['count'])} | {fmt(tau_stats['mean'])} | {fmt(tau_stats['std'])} | {fmt(tau_stats['cv'])} | {fmt(tau_stats['min'])} | {fmt(tau_stats['max'])} | {status} |",
        "",
        f"- Mean directionality agreement: `{fmt(directionality_mean)}`",
        f"- Sign consistency across missions: `{fmt(sign_consistency)}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG trajectory run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"data_source_mode: {details['data_source_mode']}",
        f"missions: {args.missions}",
        f"points_per_mission: {args.points_per_mission}",
        f"seed: {args.seed}",
        f"tau_truth: {args.tau_truth}",
        f"noise_sigma: {args.noise_sigma}",
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
    p = argparse.ArgumentParser(description="Run trajectory lag-law diagnostics for QNG trajectory tests.")
    p.add_argument("--dataset-id", default="DS-005", help="Dataset manifest id (default: DS-005).")
    p.add_argument("--input-csv", default="", help="Optional input CSV with mission_id/feature/residual/sigma.")
    p.add_argument("--missions", default=",".join(DEFAULT_MISSIONS), help="Comma-separated mission ids for synthetic mode.")
    p.add_argument("--points-per-mission", type=int, default=120, help="Samples per mission in synthetic mode.")
    p.add_argument("--seed", type=int, default=828, help="Base random seed.")
    p.add_argument("--tau-truth", type=float, default=2.6e-9, help="Synthetic truth tau.")
    p.add_argument("--noise-sigma", type=float, default=5.2e-10, help="Synthetic residual noise sigma.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Artifact output directory.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.points_per_mission < 40:
        print("Error: --points-per-mission should be >= 40", file=sys.stderr)
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
        if "telemetry" not in ds_name.lower() and "flyby" not in ds_name.lower():
            warnings.append(
                f"Dataset id '{args.dataset_id}' points to '{ds_name}', expected trajectory telemetry family."
            )

    data_source_mode = "synthetic"
    if args.input_csv.strip():
        points, read_warnings = read_input_csv(Path(args.input_csv))
        warnings.extend(read_warnings)
        data_source_mode = "provided"
    else:
        missions = parse_list(args.missions, DEFAULT_MISSIONS)
        points = generate_synthetic_points(
            missions=missions,
            points_per_mission=args.points_per_mission,
            tau_truth=args.tau_truth,
            noise_sigma=args.noise_sigma,
            seed=args.seed,
        )

    tau_fit, chi2_base, chi2_mem = fit_tau_global(points)
    delta_chi2 = chi2_mem - chi2_base
    aic_base = chi2_base + 2 * 0
    aic_mem = chi2_mem + 2 * 1
    delta_aic = aic_mem - aic_base

    mfits = fit_per_mission(points, tau_global=tau_fit)
    tau_stats = summarize([m.tau_hat for m in mfits])
    directionality_mean = statistics.fmean([m.directionality for m in mfits]) if mfits else 0.0
    sign_matches = [1.0 if (m.tau_hat * tau_fit) >= 0 else 0.0 for m in mfits if abs(m.tau_hat) > 1e-18 and abs(tau_fit) > 1e-18]
    sign_consistency = statistics.fmean(sign_matches) if sign_matches else 0.0
    amp_medians = [m.amp_median for m in mfits]
    amp_median_global = statistics.median(amp_medians) if amp_medians else 0.0
    amp_band_ok = 1.0e-10 <= amp_median_global <= 1.0e-8

    rule_pass_delta_chi2 = delta_chi2 < 0.0
    rule_pass_delta_aic = delta_aic <= -10.0
    rule_pass_directionality = directionality_mean >= 0.62
    rule_pass_sign = sign_consistency >= 0.80
    rule_pass_stability = tau_stats["cv"] < 0.35
    rule_pass_amp_band = amp_band_ok
    recommendation = (
        "pass"
        if all(
            [
                rule_pass_delta_chi2,
                rule_pass_delta_aic,
                rule_pass_directionality,
                rule_pass_sign,
                rule_pass_stability,
                rule_pass_amp_band,
            ]
        )
        else "fail"
    )

    # Export detailed telemetry CSV and mission fit CSV.
    write_points_csv(out_dir / "telemetry-sample.csv", points, tau_fit=tau_fit)
    write_mission_fits_csv(out_dir / "mission-fits.csv", mfits)
    write_stability_md(
        out_dir / "parameter-stability.md",
        tau_stats=tau_stats,
        cv_threshold=0.35,
        directionality_mean=directionality_mean,
        sign_consistency=sign_consistency,
    )

    # Plot 1: centered residual vs centered memory prediction by sample index.
    residual_centered: list[float] = []
    pred_centered: list[float] = []
    baseline_centered: list[float] = []
    idx_x: list[float] = []
    idx = 0
    for mission in sorted(mission_groups(points).keys()):
        rows = mission_groups(points)[mission]
        x = center_values([r.feature for r in rows])
        y = center_values([r.residual for r in rows])
        for xi, yi in zip(x, y):
            idx += 1
            idx_x.append(float(idx))
            residual_centered.append(yi)
            pred_centered.append(tau_fit * xi)
            baseline_centered.append(0.0)

    plot_series_png(
        out_dir / "trajectory-residuals.png",
        idx_x,
        [
            ("observed", residual_centered, (35, 97, 185)),
            ("baseline", baseline_centered, (164, 168, 170)),
            ("memory-fit", pred_centered, (22, 148, 112)),
        ],
    )

    # Plot 2: directionality relation (feature vs residual, sorted by feature).
    feats = []
    ress = []
    for mission in sorted(mission_groups(points).keys()):
        rows = mission_groups(points)[mission]
        x = center_values([r.feature for r in rows])
        y = center_values([r.residual for r in rows])
        feats.extend(x)
        ress.extend(y)
    pairs = sorted(zip(feats, ress), key=lambda t: t[0])
    x_sorted = [p[0] for p in pairs]
    y_sorted = [p[1] for p in pairs]
    y_fit = [tau_fit * xx for xx in x_sorted]
    plot_series_png(
        out_dir / "directionality.png",
        x_sorted,
        [
            ("residual", y_sorted, (211, 112, 55)),
            ("tau-fit*feature", y_fit, (31, 132, 96)),
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
        "n_points": str(len(points)),
        "n_missions": str(len(mfits)),
        "tau_fit": fmt(tau_fit),
        "chi2_baseline": fmt(chi2_base),
        "chi2_memory": fmt(chi2_mem),
        "delta_chi2": fmt(delta_chi2),
        "aic_baseline": fmt(aic_base),
        "aic_memory": fmt(aic_mem),
        "delta_aic": fmt(delta_aic),
        "directionality_score": fmt(directionality_mean),
        "sign_consistency": fmt(sign_consistency),
        "amp_median": fmt(amp_median_global),
        "amp_in_claim_band": str(amp_band_ok),
        "cv_tau": fmt(tau_stats["cv"]),
        "rule_pass_delta_chi2": str(rule_pass_delta_chi2),
        "rule_pass_delta_aic": str(rule_pass_delta_aic),
        "rule_pass_directionality": str(rule_pass_directionality),
        "rule_pass_sign_consistency": str(rule_pass_sign),
        "rule_pass_stability": str(rule_pass_stability),
        "rule_pass_amp_band": str(rule_pass_amp_band),
        "pass_recommendation": recommendation,
        "duration_seconds": fmt(duration),
    }
    write_csv_dict(out_dir / "fit-summary.csv", summary)

    print(f"QNG trajectory run completed. data_source_mode={data_source_mode}")
    print(
        f"delta_chi2={summary['delta_chi2']} "
        f"delta_aic={summary['delta_aic']} "
        f"tau_fit={summary['tau_fit']} "
        f"pass_recommendation={recommendation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
