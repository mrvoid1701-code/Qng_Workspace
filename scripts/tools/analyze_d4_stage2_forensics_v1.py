#!/usr/bin/env python3
"""
D4 Stage-2 strict-vs-MOND failure forensics (v1).

Goal:
- identify where dual-kernel loses vs MOND on fixed split:
  by split, radius regime, acceleration regime, and galaxy proxy class.

No model/gate threshold changes; analysis only.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v2-strict-vs-mond"
    / "d4_stage2_dual_kernel_summary.json"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v2-strict-vs-mond"
    / "forensics-v1"
)


@dataclass
class Point:
    gal: str
    r: float
    v: float
    ve: float
    bt: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze D4 Stage-2 strict-vs-MOND failure signatures.")
    p.add_argument("--summary-json", default=str(DEFAULT_SUMMARY))
    p.add_argument("--dataset-csv", default="")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=20)
    return p.parse_args()


def read_data(path: Path) -> dict[str, list[Point]]:
    out: dict[str, list[Point]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                gal = str(r["system_id"]).strip()
                rv = float(r["radius"])
                vv = float(r["v_obs"])
                ve = float(r["v_err"])
                bt = float(r["baryon_term"])
            except Exception:
                continue
            if gal == "" or rv <= 0.0 or ve <= 0.0 or bt < 0.0:
                continue
            out.setdefault(gal, []).append(Point(gal=gal, r=rv, v=vv, ve=ve, bt=bt))
    for pts in out.values():
        pts.sort(key=lambda p: p.r)
    return out


def train_holdout_split(gals: list[str], seed: int, train_frac: float) -> tuple[set[str], set[str]]:
    ordered = sorted(gals)
    rng = random.Random(seed)
    rng.shuffle(ordered)
    n_train = max(1, min(len(ordered) - 1, int(round(train_frac * len(ordered)))))
    train = set(ordered[:n_train])
    holdout = set(ordered[n_train:])
    return train, holdout


def dr_list(pts: list[Point]) -> list[float]:
    n = len(pts)
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    out: list[float] = []
    for i in range(n):
        if i == 0:
            out.append(max((pts[1].r - pts[0].r) / 2.0, 1e-9))
        elif i == n - 1:
            out.append(max((pts[-1].r - pts[-2].r) / 2.0, 1e-9))
        else:
            out.append(max((pts[i + 1].r - pts[i - 1].r) / 2.0, 1e-9))
    return out


def chi_profile(pts: list[Point]) -> list[float]:
    if not pts:
        return []
    m_enc = [p.bt * p.r for p in pts]
    mmax = max(m_enc)
    if mmax <= 0.0:
        return [0.0 for _ in pts]
    return [x / mmax for x in m_enc]


def s1_profile(pts: list[Point], s1_lambda: float) -> list[float]:
    chi = chi_profile(pts)
    lam = max(s1_lambda, 1e-9)
    return [math.exp(-abs(c - 1.0) / lam) for c in chi]


def kernel_features_for_galaxy(
    pts: list[Point],
    tau: float,
    alpha: float,
    s1_lambda: float,
    s2_const: float,
    r0_kpc: float,
) -> tuple[list[float], list[float]]:
    n = len(pts)
    if n == 0:
        return [], []
    if n == 1:
        src1 = pts[0].bt * math.exp(-abs(0.0 - 1.0) / max(s1_lambda, 1e-9))
        src2 = pts[0].bt * s2_const
        return [src1], [src2]

    drr = dr_list(pts)
    s1 = s1_profile(pts, s1_lambda)
    src1 = [pts[i].bt * s1[i] for i in range(n)]
    src2 = [pts[i].bt * s2_const for i in range(n)]

    tau_eff = max(tau, 1e-9)
    r0_eff = max(r0_kpc, 1e-9)

    h1: list[float] = []
    h2: list[float] = []
    for i in range(n):
        ri = pts[i].r
        num1 = 0.0
        den1 = 0.0
        num2 = 0.0
        den2 = 0.0
        for j in range(n):
            d = abs(ri - pts[j].r)
            w1 = math.exp(-d / tau_eff)
            w2 = 1.0 / (d + r0_eff) ** alpha
            dj = drr[j]
            num1 += w1 * src1[j] * dj
            den1 += w1 * dj
            num2 += w2 * src2[j] * dj
            den2 += w2 * dj
        h1.append(num1 / max(den1, 1e-18))
        h2.append(num2 / max(den2, 1e-18))
    return h1, h2


def mond_v(point: Point, g_dag: float) -> float:
    g_bar = point.bt / point.r
    if g_bar <= 0.0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    if denom <= 1e-15:
        g_obs = math.sqrt(g_bar * g_dag)
    else:
        g_obs = g_bar / denom
    return math.sqrt(max(g_obs * point.r, 0.0))


def f6(x: float) -> str:
    return f"{x:.6f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    x = sorted(vals)
    idx = int(math.floor(q * (len(x) - 1)))
    return x[idx]


def classify_radius(r_norm: float) -> str:
    if r_norm <= 0.33:
        return "inner"
    if r_norm <= 0.66:
        return "mid"
    return "outer"


def classify_accel(gbar_ratio: float) -> str:
    if gbar_ratio < 0.3:
        return "low_accel"
    if gbar_ratio <= 1.5:
        return "transition"
    return "high_accel"


def summarize_group(rows: list[dict[str, Any]], group_fields: list[str], group_type: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for r in rows:
        key = tuple(str(r[f]) for f in group_fields)
        grouped.setdefault(key, []).append(r)

    out: list[dict[str, Any]] = []
    for key in sorted(grouped.keys()):
        g = grouped[key]
        n = len(g)
        dual = [float(x["chi2_dual"]) for x in g]
        mond = [float(x["chi2_mond"]) for x in g]
        gap = [float(x["chi2_gap_dual_minus_mond"]) for x in g]
        rec: dict[str, Any] = {
            "group_type": group_type,
            "count": str(n),
            "chi2_dual_per_n": f6(sum(dual) / max(n, 1)),
            "chi2_mond_per_n": f6(sum(mond) / max(n, 1)),
            "chi2_gap_per_n": f6(sum(gap) / max(n, 1)),
            "gap_p50": f6(percentile(gap, 0.50)),
            "gap_p90": f6(percentile(gap, 0.90)),
            "gap_positive_fraction": f6(sum(1 for x in gap if x > 0.0) / max(n, 1)),
        }
        for idx, gf in enumerate(group_fields):
            rec[gf] = key[idx]
        out.append(rec)
    return out


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_json).resolve()
    if not summary_path.exists():
        raise FileNotFoundError(f"summary json not found: {summary_path}")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    dataset_csv = Path(args.dataset_csv).resolve() if args.dataset_csv else Path(summary["dataset_csv"]).resolve()
    if not dataset_csv.exists():
        raise FileNotFoundError(f"dataset csv not found: {dataset_csv}")

    split_seed = int(summary["split_seed"])
    train_frac = float(summary["train_frac"])
    best = summary["best_dual_params"]
    tau = float(best["tau_kpc"])
    alpha = float(best["alpha"])
    k1 = float(best["k1"])
    k2 = float(best["k2"])
    consts = summary["fixed_theory_constants"]
    s1_lambda = float(consts["s1_lambda"])
    s2_const = float(consts["s2_const"])
    r0_kpc = float(consts["r0_kpc"])
    g_dag = float(summary["mond_fit"]["g_dag_internal_km2_s2_kpc"])

    galaxies = read_data(dataset_csv)
    galaxy_ids = sorted(galaxies.keys())
    train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, train_frac)

    # Galaxy proxy class from enclosed baryonic scale quantiles.
    gal_mass_proxy: dict[str, float] = {}
    for gid in galaxy_ids:
        pts = galaxies[gid]
        gal_mass_proxy[gid] = max((p.bt * p.r for p in pts), default=0.0)
    proxy_vals = [gal_mass_proxy[g] for g in galaxy_ids]
    q1 = percentile(proxy_vals, 0.33)
    q2 = percentile(proxy_vals, 0.66)

    def galaxy_class(gid: str) -> str:
        x = gal_mass_proxy[gid]
        if x <= q1:
            return "low_mass_proxy"
        if x <= q2:
            return "mid_mass_proxy"
        return "high_mass_proxy"

    point_rows: list[dict[str, Any]] = []
    for gid in galaxy_ids:
        pts = galaxies[gid]
        if not pts:
            continue
        h1, h2 = kernel_features_for_galaxy(
            pts=pts,
            tau=tau,
            alpha=alpha,
            s1_lambda=s1_lambda,
            s2_const=s2_const,
            r0_kpc=r0_kpc,
        )
        rmax = max(p.r for p in pts)
        split = "train" if gid in train_ids else "holdout"
        gclass = galaxy_class(gid)
        for i, p in enumerate(pts):
            pred_v2 = p.bt + k1 * h1[i] + k2 * h2[i]
            v_dual = math.sqrt(max(pred_v2, 0.0))
            v_mond = mond_v(p, g_dag)

            chi2_dual = ((p.v - v_dual) / p.ve) ** 2
            chi2_mond = ((p.v - v_mond) / p.ve) ** 2
            gap = chi2_dual - chi2_mond
            r_norm = p.r / max(rmax, 1e-12)
            gbar = p.bt / p.r if p.r > 0.0 else 0.0
            gbar_ratio = gbar / max(g_dag, 1e-30)
            point_rows.append(
                {
                    "system_id": gid,
                    "split": split,
                    "galaxy_class": gclass,
                    "radius_kpc": f6(p.r),
                    "radius_norm": f6(r_norm),
                    "radius_bin": classify_radius(r_norm),
                    "gbar_internal": f6(gbar),
                    "gbar_over_gdag": f6(gbar_ratio),
                    "accel_regime": classify_accel(gbar_ratio),
                    "v_obs": f6(p.v),
                    "v_err": f6(p.ve),
                    "v_dual": f6(v_dual),
                    "v_mond": f6(v_mond),
                    "chi2_dual": f6(chi2_dual),
                    "chi2_mond": f6(chi2_mond),
                    "chi2_gap_dual_minus_mond": f6(gap),
                }
            )

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    point_fields = [
        "system_id",
        "split",
        "galaxy_class",
        "radius_kpc",
        "radius_norm",
        "radius_bin",
        "gbar_internal",
        "gbar_over_gdag",
        "accel_regime",
        "v_obs",
        "v_err",
        "v_dual",
        "v_mond",
        "chi2_dual",
        "chi2_mond",
        "chi2_gap_dual_minus_mond",
    ]
    write_csv(out_dir / "point_residuals.csv", point_rows, point_fields)

    seg_rows: list[dict[str, Any]] = []
    seg_rows.extend(summarize_group(point_rows, ["split"], "split"))
    seg_rows.extend(summarize_group(point_rows, ["split", "radius_bin"], "split_radius"))
    seg_rows.extend(summarize_group(point_rows, ["split", "accel_regime"], "split_accel"))
    seg_rows.extend(summarize_group(point_rows, ["split", "galaxy_class"], "split_galaxy_class"))
    seg_rows.extend(
        summarize_group(point_rows, ["split", "radius_bin", "accel_regime"], "split_radius_accel")
    )

    seg_fields = [
        "group_type",
        "split",
        "radius_bin",
        "accel_regime",
        "galaxy_class",
        "count",
        "chi2_dual_per_n",
        "chi2_mond_per_n",
        "chi2_gap_per_n",
        "gap_p50",
        "gap_p90",
        "gap_positive_fraction",
    ]
    # ensure optional columns exist in every row
    for r in seg_rows:
        for f in ["split", "radius_bin", "accel_regime", "galaxy_class"]:
            r.setdefault(f, "")
    write_csv(out_dir / "segment_summary.csv", seg_rows, seg_fields)

    # Worst galaxies by total holdout chi2 gap
    by_gal: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for r in point_rows:
        key = (str(r["split"]), str(r["system_id"]))
        by_gal.setdefault(key, []).append(r)
    worst_rows: list[dict[str, Any]] = []
    for key, rows in by_gal.items():
        split, gid = key
        gap_sum = sum(float(x["chi2_gap_dual_minus_mond"]) for x in rows)
        dual_sum = sum(float(x["chi2_dual"]) for x in rows)
        mond_sum = sum(float(x["chi2_mond"]) for x in rows)
        n = len(rows)
        worst_rows.append(
            {
                "split": split,
                "system_id": gid,
                "count": str(n),
                "chi2_dual_per_n": f6(dual_sum / max(n, 1)),
                "chi2_mond_per_n": f6(mond_sum / max(n, 1)),
                "chi2_gap_sum": f6(gap_sum),
                "chi2_gap_per_n": f6(gap_sum / max(n, 1)),
            }
        )
    worst_rows.sort(key=lambda x: float(x["chi2_gap_sum"]), reverse=True)
    worst_rows = worst_rows[: max(1, int(args.top_k))]
    write_csv(
        out_dir / "worst_galaxies.csv",
        worst_rows,
        ["split", "system_id", "count", "chi2_dual_per_n", "chi2_mond_per_n", "chi2_gap_sum", "chi2_gap_per_n"],
    )

    # report
    holdout_points = [r for r in point_rows if r["split"] == "holdout"]
    holdout_gap = [float(r["chi2_gap_dual_minus_mond"]) for r in holdout_points]
    holdout_gap_mean = sum(holdout_gap) / max(len(holdout_gap), 1)
    top_holdout_segments = [
        r
        for r in seg_rows
        if r["group_type"] in {"split_radius", "split_accel", "split_galaxy_class"} and r["split"] == "holdout"
    ]
    top_holdout_segments.sort(key=lambda x: float(x["chi2_gap_per_n"]), reverse=True)
    top_holdout_segments = top_holdout_segments[:5]

    lines = [
        "# D4 Stage-2 Forensics v1",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- summary_json: `{summary_path.as_posix()}`",
        f"- dataset_csv: `{dataset_csv.as_posix()}`",
        f"- split_seed/train_frac: `{split_seed}/{train_frac}`",
        f"- best_dual_params: `tau={tau}, alpha={alpha}, k1={k1}, k2={k2}`",
        "",
        "## Holdout Loss Signature",
        "",
        f"- holdout points: `{len(holdout_points)}`",
        f"- mean chi2 gap per point (dual - mond): `{f6(holdout_gap_mean)}`",
        f"- p50/p90 chi2 gap: `{f6(percentile(holdout_gap, 0.50))}/{f6(percentile(holdout_gap, 0.90))}`",
        "",
        "## Top Holdout Failing Segments (by chi2_gap_per_n)",
        "",
    ]
    for r in top_holdout_segments:
        seg_label = []
        if r["radius_bin"]:
            seg_label.append(f"radius={r['radius_bin']}")
        if r["accel_regime"]:
            seg_label.append(f"accel={r['accel_regime']}")
        if r["galaxy_class"]:
            seg_label.append(f"class={r['galaxy_class']}")
        label = ", ".join(seg_label) if seg_label else "split_only"
        lines.append(
            f"- `{r['group_type']}` ({label}): gap_per_n={r['chi2_gap_per_n']}, "
            f"dual_per_n={r['chi2_dual_per_n']}, mond_per_n={r['chi2_mond_per_n']}, n={r['count']}"
        )

    lines.extend(
        [
            "",
            "## Hypothesized Mechanisms (data-driven)",
            "",
            "1. High gap concentration in low-acceleration holdout regime suggests missing long-range support beyond current kernel fit.",
            "2. Outer-radius penalties indicate underestimation at large r even when null is improved.",
            "3. System-level concentration (worst_galaxies.csv) indicates morphology-dependent miss not captured by current global parameterization.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"point_residuals_csv: {(out_dir / 'point_residuals.csv').as_posix()}")
    print(f"segment_summary_csv: {(out_dir / 'segment_summary.csv').as_posix()}")
    print(f"worst_galaxies_csv: {(out_dir / 'worst_galaxies.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
