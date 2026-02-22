#!/usr/bin/env python3
"""
Rotation baseline-upgrade check for QNG-T-039 publish defensibility.

Goal:
- Keep identical sample rows, sigmas, and weighted-chi2 likelihood.
- Compare a flexible non-memory baseline (1 parameter) against
  the memory model (1 parameter) on the same rotation data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import math
import statistics


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROT_CSV = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-baseline-upgrade"


@dataclass
class RotationPoint:
    system_id: str
    radius: float
    v_obs: float
    v_err: float
    baryon_term: float
    history_term: float
    halo_proxy: float


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


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if av >= 1e4 or (0.0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def compute_aic(chi2: float, k_params: int) -> float:
    return chi2 + 2.0 * k_params


def compute_bic(chi2: float, k_params: int, n_samples: int) -> float:
    n = max(n_samples, 1)
    return chi2 + k_params * math.log(n)


def parse_rotation_csv(path: Path) -> list[RotationPoint]:
    rows_raw: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"system_id", "radius", "v_obs", "v_err", "baryon_term", "history_term"}
        if not required.issubset(set(reader.fieldnames or [])):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"Missing rotation columns: {', '.join(missing)}")
        for row in reader:
            rows_raw.append(row)

    by_system: dict[str, list[float]] = {}
    for row in rows_raw:
        sid = str(row.get("system_id", "")).strip() or "unknown"
        r = safe_float(row.get("radius"))
        if r is None:
            continue
        by_system.setdefault(sid, []).append(max(r, 1e-12))
    r_scale = {sid: max(statistics.median(vals), 1e-6) for sid, vals in by_system.items() if vals}

    points: list[RotationPoint] = []
    for row in rows_raw:
        sid = str(row.get("system_id", "")).strip() or "unknown"
        radius = safe_float(row.get("radius"))
        v_obs = safe_float(row.get("v_obs"))
        v_err = safe_float(row.get("v_err"), default=4.0)
        bary = safe_float(row.get("baryon_term"))
        hist = safe_float(row.get("history_term"))
        if None in {radius, v_obs, v_err, bary, hist}:
            continue
        radius = max(float(radius), 1e-9)
        v_err = max(float(v_err), 1e-9)
        bary = max(float(bary), 0.0)
        hist = max(float(hist), 0.0)
        rs = r_scale.get(sid, max(radius, 1e-6))
        halo_proxy = radius / (radius + rs)
        points.append(
            RotationPoint(
                system_id=sid,
                radius=radius,
                v_obs=float(v_obs),
                v_err=v_err,
                baryon_term=bary,
                history_term=hist,
                halo_proxy=halo_proxy,
            )
        )
    if len(points) < 32:
        raise ValueError(f"Too few usable rotation rows: {len(points)}")
    return points


def chi2_for_feature(points: list[RotationPoint], coeff: float, feature_name: str) -> float:
    total = 0.0
    for p in points:
        feature = p.history_term if feature_name == "history_term" else p.halo_proxy
        v2_model = max(p.baryon_term + coeff * feature, 1e-12)
        v_model = math.sqrt(v2_model)
        z = (p.v_obs - v_model) / p.v_err
        total += z * z
    return total


def chi2_baseline_null(points: list[RotationPoint]) -> float:
    total = 0.0
    for p in points:
        v_model = math.sqrt(max(p.baryon_term, 1e-12))
        z = (p.v_obs - v_model) / p.v_err
        total += z * z
    return total


def fit_coeff(points: list[RotationPoint], feature_name: str) -> tuple[float, float]:
    if feature_name == "history_term":
        vals = [p.history_term for p in points]
    else:
        vals = [p.halo_proxy for p in points]
    vmax = max(p.v_obs * p.v_obs for p in points)
    diff_max = max(max(p.v_obs * p.v_obs - p.baryon_term, 0.0) for p in points)
    x_max = max(max(vals), 1e-12)
    upper = max(1.0, 5.0 * diff_max / x_max, 0.25 * vmax / x_max)
    upper = min(upper, 1e8)

    best_p = 0.0
    best_c = chi2_for_feature(points, 0.0, feature_name)
    n_grid = 800
    for i in range(1, n_grid + 1):
        p = upper * i / n_grid
        c = chi2_for_feature(points, p, feature_name)
        if c < best_c:
            best_p, best_c = p, c

    window = upper / max(n_grid // 4, 1)
    lo = max(0.0, best_p - window)
    hi = min(upper, best_p + window)
    for _ in range(80):
        if hi - lo < 1e-12:
            break
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        c1 = chi2_for_feature(points, m1, feature_name)
        c2 = chi2_for_feature(points, m2, feature_name)
        if c1 <= c2:
            hi = m2
        else:
            lo = m1
    p_ref = 0.5 * (lo + hi)
    c_ref = chi2_for_feature(points, p_ref, feature_name)
    if c_ref < best_c:
        return p_ref, c_ref
    return best_p, best_c


def write_csv(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in payload.items():
            w.writerow([k, v])


def write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-039 rotation baseline-upgrade check.")
    p.add_argument("--rotation-csv", default=str(DEFAULT_ROT_CSV))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--seed", type=int, default=20260221, help="Logged for reproducibility.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    rot_csv = Path(args.rotation_csv)
    if not rot_csv.is_absolute():
        rot_csv = (ROOT / rot_csv).resolve()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    points = parse_rotation_csv(rot_csv)
    n = len(points)

    chi2_null = chi2_baseline_null(points)
    a_flex, chi2_flex = fit_coeff(points, "halo_proxy")
    k_mem, chi2_mem = fit_coeff(points, "history_term")

    aic_null = compute_aic(chi2_null, 0)
    bic_null = compute_bic(chi2_null, 0, n)
    aic_flex = compute_aic(chi2_flex, 1)
    bic_flex = compute_bic(chi2_flex, 1, n)
    aic_mem = compute_aic(chi2_mem, 1)
    bic_mem = compute_bic(chi2_mem, 1, n)

    dchi2_mem_vs_flex = chi2_mem - chi2_flex
    daic_mem_vs_flex = aic_mem - aic_flex
    dbic_mem_vs_flex = bic_mem - bic_flex
    dchi2_per_point = dchi2_mem_vs_flex / max(n, 1)
    rule_pass = dchi2_mem_vs_flex < 0.0

    summary = {
        "rotation_csv": str(rot_csv),
        "n_rotation": str(n),
        "chi2_null_baseline": fmt(chi2_null),
        "chi2_flex_baseline": fmt(chi2_flex),
        "chi2_memory": fmt(chi2_mem),
        "aic_null_baseline": fmt(aic_null),
        "aic_flex_baseline": fmt(aic_flex),
        "aic_memory": fmt(aic_mem),
        "bic_null_baseline": fmt(bic_null),
        "bic_flex_baseline": fmt(bic_flex),
        "bic_memory": fmt(bic_mem),
        "a_flex_baseline": fmt(a_flex),
        "k_memory": fmt(k_mem),
        "delta_chi2_memory_vs_flex": fmt(dchi2_mem_vs_flex),
        "delta_aic_memory_vs_flex": fmt(daic_mem_vs_flex),
        "delta_bic_memory_vs_flex": fmt(dbic_mem_vs_flex),
        "delta_chi2_per_point_memory_vs_flex": fmt(dchi2_per_point),
        "rule_pass_memory_beats_flex": str(rule_pass),
    }
    write_csv(out_dir / "fit-summary.csv", summary)

    model_lines = [
        "# Rotation Baseline Upgrade Check",
        "",
        "| Check | Flexible baseline | Memory model | Status |",
        "| --- | --- | --- | --- |",
        f"| Sample rows | n={n} | n={n} | pass |",
        "| Sigma weights | same `v_err` rows | same `v_err` rows | pass |",
        "| Likelihood form | weighted chi-square | weighted chi-square | pass |",
        "| Free parameters | 1 (`a_flex`) | 1 (`k_memory`) | pass |",
        "| Priors | `a_flex >= 0` | `k_memory >= 0` | pass |",
        "",
        "| Metric | Flexible baseline | Memory | Delta (memory - flex) |",
        "| --- | --- | --- | --- |",
        f"| chi2_rotation | {fmt(chi2_flex)} | {fmt(chi2_mem)} | {fmt(dchi2_mem_vs_flex)} |",
        f"| AIC_rotation | {fmt(aic_flex)} | {fmt(aic_mem)} | {fmt(daic_mem_vs_flex)} |",
        f"| BIC_rotation | {fmt(bic_flex)} | {fmt(bic_mem)} | {fmt(dbic_mem_vs_flex)} |",
        f"| delta_chi2_per_point | - | - | {fmt(dchi2_per_point)} |",
        "",
        "Interpretation:",
        f"- Flexible baseline fit parameter: `a_flex={fmt(a_flex)}`.",
        f"- Memory fit parameter: `k_memory={fmt(k_mem)}`.",
        f"- Memory beats flexible baseline: `{str(rule_pass).lower()}`.",
        "",
    ]
    write_md(out_dir / "model-comparison.md", model_lines)

    run_log = [
        "QNG-T-039 rotation baseline-upgrade run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"rotation_csv: {rot_csv}",
        f"seed: {args.seed}",
        f"n_rotation: {n}",
        f"a_flex_baseline: {fmt(a_flex)}",
        f"k_memory: {fmt(k_mem)}",
        f"delta_chi2_memory_vs_flex: {fmt(dchi2_mem_vs_flex)}",
        f"delta_aic_memory_vs_flex: {fmt(daic_mem_vs_flex)}",
        f"delta_bic_memory_vs_flex: {fmt(dbic_mem_vs_flex)}",
        f"pass_memory_beats_flex: {str(rule_pass).lower()}",
        "",
    ]
    write_md(out_dir / "run-log.txt", run_log)

    print(
        " ".join(
            [
                "QNG-T-039 baseline-upgrade check complete:",
                f"n={n}",
                f"dchi2_mem_vs_flex={fmt(dchi2_mem_vs_flex)}",
                f"daic_mem_vs_flex={fmt(daic_mem_vs_flex)}",
                f"dbic_mem_vs_flex={fmt(dbic_mem_vs_flex)}",
                f"pass={str(rule_pass).lower()}",
            ]
        )
    )
    print(f"Artifacts written to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
