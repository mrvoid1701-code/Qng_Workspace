#!/usr/bin/env python3
"""
Executable pipeline for QNG-T-027:
Lensing + rotation baseline vs Sigma-memory comparison.

This script is intentionally dependency-light (stdlib only).
It will:
1) Load user CSV inputs if provided, otherwise generate reproducible synthetic data.
2) Fit baseline vs memory parameters.
3) Compute core metrics (chi2, AIC delta, stability, offset score).
4) Export artifacts expected by the evidence file.
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-027"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"
DEFAULT_TEST_ID = "QNG-T-027"


@dataclass
class LensingPoint:
    system_id: str
    obs_dx: float
    obs_dy: float
    grad_dx: float
    grad_dy: float
    sigma: float


@dataclass
class RotationPoint:
    system_id: str
    radius: float
    v_obs: float
    v_err: float
    baryon_term: float
    history_term: float


@dataclass
class FitMetrics:
    tau_fit: float
    k_fit: float
    n_lensing: int
    n_rotation: int
    n_total: int
    chi2_lens_baseline: float
    chi2_lens_memory: float
    chi2_rot_baseline: float
    chi2_rot_memory: float
    chi2_baseline: float
    chi2_memory: float
    delta_chi2_lens: float
    delta_chi2_rot: float
    delta_chi2_total: float
    delta_chi2_lens_per_point: float
    delta_chi2_rot_per_point: float
    delta_chi2_total_per_point: float
    aic_lens_baseline: float
    aic_lens_memory: float
    aic_rot_baseline: float
    aic_rot_memory: float
    aic_baseline: float
    aic_memory: float
    delta_aic_lens: float
    delta_aic_rot: float
    delta_aic_total: float
    bic_lens_baseline: float
    bic_lens_memory: float
    bic_rot_baseline: float
    bic_rot_memory: float
    bic_baseline: float
    bic_memory: float
    delta_bic_lens: float
    delta_bic_rot: float
    delta_bic_total: float
    offset_score: float


def safe_float(value: str | None, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def normalize_header_map(fieldnames: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for name in fieldnames or []:
        out[name.lower().strip()] = name
    return out


def pick_col(hmap: dict[str, str], aliases: list[str]) -> str | None:
    for alias in aliases:
        key = alias.lower().strip()
        if key in hmap:
            return hmap[key]
    return None


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


def parse_lensing_csv(path: Path) -> tuple[list[LensingPoint], list[str]]:
    warnings: list[str] = []
    points: list[LensingPoint] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        hmap = normalize_header_map(reader.fieldnames)

        c_sid = pick_col(hmap, ["system_id", "cluster_id", "id", "name"])
        c_obs_dx = pick_col(hmap, ["obs_dx", "offset_x", "delta_x"])
        c_obs_dy = pick_col(hmap, ["obs_dy", "offset_y", "delta_y"])
        c_bx = pick_col(hmap, ["baryon_x", "x_baryon", "baryonic_x"])
        c_by = pick_col(hmap, ["baryon_y", "y_baryon", "baryonic_y"])
        c_lx = pick_col(hmap, ["lens_x", "x_lens", "lensing_x"])
        c_ly = pick_col(hmap, ["lens_y", "y_lens", "lensing_y"])
        c_grad_x = pick_col(hmap, ["sigma_grad_x", "grad_x", "history_dx", "memory_dx"])
        c_grad_y = pick_col(hmap, ["sigma_grad_y", "grad_y", "history_dy", "memory_dy"])
        c_sigma = pick_col(hmap, ["sigma", "offset_err", "error", "err"])

        if (c_obs_dx is None or c_obs_dy is None) and (None in {c_bx, c_by, c_lx, c_ly}):
            raise ValueError(
                "Lensing CSV needs either (obs_dx, obs_dy) or (baryon_x, baryon_y, lens_x, lens_y) columns."
            )
        if c_grad_x is None or c_grad_y is None:
            raise ValueError("Lensing CSV needs gradient columns (sigma_grad_x/sigma_grad_y or aliases).")

        for idx, row in enumerate(reader, start=1):
            sid = str(row.get(c_sid, f"L{idx}") if c_sid else f"L{idx}").strip() or f"L{idx}"
            if c_obs_dx and c_obs_dy:
                obs_dx = safe_float(row.get(c_obs_dx))
                obs_dy = safe_float(row.get(c_obs_dy))
            else:
                bx = safe_float(row.get(c_bx))
                by = safe_float(row.get(c_by))
                lx = safe_float(row.get(c_lx))
                ly = safe_float(row.get(c_ly))
                if None in {bx, by, lx, ly}:
                    warnings.append(f"row {idx}: skipped (missing baryon/lens coordinates)")
                    continue
                obs_dx = lx - bx
                obs_dy = ly - by

            grad_dx = safe_float(row.get(c_grad_x))
            grad_dy = safe_float(row.get(c_grad_y))
            sigma = safe_float(row.get(c_sigma), default=1.0)

            if None in {obs_dx, obs_dy, grad_dx, grad_dy}:
                warnings.append(f"row {idx}: skipped (missing required lensing value)")
                continue
            sigma = max(float(sigma or 1.0), 1e-6)
            points.append(
                LensingPoint(
                    system_id=sid,
                    obs_dx=float(obs_dx),
                    obs_dy=float(obs_dy),
                    grad_dx=float(grad_dx),
                    grad_dy=float(grad_dy),
                    sigma=sigma,
                )
            )
    if len(points) < 8:
        raise ValueError(f"Lensing CSV produced too few usable rows: {len(points)}")
    return points, warnings


def parse_rotation_csv(path: Path) -> tuple[list[RotationPoint], list[str]]:
    warnings: list[str] = []
    points: list[RotationPoint] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        hmap = normalize_header_map(reader.fieldnames)

        c_sid = pick_col(hmap, ["system_id", "galaxy_id", "id", "name"])
        c_r = pick_col(hmap, ["radius", "r", "rad"])
        c_v = pick_col(hmap, ["v_obs", "velocity_obs", "velocity", "v"])
        c_ve = pick_col(hmap, ["v_err", "velocity_err", "err", "sigma_v"])
        c_bary = pick_col(hmap, ["baryon_term", "v_baryon2", "g_baryon"])
        c_hist = pick_col(hmap, ["history_term", "memory_term", "g_memory_unit", "sigma_lag_term"])

        if c_r is None or c_v is None:
            raise ValueError("Rotation CSV needs at least radius and observed velocity columns.")

        for idx, row in enumerate(reader, start=1):
            sid = str(row.get(c_sid, f"R{idx}") if c_sid else f"R{idx}").strip() or f"R{idx}"
            radius = safe_float(row.get(c_r))
            v_obs = safe_float(row.get(c_v))
            v_err = safe_float(row.get(c_ve), default=4.0)
            baryon_term = safe_float(row.get(c_bary))
            history_term = safe_float(row.get(c_hist))

            if radius is None or v_obs is None:
                warnings.append(f"row {idx}: skipped (missing radius or velocity)")
                continue

            if baryon_term is None:
                baryon_term = 0.7 * max(v_obs, 0.0) ** 2
            if history_term is None:
                history_term = max(max(v_obs, 0.0) ** 2 - baryon_term, 0.0)

            points.append(
                RotationPoint(
                    system_id=sid,
                    radius=float(radius),
                    v_obs=float(v_obs),
                    v_err=max(float(v_err or 4.0), 1e-6),
                    baryon_term=max(float(baryon_term), 0.0),
                    history_term=max(float(history_term), 0.0),
                )
            )
    if len(points) < 16:
        raise ValueError(f"Rotation CSV produced too few usable rows: {len(points)}")
    return points, warnings


def generate_synthetic_data(seed: int) -> tuple[list[LensingPoint], list[RotationPoint], dict]:
    rng = random.Random(seed)
    true_tau = 0.42
    true_k = 1.15

    lensing: list[LensingPoint] = []
    for i in range(36):
        grad_dx = rng.gauss(0.0, 1.35)
        grad_dy = rng.gauss(0.0, 1.35)
        obs_dx = true_tau * grad_dx + rng.gauss(0.0, 0.24)
        obs_dy = true_tau * grad_dy + rng.gauss(0.0, 0.24)
        sigma = 0.28 + abs(rng.gauss(0.0, 0.04))
        lensing.append(
            LensingPoint(
                system_id=f"L{i+1:03d}",
                obs_dx=obs_dx,
                obs_dy=obs_dy,
                grad_dx=grad_dx,
                grad_dy=grad_dy,
                sigma=max(sigma, 0.08),
            )
        )

    rotation: list[RotationPoint] = []
    for gid in range(22):
        for j in range(18):
            r = 1.6 + 1.1 * j + rng.random() * 0.35
            v_bary = 35.0 + 95.0 * (1.0 - math.exp(-r / 6.0)) * math.exp(-r / 50.0) + 22.0
            baryon_term = max(v_bary**2, 1.0)
            history_term = max(5200.0 * (1.0 - math.exp(-r / 24.0)) * math.exp(-r / 130.0) + 180.0, 0.0)
            v_true = math.sqrt(max(baryon_term + true_k * history_term, 1e-9))
            v_obs = v_true + rng.gauss(0.0, 4.2)
            v_err = 3.2 + rng.random() * 1.3
            rotation.append(
                RotationPoint(
                    system_id=f"G{gid+1:03d}",
                    radius=r,
                    v_obs=max(v_obs, 1.0),
                    v_err=v_err,
                    baryon_term=baryon_term,
                    history_term=history_term,
                )
            )

    meta = {"true_tau": true_tau, "true_k": true_k}
    return lensing, rotation, meta


def fit_tau(points: list[LensingPoint]) -> tuple[float, float]:
    num = 0.0
    den = 0.0
    for p in points:
        w = 1.0 / (p.sigma**2)
        num += (p.obs_dx * p.grad_dx + p.obs_dy * p.grad_dy) * w
        den += (p.grad_dx**2 + p.grad_dy**2) * w
    tau = num / den if den > 1e-12 else 0.0
    return tau, chi2_lensing(points, tau)


def chi2_lensing(points: list[LensingPoint], tau: float) -> float:
    total = 0.0
    for p in points:
        dx = p.obs_dx - tau * p.grad_dx
        dy = p.obs_dy - tau * p.grad_dy
        total += (dx * dx + dy * dy) / (p.sigma**2)
    return total


def chi2_rotation(points: list[RotationPoint], k: float) -> float:
    total = 0.0
    for p in points:
        v_model = math.sqrt(max(p.baryon_term + k * p.history_term, 1e-9))
        total += ((p.v_obs - v_model) ** 2) / (p.v_err**2)
    return total


def compute_aic(chi2: float, k_params: int) -> float:
    return chi2 + 2.0 * float(k_params)


def compute_bic(chi2: float, k_params: int, n_samples: int) -> float:
    n_eff = max(int(n_samples), 1)
    return chi2 + float(k_params) * math.log(n_eff)


def fit_k(points: list[RotationPoint]) -> tuple[float, float]:
    best_k = 0.0
    best_chi2 = float("inf")
    for i in range(1001):
        k = 5.0 * i / 1000.0
        c = chi2_rotation(points, k)
        if c < best_chi2:
            best_k = k
            best_chi2 = c

    lo = max(0.0, best_k - 0.25)
    hi = best_k + 0.25
    for i in range(801):
        k = lo + (hi - lo) * i / 800.0
        c = chi2_rotation(points, k)
        if c < best_chi2:
            best_k = k
            best_chi2 = c
    return best_k, best_chi2


def offset_score(points: list[LensingPoint], tau: float) -> float:
    obs = [math.hypot(p.obs_dx, p.obs_dy) for p in points]
    pred = [math.hypot(tau * p.grad_dx, tau * p.grad_dy) for p in points]
    mae_base = statistics.fmean(abs(v) for v in obs)
    mae_mem = statistics.fmean(abs(v - pv) for v, pv in zip(obs, pred))
    return 1.0 - (mae_mem / (mae_base + 1e-12))


def evaluate_models(lensing: list[LensingPoint], rotation: list[RotationPoint]) -> FitMetrics:
    tau_fit, chi2_lens_memory = fit_tau(lensing)
    chi2_lens_baseline = chi2_lensing(lensing, tau=0.0)
    k_fit, chi2_rot_memory = fit_k(rotation)
    chi2_rot_baseline = chi2_rotation(rotation, k=0.0)

    n_lens = len(lensing)
    n_rot = len(rotation)
    n_total = n_lens + n_rot

    delta_chi2_lens = chi2_lens_memory - chi2_lens_baseline
    delta_chi2_rot = chi2_rot_memory - chi2_rot_baseline
    delta_chi2_total = delta_chi2_lens + delta_chi2_rot

    aic_lens_baseline = compute_aic(chi2_lens_baseline, k_params=0)
    aic_lens_memory = compute_aic(chi2_lens_memory, k_params=1)
    aic_rot_baseline = compute_aic(chi2_rot_baseline, k_params=0)
    aic_rot_memory = compute_aic(chi2_rot_memory, k_params=1)
    aic_baseline = compute_aic(chi2_lens_baseline + chi2_rot_baseline, k_params=0)
    aic_memory = compute_aic(chi2_lens_memory + chi2_rot_memory, k_params=2)

    bic_lens_baseline = compute_bic(chi2_lens_baseline, k_params=0, n_samples=n_lens)
    bic_lens_memory = compute_bic(chi2_lens_memory, k_params=1, n_samples=n_lens)
    bic_rot_baseline = compute_bic(chi2_rot_baseline, k_params=0, n_samples=n_rot)
    bic_rot_memory = compute_bic(chi2_rot_memory, k_params=1, n_samples=n_rot)
    bic_baseline = compute_bic(chi2_lens_baseline + chi2_rot_baseline, k_params=0, n_samples=n_total)
    bic_memory = compute_bic(chi2_lens_memory + chi2_rot_memory, k_params=2, n_samples=n_total)

    return FitMetrics(
        tau_fit=tau_fit,
        k_fit=k_fit,
        n_lensing=n_lens,
        n_rotation=n_rot,
        n_total=n_total,
        chi2_lens_baseline=chi2_lens_baseline,
        chi2_lens_memory=chi2_lens_memory,
        chi2_rot_baseline=chi2_rot_baseline,
        chi2_rot_memory=chi2_rot_memory,
        chi2_baseline=chi2_lens_baseline + chi2_rot_baseline,
        chi2_memory=chi2_lens_memory + chi2_rot_memory,
        delta_chi2_lens=delta_chi2_lens,
        delta_chi2_rot=delta_chi2_rot,
        delta_chi2_total=delta_chi2_total,
        delta_chi2_lens_per_point=delta_chi2_lens / max(n_lens, 1),
        delta_chi2_rot_per_point=delta_chi2_rot / max(n_rot, 1),
        delta_chi2_total_per_point=delta_chi2_total / max(n_total, 1),
        aic_lens_baseline=aic_lens_baseline,
        aic_lens_memory=aic_lens_memory,
        aic_rot_baseline=aic_rot_baseline,
        aic_rot_memory=aic_rot_memory,
        aic_baseline=aic_baseline,
        aic_memory=aic_memory,
        delta_aic_lens=aic_lens_memory - aic_lens_baseline,
        delta_aic_rot=aic_rot_memory - aic_rot_baseline,
        delta_aic_total=aic_memory - aic_baseline,
        bic_lens_baseline=bic_lens_baseline,
        bic_lens_memory=bic_lens_memory,
        bic_rot_baseline=bic_rot_baseline,
        bic_rot_memory=bic_rot_memory,
        bic_baseline=bic_baseline,
        bic_memory=bic_memory,
        delta_bic_lens=bic_lens_memory - bic_lens_baseline,
        delta_bic_rot=bic_rot_memory - bic_rot_baseline,
        delta_bic_total=bic_memory - bic_baseline,
        offset_score=offset_score(lensing, tau_fit),
    )


def lens_norm_residual(p: LensingPoint, tau: float) -> float:
    dx = p.obs_dx - tau * p.grad_dx
    dy = p.obs_dy - tau * p.grad_dy
    return math.hypot(dx, dy) / max(p.sigma, 1e-12)


def rot_norm_residual(p: RotationPoint, k_fit: float) -> float:
    v_model = math.sqrt(max(p.baryon_term + k_fit * p.history_term, 1e-9))
    return abs(p.v_obs - v_model) / max(p.v_err, 1e-12)


def trimmed_by_outliers(
    lensing: list[LensingPoint],
    rotation: list[RotationPoint],
    tau_fit: float,
    k_fit: float,
    trim_fraction: float,
) -> tuple[list[LensingPoint], list[RotationPoint], int, int]:
    n_lens = len(lensing)
    n_rot = len(rotation)
    n_trim_lens = min(max(0, int(round(n_lens * trim_fraction))), max(0, n_lens - 8))
    n_trim_rot = min(max(0, int(round(n_rot * trim_fraction))), max(0, n_rot - 16))

    lens_sorted = sorted(lensing, key=lambda p: lens_norm_residual(p, tau_fit), reverse=True)
    rot_sorted = sorted(rotation, key=lambda p: rot_norm_residual(p, k_fit), reverse=True)

    lens_trimmed = lens_sorted[n_trim_lens:]
    rot_trimmed = rot_sorted[n_trim_rot:]
    return lens_trimmed, rot_trimmed, n_trim_lens, n_trim_rot


def robustness_checks(
    lensing: list[LensingPoint],
    rotation: list[RotationPoint],
    fit_ref: FitMetrics,
    seed: int,
    holdout_fraction: float = 0.10,
    n_leave_runs: int = 24,
    trim_fraction: float = 0.05,
) -> dict:
    rng = random.Random(seed + 1777)
    leave_chi2: list[float] = []
    leave_aic: list[float] = []
    leave_bic: list[float] = []
    leave_pass = 0

    keep_lens = max(8, int(round(len(lensing) * (1.0 - holdout_fraction))))
    keep_rot = max(16, int(round(len(rotation) * (1.0 - holdout_fraction))))

    n_runs = max(1, n_leave_runs)
    for _ in range(n_runs):
        lens_sub = rng.sample(lensing, min(keep_lens, len(lensing)))
        rot_sub = rng.sample(rotation, min(keep_rot, len(rotation)))
        m = evaluate_models(lens_sub, rot_sub)
        leave_chi2.append(m.delta_chi2_total)
        leave_aic.append(m.delta_aic_total)
        leave_bic.append(m.delta_bic_total)
        if (m.delta_chi2_total < 0.0) and (m.delta_aic_total <= -10.0) and (m.delta_bic_total <= -10.0):
            leave_pass += 1

    lens_trimmed, rot_trimmed, n_trim_lens, n_trim_rot = trimmed_by_outliers(
        lensing=lensing,
        rotation=rotation,
        tau_fit=fit_ref.tau_fit,
        k_fit=fit_ref.k_fit,
        trim_fraction=trim_fraction,
    )
    trim_metrics = evaluate_models(lens_trimmed, rot_trimmed)
    trim_pass = (
        (trim_metrics.delta_chi2_total < 0.0)
        and (trim_metrics.delta_aic_total <= -10.0)
        and (trim_metrics.delta_bic_total <= -10.0)
    )

    return {
        "leave_out_fraction": holdout_fraction,
        "leave_out_runs": n_runs,
        "leave_out_n_lensing_kept": len(lens_trimmed) if n_runs == 0 else keep_lens,
        "leave_out_n_rotation_kept": len(rot_trimmed) if n_runs == 0 else keep_rot,
        "leave_out_delta_chi2_median": statistics.median(leave_chi2),
        "leave_out_delta_chi2_min": min(leave_chi2),
        "leave_out_delta_chi2_max": max(leave_chi2),
        "leave_out_delta_aic_median": statistics.median(leave_aic),
        "leave_out_delta_bic_median": statistics.median(leave_bic),
        "leave_out_pass_fraction": leave_pass / max(n_runs, 1),
        "leave_out_pass_all": leave_pass == n_runs,
        "outlier_trim_fraction": trim_fraction,
        "outlier_trim_n_lensing_removed": n_trim_lens,
        "outlier_trim_n_rotation_removed": n_trim_rot,
        "outlier_trim_n_lensing_kept": len(lens_trimmed),
        "outlier_trim_n_rotation_kept": len(rot_trimmed),
        "outlier_trim_delta_chi2": trim_metrics.delta_chi2_total,
        "outlier_trim_delta_aic": trim_metrics.delta_aic_total,
        "outlier_trim_delta_bic": trim_metrics.delta_bic_total,
        "outlier_trim_pass": trim_pass,
    }


def summarize(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "mean": float("nan"), "std": float("nan"), "cv": float("inf"), "min": float("nan"), "max": float("nan")}
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv_v = std_v / abs(mean_v) if abs(mean_v) > 1e-12 else float("inf")
    return {
        "count": len(values),
        "mean": mean_v,
        "std": std_v,
        "cv": cv_v,
        "min": min(values),
        "max": max(values),
    }


def stability_analysis(
    lensing: list[LensingPoint],
    rotation: list[RotationPoint],
    seed: int,
    n_iter: int,
    fraction: float,
) -> tuple[dict, dict]:
    rng = random.Random(seed + 991)
    taus: list[float] = []
    ks: list[float] = []

    n_lens = max(8, int(len(lensing) * fraction))
    n_rot = max(16, int(len(rotation) * fraction))

    for _ in range(max(n_iter, 0)):
        lens_sub = rng.sample(lensing, min(n_lens, len(lensing)))
        rot_sub = rng.sample(rotation, min(n_rot, len(rotation)))
        tau, _ = fit_tau(lens_sub)
        k, _ = fit_k(rot_sub)
        taus.append(tau)
        ks.append(k)

    return summarize(taus), summarize(ks)


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
    w, h = 1200, 720
    left, top, right, bottom = 80, 35, w - 35, h - 70
    c = Canvas(w, h, bg=(250, 252, 251))

    xmin, xmax = min(x), max(x)
    yvals = [v for _, ys, _ in series for v in ys]
    ymin, ymax = min(yvals), max(yvals)
    if math.isclose(ymin, ymax):
        ymin -= 1.0
        ymax += 1.0
    pad = 0.08 * (ymax - ymin)
    ymin -= pad
    ymax += pad

    c.rect(left, top, right, bottom, (70, 90, 85))
    for t in range(1, 5):
        gy = top + int((bottom - top) * t / 5)
        c.line(left, gy, right, gy, (220, 228, 224))

    for _, ys, color in series:
        pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, ys)]
        c.polyline(pts, color)

    c.save_png(path)


def aggregate_rotation(points: list[RotationPoint], k_mem: float, bins: int = 36) -> tuple[list[float], list[float], list[float], list[float]]:
    rmin = min(p.radius for p in points)
    rmax = max(p.radius for p in points)
    if rmax <= rmin:
        rmax = rmin + 1.0

    edges = [rmin + (rmax - rmin) * i / bins for i in range(bins + 1)]
    grouped: list[list[RotationPoint]] = [[] for _ in range(bins)]
    for p in points:
        idx = int((p.radius - rmin) / (rmax - rmin) * bins)
        idx = max(0, min(bins - 1, idx))
        grouped[idx].append(p)

    x: list[float] = []
    obs: list[float] = []
    base: list[float] = []
    mem: list[float] = []
    for i, grp in enumerate(grouped):
        if not grp:
            continue
        xc = 0.5 * (edges[i] + edges[i + 1])
        x.append(xc)
        obs.append(statistics.fmean(p.v_obs for p in grp))
        base.append(statistics.fmean(math.sqrt(max(p.baryon_term, 1e-9)) for p in grp))
        mem.append(statistics.fmean(math.sqrt(max(p.baryon_term + k_mem * p.history_term, 1e-9)) for p in grp))
    return x, obs, base, mem


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
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for key, value in payload.items():
            writer.writerow([key, value])


def write_parameter_stability(path: Path, tau_stats: dict, k_stats: dict, threshold: float, source_mode: str, test_id: str) -> None:
    def row(name: str, stats: dict) -> str:
        cv = stats["cv"]
        status = "pass" if (not math.isinf(cv) and cv < threshold) else "fail"
        return (
            f"| {name} | {stats['count']} | {fmt(stats['mean'])} | {fmt(stats['std'])} | "
            f"{fmt(cv)} | < {threshold:.2f} | {status} |"
        )

    lines = [
        f"# Parameter Stability - {test_id}",
        "",
        f"- Data source mode: `{source_mode}`",
        f"- CV threshold: `{threshold:.2f}`",
        "",
        "| Parameter | Samples | Mean | StdDev | CV | Threshold | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        row("tau", tau_stats),
        row("k_memory", k_stats),
        "",
        "Interpretation:",
        "- Lower CV means better parameter stability under subsampling.",
        "- If synthetic/mixed data is used, treat these values as pipeline diagnostics, not publication evidence.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        f"{args.test_id} run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"baseline_model: {args.model_baseline}",
        f"memory_model: {args.model_memory}",
        f"seed: {args.seed}",
        f"subsamples: {args.subsamples}",
        f"fraction: {args.fraction}",
        f"data_source_mode: {details['data_source_mode']}",
        f"lensing_points: {details['n_lensing']}",
        f"rotation_points: {details['n_rotation']}",
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


def write_model_comparison(path: Path, fit: FitMetrics) -> None:
    lines = [
        "# Model Comparison",
        "",
        "Strict comparability checklist:",
        "",
        "| Check | Baseline | Memory | Status |",
        "| --- | --- | --- | --- |",
        f"| Sample rows | lensing={fit.n_lensing}, rotation={fit.n_rotation} | lensing={fit.n_lensing}, rotation={fit.n_rotation} | pass |",
        "| Sigma weights | Same input sigma (`sigma`, `v_err`) | Same input sigma (`sigma`, `v_err`) | pass |",
        "| Likelihood form | Weighted chi-square over identical rows | Weighted chi-square over identical rows | pass |",
        "| Priors / search space | Null fixed model (`tau=0`, `k=0`) | Same row set; fitted `tau` and `k` with deterministic solver | pass |",
        "",
        "Metric comparison:",
        "",
        "| Metric | Baseline | Memory | Delta (memory - baseline) |",
        "| --- | --- | --- | --- |",
        f"| chi2_lensing | {fmt(fit.chi2_lens_baseline)} | {fmt(fit.chi2_lens_memory)} | {fmt(fit.delta_chi2_lens)} |",
        f"| chi2_rotation | {fmt(fit.chi2_rot_baseline)} | {fmt(fit.chi2_rot_memory)} | {fmt(fit.delta_chi2_rot)} |",
        f"| chi2_total | {fmt(fit.chi2_baseline)} | {fmt(fit.chi2_memory)} | {fmt(fit.delta_chi2_total)} |",
        f"| delta_chi2_per_point (lensing) | - | - | {fmt(fit.delta_chi2_lens_per_point)} |",
        f"| delta_chi2_per_point (rotation) | - | - | {fmt(fit.delta_chi2_rot_per_point)} |",
        f"| delta_chi2_per_point (total) | - | - | {fmt(fit.delta_chi2_total_per_point)} |",
        f"| AIC_total | {fmt(fit.aic_baseline)} | {fmt(fit.aic_memory)} | {fmt(fit.delta_aic_total)} |",
        f"| BIC_total | {fmt(fit.bic_baseline)} | {fmt(fit.bic_memory)} | {fmt(fit.delta_bic_total)} |",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_robustness_report(path: Path, data: dict) -> None:
    lines = [
        "# Robustness Checks",
        "",
        "## Leave-10%-Out",
        "",
        f"- Runs: `{data['leave_out_runs']}`",
        f"- Fraction removed each run: `{fmt(data['leave_out_fraction'])}`",
        f"- Kept rows per run: lensing=`{data['leave_out_n_lensing_kept']}`, rotation=`{data['leave_out_n_rotation_kept']}`",
        f"- delta_chi2 median/min/max: `{fmt(data['leave_out_delta_chi2_median'])}` / `{fmt(data['leave_out_delta_chi2_min'])}` / `{fmt(data['leave_out_delta_chi2_max'])}`",
        f"- delta_aic median: `{fmt(data['leave_out_delta_aic_median'])}`",
        f"- delta_bic median: `{fmt(data['leave_out_delta_bic_median'])}`",
        f"- pass fraction (chi2<0, AIC<=-10, BIC<=-10): `{fmt(data['leave_out_pass_fraction'])}`",
        f"- pass all runs: `{str(bool(data['leave_out_pass_all'])).lower()}`",
        "",
        "## Top-Outlier Trim",
        "",
        f"- Trim fraction: `{fmt(data['outlier_trim_fraction'])}`",
        f"- Removed rows: lensing=`{data['outlier_trim_n_lensing_removed']}`, rotation=`{data['outlier_trim_n_rotation_removed']}`",
        f"- Kept rows: lensing=`{data['outlier_trim_n_lensing_kept']}`, rotation=`{data['outlier_trim_n_rotation_kept']}`",
        f"- delta_chi2: `{fmt(data['outlier_trim_delta_chi2'])}`",
        f"- delta_aic: `{fmt(data['outlier_trim_delta_aic'])}`",
        f"- delta_bic: `{fmt(data['outlier_trim_delta_bic'])}`",
        f"- trim pass (chi2<0, AIC<=-10, BIC<=-10): `{str(bool(data['outlier_trim_pass'])).lower()}`",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def maybe_export_synthetic_inputs(out_dir: Path, lensing: list[LensingPoint], rotation: list[RotationPoint], source_mode: str) -> None:
    if source_mode != "synthetic":
        return
    lens_path = out_dir / "synthetic-lensing.csv"
    rot_path = out_dir / "synthetic-rotation.csv"

    with lens_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "obs_dx", "obs_dy", "sigma_grad_x", "sigma_grad_y", "sigma"])
        for p in lensing:
            w.writerow([p.system_id, fmt(p.obs_dx), fmt(p.obs_dy), fmt(p.grad_dx), fmt(p.grad_dy), fmt(p.sigma)])

    with rot_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["system_id", "radius", "v_obs", "v_err", "baryon_term", "history_term"])
        for p in rotation:
            w.writerow([p.system_id, fmt(p.radius), fmt(p.v_obs), fmt(p.v_err), fmt(p.baryon_term), fmt(p.history_term)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QNG lensing/dark-memory comparison.")
    parser.add_argument("--test-id", default=DEFAULT_TEST_ID, help="Logical test ID label used in report headers/logs.")
    parser.add_argument("--dataset-id", default="DS-006", help="Dataset manifest ID (default: DS-006).")
    parser.add_argument("--model-baseline", default="gr_dm", help="Baseline model label.")
    parser.add_argument("--model-memory", default="qng_sigma_memory", help="Memory model label.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output artifact directory.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--lensing-csv", default="", help="Optional path to lensing CSV.")
    parser.add_argument("--rotation-csv", default="", help="Optional path to rotation CSV.")
    parser.add_argument("--subsamples", type=int, default=24, help="Number of subsampling runs for stability.")
    parser.add_argument("--fraction", type=float, default=0.8, help="Subsample fraction in (0,1].")
    parser.add_argument("--force-synthetic", action="store_true", help="Force synthetic data, ignore CSV inputs.")
    parser.add_argument("--strict-input", action="store_true", help="Fail instead of synthetic fallback if CSV parse fails.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fraction <= 0 or args.fraction > 1:
        print("Error: --fraction must be in (0,1].", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    warnings: list[str] = []

    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"No dataset-manifest entry found for {args.dataset_id}.")

    lensing: list[LensingPoint] | None = None
    rotation: list[RotationPoint] | None = None
    synthetic_meta: dict = {}
    source_mode = "synthetic"

    if not args.force_synthetic and args.lensing_csv and args.rotation_csv:
        try:
            lensing, w1 = parse_lensing_csv(Path(args.lensing_csv))
            rotation, w2 = parse_rotation_csv(Path(args.rotation_csv))
            warnings.extend(w1)
            warnings.extend(w2)
            source_mode = "provided"
        except Exception as exc:  # noqa: BLE001
            if args.strict_input:
                print(f"Error: input parsing failed under --strict-input: {exc}", file=sys.stderr)
                return 2
            warnings.append(f"Input parsing failed; falling back to synthetic data: {exc}")

    if lensing is None or rotation is None:
        lensing, rotation, synthetic_meta = generate_synthetic_data(args.seed)
        source_mode = "synthetic"
        warnings.append("Synthetic data was used. Metrics are pipeline diagnostics only.")

    fit = evaluate_models(lensing, rotation)
    tau_stats, k_stats = stability_analysis(
        lensing=lensing,
        rotation=rotation,
        seed=args.seed,
        n_iter=args.subsamples,
        fraction=args.fraction,
    )
    robust = robustness_checks(
        lensing=lensing,
        rotation=rotation,
        fit_ref=fit,
        seed=args.seed,
        holdout_fraction=0.10,
        n_leave_runs=24,
        trim_fraction=0.05,
    )

    cv_threshold = 0.30
    offset_threshold = 0.25
    stable = (not math.isinf(tau_stats["cv"])) and (not math.isinf(k_stats["cv"])) and tau_stats["cv"] < cv_threshold and k_stats["cv"] < cv_threshold
    pass_rule = (
        (fit.delta_chi2_total < 0.0)
        and (fit.delta_aic_total <= -10.0)
        and (fit.delta_bic_total <= -10.0)
        and stable
        and (fit.offset_score >= offset_threshold)
        and bool(robust["leave_out_pass_all"])
        and bool(robust["outlier_trim_pass"])
    )
    recommendation = "pending" if source_mode != "provided" else ("pass" if pass_rule else "fail")

    lens_sorted = sorted(lensing, key=lambda p: math.hypot(p.obs_dx, p.obs_dy))
    x_lens = list(range(1, len(lens_sorted) + 1))
    y_lens_obs = [math.hypot(p.obs_dx, p.obs_dy) for p in lens_sorted]
    y_lens_base = [0.0 for _ in lens_sorted]
    y_lens_mem = [math.hypot(fit.tau_fit * p.grad_dx, fit.tau_fit * p.grad_dy) for p in lens_sorted]
    plot_series_png(
        out_dir / "lensing-offsets.png",
        x_lens,
        [
            ("observed", y_lens_obs, (20, 70, 140)),
            ("baseline", y_lens_base, (160, 45, 40)),
            ("memory", y_lens_mem, (25, 130, 70)),
        ],
    )

    x_rot, y_rot_obs, y_rot_base, y_rot_mem = aggregate_rotation(rotation, k_mem=fit.k_fit, bins=36)
    plot_series_png(
        out_dir / "rotation-overlay.png",
        x_rot,
        [
            ("observed", y_rot_obs, (20, 70, 140)),
            ("baseline", y_rot_base, (160, 45, 40)),
            ("memory", y_rot_mem, (25, 130, 70)),
        ],
    )

    maybe_export_synthetic_inputs(out_dir, lensing, rotation, source_mode=source_mode)

    duration = time.perf_counter() - started
    details = {
        "dataset_id": args.dataset_id,
        "n_lensing": len(lensing),
        "n_rotation": len(rotation),
        "data_source_mode": source_mode,
        "duration_seconds": duration,
        "dataset_manifest": dataset_meta,
    }

    write_run_log(out_dir / "run-log.txt", args=args, details=details, warnings=warnings)
    write_parameter_stability(
        out_dir / "parameter-stability.md",
        tau_stats=tau_stats,
        k_stats=k_stats,
        threshold=cv_threshold,
        source_mode=source_mode,
        test_id=args.test_id,
    )
    write_model_comparison(out_dir / "model-comparison.md", fit=fit)
    write_robustness_report(out_dir / "robustness-checks.md", data=robust)
    write_csv_dict(
        out_dir / "robustness-checks.csv",
        {k: (fmt(v) if isinstance(v, float) else str(v)) for k, v in robust.items()},
    )

    summary = {
        "test_id": args.test_id,
        "dataset_id": args.dataset_id,
        "data_source_mode": source_mode,
        "n_lensing": str(fit.n_lensing),
        "n_rotation": str(fit.n_rotation),
        "n_total": str(fit.n_total),
        "tau_fit": fmt(fit.tau_fit),
        "k_memory_fit": fmt(fit.k_fit),
        "chi2_lensing_baseline": fmt(fit.chi2_lens_baseline),
        "chi2_lensing_memory": fmt(fit.chi2_lens_memory),
        "delta_chi2_lensing": fmt(fit.delta_chi2_lens),
        "delta_chi2_lensing_per_point": fmt(fit.delta_chi2_lens_per_point),
        "chi2_rotation_baseline": fmt(fit.chi2_rot_baseline),
        "chi2_rotation_memory": fmt(fit.chi2_rot_memory),
        "delta_chi2_rotation": fmt(fit.delta_chi2_rot),
        "delta_chi2_rotation_per_point": fmt(fit.delta_chi2_rot_per_point),
        "chi2_baseline": fmt(fit.chi2_baseline),
        "chi2_memory": fmt(fit.chi2_memory),
        "delta_chi2": fmt(fit.delta_chi2_total),
        "delta_chi2_per_point_total": fmt(fit.delta_chi2_total_per_point),
        "aic_lensing_baseline": fmt(fit.aic_lens_baseline),
        "aic_lensing_memory": fmt(fit.aic_lens_memory),
        "delta_aic_lensing": fmt(fit.delta_aic_lens),
        "aic_rotation_baseline": fmt(fit.aic_rot_baseline),
        "aic_rotation_memory": fmt(fit.aic_rot_memory),
        "delta_aic_rotation": fmt(fit.delta_aic_rot),
        "aic_baseline": fmt(fit.aic_baseline),
        "aic_memory": fmt(fit.aic_memory),
        "delta_aic": fmt(fit.delta_aic_total),
        "bic_lensing_baseline": fmt(fit.bic_lens_baseline),
        "bic_lensing_memory": fmt(fit.bic_lens_memory),
        "delta_bic_lensing": fmt(fit.delta_bic_lens),
        "bic_rotation_baseline": fmt(fit.bic_rot_baseline),
        "bic_rotation_memory": fmt(fit.bic_rot_memory),
        "delta_bic_rotation": fmt(fit.delta_bic_rot),
        "bic_baseline": fmt(fit.bic_baseline),
        "bic_memory": fmt(fit.bic_memory),
        "delta_bic": fmt(fit.delta_bic_total),
        "offset_score": fmt(fit.offset_score),
        "cv_tau": fmt(tau_stats["cv"]),
        "cv_k_memory": fmt(k_stats["cv"]),
        "leave_out_pass_fraction": fmt(float(robust["leave_out_pass_fraction"])),
        "leave_out_pass_all": str(bool(robust["leave_out_pass_all"])),
        "outlier_trim_pass": str(bool(robust["outlier_trim_pass"])),
        "outlier_trim_delta_chi2": fmt(float(robust["outlier_trim_delta_chi2"])),
        "outlier_trim_delta_aic": fmt(float(robust["outlier_trim_delta_aic"])),
        "outlier_trim_delta_bic": fmt(float(robust["outlier_trim_delta_bic"])),
        "rule_pass_delta_chi2": str(fit.delta_chi2_total < 0.0),
        "rule_pass_delta_aic": str(fit.delta_aic_total <= -10.0),
        "rule_pass_delta_bic": str(fit.delta_bic_total <= -10.0),
        "rule_pass_stability": str(stable),
        "rule_pass_offset_score": str(fit.offset_score >= offset_threshold),
        "rule_pass_leave_out": str(bool(robust["leave_out_pass_all"])),
        "rule_pass_outlier_trim": str(bool(robust["outlier_trim_pass"])),
        "pass_recommendation": recommendation,
        "duration_seconds": fmt(duration),
    }
    if synthetic_meta:
        summary["synthetic_true_tau"] = fmt(synthetic_meta.get("true_tau", float("nan")))
        summary["synthetic_true_k"] = fmt(synthetic_meta.get("true_k", float("nan")))

    write_csv_dict(out_dir / "fit-summary.csv", summary)

    print(f"{args.test_id} completed. data_source_mode={source_mode}")
    print(f"Artifacts written to: {out_dir}")
    print(
        " ".join(
            [
                f"delta_chi2={summary['delta_chi2']}",
                f"delta_aic={summary['delta_aic']}",
                f"delta_bic={summary['delta_bic']}",
                f"pass_recommendation={recommendation}",
            ]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
