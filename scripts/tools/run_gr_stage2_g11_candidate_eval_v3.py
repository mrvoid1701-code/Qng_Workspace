#!/usr/bin/env python3
"""
Evaluate G11a-v3 candidate-only decision layer over Stage-2 summary packages.

Policy:
- no edits to official gate scripts
- candidate is computed in post-processing from existing run artifacts
- v2 remains official baseline for this evaluation

G11a-v3 candidate core:
- Source proxy: S(i) = |L_rw sigma_norm(i)|  (Poisson-like source term)
- Curvature target: T(i) = |R_smooth(i)|, with one random-walk smoothing step
- High-signal subset: top 20% S
- Candidate fallback pass if:
  - G11b/G11c/G11d are pass
  - |Spearman(S,T)| >= 0.20
  - |Pearson(S,T)| >= 0.20

Multi-peak / G11b-fail branch:
- emitted as diagnostic-only fields (no decision override in v3)
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v2"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-g11-candidate-v3"
)

HIGH_SIGNAL_QUANTILE = 0.80
CORR_MIN = 0.20
R_SMOOTH_ALPHA = 0.50
R_SMOOTH_ITERS = 1
MULTI_PEAK_RATIO_THRESHOLD = 0.98
MULTI_PEAK_DISTANCE_THRESHOLD = 0.10


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-2 G11a-v3 candidate-only layer.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--high-signal-quantile", type=float, default=HIGH_SIGNAL_QUANTILE)
    p.add_argument("--corr-min", type=float, default=CORR_MIN)
    p.add_argument("--r-smooth-alpha", type=float, default=R_SMOOTH_ALPHA)
    p.add_argument("--r-smooth-iters", type=int, default=R_SMOOTH_ITERS)
    p.add_argument("--multi-peak-ratio-threshold", type=float, default=MULTI_PEAK_RATIO_THRESHOLD)
    p.add_argument("--multi-peak-distance-threshold", type=float, default=MULTI_PEAK_DISTANCE_THRESHOLD)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def f6(v: float | None) -> str:
    if v is None or math.isnan(v):
        return ""
    return f"{v:.6f}"


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def get_first(row: dict[str, str], keys: list[str], default: str = "") -> str:
    for k in keys:
        if k in row and str(row[k]).strip() != "":
            return str(row[k])
    return default


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = max(0.0, min(1.0, q)) * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def rank_values(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        r = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = r
        i = j + 1
    return ranks


def pearson_corr(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = statistics.mean(x)
    my = statistics.mean(y)
    sx = sum((v - mx) ** 2 for v in x)
    sy = sum((v - my) ** 2 for v in y)
    if sx <= 1e-30 or sy <= 1e-30:
        return float("nan")
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(len(x)))
    return cov / math.sqrt(sx * sy)


def spearman_corr(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    return pearson_corr(rank_values(x), rank_values(y))


def smooth_values(values: list[float], neighbours: list[list[int]], alpha: float, iters: int) -> list[float]:
    out = list(values)
    alpha = max(0.0, min(1.0, alpha))
    for _ in range(max(0, iters)):
        nxt = list(out)
        for i, nb in enumerate(neighbours):
            if not nb:
                continue
            m = sum(out[j] for j in nb) / len(nb)
            nxt[i] = (1.0 - alpha) * out[i] + alpha * m
        out = nxt
    return out


def laplacian_rw(values: list[float], neighbours: list[list[int]]) -> list[float]:
    out: list[float] = []
    for i, nb in enumerate(neighbours):
        if not nb:
            out.append(0.0)
            continue
        m = sum(values[j] for j in nb) / len(nb)
        out.append(m - values[i])
    return out


def multi_peak_info(
    coords: list[tuple[float, float]],
    sigma: list[float],
    ratio_thr: float,
    dist_thr: float,
) -> dict[str, Any]:
    if len(sigma) < 2:
        return {
            "multi_peak_flag": False,
            "peak1_idx": 0,
            "peak2_idx": 0,
            "peak2_to_peak1": 0.0,
            "peak12_distance_norm": 0.0,
        }
    top = sorted(range(len(sigma)), key=lambda i: sigma[i], reverse=True)[:2]
    i1, i2 = top[0], top[1]
    ratio = sigma[i2] / max(sigma[i1], 1e-12)
    x_min = min(c[0] for c in coords)
    x_max = max(c[0] for c in coords)
    y_min = min(c[1] for c in coords)
    y_max = max(c[1] for c in coords)
    diag = math.hypot(x_max - x_min, y_max - y_min)
    dist = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
    dist_norm = dist / max(diag, 1e-12)
    return {
        "multi_peak_flag": bool((ratio >= ratio_thr) and (dist_norm <= dist_thr)),
        "peak1_idx": i1,
        "peak2_idx": i2,
        "peak2_to_peak1": ratio,
        "peak12_distance_norm": dist_norm,
    }


def two_peak_u_eff(
    coords: list[tuple[float, float]],
    sigma: list[float],
    peak1_idx: int,
    peak2_idx: int,
    use_two_peak: bool,
) -> list[float]:
    eps = 0.05
    a1 = max(sigma[peak1_idx], 1e-9)
    a2 = max(sigma[peak2_idx], 1e-9)
    out: list[float] = []
    p1 = coords[peak1_idx]
    p2 = coords[peak2_idx]
    for x, y in coords:
        u1 = a1 / (math.hypot(x - p1[0], y - p1[1]) + eps)
        if use_two_peak:
            u2 = a2 / (math.hypot(x - p2[0], y - p2[1]) + eps)
            u = max(u1, u2)
        else:
            u = u1
        out.append(u)
    m = max(out) if out else 1.0
    return [v / max(m, 1e-12) for v in out]


def g11_v3_poisson_rule(
    r_vals: list[float],
    sigma_norm: list[float],
    neighbours: list[list[int]],
    high_signal_quantile: float,
    corr_min: float,
    smooth_alpha: float,
    smooth_iters: int,
) -> dict[str, Any]:
    n = min(len(r_vals), len(sigma_norm), len(neighbours))
    if n < 3:
        return {
            "n_points": n,
            "high_signal_count": 0,
            "s_threshold": float("nan"),
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "rule_pass": False,
        }
    r = r_vals[:n]
    s = sigma_norm[:n]
    nb = neighbours[:n]

    r_smooth = smooth_values(r, nb, alpha=smooth_alpha, iters=smooth_iters)
    t_vals = [abs(v) for v in r_smooth]
    s_poisson = [abs(v) for v in laplacian_rw(s, nb)]
    s_thr = percentile(s_poisson, high_signal_quantile)
    idx = [i for i, v in enumerate(s_poisson) if v >= s_thr]
    if len(idx) < 3:
        return {
            "n_points": n,
            "high_signal_count": len(idx),
            "s_threshold": s_thr,
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "rule_pass": False,
        }
    sx = [s_poisson[i] for i in idx]
    tx = [t_vals[i] for i in idx]
    sp = spearman_corr(sx, tx)
    pe = pearson_corr(sx, tx)
    rule_pass = (
        (not math.isnan(sp))
        and (not math.isnan(pe))
        and (abs(sp) >= corr_min)
        and (abs(pe) >= corr_min)
    )
    return {
        "n_points": n,
        "high_signal_count": len(idx),
        "s_threshold": s_thr,
        "spearman_hs": sp,
        "pearson_hs": pe,
        "rule_pass": rule_pass,
    }


def g11b_fail_branch_diag(
    r_vals: list[float],
    coords: list[tuple[float, float]],
    sigma: list[float],
    neighbours: list[list[int]],
    peak_info: dict[str, Any],
    high_signal_quantile: float,
    corr_min: float,
    smooth_alpha: float,
    smooth_iters: int,
) -> dict[str, Any]:
    n = min(len(r_vals), len(coords), len(sigma), len(neighbours))
    if n < 3:
        return {
            "high_signal_count": 0,
            "u_threshold": float("nan"),
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "diag_rule_pass": False,
        }

    r = r_vals[:n]
    c = coords[:n]
    s = sigma[:n]
    nb = neighbours[:n]
    r_smooth = smooth_values(r, nb, alpha=smooth_alpha, iters=smooth_iters)
    t_vals = [abs(v) for v in r_smooth]
    u_vals = two_peak_u_eff(
        coords=c,
        sigma=s,
        peak1_idx=int(peak_info["peak1_idx"]),
        peak2_idx=int(peak_info["peak2_idx"]),
        use_two_peak=bool(peak_info["multi_peak_flag"]),
    )
    u_thr = percentile(u_vals, high_signal_quantile)
    idx = [i for i, v in enumerate(u_vals) if v >= u_thr]
    if len(idx) < 3:
        return {
            "high_signal_count": len(idx),
            "u_threshold": u_thr,
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "diag_rule_pass": False,
        }
    ux = [u_vals[i] for i in idx]
    tx = [t_vals[i] for i in idx]
    sp = spearman_corr(ux, tx)
    pe = pearson_corr(ux, tx)
    return {
        "high_signal_count": len(idx),
        "u_threshold": u_thr,
        "spearman_hs": sp,
        "pearson_hs": pe,
        "diag_rule_pass": (
            (not math.isnan(sp))
            and (not math.isnan(pe))
            and (abs(sp) >= corr_min)
            and (abs(pe) >= corr_min)
        ),
    }


def gate_from_statuses(*statuses: str) -> str:
    return "pass" if all(norm_status(s) == "pass" for s in statuses) else "fail"


def main() -> int:
    args = parse_args()
    source_csv = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []

    for row in src_rows:
        dataset_id = str(row["dataset_id"])
        seed = int(str(row["seed"]))
        run_root = (ROOT / row["run_root"]).resolve()

        g10_status = norm_status(get_first(row, ["g10_status", "g10_v1_status"]))
        g12_status = norm_status(get_first(row, ["g12_status", "g12_v2_status", "g12_v1_status"]))
        g7_status = norm_status(get_first(row, ["g7_status", "g7_v1_status"]))
        g11_v2_status = norm_status(get_first(row, ["g11_status", "g11_v2_status", "g11_v1_status"]))

        g11b_status = norm_status(get_first(row, ["g11b", "g11b_status", "g11b_v1_status"]))
        g11c_status = norm_status(get_first(row, ["g11c", "g11c_status", "g11c_v1_status"]))
        g11d_status = norm_status(get_first(row, ["g11d", "g11d_status", "g11d_v1_status"]))

        sp_v2 = abs(to_float(get_first(row, ["g11_spearman_high_signal"], "nan")) or float("nan"))
        pe_v2 = abs(to_float(get_first(row, ["g11_pearson_high_signal"], "nan")) or float("nan"))
        weak_corr_v2 = (
            (not math.isnan(sp_v2))
            and (not math.isnan(pe_v2))
            and ((sp_v2 < args.corr_min) or (pe_v2 < args.corr_min))
        )

        eq_csv = run_root / "g11" / "einstein_eq.csv"
        eq_rows = read_csv(eq_csv) if eq_csv.exists() else []
        r_vals: list[float] = []
        sigma_norm: list[float] = []
        for r in eq_rows:
            rv = to_float(r.get("R", ""))
            sv = to_float(r.get("sigma_norm", ""))
            if rv is None or sv is None:
                continue
            r_vals.append(rv)
            sigma_norm.append(sv)

        coords, sigma, adj_w = build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]

        diag = g11_v3_poisson_rule(
            r_vals=r_vals,
            sigma_norm=sigma_norm,
            neighbours=neighbours,
            high_signal_quantile=args.high_signal_quantile,
            corr_min=args.corr_min,
            smooth_alpha=args.r_smooth_alpha,
            smooth_iters=args.r_smooth_iters,
        )

        g11a_v3_fallback = (
            g11b_status == "pass"
            and g11c_status == "pass"
            and g11d_status == "pass"
            and bool(diag["rule_pass"])
        )
        g11_v3_status = "pass" if (g11_v2_status == "pass" or g11a_v3_fallback) else "fail"

        weak_corr_v3 = (
            (not math.isnan(diag["spearman_hs"]))
            and (not math.isnan(diag["pearson_hs"]))
            and ((abs(diag["spearman_hs"]) < args.corr_min) or (abs(diag["pearson_hs"]) < args.corr_min))
        )

        peak_info = multi_peak_info(
            coords=coords,
            sigma=sigma,
            ratio_thr=args.multi_peak_ratio_threshold,
            dist_thr=args.multi_peak_distance_threshold,
        )
        g11b_branch_active = (g11b_status != "pass") and (g11c_status == "pass") and (g11d_status == "pass")
        g11b_diag = g11b_fail_branch_diag(
            r_vals=r_vals,
            coords=coords,
            sigma=sigma,
            neighbours=neighbours,
            peak_info=peak_info,
            high_signal_quantile=args.high_signal_quantile,
            corr_min=args.corr_min,
            smooth_alpha=args.r_smooth_alpha,
            smooth_iters=args.r_smooth_iters,
        )

        stage2_v2 = gate_from_statuses(g10_status, g11_v2_status, g12_status, g7_status)
        stage2_v3 = gate_from_statuses(g10_status, g11_v3_status, g12_status, g7_status)

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "g10_status": g10_status,
                "g12_status": g12_status,
                "g7_status": g7_status,
                "g11b_status": g11b_status,
                "g11c_status": g11c_status,
                "g11d_status": g11d_status,
                "g11_v2_status": g11_v2_status,
                "g11_v3_status": g11_v3_status,
                "g11a_v3_fallback_pass": "true" if g11a_v3_fallback else "false",
                "g11_poisson_hs_count": int(diag["high_signal_count"]),
                "g11_poisson_s_threshold": f6(diag["s_threshold"]),
                "g11_poisson_spearman_hs": f6(diag["spearman_hs"]),
                "g11_poisson_pearson_hs": f6(diag["pearson_hs"]),
                "g11_poisson_rule_pass": "true" if bool(diag["rule_pass"]) else "false",
                "g11_v2_weak_corr_flag": "true" if weak_corr_v2 else "false",
                "g11_v3_weak_corr_flag": "true" if weak_corr_v3 else "false",
                "g11b_fail_branch_active": "true" if g11b_branch_active else "false",
                "g11b_branch_multi_peak_flag": "true" if bool(peak_info["multi_peak_flag"]) else "false",
                "g11b_branch_peak2_to_peak1": f6(peak_info["peak2_to_peak1"]),
                "g11b_branch_peak12_distance_norm": f6(peak_info["peak12_distance_norm"]),
                "g11b_branch_hs_count": int(g11b_diag["high_signal_count"]),
                "g11b_branch_u_threshold": f6(g11b_diag["u_threshold"]),
                "g11b_branch_spearman_hs": f6(g11b_diag["spearman_hs"]),
                "g11b_branch_pearson_hs": f6(g11b_diag["pearson_hs"]),
                "g11b_branch_diag_rule_pass": "true" if bool(g11b_diag["diag_rule_pass"]) else "false",
                "stage2_v2_status": stage2_v2,
                "stage2_v3_status": stage2_v3,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    g11_v2_pass = sum(1 for r in out_rows if r["g11_v2_status"] == "pass")
    g11_v3_pass = sum(1 for r in out_rows if r["g11_v3_status"] == "pass")
    improved = sum(1 for r in out_rows if r["g11_v2_status"] == "fail" and r["g11_v3_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["g11_v2_status"] == "pass" and r["g11_v3_status"] == "fail")
    weak_v2 = sum(1 for r in out_rows if r["g11_v2_status"] == "fail" and r["g11_v2_weak_corr_flag"] == "true")
    weak_v3 = sum(1 for r in out_rows if r["g11_v3_status"] == "fail" and r["g11_v3_weak_corr_flag"] == "true")

    report_lines = [
        "# GR Stage-2 G11 Candidate Evaluation (v3)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## G11 Counts (v2 -> v3)",
        "",
        f"- g11_v2_pass: `{g11_v2_pass}/{n}`",
        f"- g11_v3_pass: `{g11_v3_pass}/{n}`",
        f"- improved_vs_v2: `{improved}`",
        f"- degraded_vs_v2: `{degraded}`",
        "",
        "## Weak-Corr Signature in Fails",
        "",
        f"- weak_corr_fail_count_v2: `{weak_v2}`",
        f"- weak_corr_fail_count_v3: `{weak_v3}`",
        "",
        "## Notes",
        "",
        "- v3 is candidate-only; official Stage-2 policy remains v2 until explicit switch.",
        "- g11b-fail branch is diagnostic-only in this version (no decision override).",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "constants": {
            "high_signal_quantile": args.high_signal_quantile,
            "corr_min": args.corr_min,
            "r_smooth_alpha": args.r_smooth_alpha,
            "r_smooth_iters": args.r_smooth_iters,
            "multi_peak_ratio_threshold": args.multi_peak_ratio_threshold,
            "multi_peak_distance_threshold": args.multi_peak_distance_threshold,
        },
        "notes": [
            "No edits to official gate scripts.",
            "Candidate v3 computed from frozen run artifacts.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
