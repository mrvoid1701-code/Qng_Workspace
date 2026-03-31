#!/usr/bin/env python3
"""
Executable pipeline for QNG-T-052:
CMB coherence diagnostics using Planck TT/TE/EE spectra.

Operationalization (claim anchor: J = -mu_s * nablaSigma):
1) Build smoothed stability proxy Sigma from each spectrum.
2) Compute gradient-driven flux J along multipole ell.
3) Detect coherent extrema and test local flux convergence.
4) Compare baseline (heavy smoothing) vs coherence model (lighter smoothing).

This implementation is stdlib-only and produces artifacts ready for evidence docs.
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
import statistics
import struct
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-052"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"
BEST_FIT_REF = ROOT / "data" / "cmb" / "planck" / "qng_v3_unified_best_fit.txt"
DEFAULT_TT = ROOT / "data" / "cmb" / "planck" / "COM_PowerSpect_CMB-TT-full_R3.01.txt"
DEFAULT_TE = ROOT / "data" / "cmb" / "planck" / "COM_PowerSpect_CMB-TE-full_R3.01.txt"
DEFAULT_EE = ROOT / "data" / "cmb" / "planck" / "COM_PowerSpect_CMB-EE-full_R3.01.txt"


@dataclass
class SpectrumPoint:
    ell: float
    dl: float
    err: float


@dataclass
class Extremum:
    idx: int
    kind: str  # "max" or "min"
    prominence: float


@dataclass
class SpectrumAnalysis:
    name: str
    ells: list[float]
    observed: list[float]
    errors: list[float]
    baseline: list[float]
    coherence_model: list[float]
    sigma: list[float]
    flux: list[float]
    extrema: list[Extremum]
    chi2_baseline: float
    chi2_coherence: float
    coherence_score: float
    flux_strength: float


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


def odd_at_least(value: int, minimum: int) -> int:
    v = max(int(value), int(minimum))
    if v % 2 == 0:
        v += 1
    return v


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


def parse_best_fit_reference(path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        key, val = line.split("=", 1)
        fval = safe_float(val)
        if fval is None:
            continue
        out[key.strip()] = float(fval)
    return out


def parse_planck_spectrum(path: Path) -> list[SpectrumPoint]:
    if not path.exists():
        raise FileNotFoundError(f"Missing spectrum file: {path}")
    points: list[SpectrumPoint] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        cols = line.split()
        if len(cols) < 4:
            continue
        ell = safe_float(cols[0])
        dl = safe_float(cols[1])
        err_lo = safe_float(cols[2])
        err_hi = safe_float(cols[3])
        if None in {ell, dl, err_lo, err_hi}:
            continue
        err = 0.5 * (abs(float(err_lo)) + abs(float(err_hi)))
        if err <= 0:
            err = max(abs(float(dl)) * 0.03, 1e-6)
        points.append(SpectrumPoint(float(ell), float(dl), float(err)))
    if len(points) < 80:
        raise ValueError(f"Too few usable rows in {path}: {len(points)}")
    points.sort(key=lambda p: p.ell)
    return points


def filter_ell_range(points: list[SpectrumPoint], ell_min: float, ell_max: float) -> list[SpectrumPoint]:
    out = [p for p in points if ell_min <= p.ell <= ell_max]
    if len(out) < 80:
        raise ValueError(f"Too few points in ell-range [{ell_min}, {ell_max}]: {len(out)}")
    return out


def moving_average(values: list[float], window: int) -> list[float]:
    n = len(values)
    if n == 0:
        return []
    w = odd_at_least(window, 3)
    h = w // 2
    out: list[float] = []
    for i in range(n):
        lo = max(0, i - h)
        hi = min(n, i + h + 1)
        out.append(statistics.fmean(values[lo:hi]))
    return out


def derivative(x: list[float], y: list[float]) -> list[float]:
    n = len(x)
    if n == 0:
        return []
    if n == 1:
        return [0.0]
    out = [0.0] * n
    for i in range(n):
        if i == 0:
            dx = x[1] - x[0]
            out[i] = (y[1] - y[0]) / dx if abs(dx) > 0 else 0.0
        elif i == n - 1:
            dx = x[-1] - x[-2]
            out[i] = (y[-1] - y[-2]) / dx if abs(dx) > 0 else 0.0
        else:
            dx = x[i + 1] - x[i - 1]
            out[i] = (y[i + 1] - y[i - 1]) / dx if abs(dx) > 0 else 0.0
    return out


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    span = hi - lo
    if span <= 1e-12:
        return [0.5 for _ in values]
    return [(v - lo) / span for v in values]


def chi2(observed: list[float], model: list[float], errors: list[float]) -> float:
    total = 0.0
    for y, m, e in zip(observed, model, errors):
        sigma = max(float(e), 1e-9)
        total += ((y - m) ** 2) / (sigma * sigma)
    return total


def detect_extrema(
    values: list[float],
    *,
    use_abs: bool,
    min_distance: int,
    prominence_frac: float,
) -> list[Extremum]:
    n = len(values)
    if n < 3:
        return []

    probe = [abs(v) for v in values] if use_abs else list(values)
    vmin, vmax = min(probe), max(probe)
    prom_threshold = max(0.0, prominence_frac) * max(vmax - vmin, 1e-12)
    dist = max(1, int(min_distance))

    candidates: list[Extremum] = []
    for i in range(1, n - 1):
        if not (probe[i] > probe[i - 1] and probe[i] >= probe[i + 1]):
            continue
        prom = probe[i] - 0.5 * (probe[i - 1] + probe[i + 1])
        if prom < prom_threshold:
            continue
        if values[i] >= values[i - 1] and values[i] >= values[i + 1]:
            kind = "max"
        elif values[i] <= values[i - 1] and values[i] <= values[i + 1]:
            kind = "min"
        else:
            kind = "max" if values[i] >= 0 else "min"
        candidates.append(Extremum(idx=i, kind=kind, prominence=prom))

    candidates.sort(key=lambda ex: ex.prominence, reverse=True)
    selected: list[Extremum] = []
    for ex in candidates:
        if all(abs(ex.idx - keep.idx) >= dist for keep in selected):
            selected.append(ex)
    selected.sort(key=lambda ex: ex.idx)

    if not selected:
        best = max(range(n), key=lambda i: probe[i])
        kind = "max" if values[best] >= 0 else "min"
        selected = [Extremum(idx=best, kind=kind, prominence=0.0)]
    return selected


def coherence_from_flux(flux: list[float], extrema: list[Extremum]) -> tuple[float, float]:
    if not extrema or not flux:
        return 0.0, 0.0
    n = len(flux)
    ok = 0
    strengths: list[float] = []
    for ex in extrema:
        li = max(0, ex.idx - 1)
        ri = min(n - 1, ex.idx + 1)
        left = flux[li]
        right = flux[ri]
        if ex.kind == "max":
            # For J = -nablaSigma, convergence into a local maximum means:
            # left side flux points right (negative), right side points left (positive).
            convergent = left < 0 and right > 0
        else:
            # Around a local minimum, the direction is inverted.
            convergent = left > 0 and right < 0
        if convergent:
            ok += 1
        strengths.append(abs(left) + abs(right))
    score = ok / len(extrema)
    strength = statistics.fmean(strengths) if strengths else 0.0
    return score, strength


def peak_alignment(primary: list[float], other: list[float], limit: int) -> float:
    if not primary or not other or limit <= 0:
        return float("inf")
    source = primary[:limit]
    vals: list[float] = []
    for p in source:
        nearest = min(abs(p - q) for q in other)
        vals.append(nearest / max(abs(p), 1.0))
    return statistics.fmean(vals) if vals else float("inf")


def dominant_peak_ells(result: SpectrumAnalysis, count: int, ell_lo: float = 80.0, ell_hi: float = 2200.0) -> list[float]:
    if count <= 0:
        return []
    top = sorted(result.extrema, key=lambda ex: ex.prominence, reverse=True)
    chosen: list[float] = []
    for ex in top:
        ell = result.ells[ex.idx]
        if ell_lo <= ell <= ell_hi:
            chosen.append(ell)
        if len(chosen) >= count:
            break
    if not chosen:
        chosen = [result.ells[ex.idx] for ex in top[:count]]
    chosen.sort()
    return chosen


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


def cross_spectrum_correlation(
    ref_ells: list[float],
    ref_vals: list[float],
    other_ells: list[float],
    other_vals: list[float],
) -> float:
    ref_map = {int(round(e)): v for e, v in zip(ref_ells, ref_vals)}
    other_map = {int(round(e)): v for e, v in zip(other_ells, other_vals)}
    common = sorted(set(ref_map.keys()) & set(other_map.keys()))
    if len(common) < 30:
        return float("nan")
    x = [ref_map[k] for k in common]
    y = [other_map[k] for k in common]
    return pearson_corr(x, y)


def analyze_spectrum(
    name: str,
    points: list[SpectrumPoint],
    baseline_window: int,
    memory_window: int,
    peak_min_distance: int,
    prominence_frac: float,
    use_abs_extrema: bool,
) -> SpectrumAnalysis:
    ells = [p.ell for p in points]
    observed = [p.dl for p in points]
    errors = [p.err for p in points]

    baseline = moving_average(observed, baseline_window)
    coherence_model = moving_average(observed, memory_window)

    sigma = normalize(coherence_model)
    flux = [-g for g in derivative(ells, sigma)]
    extrema = detect_extrema(
        coherence_model,
        use_abs=use_abs_extrema,
        min_distance=peak_min_distance,
        prominence_frac=prominence_frac,
    )
    coherence_score, flux_strength = coherence_from_flux(flux, extrema)
    chi2_baseline = chi2(observed, baseline, errors)
    chi2_coherence = chi2(observed, coherence_model, errors)

    return SpectrumAnalysis(
        name=name,
        ells=ells,
        observed=observed,
        errors=errors,
        baseline=baseline,
        coherence_model=coherence_model,
        sigma=sigma,
        flux=flux,
        extrema=extrema,
        chi2_baseline=chi2_baseline,
        chi2_coherence=chi2_coherence,
        coherence_score=coherence_score,
        flux_strength=flux_strength,
    )


def summary_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": float("nan"), "std": float("nan"), "cv": float("inf")}
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv = std_v / abs(mean_v) if abs(mean_v) > 1e-12 else float("inf")
    return {"count": float(len(values)), "mean": mean_v, "std": std_v, "cv": cv}


def robustness_scan(
    name: str,
    points: list[SpectrumPoint],
    baseline_window: int,
    memory_window: int,
    peak_min_distance: int,
    prominence_frac: float,
    use_abs_extrema: bool,
) -> dict[str, dict[str, float]]:
    mem_candidates = sorted({odd_at_least(memory_window + d, 5) for d in (-6, -2, 0, 2, 6)})
    prom_candidates = [max(0.005, prominence_frac * f) for f in (0.7, 0.85, 1.0, 1.15, 1.3)]

    coherence_values: list[float] = []
    delta_values: list[float] = []
    peak_values: list[float] = []
    for mem_w in mem_candidates:
        for prom in prom_candidates:
            res = analyze_spectrum(
                name=name,
                points=points,
                baseline_window=baseline_window,
                memory_window=mem_w,
                peak_min_distance=peak_min_distance,
                prominence_frac=prom,
                use_abs_extrema=use_abs_extrema,
            )
            coherence_values.append(res.coherence_score)
            delta_values.append(res.chi2_coherence - res.chi2_baseline)
            peak_values.append(float(len(res.extrema)))

    return {
        "coherence_score": summary_stats(coherence_values),
        "delta_chi2": summary_stats(delta_values),
        "peak_count": summary_stats(peak_values),
    }


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


def plot_spectrum_png(path: Path, result: SpectrumAnalysis) -> None:
    w, h = 1360, 760
    left, top, right, bottom = 85, 30, w - 30, h - 70
    c = Canvas(w, h, bg=(250, 252, 250))
    c.rect(left, top, right, bottom, (70, 90, 85))

    x = result.ells
    y_series = result.observed + result.baseline + result.coherence_model
    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y_series), max(y_series)
    if math.isclose(ymin, ymax):
        ymin -= 1.0
        ymax += 1.0
    pad = 0.08 * (ymax - ymin)
    ymin -= pad
    ymax += pad

    for t in range(1, 6):
        gy = top + int((bottom - top) * t / 6)
        c.line(left, gy, right, gy, (222, 229, 225))

    obs_pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, result.observed)]
    base_pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, result.baseline)]
    mem_pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, result.coherence_model)]

    c.polyline(obs_pts, (35, 70, 130))
    c.polyline(base_pts, (160, 55, 45))
    c.polyline(mem_pts, (20, 130, 70))

    for ex in result.extrema:
        px, py = mem_pts[ex.idx]
        marker = (120, 35, 150) if ex.kind == "max" else (180, 120, 20)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                c.set(px + dx, py + dy, marker)

    c.save_png(path)


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv_dict(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in payload.items():
            w.writerow([k, v])


def write_peak_table(path: Path, results: list[SpectrumAnalysis], top_n: int = 18) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["spectrum", "rank", "ell", "dl", "kind", "prominence"])
        for res in results:
            ordered = sorted(res.extrema, key=lambda ex: ex.prominence, reverse=True)[:top_n]
            ordered.sort(key=lambda ex: ex.idx)
            for rank, ex in enumerate(ordered, start=1):
                w.writerow(
                    [
                        res.name,
                        rank,
                        fmt(res.ells[ex.idx]),
                        fmt(res.observed[ex.idx]),
                        ex.kind,
                        fmt(ex.prominence),
                    ]
                )


def write_stability_report(path: Path, stability: dict[str, dict[str, dict[str, float]]], cv_threshold: float) -> None:
    lines = [
        "# Parameter Stability - QNG-T-052",
        "",
        f"- CV threshold: `{cv_threshold:.2f}`",
        "- Grid: memory-window offsets and prominence scaling factors.",
        "",
        "| Spectrum | Metric | Samples | Mean | StdDev | CV | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for spectrum in ("TT", "TE", "EE"):
        metrics = stability.get(spectrum, {})
        for metric in ("coherence_score", "delta_chi2", "peak_count"):
            row = metrics.get(metric, {})
            count = int(row.get("count", 0.0))
            mean_v = row.get("mean", float("nan"))
            std_v = row.get("std", float("nan"))
            cv_v = row.get("cv", float("inf"))
            status = "pass" if (not math.isinf(cv_v) and cv_v < cv_threshold) else "warn"
            lines.append(
                f"| {spectrum} | {metric} | {count} | {fmt(mean_v)} | {fmt(std_v)} | {fmt(cv_v)} | {status} |"
            )
    lines += [
        "",
        "Interpretation:",
        "- Lower CV indicates robustness to moderate preprocessing choices.",
        "- `delta_chi2` should remain negative if coherence model consistently improves over baseline.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG-T-052 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"ell_range: [{args.ell_min}, {args.ell_max}]",
        f"baseline_window: {args.baseline_window}",
        f"memory_window: {args.memory_window}",
        f"peak_min_distance: {args.peak_min_distance}",
        f"prominence_frac: {args.prominence_frac}",
        f"duration_seconds: {details['duration_seconds']:.3f}",
        "",
    ]
    if details.get("dataset_manifest"):
        lines += [
            "dataset_manifest_entry:",
            json.dumps(details["dataset_manifest"], ensure_ascii=False, indent=2),
            "",
        ]
    if details.get("best_fit_reference"):
        lines += [
            "qng_best_fit_reference:",
            json.dumps(details["best_fit_reference"], ensure_ascii=False, indent=2),
            "",
        ]
    if warnings:
        lines.append("warnings:")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-052 CMB coherence diagnostics on Planck spectra.")
    p.add_argument("--dataset-id", default="DS-002", help="Dataset manifest id (default: DS-002).")
    p.add_argument("--tt-file", default=str(DEFAULT_TT), help="Path to Planck TT spectrum.")
    p.add_argument("--te-file", default=str(DEFAULT_TE), help="Path to Planck TE spectrum.")
    p.add_argument("--ee-file", default=str(DEFAULT_EE), help="Path to Planck EE spectrum.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Artifact output directory.")
    p.add_argument("--ell-min", type=float, default=30.0, help="Minimum ell included.")
    p.add_argument("--ell-max", type=float, default=2500.0, help="Maximum ell included.")
    p.add_argument("--baseline-window", type=int, default=121, help="Heavy smoothing window.")
    p.add_argument("--memory-window", type=int, default=21, help="Coherence smoothing window.")
    p.add_argument("--peak-min-distance", type=int, default=60, help="Minimum index distance between extrema.")
    p.add_argument("--prominence-frac", type=float, default=0.02, help="Peak prominence fraction of dynamic range.")
    p.add_argument("--alignment-count", type=int, default=6, help="Number of TT extrema used for cross-alignment.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.ell_min >= args.ell_max:
        print("Error: --ell-min must be < --ell-max.", file=sys.stderr)
        return 2
    if args.prominence_frac < 0:
        print("Error: --prominence-frac must be >= 0.", file=sys.stderr)
        return 2

    args.baseline_window = odd_at_least(args.baseline_window, 9)
    args.memory_window = odd_at_least(args.memory_window, 5)
    if args.memory_window >= args.baseline_window:
        args.baseline_window = odd_at_least(args.memory_window + 20, 9)

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    warnings: list[str] = []

    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"No dataset-manifest entry found for {args.dataset_id}.")

    best_fit_ref = parse_best_fit_reference(BEST_FIT_REF)
    if not best_fit_ref:
        warnings.append("No parsed entries from qng_v3_unified_best_fit.txt reference file.")

    tt_points = filter_ell_range(parse_planck_spectrum(Path(args.tt_file)), args.ell_min, args.ell_max)
    te_points = filter_ell_range(parse_planck_spectrum(Path(args.te_file)), args.ell_min, args.ell_max)
    ee_points = filter_ell_range(parse_planck_spectrum(Path(args.ee_file)), args.ell_min, args.ell_max)

    tt_prominence = max(0.005, args.prominence_frac * 0.30)
    tt_distance = max(20, args.peak_min_distance // 2)

    tt = analyze_spectrum(
        name="TT",
        points=tt_points,
        baseline_window=args.baseline_window,
        memory_window=args.memory_window,
        peak_min_distance=tt_distance,
        prominence_frac=tt_prominence,
        use_abs_extrema=False,
    )
    te = analyze_spectrum(
        name="TE",
        points=te_points,
        baseline_window=args.baseline_window,
        memory_window=args.memory_window,
        peak_min_distance=args.peak_min_distance,
        prominence_frac=args.prominence_frac,
        use_abs_extrema=True,
    )
    ee = analyze_spectrum(
        name="EE",
        points=ee_points,
        baseline_window=args.baseline_window,
        memory_window=args.memory_window,
        peak_min_distance=args.peak_min_distance,
        prominence_frac=args.prominence_frac,
        use_abs_extrema=True,
    )
    results = [tt, te, ee]

    chi2_base_total = sum(r.chi2_baseline for r in results)
    chi2_mem_total = sum(r.chi2_coherence for r in results)
    delta_chi2_total = chi2_mem_total - chi2_base_total

    coherence_mean = statistics.fmean(r.coherence_score for r in results)
    flux_strength_mean = statistics.fmean(r.flux_strength for r in results)

    tt_ells = dominant_peak_ells(tt, count=args.alignment_count)
    te_ells = dominant_peak_ells(te, count=args.alignment_count)
    ee_ells = dominant_peak_ells(ee, count=args.alignment_count)
    align_te = peak_alignment(tt_ells, te_ells, limit=args.alignment_count)
    align_ee = peak_alignment(tt_ells, ee_ells, limit=args.alignment_count)
    alignment_mean = statistics.fmean([align_te, align_ee]) if all(not math.isinf(v) for v in (align_te, align_ee)) else float("inf")

    tt_abs_norm = normalize(tt.coherence_model)
    te_abs_norm = normalize([abs(v) for v in te.coherence_model])
    ee_abs_norm = normalize([abs(v) for v in ee.coherence_model])
    corr_te = cross_spectrum_correlation(tt.ells, tt_abs_norm, te.ells, te_abs_norm)
    corr_ee = cross_spectrum_correlation(tt.ells, tt_abs_norm, ee.ells, ee_abs_norm)
    corr_values = [v for v in (corr_te, corr_ee) if not math.isnan(v)]
    corr_mean = statistics.fmean(corr_values) if corr_values else float("nan")

    rule_delta = delta_chi2_total < 0.0
    rule_coherence = coherence_mean >= 0.55
    rule_alignment = (
        not math.isnan(corr_te)
        and not math.isnan(corr_ee)
        and abs(corr_te) >= 0.20
        and abs(corr_ee) >= 0.20
    )
    recommendation = "pass" if (rule_delta and rule_coherence and rule_alignment) else "fail"

    plot_spectrum_png(out_dir / "tt-spectrum.png", tt)
    plot_spectrum_png(out_dir / "te-spectrum.png", te)
    plot_spectrum_png(out_dir / "ee-spectrum.png", ee)
    write_peak_table(out_dir / "peak-table.csv", results)

    stability = {
        "TT": robustness_scan(
            "TT",
            tt_points,
            baseline_window=args.baseline_window,
            memory_window=args.memory_window,
            peak_min_distance=tt_distance,
            prominence_frac=tt_prominence,
            use_abs_extrema=False,
        ),
        "TE": robustness_scan(
            "TE",
            te_points,
            baseline_window=args.baseline_window,
            memory_window=args.memory_window,
            peak_min_distance=args.peak_min_distance,
            prominence_frac=args.prominence_frac,
            use_abs_extrema=True,
        ),
        "EE": robustness_scan(
            "EE",
            ee_points,
            baseline_window=args.baseline_window,
            memory_window=args.memory_window,
            peak_min_distance=args.peak_min_distance,
            prominence_frac=args.prominence_frac,
            use_abs_extrema=True,
        ),
    }
    write_stability_report(out_dir / "parameter-stability.md", stability=stability, cv_threshold=0.30)

    duration = time.perf_counter() - started
    details = {
        "dataset_manifest": dataset_meta,
        "best_fit_reference": best_fit_ref,
        "duration_seconds": duration,
    }
    write_run_log(out_dir / "run-log.txt", args=args, details=details, warnings=warnings)

    summary = {
        "dataset_id": args.dataset_id,
        "ell_min": fmt(args.ell_min),
        "ell_max": fmt(args.ell_max),
        "baseline_window": str(args.baseline_window),
        "memory_window": str(args.memory_window),
        "peak_min_distance": str(args.peak_min_distance),
        "prominence_frac": fmt(args.prominence_frac),
        "tt_points": str(len(tt.ells)),
        "te_points": str(len(te.ells)),
        "ee_points": str(len(ee.ells)),
        "chi2_baseline_total": fmt(chi2_base_total),
        "chi2_coherence_total": fmt(chi2_mem_total),
        "delta_chi2_total": fmt(delta_chi2_total),
        "tt_coherence_score": fmt(tt.coherence_score),
        "te_coherence_score": fmt(te.coherence_score),
        "ee_coherence_score": fmt(ee.coherence_score),
        "coherence_score_mean": fmt(coherence_mean),
        "flux_strength_mean": fmt(flux_strength_mean),
        "tt_peak_count": str(len(tt.extrema)),
        "te_peak_count": str(len(te.extrema)),
        "ee_peak_count": str(len(ee.extrema)),
        "peak_alignment_te_to_tt": fmt(align_te),
        "peak_alignment_ee_to_tt": fmt(align_ee),
        "peak_alignment_mean": fmt(alignment_mean),
        "cross_corr_tt_abs_te": fmt(corr_te),
        "cross_corr_tt_abs_ee": fmt(corr_ee),
        "cross_corr_mean": fmt(corr_mean),
        "rule_delta_chi2": str(rule_delta),
        "rule_coherence": str(rule_coherence),
        "rule_cross_spectrum_corr": str(rule_alignment),
        "pass_recommendation": recommendation,
        "duration_seconds": fmt(duration),
    }
    if "chi2_rel_total" in best_fit_ref:
        summary["qng_v3_ref_chi2_rel_total"] = fmt(best_fit_ref["chi2_rel_total"])
    write_csv_dict(out_dir / "fit-summary.csv", summary)

    print("QNG-T-052 completed on Planck TT/TE/EE data.")
    print(f"Artifacts written to: {out_dir}")
    print(
        f"delta_chi2_total={summary['delta_chi2_total']} "
        f"coherence_mean={summary['coherence_score_mean']} "
        f"alignment_mean={summary['peak_alignment_mean']} "
        f"pass_recommendation={recommendation}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
