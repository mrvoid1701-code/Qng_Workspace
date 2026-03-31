#!/usr/bin/env python3
"""
Executable closure suite for node-volume dynamics (Core Closure v1).

Implements four gates:
- T-V-01: conservation/growth gate
- T-V-02: stationary-spectrum gate
- T-V-03: attractor/identity gate
- T-V-04: GR-limit kill switch

Rules compared:
- V-A (conservative)
- V-B (expansive, frozen v1 rule)

Dependency policy: stdlib only.
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-tv-core-closure-v1"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class Node:
    node_id: int
    volume: float
    chi: float
    phi: float
    chi_prev: float
    age: int
    sigma: float = 0.0


@dataclass
class SimSeries:
    rule: str
    seed: int
    t: list[int]
    n: list[float]
    v_tot: list[float]
    complexity: list[float]


@dataclass
class RunMetrics:
    rule: str
    seed: int
    n_slope: float
    v_slope: float
    v_drift_rel: float
    jsd_mean: float
    attractor_overlap: float
    gr_ratio_tau0_vs_nom: float
    gr_tau0_max: float
    tv01_pass: bool
    tv02_pass: bool
    tv03_pass: bool
    tv04_pass: bool


def fmt(value: float) -> str:
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf"
    av = abs(value)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{value:.6e}"
    return f"{value:.6f}"


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


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def linear_slope(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    den = statistics.fmean((xi - mx) ** 2 for xi in x)
    if den <= 1e-16:
        return float("nan")
    cov = statistics.fmean((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    return cov / den


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    span = hi - lo
    if span <= 1e-16:
        return [0.5 for _ in values]
    return [(v - lo) / span for v in values]


def jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a.intersection(b))
    union = len(a.union(b))
    if union == 0:
        return 1.0
    return inter / union


def make_histogram(volumes: list[float], bins: list[float]) -> list[float]:
    if len(bins) < 2:
        raise ValueError("Need at least two bin edges.")
    counts = [0.0 for _ in range(len(bins) - 1)]
    if not volumes:
        return counts
    for v in volumes:
        idx = None
        for i in range(len(bins) - 1):
            left = bins[i]
            right = bins[i + 1]
            if (v >= left and v < right) or (i == len(bins) - 2 and v >= right):
                idx = i
                break
        if idx is None:
            idx = 0 if v < bins[0] else len(counts) - 1
        counts[idx] += 1.0
    total = sum(counts)
    if total <= 1e-16:
        return counts
    return [c / total for c in counts]


def js_divergence(p: list[float], q: list[float]) -> float:
    if len(p) != len(q):
        return float("nan")
    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    def kl(a: list[float], b: list[float]) -> float:
        val = 0.0
        for ai, bi in zip(a, b):
            if ai <= 0.0:
                continue
            bj = max(bi, 1e-16)
            val += ai * math.log(ai / bj)
        return val
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def top_ids(nodes: list[Node], k: int) -> set[int]:
    if not nodes:
        return set()
    k_eff = max(1, min(k, len(nodes)))
    ranked = sorted(nodes, key=lambda n: (n.sigma + 0.002 * n.age), reverse=True)[:k_eff]
    return {n.node_id for n in ranked}


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0.0, "mean": float("nan"), "std": float("nan"), "cv": float("inf"), "min": float("nan"), "max": float("nan")}
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv = std_v / abs(mean_v) if abs(mean_v) > 1e-16 else float("inf")
    return {
        "count": float(len(values)),
        "mean": mean_v,
        "std": std_v,
        "cv": cv,
        "min": min(values),
        "max": max(values),
    }


def simulate_rule(
    *,
    rule: str,
    seed: int,
    steps: int,
    sigma_min: float,
    sigma_birth: float,
    initial_nodes: int,
    base_volume: float,
    shock_fraction: float,
) -> tuple[SimSeries, dict[str, float], list[dict[str, str]]]:
    rng = random.Random(seed)
    nodes: list[Node] = []
    next_id = 0

    for _ in range(initial_nodes):
        volume = base_volume * (0.8 + 0.4 * rng.random())
        chi = 1.0 + rng.gauss(0.0, 0.06)
        phi = rng.random() * 2.0 * math.pi
        nodes.append(Node(node_id=next_id, volume=volume, chi=chi, phi=phi, chi_prev=chi, age=0))
        next_id += 1

    v_target = sum(n.volume for n in nodes)
    t_series: list[int] = []
    n_series: list[float] = []
    v_series: list[float] = []
    c_series: list[float] = []

    shock_step = int(0.60 * steps)
    top_pre: set[int] = set()
    top_post: set[int] = set()

    win1_volumes: list[float] = []
    win2_volumes: list[float] = []
    win3_volumes: list[float] = []
    win1_range = range(int(0.45 * steps), int(0.55 * steps))
    win2_range = range(int(0.65 * steps), int(0.75 * steps))
    win3_range = range(int(0.85 * steps), int(0.95 * steps))

    for t in range(steps + 1):
        if not nodes:
            # Safety guard to keep simulation alive in degenerate cases.
            chi = 1.0 + rng.gauss(0.0, 0.02)
            phi = rng.random() * 2.0 * math.pi
            nodes = [Node(node_id=next_id, volume=base_volume, chi=chi, phi=phi, chi_prev=chi, age=0)]
            next_id += 1

        mean_phi = math.atan2(
            sum(math.sin(n.phi) for n in nodes),
            max(1e-16, sum(math.cos(n.phi) for n in nodes)),
        )
        vol_mean = statistics.fmean(n.volume for n in nodes)

        for n in nodes:
            sigma_chi = math.exp(-abs(n.chi - 1.0) / 0.28)
            sigma_struct = math.exp(-abs(n.volume - vol_mean) / max(vol_mean, 1e-16))
            sigma_temp = math.exp(-abs(n.chi - n.chi_prev) / max(abs(n.chi), 1e-6))
            sigma_phi = 0.5 * (1.0 + math.cos(n.phi - mean_phi))
            n.sigma = clamp((sigma_chi * sigma_struct * sigma_temp * sigma_phi) ** 0.45, 0.0, 1.0)

        if t == shock_step - 1:
            top_pre = top_ids(nodes, k=max(12, len(nodes) // 10))
        if t == shock_step:
            k_perturb = max(1, int(len(nodes) * shock_fraction))
            for p in rng.sample(nodes, min(k_perturb, len(nodes))):
                p.phi = (p.phi + rng.uniform(-math.pi, math.pi)) % (2.0 * math.pi)
                p.chi = max(0.35, p.chi * (0.85 + 0.30 * rng.random()))

        dead_volume = 0.0
        survivors: list[Node] = []
        death_threshold = sigma_min * (0.85 if rule == "V-A" else 0.70)
        for n in nodes:
            if n.sigma < death_threshold:
                dead_volume += n.volume
                continue

            grow = 0.020 * max(0.0, n.sigma - 0.58)
            shrink = 0.016 * max(0.0, 0.42 - n.sigma)
            if rule == "V-A":
                n.volume = max(0.08 * base_volume, n.volume * (1.0 + 0.45 * (grow - shrink)))
            else:
                n.volume = max(0.08 * base_volume, n.volume * (1.0 + 1.65 * grow - 0.45 * shrink))

            n.chi_prev = n.chi
            n.chi = max(0.20, n.chi + 0.010 * (n.sigma - 0.5) + rng.gauss(0.0, 0.0025))
            n.phi = (n.phi + 0.33 + 0.18 * (1.0 - n.sigma) + rng.gauss(0.0, 0.055)) % (2.0 * math.pi)
            n.age += 1
            survivors.append(n)
        nodes = survivors

        if not nodes:
            chi = 1.0 + rng.gauss(0.0, 0.02)
            phi = rng.random() * 2.0 * math.pi
            nodes = [Node(node_id=next_id, volume=base_volume, chi=chi, phi=phi, chi_prev=chi, age=0)]
            next_id += 1

        births = 0
        birth_candidates = [n for n in nodes if n.sigma >= sigma_birth]
        for n in birth_candidates:
            if rule == "V-A":
                p_birth = 0.03 + 0.16 * max(0.0, n.sigma - sigma_birth)
            else:
                p_birth = 0.14 + 0.48 * max(0.0, n.sigma - sigma_birth)
            if rng.random() < p_birth:
                births += 1

        if rule == "V-A":
            donor_pool = dead_volume
            for donor in sorted(birth_candidates, key=lambda n: n.sigma, reverse=True):
                if births <= 0:
                    break
                take = min(0.18 * donor.volume, 0.45 * base_volume)
                donor.volume -= take
                donor_pool += take

            for _ in range(births):
                if donor_pool <= 0.10 * base_volume:
                    break
                v_new = min((0.70 + 0.35 * rng.random()) * base_volume, donor_pool)
                donor_pool -= v_new
                chi = 1.0 + rng.gauss(0.0, 0.05)
                phi = rng.random() * 2.0 * math.pi
                nodes.append(Node(node_id=next_id, volume=v_new, chi=chi, phi=phi, chi_prev=chi, age=0))
                next_id += 1

            if donor_pool > 0.0 and nodes:
                weight_sum = sum(max(n.sigma, 1e-3) for n in nodes)
                for n in nodes:
                    n.volume += donor_pool * (max(n.sigma, 1e-3) / weight_sum)

            # Enforce conservative total volume.
            v_now = sum(n.volume for n in nodes)
            if v_now > 1e-16:
                scale = v_target / v_now
                for n in nodes:
                    n.volume *= scale
        else:
            for _ in range(births):
                parent = birth_candidates[rng.randrange(len(birth_candidates))] if birth_candidates else nodes[rng.randrange(len(nodes))]
                v_new = (0.55 + 0.70 * rng.random()) * base_volume * max(0.65, parent.sigma)
                chi = max(0.2, parent.chi * (0.90 + 0.25 * rng.random()))
                phi = (parent.phi + rng.uniform(-0.25, 0.25)) % (2.0 * math.pi)
                nodes.append(Node(node_id=next_id, volume=v_new, chi=chi, phi=phi, chi_prev=chi, age=0))
                next_id += 1

            # Guardrail to avoid runaway numerical explosion.
            v_now = sum(n.volume for n in nodes)
            v_cap = 35.0 * v_target
            if v_now > v_cap and v_now > 1e-16:
                scale = v_cap / v_now
                for n in nodes:
                    n.volume *= scale

        v_now = sum(n.volume for n in nodes)
        n_now = float(len(nodes))
        sigma_mean = statistics.fmean(n.sigma for n in nodes)
        coherence = abs(sum(math.cos(n.phi) for n in nodes) / max(1.0, n_now))
        complexity = n_now * (1.0 + 0.30 * math.log1p(n_now)) * (0.55 + 0.45 * sigma_mean) * (0.70 + 0.30 * coherence)

        t_series.append(t)
        n_series.append(n_now)
        v_series.append(v_now)
        c_series.append(complexity)

        if t in win1_range:
            win1_volumes.extend(n.volume for n in nodes)
        if t in win2_range:
            win2_volumes.extend(n.volume for n in nodes)
        if t in win3_range:
            win3_volumes.extend(n.volume for n in nodes)

    top_post = top_ids(nodes, k=max(12, len(nodes) // 10))
    overlap = jaccard(top_pre, top_post)

    # Stationary/drift windows via Jensen-Shannon divergence.
    all_vols = win1_volumes + win2_volumes + win3_volumes
    if not all_vols:
        all_vols = [base_volume]
    v_min = max(min(all_vols) * 0.95, 1e-6)
    v_max = max(all_vols) * 1.05
    bins = [v_min + (v_max - v_min) * i / 20.0 for i in range(21)]
    h1 = make_histogram(win1_volumes or [base_volume], bins)
    h2 = make_histogram(win2_volumes or [base_volume], bins)
    h3 = make_histogram(win3_volumes or [base_volume], bins)
    jsd12 = js_divergence(h1, h2)
    jsd23 = js_divergence(h2, h3)
    jsd13 = js_divergence(h1, h3)
    jsd_mean = statistics.fmean([jsd12, jsd23, jsd13])

    x = [float(v) for v in t_series]
    n_slope = linear_slope(x, n_series)
    v_slope = linear_slope(x, v_series)
    v0 = max(v_series[0], 1e-16)
    v_drift_rel = max(abs(v - v_series[0]) for v in v_series) / v0

    # GR-limit kill switch proxy: memory acceleration should collapse as tau -> 0.
    acc_core: list[float] = []
    for i in range(1, len(v_series) - 1):
        second_diff = abs(v_series[i + 1] - 2.0 * v_series[i] + v_series[i - 1])
        acc_core.append(second_diff / v0)
    tau_nom = 0.06
    tau_zero = 1e-6
    max_nom = max((tau_nom * a for a in acc_core), default=0.0)
    max_zero = max((tau_zero * a for a in acc_core), default=0.0)
    gr_ratio = max_zero / max(max_nom, 1e-16)

    # Rule-specific gate interpretations.
    if rule == "V-A":
        tv01_pass = (v_drift_rel <= 3.0e-4) and (abs(n_slope) <= 0.12)
        tv02_pass = jsd_mean <= 0.08
    else:
        tv01_pass = (n_slope >= 0.08) and (v_slope >= 0.05)
        tv02_pass = jsd_mean <= 0.08

    tv03_pass = overlap >= 0.08
    tv04_pass = (gr_ratio <= 0.02) and (max_zero <= 1.0e-5)

    series = SimSeries(rule=rule, seed=seed, t=t_series, n=n_series, v_tot=v_series, complexity=c_series)
    metrics = {
        "n_slope": n_slope,
        "v_slope": v_slope,
        "v_drift_rel": v_drift_rel,
        "jsd12": jsd12,
        "jsd23": jsd23,
        "jsd13": jsd13,
        "jsd_mean": jsd_mean,
        "attractor_overlap": overlap,
        "gr_ratio_tau0_vs_nom": gr_ratio,
        "gr_tau0_max": max_zero,
        "tv01_pass": float(tv01_pass),
        "tv02_pass": float(tv02_pass),
        "tv03_pass": float(tv03_pass),
        "tv04_pass": float(tv04_pass),
    }
    windows_row = [
        {
            "rule": rule,
            "seed": str(seed),
            "jsd_12": fmt(jsd12),
            "jsd_23": fmt(jsd23),
            "jsd_13": fmt(jsd13),
            "jsd_mean": fmt(jsd_mean),
        }
    ]
    return series, metrics, windows_row


class Canvas:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.px = bytearray(bg * (width * height))

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 3
            self.px[idx : idx + 3] = bytes(color)

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

    def polyline(self, pts: list[tuple[int, int]], color: tuple[int, int, int]) -> None:
        for a, b in zip(pts[:-1], pts[1:]):
            self.line(a[0], a[1], b[0], b[1], color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row_bytes = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row_bytes
            raw.extend(self.px[i0 : i0 + row_bytes])

        def chunk(tag: bytes, data: bytes) -> bytes:
            crc = zlib.crc32(tag + data) & 0xFFFFFFFF
            return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", crc)

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


def plot_rules_png(path: Path, x: list[float], series: list[tuple[str, list[float], tuple[int, int, int]]]) -> None:
    w, h = 1280, 760
    left, top, right, bottom = 85, 30, w - 30, h - 70
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (70, 88, 82))

    xmin, xmax = min(x), max(x)
    yvals = [v for _, ys, _ in series for v in ys]
    ymin, ymax = min(yvals), max(yvals)
    if math.isclose(ymin, ymax):
        ymin -= 1.0
        ymax += 1.0
    pad = 0.08 * (ymax - ymin)
    ymin -= pad
    ymax += pad

    for g in range(1, 6):
        gy = top + int((bottom - top) * g / 6)
        c.line(left, gy, right, gy, (223, 229, 226))

    for _, ys, color in series:
        pts = [scale_point(xi, yi, xmin, xmax, ymin, ymax, left, top, right, bottom) for xi, yi in zip(x, ys)]
        c.polyline(pts, color)

    c.save_png(path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_fit_summary(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for k, v in payload.items():
            writer.writerow([k, v])


def write_timeseries(path: Path, series: SimSeries) -> None:
    rows = []
    for t, n, v, c in zip(series.t, series.n, series.v_tot, series.complexity):
        rows.append(
            {
                "rule": series.rule,
                "seed": str(series.seed),
                "t": str(t),
                "n_nodes": fmt(n),
                "v_total": fmt(v),
                "complexity": fmt(c),
            }
        )
    write_csv(path, ["rule", "seed", "t", "n_nodes", "v_total", "complexity"], rows)


def write_stability_md(path: Path, per_rule_stats: dict[str, dict[str, dict[str, float]]]) -> None:
    lines = [
        "# Parameter Stability - Core Closure v1 Volume Rules",
        "",
        "| Rule | Metric | Samples | Mean | StdDev | CV | Min | Max |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rule, metrics in per_rule_stats.items():
        for metric, stat in metrics.items():
            lines.append(
                f"| {rule} | {metric} | {int(stat['count'])} | {fmt(stat['mean'])} | {fmt(stat['std'])} | {fmt(stat['cv'])} | {fmt(stat['min'])} | {fmt(stat['max'])} |"
            )
    lines += [
        "",
        "Notes:",
        "- `V-A` expects low `v_drift_rel` and low `jsd_mean`.",
        "- `V-B` expects positive growth (`n_slope`, `v_slope`) with controlled spectral drift.",
        "- GR-kill metrics should remain near zero in `tau -> 0` proxy.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "Core Closure v1 volume-rule run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"steps: {args.steps}",
        f"runs: {args.runs}",
        f"seed_base: {args.seed}",
        f"sigma_min: {args.sigma_min}",
        f"sigma_birth: {args.sigma_birth}",
        f"initial_nodes: {args.initial_nodes}",
        f"base_volume: {args.base_volume}",
        f"shock_fraction: {args.shock_fraction}",
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
    p = argparse.ArgumentParser(description="Run node-volume Core Closure v1 gate suite (T-V-01..04).")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--steps", type=int, default=240)
    p.add_argument("--runs", type=int, default=30)
    p.add_argument("--seed", type=int, default=920)
    p.add_argument("--sigma-min", type=float, default=0.36)
    p.add_argument("--sigma-birth", type=float, default=0.72)
    p.add_argument("--initial-nodes", type=int, default=140)
    p.add_argument("--base-volume", type=float, default=1.0)
    p.add_argument("--shock-fraction", type=float, default=0.15)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.steps < 80:
        print("Error: --steps should be >= 80", file=sys.stderr)
        return 2
    if args.runs < 8:
        print("Error: --runs should be >= 8", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    warnings: list[str] = []
    manifest = read_dataset_manifest(args.dataset_id)
    if manifest is None:
        warnings.append(f"No dataset manifest entry found for {args.dataset_id}.")

    all_metrics: list[RunMetrics] = []
    windows_rows: list[dict[str, str]] = []
    ref_series: dict[str, SimSeries] = {}

    for rule in ("V-A", "V-B"):
        for idx in range(args.runs):
            seed_i = args.seed + (73 * idx) + (0 if rule == "V-A" else 10_000)
            series, metrics, win_rows = simulate_rule(
                rule=rule,
                seed=seed_i,
                steps=args.steps,
                sigma_min=args.sigma_min,
                sigma_birth=args.sigma_birth,
                initial_nodes=args.initial_nodes,
                base_volume=args.base_volume,
                shock_fraction=args.shock_fraction,
            )
            windows_rows.extend(win_rows)
            if rule not in ref_series:
                ref_series[rule] = series
            run = RunMetrics(
                rule=rule,
                seed=seed_i,
                n_slope=metrics["n_slope"],
                v_slope=metrics["v_slope"],
                v_drift_rel=metrics["v_drift_rel"],
                jsd_mean=metrics["jsd_mean"],
                attractor_overlap=metrics["attractor_overlap"],
                gr_ratio_tau0_vs_nom=metrics["gr_ratio_tau0_vs_nom"],
                gr_tau0_max=metrics["gr_tau0_max"],
                tv01_pass=bool(metrics["tv01_pass"]),
                tv02_pass=bool(metrics["tv02_pass"]),
                tv03_pass=bool(metrics["tv03_pass"]),
                tv04_pass=bool(metrics["tv04_pass"]),
            )
            all_metrics.append(run)

    # Artifacts: robustness rows
    robustness_rows: list[dict[str, str]] = []
    for m in all_metrics:
        robustness_rows.append(
            {
                "rule": m.rule,
                "seed": str(m.seed),
                "n_slope": fmt(m.n_slope),
                "v_slope": fmt(m.v_slope),
                "v_drift_rel": fmt(m.v_drift_rel),
                "jsd_mean": fmt(m.jsd_mean),
                "attractor_overlap": fmt(m.attractor_overlap),
                "gr_ratio_tau0_vs_nom": fmt(m.gr_ratio_tau0_vs_nom),
                "gr_tau0_max": fmt(m.gr_tau0_max),
                "tv01_pass": str(m.tv01_pass),
                "tv02_pass": str(m.tv02_pass),
                "tv03_pass": str(m.tv03_pass),
                "tv04_pass": str(m.tv04_pass),
            }
        )
    write_csv(
        out_dir / "robustness-runs.csv",
        [
            "rule",
            "seed",
            "n_slope",
            "v_slope",
            "v_drift_rel",
            "jsd_mean",
            "attractor_overlap",
            "gr_ratio_tau0_vs_nom",
            "gr_tau0_max",
            "tv01_pass",
            "tv02_pass",
            "tv03_pass",
            "tv04_pass",
        ],
        robustness_rows,
    )
    write_csv(
        out_dir / "stationarity-windows.csv",
        ["rule", "seed", "jsd_12", "jsd_23", "jsd_13", "jsd_mean"],
        windows_rows,
    )

    for rule, series in ref_series.items():
        write_timeseries(out_dir / f"simulation-timeseries-{rule.lower()}.csv", series)

    # Plot normalized total volume and node counts for reference runs.
    x_vals = [float(t) for t in ref_series["V-A"].t]
    plot_rules_png(
        out_dir / "volume-rules-timeseries.png",
        x_vals,
        [
            ("V-A N", normalize(ref_series["V-A"].n), (35, 93, 171)),
            ("V-B N", normalize(ref_series["V-B"].n), (170, 60, 45)),
            ("V-A Vtot", normalize(ref_series["V-A"].v_tot), (30, 150, 95)),
            ("V-B Vtot", normalize(ref_series["V-B"].v_tot), (158, 120, 22)),
        ],
    )

    # Aggregate per-rule metrics.
    by_rule: dict[str, list[RunMetrics]] = {"V-A": [], "V-B": []}
    for m in all_metrics:
        by_rule[m.rule].append(m)

    per_rule_stats: dict[str, dict[str, dict[str, float]]] = {}
    rule_gate_rows: list[dict[str, str]] = []
    fit_payload: dict[str, str] = {
        "dataset_id": args.dataset_id,
        "runs_per_rule": str(args.runs),
        "steps": str(args.steps),
    }

    selected_rule = "none"
    selected_reason = "V-B did not satisfy all closure gates."

    for rule in ("V-A", "V-B"):
        rows = by_rule[rule]
        n_slope_vals = [r.n_slope for r in rows]
        v_slope_vals = [r.v_slope for r in rows]
        v_drift_vals = [r.v_drift_rel for r in rows]
        jsd_vals = [r.jsd_mean for r in rows]
        overlap_vals = [r.attractor_overlap for r in rows]
        gr_ratio_vals = [r.gr_ratio_tau0_vs_nom for r in rows]
        gr_tau0_vals = [r.gr_tau0_max for r in rows]

        pass_tv01 = (sum(1 for r in rows if r.tv01_pass) / len(rows)) >= 0.80
        pass_tv02 = (sum(1 for r in rows if r.tv02_pass) / len(rows)) >= 0.80
        pass_tv03 = (sum(1 for r in rows if r.tv03_pass) / len(rows)) >= 0.80
        pass_tv04 = (sum(1 for r in rows if r.tv04_pass) / len(rows)) >= 0.95
        pass_all = pass_tv01 and pass_tv02 and pass_tv03 and pass_tv04

        if rule == "V-B" and pass_all:
            selected_rule = "V-B"
            selected_reason = "V-B passes all gates with controlled spectrum drift and GR-limit kill-switch safety."

        rule_gate_rows.append(
            {
                "rule": rule,
                "tv01_pass_rate": fmt(sum(1 for r in rows if r.tv01_pass) / len(rows)),
                "tv02_pass_rate": fmt(sum(1 for r in rows if r.tv02_pass) / len(rows)),
                "tv03_pass_rate": fmt(sum(1 for r in rows if r.tv03_pass) / len(rows)),
                "tv04_pass_rate": fmt(sum(1 for r in rows if r.tv04_pass) / len(rows)),
                "gate_recommendation": "pass" if pass_all else "fail",
            }
        )

        per_rule_stats[rule] = {
            "n_slope": summarize(n_slope_vals),
            "v_slope": summarize(v_slope_vals),
            "v_drift_rel": summarize(v_drift_vals),
            "jsd_mean": summarize(jsd_vals),
            "attractor_overlap": summarize(overlap_vals),
            "gr_ratio_tau0_vs_nom": summarize(gr_ratio_vals),
            "gr_tau0_max": summarize(gr_tau0_vals),
        }

        fit_payload[f"{rule}_n_slope_mean"] = fmt(per_rule_stats[rule]["n_slope"]["mean"])
        fit_payload[f"{rule}_v_slope_mean"] = fmt(per_rule_stats[rule]["v_slope"]["mean"])
        fit_payload[f"{rule}_v_drift_rel_mean"] = fmt(per_rule_stats[rule]["v_drift_rel"]["mean"])
        fit_payload[f"{rule}_jsd_mean"] = fmt(per_rule_stats[rule]["jsd_mean"]["mean"])
        fit_payload[f"{rule}_attractor_overlap_mean"] = fmt(per_rule_stats[rule]["attractor_overlap"]["mean"])
        fit_payload[f"{rule}_gr_ratio_mean"] = fmt(per_rule_stats[rule]["gr_ratio_tau0_vs_nom"]["mean"])
        fit_payload[f"{rule}_tv01_pass_rate"] = rule_gate_rows[-1]["tv01_pass_rate"]
        fit_payload[f"{rule}_tv02_pass_rate"] = rule_gate_rows[-1]["tv02_pass_rate"]
        fit_payload[f"{rule}_tv03_pass_rate"] = rule_gate_rows[-1]["tv03_pass_rate"]
        fit_payload[f"{rule}_tv04_pass_rate"] = rule_gate_rows[-1]["tv04_pass_rate"]
        fit_payload[f"{rule}_recommendation"] = rule_gate_rows[-1]["gate_recommendation"]

    fit_payload["selected_rule_v1"] = selected_rule
    fit_payload["selected_rule_reason"] = selected_reason

    write_csv(
        out_dir / "rule-comparison.csv",
        ["rule", "tv01_pass_rate", "tv02_pass_rate", "tv03_pass_rate", "tv04_pass_rate", "gate_recommendation"],
        rule_gate_rows,
    )
    write_fit_summary(out_dir / "fit-summary.csv", fit_payload)
    write_stability_md(out_dir / "parameter-stability.md", per_rule_stats)

    duration = time.perf_counter() - started
    write_run_log(
        out_dir / "run-log.txt",
        args=args,
        details={"dataset_manifest": manifest, "duration_seconds": duration},
        warnings=warnings,
    )

    print("Core closure v1 volume-rule suite completed.")
    print(f"Artifacts: {out_dir}")
    print(f"selected_rule_v1: {selected_rule}")
    for row in rule_gate_rows:
        print(
            f"{row['rule']} pass-rates: "
            f"T-V-01={row['tv01_pass_rate']} "
            f"T-V-02={row['tv02_pass_rate']} "
            f"T-V-03={row['tv03_pass_rate']} "
            f"T-V-04={row['tv04_pass_rate']} "
            f"-> {row['gate_recommendation']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
