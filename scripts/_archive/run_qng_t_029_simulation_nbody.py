#!/usr/bin/env python3
"""
Executable pipeline for QNG-T-029:
N-body baseline vs Sigma-memory-kernel comparison (dependency-light, stdlib only).

Outputs under 05_validation/evidence/artifacts/qng-t-029:
- fit-summary.csv
- robustness-runs.csv
- parameter-stability.md
- profile-overlay.png
- centroid-offset.png
- simulation-timeseries.csv
- run-log.txt
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-029"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class SimFeatures:
    profile: list[float]
    profile_r: list[float]
    centroid_offset: float
    coherence: float
    radius90: float
    offset_series: list[float]


@dataclass
class RunRecord:
    seed: int
    tau_fit: float
    k_fit: float
    g_base_fit: float
    chi2_baseline: float
    chi2_memory: float
    delta_chi2: float
    profile_rmse_baseline: float
    profile_rmse_memory: float
    offset_err_baseline: float
    offset_err_memory: float
    coherence_err_baseline: float
    coherence_err_memory: float


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


def parse_grid(text: str, fallback: list[float]) -> list[float]:
    if not text.strip():
        return fallback
    out: list[float] = []
    for part in text.split(","):
        v = safe_float(part, None)
        if v is None:
            continue
        out.append(float(v))
    return out or fallback


def barycenter_xy(step_idx: int) -> tuple[float, float]:
    t = float(step_idx)
    bx = 0.26 * math.sin(0.041 * t)
    by = 0.20 * math.cos(0.036 * t + 0.62)
    return bx, by


def make_initial_state(seed: int, n_particles: int) -> tuple[list[float], list[float], list[float], list[float]]:
    rng = random.Random(seed)
    x: list[float] = []
    y: list[float] = []
    vx: list[float] = []
    vy: list[float] = []
    for _ in range(n_particles):
        theta = rng.random() * 2.0 * math.pi
        r = abs(rng.gauss(1.45, 0.55))
        r = min(max(r, 0.20), 3.4)
        px = r * math.cos(theta)
        py = r * math.sin(theta)
        speed = 0.22 / math.sqrt(r + 0.15)
        tx = -math.sin(theta)
        ty = math.cos(theta)
        x.append(px)
        y.append(py)
        vx.append(speed * tx + rng.gauss(0.0, 0.02))
        vy.append(speed * ty + rng.gauss(0.0, 0.02))
    return x, y, vx, vy


def profile_from_particles(
    x: list[float],
    y: list[float],
    bx: float,
    by: float,
    nbins: int = 18,
    rmax: float = 5.4,
) -> tuple[list[float], list[float]]:
    dr = rmax / nbins
    counts = [0.0 for _ in range(nbins)]
    for px, py in zip(x, y):
        r = math.hypot(px - bx, py - by)
        idx = int(r / dr)
        if 0 <= idx < nbins:
            counts[idx] += 1.0
    total = sum(counts)
    if total <= 1e-12:
        profile = [0.0 for _ in range(nbins)]
    else:
        profile = [v / total for v in counts]
    centers = [(i + 0.5) * dr for i in range(nbins)]
    return profile, centers


def coherence_score(x: list[float], y: list[float], vx: list[float], vy: list[float], cx: float, cy: float) -> float:
    vals: list[float] = []
    for px, py, ux, uy in zip(x, y, vx, vy):
        dx = px - cx
        dy = py - cy
        r = math.hypot(dx, dy)
        sp = math.hypot(ux, uy)
        if r <= 1e-9 or sp <= 1e-9:
            continue
        tx = -dy / r
        ty = dx / r
        vals.append(abs((ux * tx + uy * ty) / sp))
    if not vals:
        return 0.0
    return statistics.fmean(vals)


def percentile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    if q <= 0.0:
        return sorted_vals[0]
    if q >= 1.0:
        return sorted_vals[-1]
    pos = q * (len(sorted_vals) - 1)
    i0 = int(math.floor(pos))
    i1 = min(i0 + 1, len(sorted_vals) - 1)
    w = pos - i0
    return sorted_vals[i0] * (1.0 - w) + sorted_vals[i1] * w


def simulate_features(
    seed: int,
    tau: float,
    k_memory: float,
    g_inst: float,
    steps: int,
    n_particles: int,
    dt: float,
    noise_scale: float,
) -> SimFeatures:
    x, y, vx, vy = make_initial_state(seed, n_particles)
    rng = random.Random(seed + 8191 + int(round(1000.0 * tau)) + int(round(1000.0 * k_memory)) * 13 + int(round(1000.0 * g_inst)) * 17)

    bx, by = barycenter_xy(0)
    mx, my = bx, by
    tau_eff = max(tau, 1e-4)
    alpha = min(1.0, dt / tau_eff)
    soft = 0.085
    g_mem = 0.82
    drag = 0.992
    confine = 0.0044

    offset_series: list[float] = []

    for step_idx in range(steps + 1):
        bx, by = barycenter_xy(step_idx)
        mx += alpha * (bx - mx)
        my += alpha * (by - my)

        sum_x = 0.0
        sum_y = 0.0
        for i in range(n_particles):
            px = x[i]
            py = y[i]

            dxb = bx - px
            dyb = by - py
            r2b = dxb * dxb + dyb * dyb + soft
            invb = 1.0 / (r2b * math.sqrt(r2b))
            ax = g_inst * dxb * invb
            ay = g_inst * dyb * invb

            if k_memory > 0.0:
                dxm = mx - px
                dym = my - py
                r2m = dxm * dxm + dym * dym + soft
                invm = 1.0 / (r2m * math.sqrt(r2m))
                ax += k_memory * g_mem * dxm * invm
                ay += k_memory * g_mem * dym * invm

            ax += -confine * px + rng.gauss(0.0, 0.0018 * noise_scale)
            ay += -confine * py + rng.gauss(0.0, 0.0018 * noise_scale)

            vx[i] = drag * (vx[i] + ax * dt)
            vy[i] = drag * (vy[i] + ay * dt)
            x[i] = px + vx[i] * dt
            y[i] = py + vy[i] * dt

            r_clip = math.hypot(x[i], y[i])
            if r_clip > 8.4:
                scale = 8.4 / max(r_clip, 1e-12)
                x[i] *= scale
                y[i] *= scale
                vx[i] *= 0.75
                vy[i] *= 0.75

            sum_x += x[i]
            sum_y += y[i]

        cx = sum_x / n_particles
        cy = sum_y / n_particles
        offset_series.append(math.hypot(cx - bx, cy - by))

    cx = statistics.fmean(x)
    cy = statistics.fmean(y)
    offset = math.hypot(cx - bx, cy - by)
    profile, profile_r = profile_from_particles(x, y, bx, by)
    coherence = coherence_score(x, y, vx, vy, cx, cy)
    radii = sorted(math.hypot(px - bx, py - by) for px, py in zip(x, y))
    r90 = percentile(radii, 0.90)

    return SimFeatures(
        profile=profile,
        profile_r=profile_r,
        centroid_offset=offset,
        coherence=coherence,
        radius90=r90,
        offset_series=offset_series,
    )


def normalize_profile(profile: list[float]) -> list[float]:
    s = sum(max(v, 0.0) for v in profile)
    if s <= 1e-12:
        return [0.0 for _ in profile]
    return [max(v, 0.0) / s for v in profile]


def make_observation(
    seed: int,
    steps: int,
    n_particles: int,
    dt: float,
    noise_scale: float,
    truth_tau: float,
    truth_k: float,
) -> tuple[SimFeatures, SimFeatures]:
    truth = simulate_features(
        seed=seed,
        tau=truth_tau,
        k_memory=truth_k,
        g_inst=1.0,
        steps=steps,
        n_particles=n_particles,
        dt=dt,
        noise_scale=noise_scale * 0.75,
    )
    rng = random.Random(seed + 112_233)
    obs_profile = [p * (1.0 + rng.gauss(0.0, 0.040 * noise_scale)) for p in truth.profile]
    obs_profile = normalize_profile(obs_profile)
    obs_offset = max(0.0, truth.centroid_offset + rng.gauss(0.0, 0.015 * noise_scale))
    obs_coherence = min(1.0, max(0.0, truth.coherence + rng.gauss(0.0, 0.012 * noise_scale)))
    obs_r90 = max(0.08, truth.radius90 + rng.gauss(0.0, 0.030 * noise_scale))
    obs_offsets = [max(0.0, v + rng.gauss(0.0, 0.012 * noise_scale)) for v in truth.offset_series]

    observed = SimFeatures(
        profile=obs_profile,
        profile_r=truth.profile_r,
        centroid_offset=obs_offset,
        coherence=obs_coherence,
        radius90=obs_r90,
        offset_series=obs_offsets,
    )
    return truth, observed


def score_model(pred: SimFeatures, obs: SimFeatures) -> float:
    p_term = 0.0
    for a, b in zip(pred.profile, obs.profile):
        sigma = max(0.004, b * 0.35)
        p_term += ((a - b) / sigma) ** 2

    off_term = ((pred.centroid_offset - obs.centroid_offset) / 0.020) ** 2
    coh_term = ((pred.coherence - obs.coherence) / 0.020) ** 2
    r90_term = ((pred.radius90 - obs.radius90) / 0.050) ** 2
    return p_term + off_term + coh_term + r90_term


def rmse_profile(pred: SimFeatures, obs: SimFeatures) -> float:
    if not pred.profile:
        return float("nan")
    mse = statistics.fmean((a - b) ** 2 for a, b in zip(pred.profile, obs.profile))
    return math.sqrt(mse)


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


def write_runs_csv(path: Path, rows: list[RunRecord]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "seed",
                "tau_fit",
                "k_fit",
                "g_base_fit",
                "chi2_baseline",
                "chi2_memory",
                "delta_chi2",
                "profile_rmse_baseline",
                "profile_rmse_memory",
                "offset_err_baseline",
                "offset_err_memory",
                "coherence_err_baseline",
                "coherence_err_memory",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.seed,
                    fmt(r.tau_fit),
                    fmt(r.k_fit),
                    fmt(r.g_base_fit),
                    fmt(r.chi2_baseline),
                    fmt(r.chi2_memory),
                    fmt(r.delta_chi2),
                    fmt(r.profile_rmse_baseline),
                    fmt(r.profile_rmse_memory),
                    fmt(r.offset_err_baseline),
                    fmt(r.offset_err_memory),
                    fmt(r.coherence_err_baseline),
                    fmt(r.coherence_err_memory),
                ]
            )


def write_timeseries_csv(
    path: Path,
    obs: SimFeatures,
    base: SimFeatures,
    mem: SimFeatures,
    truth: SimFeatures,
) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "offset_obs", "offset_baseline", "offset_memory", "offset_truth"])
        for i in range(len(obs.offset_series)):
            w.writerow(
                [
                    i,
                    fmt(obs.offset_series[i]),
                    fmt(base.offset_series[i]),
                    fmt(mem.offset_series[i]),
                    fmt(truth.offset_series[i]),
                ]
            )


def write_stability_md(path: Path, summaries: dict[str, dict[str, float]], cv_threshold: float) -> None:
    lines = [
        "# Parameter Stability - QNG-T-029",
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
        "- Low CV indicates robust parameter recovery across seeds.",
        "- `warn` means fit variability should be reviewed before publication-grade claims.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG-T-029 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"runs: {args.runs}",
        f"steps: {args.steps}",
        f"particles: {args.particles}",
        f"seed_base: {args.seed}",
        f"dt: {args.dt}",
        f"noise_scale: {args.noise_scale}",
        f"truth_tau: {args.truth_tau}",
        f"truth_k: {args.truth_k}",
        f"tau_grid: {args.tau_grid}",
        f"k_grid: {args.k_grid}",
        f"g_base_grid: {args.g_base_grid}",
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
    p = argparse.ArgumentParser(description="Run QNG-T-029 N-body memory-kernel comparison.")
    p.add_argument("--dataset-id", default="DS-003", help="Dataset manifest id (default: DS-003).")
    p.add_argument("--runs", type=int, default=12, help="Number of seed runs for robustness.")
    p.add_argument("--steps", type=int, default=160, help="Simulation steps per run.")
    p.add_argument("--particles", type=int, default=140, help="Particle count per run.")
    p.add_argument("--seed", type=int, default=730, help="Base random seed.")
    p.add_argument("--dt", type=float, default=0.06, help="Integrator dt.")
    p.add_argument("--noise-scale", type=float, default=1.0, help="Observation/simulation noise scale.")
    p.add_argument("--truth-tau", type=float, default=1.30, help="Hidden reference memory tau.")
    p.add_argument("--truth-k", type=float, default=0.85, help="Hidden reference memory coupling.")
    p.add_argument("--tau-grid", default="0.45,0.70,1.00,1.30,1.70,2.20", help="Comma-separated tau candidates.")
    p.add_argument("--k-grid", default="0.25,0.45,0.65,0.85,1.05", help="Comma-separated k-memory candidates.")
    p.add_argument("--g-base-grid", default="0.82,0.94,1.06,1.18", help="Comma-separated baseline gain candidates.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output artifact directory.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.runs < 4:
        print("Error: --runs should be >= 4", file=sys.stderr)
        return 2
    if args.steps < 80:
        print("Error: --steps should be >= 80", file=sys.stderr)
        return 2
    if args.particles < 60:
        print("Error: --particles should be >= 60", file=sys.stderr)
        return 2

    tau_candidates = parse_grid(args.tau_grid, [0.45, 0.70, 1.00, 1.30, 1.70, 2.20])
    k_candidates = parse_grid(args.k_grid, [0.25, 0.45, 0.65, 0.85, 1.05])
    g_base_candidates = parse_grid(args.g_base_grid, [0.82, 0.94, 1.06, 1.18])

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
        if "n-body" not in ds_name.lower():
            warnings.append(
                f"Dataset id '{args.dataset_id}' points to '{ds_name}', expected N-body simulation environment."
            )

    records: list[RunRecord] = []
    representative_truth: SimFeatures | None = None
    representative_obs: SimFeatures | None = None
    representative_base: SimFeatures | None = None
    representative_mem: SimFeatures | None = None

    for run_idx in range(args.runs):
        seed = args.seed + run_idx
        truth, obs = make_observation(
            seed=seed,
            steps=args.steps,
            n_particles=args.particles,
            dt=args.dt,
            noise_scale=args.noise_scale,
            truth_tau=args.truth_tau,
            truth_k=args.truth_k,
        )

        best_base = None
        for g_base in g_base_candidates:
            pred_base = simulate_features(
                seed=seed,
                tau=0.05,
                k_memory=0.0,
                g_inst=g_base,
                steps=args.steps,
                n_particles=args.particles,
                dt=args.dt,
                noise_scale=args.noise_scale * 0.55,
            )
            chi2 = score_model(pred_base, obs)
            if best_base is None or chi2 < best_base[0]:
                best_base = (chi2, g_base, pred_base)
        assert best_base is not None

        best_mem = None
        for tau in tau_candidates:
            for k_mem in k_candidates:
                pred_mem = simulate_features(
                    seed=seed,
                    tau=tau,
                    k_memory=k_mem,
                    g_inst=1.0,
                    steps=args.steps,
                    n_particles=args.particles,
                    dt=args.dt,
                    noise_scale=args.noise_scale * 0.55,
                )
                chi2 = score_model(pred_mem, obs)
                if best_mem is None or chi2 < best_mem[0]:
                    best_mem = (chi2, tau, k_mem, pred_mem)
        assert best_mem is not None

        chi2_base, g_fit, base_pred = best_base
        chi2_mem, tau_fit, k_fit, mem_pred = best_mem

        records.append(
            RunRecord(
                seed=seed,
                tau_fit=tau_fit,
                k_fit=k_fit,
                g_base_fit=g_fit,
                chi2_baseline=chi2_base,
                chi2_memory=chi2_mem,
                delta_chi2=chi2_mem - chi2_base,
                profile_rmse_baseline=rmse_profile(base_pred, obs),
                profile_rmse_memory=rmse_profile(mem_pred, obs),
                offset_err_baseline=abs(base_pred.centroid_offset - obs.centroid_offset),
                offset_err_memory=abs(mem_pred.centroid_offset - obs.centroid_offset),
                coherence_err_baseline=abs(base_pred.coherence - obs.coherence),
                coherence_err_memory=abs(mem_pred.coherence - obs.coherence),
            )
        )

        if run_idx == 0:
            representative_truth = truth
            representative_obs = obs
            representative_base = base_pred
            representative_mem = mem_pred

    chi2_base_total = sum(r.chi2_baseline for r in records)
    chi2_mem_total = sum(r.chi2_memory for r in records)
    delta_chi2 = chi2_mem_total - chi2_base_total

    aic_base = chi2_base_total + 2 * 1
    aic_mem = chi2_mem_total + 2 * 2
    delta_aic = aic_mem - aic_base

    prof_base_mean = statistics.fmean(r.profile_rmse_baseline for r in records)
    prof_mem_mean = statistics.fmean(r.profile_rmse_memory for r in records)
    off_base_mean = statistics.fmean(r.offset_err_baseline for r in records)
    off_mem_mean = statistics.fmean(r.offset_err_memory for r in records)
    coh_base_mean = statistics.fmean(r.coherence_err_baseline for r in records)
    coh_mem_mean = statistics.fmean(r.coherence_err_memory for r in records)

    tau_stats = summarize([r.tau_fit for r in records])
    k_stats = summarize([r.k_fit for r in records])
    g_stats = summarize([r.g_base_fit for r in records])

    profile_gain = (prof_base_mean - prof_mem_mean) / max(prof_base_mean, 1e-12)
    offset_gain = (off_base_mean - off_mem_mean) / max(off_base_mean, 1e-12)
    coherence_gain = (coh_base_mean - coh_mem_mean) / max(coh_base_mean, 1e-12)

    rule_pass_delta_chi2 = delta_chi2 < 0.0
    rule_pass_delta_aic = delta_aic <= -10.0
    rule_pass_profile = prof_mem_mean <= 0.90 * prof_base_mean
    rule_pass_offset = off_mem_mean <= 0.90 * off_base_mean
    rule_pass_stability = tau_stats["cv"] < 0.30 and k_stats["cv"] < 0.30
    recommendation = (
        "pass"
        if all(
            [
                rule_pass_delta_chi2,
                rule_pass_delta_aic,
                rule_pass_profile,
                rule_pass_offset,
                rule_pass_stability,
            ]
        )
        else "fail"
    )

    write_runs_csv(out_dir / "robustness-runs.csv", records)
    write_stability_md(
        out_dir / "parameter-stability.md",
        {
            "tau_fit": tau_stats,
            "k_memory_fit": k_stats,
            "g_base_fit": g_stats,
        },
        cv_threshold=0.30,
    )

    assert representative_obs is not None
    assert representative_base is not None
    assert representative_mem is not None
    assert representative_truth is not None

    plot_series_png(
        out_dir / "profile-overlay.png",
        representative_obs.profile_r,
        [
            ("obs", representative_obs.profile, (42, 88, 185)),
            ("baseline", representative_base.profile, (223, 106, 63)),
            ("memory", representative_mem.profile, (30, 156, 111)),
        ],
    )
    plot_series_png(
        out_dir / "centroid-offset.png",
        list(range(len(representative_obs.offset_series))),
        [
            ("obs", representative_obs.offset_series, (42, 88, 185)),
            ("baseline", representative_base.offset_series, (223, 106, 63)),
            ("memory", representative_mem.offset_series, (30, 156, 111)),
        ],
    )
    write_timeseries_csv(
        out_dir / "simulation-timeseries.csv",
        obs=representative_obs,
        base=representative_base,
        mem=representative_mem,
        truth=representative_truth,
    )

    duration = time.perf_counter() - started
    details = {"duration_seconds": duration, "dataset_manifest": dataset_meta}
    write_run_log(out_dir / "run-log.txt", args=args, details=details, warnings=warnings)

    summary = {
        "dataset_id": args.dataset_id,
        "n_runs": str(args.runs),
        "steps": str(args.steps),
        "particles": str(args.particles),
        "tau_fit_mean": fmt(tau_stats["mean"]),
        "k_memory_fit_mean": fmt(k_stats["mean"]),
        "chi2_baseline_total": fmt(chi2_base_total),
        "chi2_memory_total": fmt(chi2_mem_total),
        "delta_chi2": fmt(delta_chi2),
        "aic_baseline": fmt(aic_base),
        "aic_memory": fmt(aic_mem),
        "delta_aic": fmt(delta_aic),
        "profile_rmse_baseline_mean": fmt(prof_base_mean),
        "profile_rmse_memory_mean": fmt(prof_mem_mean),
        "offset_err_baseline_mean": fmt(off_base_mean),
        "offset_err_memory_mean": fmt(off_mem_mean),
        "coherence_err_baseline_mean": fmt(coh_base_mean),
        "coherence_err_memory_mean": fmt(coh_mem_mean),
        "profile_gain": fmt(profile_gain),
        "offset_gain": fmt(offset_gain),
        "coherence_gain": fmt(coherence_gain),
        "cv_tau": fmt(tau_stats["cv"]),
        "cv_k_memory": fmt(k_stats["cv"]),
        "rule_pass_delta_chi2": str(rule_pass_delta_chi2),
        "rule_pass_delta_aic": str(rule_pass_delta_aic),
        "rule_pass_profile": str(rule_pass_profile),
        "rule_pass_offset": str(rule_pass_offset),
        "rule_pass_stability": str(rule_pass_stability),
        "pass_recommendation": recommendation,
        "duration_seconds": fmt(duration),
    }
    write_csv_dict(out_dir / "fit-summary.csv", summary)

    print("QNG-T-029 completed.")
    print(f"delta_chi2={summary['delta_chi2']} delta_aic={summary['delta_aic']} pass_recommendation={recommendation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
