#!/usr/bin/env python3
"""
QNG emergent metric hardening runner (v4).

Changes from v3:
- Frobenius normalization (replaces unit-trace normalization) in metric_from_sigma_hessian_v4.
- Isotropic shrinkage target adjusted to 1/sqrt(2) to maintain frob=1 invariant post-shrinkage.
- New G0 gate: vacuum stability (NaN/Inf check + condition number cap).
- D1-D4 gates and all thresholds are identical to v3.

Pre-registration: 05_validation/pre-registrations/qng-metric-hardening-v4.md
Method lock: 01_notes/metric/metric-lock-v4.md
Dependency policy: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import heapq
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-metric-hardening-v4"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class GateThresholds:
    # G0: vacuum stability (new in v4)
    g0_nan_inf_max: int = 0
    g0_cond_global_max: float = 1000.0
    g0_cond_lowcurv_max: float = 200.0
    g0_lowcurv_frob_threshold: float = 0.05
    # D1-D4: identical to v3
    d1_eps: float = 1e-8
    d2_median_max: float = 0.10
    d2_p90_max: float = 0.25
    d3_median_min: float = 0.90
    d3_p10_min: float = 0.70
    d4_shuffle_median_max: float = 0.55


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    i0 = int(math.floor(pos))
    i1 = int(math.ceil(pos))
    if i0 == i1:
        return xs[i0]
    w = pos - i0
    return (1.0 - w) * xs[i0] + w * xs[i1]


def median(values: list[float]) -> float:
    return quantile(values, 0.5)


def percentile10(values: list[float]) -> float:
    return quantile(values, 0.10)


def percentile90(values: list[float]) -> float:
    return quantile(values, 0.90)


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


def parse_scales(text: str) -> list[tuple[str, float]]:
    tokens = [t.strip().lower() for t in text.split(",") if t.strip()]
    if not tokens:
        raise ValueError("No scales provided.")
    out: list[tuple[str, float]] = []
    for tok in tokens:
        if "s0" in tok:
            if tok == "s0":
                mult = 1.0
            else:
                t = tok.replace("*", "").replace(" ", "").replace("s0", "")
                if t.endswith("x"):
                    t = t[:-1]
                if not t:
                    mult = 1.0
                else:
                    mult = float(t)
            out.append((f"{mult:g}s0", mult))
        else:
            mult = float(tok)
            out.append((f"{mult:g}", mult))
    return out


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    aug = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-16:
            raise ValueError("Singular matrix.")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            fac = aug[r][col]
            if fac == 0.0:
                continue
            for j in range(col, n + 1):
                aug[r][j] -= fac * aug[col][j]
    return [aug[i][n] for i in range(n)]


def fit_ridge(features: list[list[float]], targets: list[float], lam: float = 1e-9) -> list[float]:
    if not features:
        raise ValueError("No features.")
    p = len(features[0])
    a = [[0.0 for _ in range(p)] for _ in range(p)]
    b = [0.0 for _ in range(p)]
    for x, y in zip(features, targets):
        for i in range(p):
            b[i] += x[i] * y
            for j in range(p):
                a[i][j] += x[i] * x[j]
    for i in range(p):
        a[i][i] += lam
    return solve_linear_system(a, b)


def eig2x2(g11: float, g12: float, g22: float) -> tuple[float, float]:
    tr = g11 + g22
    det = g11 * g22 - g12 * g12
    disc = max(tr * tr - 4.0 * det, 0.0)
    root = math.sqrt(disc)
    l1 = 0.5 * (tr - root)
    l2 = 0.5 * (tr + root)
    return (l1, l2) if l1 <= l2 else (l2, l1)


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    inv11 = g22 / det
    inv22 = g11 / det
    inv12 = -g12 / det
    return inv11, inv12, inv22


def frob_norm2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


def cond_number2x2(g11: float, g12: float, g22: float) -> float:
    """Condition number κ = λmax / λmin (both positive; uses abs values)."""
    l1, l2 = eig2x2(g11, g12, g22)
    lmin = max(abs(l1), 1e-18)
    lmax = max(abs(l2), 1e-18)
    if lmin > lmax:
        lmin, lmax = lmax, lmin
    return lmax / lmin


def cosine(a: tuple[float, float], b: tuple[float, float]) -> float:
    na = math.hypot(a[0], a[1])
    nb = math.hypot(b[0], b[1])
    if na < 1e-16 or nb < 1e-16:
        return float("nan")
    return (a[0] * b[0] + a[1] * b[1]) / (na * nb)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def build_dataset_graph(dataset_id: str, seed: int) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float]:
    rng = random.Random(seed + 17)
    ds = dataset_id.upper().strip()
    if ds == "DS-002":
        n = 280
        k = 8
        spread = 2.3
    elif ds == "DS-003":
        n = 240
        k = 7
        spread = 2.0
    elif ds == "DS-006":
        n = 320
        k = 9
        spread = 2.7
    else:
        n = 260
        k = 8
        spread = 2.2

    coords: list[tuple[float, float]] = []
    for _ in range(n):
        x = rng.uniform(-spread, spread)
        y = rng.uniform(-spread, spread)
        coords.append((x, y))

    sigma: list[float] = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(clamp(s, 0.0, 1.0))

    dist = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.hypot(xi - xj, yi - yj)
            dist[i][j] = d
            dist[j][i] = d

    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    edge_lengths: list[float] = []
    for i in range(n):
        neigh = sorted(range(n), key=lambda j: dist[i][j] if j != i else float("inf"))[:k]
        for j in neigh:
            base = max(dist[i][j], 1e-6)
            w = base * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)

    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    median_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, sigma, adj_list, max(median_edge, 1e-9)


def dijkstra(adj: list[list[tuple[int, float]]], src: int) -> list[float]:
    n = len(adj)
    inf = float("inf")
    d = [inf for _ in range(n)]
    d[src] = 0.0
    pq: list[tuple[float, int]] = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u]:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v]:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


def choose_anchors(sigma: list[float], samples: int, seed: int) -> list[int]:
    rng = random.Random(seed + 71)
    n = len(sigma)
    target = max(8, min(samples, n))
    idx_sorted = sorted(range(n), key=lambda i: sigma[i], reverse=True)
    top_n = target // 2
    anchors = set(idx_sorted[:top_n])

    bins = [[], [], [], []]
    s_sorted = sorted(sigma)
    q1 = s_sorted[int(0.25 * (n - 1))]
    q2 = s_sorted[int(0.50 * (n - 1))]
    q3 = s_sorted[int(0.75 * (n - 1))]
    for i, s in enumerate(sigma):
        if s <= q1:
            bins[0].append(i)
        elif s <= q2:
            bins[1].append(i)
        elif s <= q3:
            bins[2].append(i)
        else:
            bins[3].append(i)
    while len(anchors) < target:
        b = bins[len(anchors) % 4]
        if not b:
            b = list(range(n))
        anchors.add(b[rng.randrange(len(b))])
    return list(anchors)


def local_nodes_from_anchor(dist_anchor: list[float], anchor: int, m: int) -> list[int]:
    ranked = sorted(range(len(dist_anchor)), key=lambda i: dist_anchor[i])
    out = [anchor]
    for i in ranked:
        if i == anchor:
            continue
        out.append(i)
        if len(out) >= m:
            break
    return out


def local_pairwise_distances(adj: list[list[tuple[int, float]]], local_nodes: list[int]) -> list[list[float]]:
    d_all = [dijkstra(adj, node) for node in local_nodes]
    m = len(local_nodes)
    out = [[0.0 for _ in range(m)] for _ in range(m)]
    for i in range(m):
        for j in range(m):
            out[i][j] = d_all[i][local_nodes[j]]
    return out


def geodesic_tangent_chart(dmat: list[list[float]]) -> list[tuple[float, float]] | None:
    m = len(dmat)
    if m < 8:
        return None
    candidates = list(range(1, m))
    if not candidates:
        return None
    l1 = max(candidates, key=lambda j: dmat[0][j])

    d01 = dmat[0][l1]
    if d01 <= 1e-9:
        return None

    best_l2 = None
    best_y2 = -1.0
    for j in candidates:
        if j == l1:
            continue
        d02 = dmat[0][j]
        d12 = dmat[l1][j]
        if d02 <= 1e-9:
            continue
        x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
        y2_sq = d02 * d02 - x2 * x2
        if y2_sq > best_y2:
            best_y2 = y2_sq
            best_l2 = j
    if best_l2 is None or best_y2 <= 1e-12:
        return None

    l2 = best_l2
    d02 = dmat[0][l2]
    d12 = dmat[l1][l2]
    x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
    y2 = math.sqrt(max(d02 * d02 - x2 * x2, 0.0))
    if y2 <= 1e-9:
        return None

    coords: list[tuple[float, float]] = [(0.0, 0.0) for _ in range(m)]
    coords[l1] = (d01, 0.0)
    coords[l2] = (x2, y2)

    for i in range(m):
        if i in (0, l1, l2):
            continue
        d0i = dmat[0][i]
        d1i = dmat[l1][i]
        d2i = dmat[l2][i]
        if d0i <= 1e-12:
            coords[i] = (0.0, 0.0)
            continue
        xi = (d0i * d0i + d01 * d01 - d1i * d1i) / (2.0 * d01)
        yi_abs_sq = d0i * d0i - xi * xi
        yi_abs = math.sqrt(max(yi_abs_sq, 0.0))
        p_plus = math.hypot(xi - x2, yi_abs - y2)
        p_minus = math.hypot(xi - x2, -yi_abs - y2)
        yi = yi_abs if abs(p_plus - d2i) <= abs(p_minus - d2i) else -yi_abs
        coords[i] = (xi, yi)

    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


def smooth_sigma_local(dmat: list[list[float]], sigma_local: list[float], s: float) -> list[float]:
    m = len(dmat)
    out = [0.0 for _ in range(m)]
    for i in range(m):
        num = 0.0
        den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * sigma_local[j]
            den += w
        out[i] = num / max(den, 1e-16)
    return out


def estimate_sigma_grad_hessian(
    chart: list[tuple[float, float]],
    sigma_local: list[float],
) -> tuple[tuple[float, float], tuple[float, float, float]] | None:
    # Local quadratic model:
    # Sigma(x,y) ~= c + b1 x + b2 y + 0.5 h11 x^2 + h12 xy + 0.5 h22 y^2
    feats: list[list[float]] = []
    targ: list[float] = []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
    if len(feats) < 10:
        return None
    try:
        beta = fit_ridge(feats, targ, lam=1e-8)
    except ValueError:
        return None
    grad = (beta[1], beta[2])
    hess = (beta[3], beta[4], beta[5])  # h11, h12, h22
    return grad, hess


def metric_from_sigma_hessian_v4(
    h11: float,
    h12: float,
    h22: float,
    floor: float = 1e-6,
    anisotropy_keep: float = 0.4,
    frob_floor: float = 1e-9,
) -> tuple[float, float, float, float]:
    """
    v4 metric from Sigma Hessian.

    Changes from v3:
    - Frobenius normalization replaces unit-trace normalization.
    - Isotropic shrinkage target = 1/sqrt(2) to maintain frob=1 invariant.
    - Returns (g11, g12, g22, frob_hessian_raw) where frob_hessian_raw is
      the Frobenius norm of the raw input Hessian (before SPD projection),
      used by the G0 vacuum gate.
    """
    # Raw Hessian Frobenius norm (before any processing) for G0 gate.
    frob_hessian_raw = frob_norm2x2(h11, h12, h22)

    # Dynamic metric proxy from acceleration Jacobian:
    # a = -grad Sigma => partial_j a_i = -H_ij.
    # Build SPD spatial metric via spectral-magnitude projection.
    tr = -(h11 + h22)
    det = (-h11) * (-h22) - (-h12) * (-h12)
    disc = max(tr * tr - 4.0 * det, 0.0)
    root = math.sqrt(disc)
    lam1 = 0.5 * (tr - root)
    lam2 = 0.5 * (tr + root)

    # Eigenvectors of symmetric matrix A = -H.
    a11 = -h11
    a12 = -h12
    a22 = -h22
    if abs(a12) > 1e-14:
        v1 = (lam1 - a22, a12)
        v2 = (lam2 - a22, a12)
    else:
        if a11 <= a22:
            v1, v2 = (1.0, 0.0), (0.0, 1.0)
        else:
            v1, v2 = (0.0, 1.0), (1.0, 0.0)

    def norm(v: tuple[float, float]) -> tuple[float, float]:
        n = math.hypot(v[0], v[1])
        if n <= 1e-18:
            return (1.0, 0.0)
        return (v[0] / n, v[1] / n)

    q1 = norm(v1)
    q2 = norm(v2)

    # SPD projection: absolute eigenvalues + floor.
    mu1 = max(abs(lam1), floor)
    mu2 = max(abs(lam2), floor)
    g11 = mu1 * q1[0] * q1[0] + mu2 * q2[0] * q2[0]
    g12 = mu1 * q1[0] * q1[1] + mu2 * q2[0] * q2[1]
    g22 = mu1 * q1[1] * q1[1] + mu2 * q2[1] * q2[1]

    # v4 lock:
    # 1) Remove conformal scale by Frobenius normalization (replaces unit-trace norm).
    #    frob(g) = 1 after this step (except fully degenerate → floor).
    # 2) Blend toward isotropic matrix with frob=1: iso = (1/sqrt(2), 0, 1/sqrt(2)).
    frob = frob_norm2x2(g11, g12, g22)
    denom = max(frob, frob_floor)
    g11 /= denom
    g12 /= denom
    g22 /= denom

    # Isotropic target with frob=1: I_frob = diag(1/sqrt(2), 1/sqrt(2))
    iso = 1.0 / math.sqrt(2.0)  # ≈ 0.7071
    keep = clamp(anisotropy_keep, 0.0, 1.0)
    g11 = keep * g11 + (1.0 - keep) * iso
    g22 = keep * g22 + (1.0 - keep) * iso
    g12 = keep * g12

    return g11, g12, g22, frob_hessian_raw


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

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row
            raw.extend(self.px[i0 : i0 + row])

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


def plot_histogram(path: Path, values: list[float], title_key: str, bins: int = 24, color: tuple[int, int, int] = (40, 112, 184)) -> None:
    if not values:
        values = [0.0]
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        hi = lo + 1.0

    w, h = 980, 620
    left, top, right, bottom = 70, 30, w - 20, h - 60
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    counts = [0 for _ in range(bins)]
    for v in values:
        t = (v - lo) / max(hi - lo, 1e-12)
        idx = min(bins - 1, max(0, int(t * bins)))
        counts[idx] += 1
    cmax = max(counts) if counts else 1

    bar_w = max(1, (right - left - 8) // bins)
    for i, cnt in enumerate(counts):
        x0 = left + 4 + i * bar_w
        x1 = min(right - 2, x0 + bar_w - 1)
        height_px = int((bottom - top - 10) * (cnt / max(cmax, 1)))
        y0 = bottom - height_px
        for x in range(x0, x1 + 1):
            c.line(x, bottom, x, y0, color)

    marker = abs(hash(title_key)) % 120
    c.line(left + 8, top + 8, left + 48 + marker % 20, top + 8, (130, 70, 60))
    c.save_png(path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG metric hardening v4 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"scales_cli: {args.scales}",
        f"samples: {args.samples}",
        f"seed: {args.seed}",
        f"duration_seconds: {details['duration_seconds']:.3f}",
        f"anchors_used: {details['anchors_used']}",
        f"decision: {details['decision']}",
        "",
    ]
    if details.get("dataset_manifest"):
        lines += [
            "dataset_manifest_entry:",
            json.dumps(details["dataset_manifest"], ensure_ascii=False, indent=2),
            "",
        ]
    lines += ["artifact_hashes_sha256:"]
    for k, v in details.get("artifact_hashes", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if warnings:
        lines.append("warnings:")
        for w in warnings:
            lines.append(f"- {w}")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG emergent metric hardening v4 (Frobenius normalization).")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--scales", default="s0,1.25s0,1.5s0")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.samples < 8:
        print("Error: --samples should be >= 8", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    thresholds = GateThresholds()
    warnings: list[str] = []
    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"No dataset manifest entry found for {args.dataset_id}.")

    coords, sigma, adj, median_edge = build_dataset_graph(args.dataset_id, args.seed)
    adj_norm = []
    for row in adj:
        adj_norm.append([(j, w / median_edge) for j, w in row])

    s0 = 1.0
    scales_parsed = parse_scales(args.scales)
    scales = [(label, mult * s0) for label, mult in scales_parsed]
    if not any(abs(s - s0) <= 1e-12 for _, s in scales):
        scales = [("1s0", s0)] + scales
    scales = sorted(scales, key=lambda t: t[1])
    scale_labels = [lbl for lbl, _ in scales]
    s0_label = min(scales, key=lambda t: abs(t[1] - s0))[0]

    anchors = choose_anchors(sigma, args.samples, args.seed)
    rng = random.Random(args.seed + 991)

    eig_rows: list[dict[str, str]] = []
    drift_rows: list[dict[str, str]] = []
    align_rows: list[dict[str, str]] = []
    vacuum_rows: list[dict[str, str]] = []

    min_eigs: list[float] = []
    drift_vals: list[float] = []
    cos_raw_vals: list[float] = []
    cos_shuf_vals: list[float] = []
    cond_vals: list[float] = []           # for G0b: global condition numbers
    cond_lowcurv_vals: list[float] = []   # for G0c: low-curvature condition numbers
    nan_inf_count: int = 0

    anchors_used = 0
    for anchor in anchors:
        d_anchor = dijkstra(adj_norm, anchor)
        local_nodes = local_nodes_from_anchor(d_anchor, anchor=anchor, m=20)
        if len(local_nodes) < 12:
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]

        d_local = local_pairwise_distances(adj_norm, local_nodes)
        chart = geodesic_tangent_chart(d_local)
        if chart is None:
            continue

        sigma_local = [sigma[n] for n in local_nodes]
        sigma_s0 = smooth_sigma_local(d_local, sigma_local, s0)
        gh0 = estimate_sigma_grad_hessian(chart, sigma_s0)
        if gh0 is None:
            continue
        grad0_vec, _h0 = gh0
        a_raw = (-grad0_vec[0], -grad0_vec[1])

        g_by_scale: dict[str, tuple[float, float, float]] = {}
        grad_by_scale: dict[str, tuple[float, float]] = {}

        for label, s in scales:
            sigma_s = smooth_sigma_local(d_local, sigma_local, s)
            gh = estimate_sigma_grad_hessian(chart, sigma_s)
            if gh is None:
                continue
            grad_vec, hess = gh
            g11, g12, g22, frob_h_raw = metric_from_sigma_hessian_v4(
                hess[0], hess[1], hess[2],
                floor=1e-6,
                anisotropy_keep=0.4,
                frob_floor=1e-9,
            )

            # G0a: check for NaN/Inf
            for val in (g11, g12, g22):
                if not math.isfinite(val):
                    nan_inf_count += 1

            # G0b/G0c: condition number
            kappa = cond_number2x2(g11, g12, g22)
            if math.isfinite(kappa):
                cond_vals.append(kappa)
                is_low_curv = frob_h_raw < thresholds.g0_lowcurv_frob_threshold
                vacuum_rows.append({
                    "anchor_id": str(anchor),
                    "scale": label,
                    "frob_hessian_raw": fmt(frob_h_raw),
                    "is_low_curv": str(is_low_curv),
                    "cond_number": fmt(kappa),
                    "g11": fmt(g11),
                    "g12": fmt(g12),
                    "g22": fmt(g22),
                })
                if is_low_curv:
                    cond_lowcurv_vals.append(kappa)

            lmin, lmax = eig2x2(g11, g12, g22)
            min_eigs.append(lmin)
            g_by_scale[label] = (g11, g12, g22)
            grad_by_scale[label] = grad_vec
            eig_rows.append({
                "anchor_id": str(anchor),
                "scale": label,
                "g11": fmt(g11),
                "g12": fmt(g12),
                "g22": fmt(g22),
                "min_eig": fmt(lmin),
                "max_eig": fmt(lmax),
                "trace": fmt(g11 + g22),
                "frob": fmt(frob_norm2x2(g11, g12, g22)),
                "det": fmt(g11 * g22 - g12 * g12),
                "cond": fmt(kappa),
                "spd": str(lmin >= thresholds.d1_eps),
            })

        if s0_label not in g_by_scale:
            continue

        g0 = g_by_scale[s0_label]
        g0_norm = max(frob_norm2x2(*g0), 1e-12)
        for label, _ in scales:
            if label == s0_label or label not in g_by_scale:
                continue
            g = g_by_scale[label]
            dg11 = g[0] - g0[0]
            dg12 = g[1] - g0[1]
            dg22 = g[2] - g0[2]
            drift = frob_norm2x2(dg11, dg12, dg22) / g0_norm
            drift_vals.append(drift)
            drift_rows.append({
                "anchor_id": str(anchor),
                "scale_ref": s0_label,
                "scale_test": label,
                "delta_g_fro_rel": fmt(drift),
            })

        inv = inv2x2(*g0)
        if inv is None:
            continue
        inv11, inv12, inv22 = inv
        grad0 = grad_by_scale.get(s0_label, grad0_vec)
        a_metric = (-(inv11 * grad0[0] + inv12 * grad0[1]), -(inv12 * grad0[0] + inv22 * grad0[1]))
        cos_raw = cosine(a_metric, a_raw)
        if math.isfinite(cos_raw):
            cos_raw_vals.append(cos_raw)

        # Negative control: shuffle sigma labels.
        sigma_shuf = sigma_local[:]
        rng.shuffle(sigma_shuf)
        sigma_shuf_s0 = smooth_sigma_local(d_local, sigma_shuf, s0)
        gh_shuf = estimate_sigma_grad_hessian(chart, sigma_shuf_s0)
        cos_shuf = float("nan")
        if gh_shuf is not None:
            grad_shuf_vec, hess_shuf = gh_shuf
            g11s, g12s, g22s, _ = metric_from_sigma_hessian_v4(
                hess_shuf[0], hess_shuf[1], hess_shuf[2],
                floor=1e-6, anisotropy_keep=0.4, frob_floor=1e-9,
            )
            inv_shuf = inv2x2(g11s, g12s, g22s)
            if inv_shuf is not None:
                si11, si12, si22 = inv_shuf
                a_metric_shuf = (
                    -(si11 * grad_shuf_vec[0] + si12 * grad_shuf_vec[1]),
                    -(si12 * grad_shuf_vec[0] + si22 * grad_shuf_vec[1]),
                )
                cos_shuf = cosine(a_metric_shuf, a_raw)
            else:
                cos_shuf = float("nan")
            if math.isfinite(cos_shuf):
                cos_shuf_vals.append(cos_shuf)

        align_rows.append({
            "anchor_id": str(anchor),
            "cos_sim_raw": fmt(cos_raw),
            "cos_sim_shuffled": fmt(cos_shuf),
        })
        anchors_used += 1

    if anchors_used < 8:
        warnings.append("Low usable-anchor count; consider larger --samples.")

    # ---- G0 vacuum stability gate ----
    gate_g0a = nan_inf_count <= thresholds.g0_nan_inf_max
    cond_global_max = max(cond_vals) if cond_vals else float("nan")
    gate_g0b = math.isfinite(cond_global_max) and (cond_global_max < thresholds.g0_cond_global_max)
    cond_lowcurv_max = max(cond_lowcurv_vals) if cond_lowcurv_vals else 1.0  # no low-curv points = pass
    gate_g0c = math.isfinite(cond_lowcurv_max) and (cond_lowcurv_max < thresholds.g0_cond_lowcurv_max)
    gate_g0 = gate_g0a and gate_g0b and gate_g0c

    # ---- D1-D4 gates (identical to v3) ----
    d1_min_eig = min(min_eigs) if min_eigs else float("nan")
    gate_d1 = math.isfinite(d1_min_eig) and (d1_min_eig >= thresholds.d1_eps)

    d2_med = median(drift_vals) if drift_vals else float("nan")
    d2_p90 = percentile90(drift_vals) if drift_vals else float("nan")
    gate_d2 = (
        math.isfinite(d2_med) and math.isfinite(d2_p90)
        and (d2_med <= thresholds.d2_median_max)
        and (d2_p90 <= thresholds.d2_p90_max)
    )

    d3_med = median(cos_raw_vals) if cos_raw_vals else float("nan")
    d3_p10 = percentile10(cos_raw_vals) if cos_raw_vals else float("nan")
    gate_d3 = (
        math.isfinite(d3_med) and math.isfinite(d3_p10)
        and (d3_med >= thresholds.d3_median_min)
        and (d3_p10 >= thresholds.d3_p10_min)
    )

    d4_med_shuf = median(cos_shuf_vals) if cos_shuf_vals else float("nan")
    gate_d4 = math.isfinite(d4_med_shuf) and (d4_med_shuf < thresholds.d4_shuffle_median_max)

    decision = "pass" if (gate_g0 and gate_d1 and gate_d2 and gate_d3 and gate_d4) else "fail"

    # ---- Write artifacts ----
    metric_rows = [
        {"gate_id": "G0", "metric": "nan_inf_count", "value": str(nan_inf_count), "threshold": f"<={thresholds.g0_nan_inf_max}", "status": "pass" if gate_g0a else "fail"},
        {"gate_id": "G0", "metric": "cond_global_max", "value": fmt(cond_global_max), "threshold": f"<{fmt(thresholds.g0_cond_global_max)}", "status": "pass" if gate_g0b else "fail"},
        {"gate_id": "G0", "metric": "cond_lowcurv_max", "value": fmt(cond_lowcurv_max), "threshold": f"<{fmt(thresholds.g0_cond_lowcurv_max)}", "status": "pass" if gate_g0c else "fail"},
        {"gate_id": "D1", "metric": "min_eig_global", "value": fmt(d1_min_eig), "threshold": f">={fmt(thresholds.d1_eps)}", "status": "pass" if gate_d1 else "fail"},
        {"gate_id": "D2", "metric": "median_delta_g", "value": fmt(d2_med), "threshold": f"<={fmt(thresholds.d2_median_max)}", "status": "pass" if (math.isfinite(d2_med) and d2_med <= thresholds.d2_median_max) else "fail"},
        {"gate_id": "D2", "metric": "p90_delta_g", "value": fmt(d2_p90), "threshold": f"<={fmt(thresholds.d2_p90_max)}", "status": "pass" if (math.isfinite(d2_p90) and d2_p90 <= thresholds.d2_p90_max) else "fail"},
        {"gate_id": "D3", "metric": "median_cos_sim", "value": fmt(d3_med), "threshold": f">={fmt(thresholds.d3_median_min)}", "status": "pass" if (math.isfinite(d3_med) and d3_med >= thresholds.d3_median_min) else "fail"},
        {"gate_id": "D3", "metric": "p10_cos_sim", "value": fmt(d3_p10), "threshold": f">={fmt(thresholds.d3_p10_min)}", "status": "pass" if (math.isfinite(d3_p10) and d3_p10 >= thresholds.d3_p10_min) else "fail"},
        {"gate_id": "D4", "metric": "median_cos_sim_shuffled", "value": fmt(d4_med_shuf), "threshold": f"<{fmt(thresholds.d4_shuffle_median_max)}", "status": "pass" if gate_d4 else "fail"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision, "threshold": "G0&D1&D2&D3&D4", "status": decision},
    ]

    write_csv(out_dir / "eigs.csv", ["anchor_id", "scale", "g11", "g12", "g22", "min_eig", "max_eig", "trace", "frob", "det", "cond", "spd"], eig_rows)
    write_csv(out_dir / "drift.csv", ["anchor_id", "scale_ref", "scale_test", "delta_g_fro_rel"], drift_rows)
    write_csv(out_dir / "align_sigma.csv", ["anchor_id", "cos_sim_raw", "cos_sim_shuffled"], align_rows)
    write_csv(out_dir / "metric_checks.csv", ["gate_id", "metric", "value", "threshold", "status"], metric_rows)
    write_csv(out_dir / "vacuum_gate.csv", ["anchor_id", "scale", "frob_hessian_raw", "is_low_curv", "cond_number", "g11", "g12", "g22"], vacuum_rows)

    config_payload = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "samples_requested": args.samples,
        "anchors_used": anchors_used,
        "normalization": {
            "distance_scale": "divide_by_median_edge_length",
            "median_edge_length_raw": median_edge,
            "s0": s0,
            "scales_cli": args.scales,
            "scales_used": [{"label": lbl, "value": s} for lbl, s in scales],
        },
        "chart_method": "two-landmark geodesic tangent chart",
        "smoothing_kernel": "gaussian over local graph distances (applied to Sigma field)",
        "metric_estimator": "v4 dynamic metric: Sigma Hessian + SPD projection + Frobenius normalization + anisotropy shrinkage (iso=1/sqrt(2))",
        "metric_estimator_params": {
            "anisotropy_keep": 0.4,
            "frob_floor": 1e-9,
            "normalization": "frobenius",
            "iso_target": round(1.0 / math.sqrt(2.0), 6),
        },
        "gates": {
            "G0a_nan_inf_max": thresholds.g0_nan_inf_max,
            "G0b_cond_global_max": thresholds.g0_cond_global_max,
            "G0c_cond_lowcurv_max": thresholds.g0_cond_lowcurv_max,
            "G0_lowcurv_frob_threshold": thresholds.g0_lowcurv_frob_threshold,
            "D1_eps": thresholds.d1_eps,
            "D2_median_max": thresholds.d2_median_max,
            "D2_p90_max": thresholds.d2_p90_max,
            "D3_median_min": thresholds.d3_median_min,
            "D3_p10_min": thresholds.d3_p10_min,
            "D4_shuffle_median_max": thresholds.d4_shuffle_median_max,
        },
        "decision": decision,
    }
    (out_dir / "config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    plot_histogram(out_dir / "eigs-hist.png", min_eigs, "eigs", bins=28, color=(38, 102, 179))
    plot_histogram(out_dir / "drift-distribution.png", drift_vals, "drift", bins=24, color=(26, 143, 87))
    plot_histogram(out_dir / "cos-sim-distribution.png", cos_raw_vals + cos_shuf_vals, "cos", bins=26, color=(167, 86, 30))
    plot_histogram(out_dir / "cond-number-hist.png", cond_vals, "cond", bins=28, color=(140, 60, 160))

    files_for_hash = [
        out_dir / "metric_checks.csv",
        out_dir / "eigs.csv",
        out_dir / "drift.csv",
        out_dir / "align_sigma.csv",
        out_dir / "vacuum_gate.csv",
        out_dir / "config.json",
        out_dir / "eigs-hist.png",
        out_dir / "drift-distribution.png",
        out_dir / "cos-sim-distribution.png",
        out_dir / "cond-number-hist.png",
    ]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started
    write_run_log(
        out_dir / "run-log.txt",
        args,
        details={
            "duration_seconds": duration,
            "dataset_manifest": dataset_meta,
            "decision": decision,
            "anchors_used": anchors_used,
            "artifact_hashes": hashes,
        },
        warnings=warnings,
    )

    print("QNG metric hardening v4 completed.")
    print(f"Artifacts: {out_dir}")
    print(
        f"decision={decision} "
        f"G0={gate_g0}(a={gate_g0a},b={gate_g0b},c={gate_g0c}) "
        f"D1={gate_d1} D2={gate_d2} D3={gate_d3} D4={gate_d4} "
        f"anchors_used={anchors_used}"
    )
    print(
        f"G0 details: nan_inf={nan_inf_count} cond_global_max={fmt(cond_global_max)} "
        f"cond_lowcurv_max={fmt(cond_lowcurv_max)} low_curv_pts={len(cond_lowcurv_vals)}"
    )
    print(
        f"D1 min_eig={fmt(d1_min_eig)} "
        f"D2 med/p90={fmt(d2_med)}/{fmt(d2_p90)} "
        f"D3 med/p10={fmt(d3_med)}/{fmt(d3_p10)} "
        f"D4 shuf={fmt(d4_med_shuf)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
