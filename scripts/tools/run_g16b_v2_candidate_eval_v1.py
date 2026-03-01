#!/usr/bin/env python3
"""
Evaluate G16b-v2 candidate gate on fixed profile grids (diagnostic only).

No changes to scientific formulas or official thresholds are applied.
This script compares:
- G16b-v1 (legacy): R2(G11, 8pi G T11) > 0.05
- G16b-v2 (candidate): low-signal aware diagnostics on full/high-signal subsets
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ACTION_SCRIPT = ROOT / "scripts" / "run_qng_action_v1.py"

DEFAULT_OUT_SANITY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-v2-candidate-sanity-v1"
)
DEFAULT_OUT_PREREG = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-v2-candidate-prereg-v1"
)

PREREG_DATASETS = ["DS-002", "DS-003", "DS-006"]
PREREG_SEED_START = 3401
PREREG_SEED_END = 3600
PREREG_PHI_SCALE = 0.08
PREREG_LOW_SIGNAL_RATIO = 10.0
PREREG_CORR_MIN = 0.2
PREREG_R2_MIN = 0.05
PREREG_HIGH_SIGNAL_QUANTILE = 0.80
PREREG_PROMOTION_RULE = "promote only if G16b-v2 passes 600/600 on DS-002/003/006 x seeds 3401..3600"


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int
    phi_scale: float

    @property
    def tag(self) -> str:
        return f"{self.dataset_id.lower()}_seed{self.seed}_phi{self.phi_scale:.2f}".replace(".", "p")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate G16b-v2 candidate gate (v1).")
    p.add_argument("--mode", choices=["sanity", "prereg"], default="sanity")
    p.add_argument("--out-dir", default="")
    p.add_argument("--reuse-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--profiles", default="", help="Comma-separated dataset:seed list for sanity mode.")
    p.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    p.add_argument("--seed-start", type=int, default=PREREG_SEED_START)
    p.add_argument("--seed-end", type=int, default=PREREG_SEED_END)
    p.add_argument("--phi-scale", type=float, default=PREREG_PHI_SCALE)
    p.add_argument("--low-signal-ratio", type=float, default=PREREG_LOW_SIGNAL_RATIO)
    p.add_argument("--corr-min", type=float, default=PREREG_CORR_MIN)
    p.add_argument("--r2-min", type=float, default=PREREG_R2_MIN)
    p.add_argument("--high-signal-quantile", type=float, default=PREREG_HIGH_SIGNAL_QUANTILE)
    p.add_argument(
        "--strict-prereg",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Fail if parameters differ from prereg constants.",
    )
    return p.parse_args()


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def f6(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.6f}"


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return vals[lo] * (1.0 - frac) + vals[hi] * frac


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    if len(values) == 1:
        return values[0], 0.0
    return statistics.mean(values), statistics.pstdev(values)


def pearson_corr(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    mx, sx = mean_std(x_vals)
    my, sy = mean_std(y_vals)
    if sx <= 1e-30 or sy <= 1e-30:
        return float("nan")
    cov = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(len(x_vals))) / len(x_vals)
    return cov / (sx * sy)


def rank_values(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        v = values[order[i]]
        while j + 1 < len(order) and values[order[j + 1]] == v:
            j += 1
        rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = rank
        i = j + 1
    return ranks


def spearman_corr(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    return pearson_corr(rank_values(x_vals), rank_values(y_vals))


def ols_r2(x_vals: list[float], y_vals: list[float]) -> float:
    if len(x_vals) != len(y_vals) or len(x_vals) < 2:
        return float("nan")
    mx = statistics.mean(x_vals)
    my = statistics.mean(y_vals)
    sxx = sum((x - mx) ** 2 for x in x_vals)
    if sxx <= 1e-30:
        return float("nan")
    sxy = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(len(x_vals)))
    b = sxy / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in y_vals)
    if ss_tot <= 1e-30:
        return 1.0
    y_pred = [a + b * x for x in x_vals]
    ss_res = sum((y_vals[i] - y_pred[i]) ** 2 for i in range(len(x_vals)))
    return max(0.0, 1.0 - ss_res / ss_tot)


def read_action_vectors(action_csv: Path) -> tuple[list[float], list[float]]:
    if not action_csv.exists():
        return [], []
    rows = read_csv(action_csv)
    g11_vals: list[float] = []
    t11_vals: list[float] = []
    for row in rows:
        g = to_float(row.get("G11", ""))
        t = to_float(row.get("T11", ""))
        if g is None or t is None:
            continue
        g11_vals.append(g)
        t11_vals.append(t)
    return g11_vals, t11_vals


def run_action(profile: Profile, out_dir: Path) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(ACTION_SCRIPT),
        "--dataset-id",
        profile.dataset_id,
        "--seed",
        str(profile.seed),
        "--phi-scale",
        f"{profile.phi_scale:.2f}",
        "--no-plots",
        "--out-dir",
        str(out_dir),
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-8:]) if merged else ""
    return proc.returncode, tail


def parse_metric_checks(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        gid = row.get("gate_id", "").strip()
        if gid:
            out[gid] = row
    return out


def high_signal_subset(
    g11_vals: list[float],
    t11_vals: list[float],
    quantile: float,
) -> tuple[list[float], list[float], float]:
    abs_t = [abs(v) for v in t11_vals]
    threshold = percentile(abs_t, quantile)
    pairs = [(g11_vals[i], t11_vals[i]) for i in range(len(t11_vals)) if abs_t[i] >= threshold]
    if not pairs:
        return [], [], threshold
    g = [p[0] for p in pairs]
    t = [p[1] for p in pairs]
    return g, t, threshold


def build_profiles(args: argparse.Namespace) -> list[Profile]:
    if args.mode == "sanity":
        if args.profiles.strip():
            parsed: list[Profile] = []
            for token in parse_csv_list(args.profiles):
                ds, seed_text = token.split(":")
                parsed.append(Profile(ds.strip().upper(), int(seed_text), float(args.phi_scale)))
            return parsed
        return [
            Profile("DS-003", 3407, float(args.phi_scale)),  # known v1 fail-like profile
            Profile("DS-002", 3401, float(args.phi_scale)),  # pass profile
            Profile("DS-006", 3401, float(args.phi_scale)),  # pass profile
        ]
    datasets = [d.upper() for d in parse_csv_list(args.datasets)]
    out: list[Profile] = []
    for ds in datasets:
        for seed in range(args.seed_start, args.seed_end + 1):
            out.append(Profile(ds, seed, float(args.phi_scale)))
    return out


def enforce_prereg(args: argparse.Namespace) -> None:
    errors: list[str] = []
    ds = [d.upper() for d in parse_csv_list(args.datasets)]
    if ds != PREREG_DATASETS:
        errors.append(f"datasets must be {PREREG_DATASETS}, got {ds}")
    if args.seed_start != PREREG_SEED_START or args.seed_end != PREREG_SEED_END:
        errors.append(f"seed range must be {PREREG_SEED_START}..{PREREG_SEED_END}")
    if abs(args.phi_scale - PREREG_PHI_SCALE) > 1e-12:
        errors.append(f"phi_scale must be {PREREG_PHI_SCALE}")
    if abs(args.low_signal_ratio - PREREG_LOW_SIGNAL_RATIO) > 1e-12:
        errors.append(f"low_signal_ratio must be {PREREG_LOW_SIGNAL_RATIO}")
    if abs(args.corr_min - PREREG_CORR_MIN) > 1e-12:
        errors.append(f"corr_min must be {PREREG_CORR_MIN}")
    if abs(args.r2_min - PREREG_R2_MIN) > 1e-12:
        errors.append(f"r2_min must be {PREREG_R2_MIN}")
    if abs(args.high_signal_quantile - PREREG_HIGH_SIGNAL_QUANTILE) > 1e-12:
        errors.append(f"high_signal_quantile must be {PREREG_HIGH_SIGNAL_QUANTILE}")
    if errors:
        raise ValueError("strict prereg violation: " + "; ".join(errors))


def write_report(path: Path, rows: list[dict[str, Any]], mode: str) -> None:
    fail_v1 = [r for r in rows if r["g16b_v1_status"] != "pass"]
    fail_v2 = [r for r in rows if r["g16b_v2_status"] != "pass"]
    improved = [r for r in rows if r["g16b_v1_status"] != "pass" and r["g16b_v2_status"] == "pass"]
    degraded = [r for r in rows if r["g16b_v1_status"] == "pass" and r["g16b_v2_status"] != "pass"]
    pass_v2 = len(rows) - len(fail_v2)

    lines: list[str] = []
    lines.append("# G16b-v2 Candidate Evaluation (v1)")
    lines.append("")
    lines.append(f"- mode: `{mode}`")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- profiles: `{len(rows)}`")
    lines.append(f"- g16b_v1_fail: `{len(fail_v1)}`")
    lines.append(f"- g16b_v2_fail: `{len(fail_v2)}`")
    lines.append(f"- g16b_v2_pass: `{pass_v2}`")
    lines.append(f"- v1_fail_to_v2_pass: `{len(improved)}`")
    lines.append(f"- v1_pass_to_v2_fail: `{len(degraded)}`")
    lines.append("")

    if mode == "prereg":
        lines.append("## Pre-Registered Decision")
        lines.append("")
        lines.append(f"- promotion target: `600/600 pass` (DS-002/003/006 x seeds 3401..3600)")
        lines.append(f"- observed g16b-v2 pass: `{pass_v2}/600`")
        lines.append("- conclusion: `NOT ELIGIBLE FOR PROMOTION` (candidate-only remains)")
        lines.append("")

    lines.append("## Dataset Summary")
    lines.append("")
    lines.append("| dataset | n | v1_fail | v2_fail | improved | degraded |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    datasets = sorted({r["dataset_id"] for r in rows})
    for ds in datasets:
        sub = [r for r in rows if r["dataset_id"] == ds]
        v1 = sum(1 for r in sub if r["g16b_v1_status"] != "pass")
        v2 = sum(1 for r in sub if r["g16b_v2_status"] != "pass")
        imp = sum(1 for r in sub if r["g16b_v1_status"] != "pass" and r["g16b_v2_status"] == "pass")
        deg = sum(1 for r in sub if r["g16b_v1_status"] == "pass" and r["g16b_v2_status"] != "pass")
        lines.append(f"| {ds} | {len(sub)} | {v1} | {v2} | {imp} | {deg} |")
    lines.append("")

    lines.append("## Signal-Regime Breakdown")
    lines.append("")
    lines.append("| low_signal | n | v1_fail | v2_fail | improved | degraded |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for key in ["true", "false"]:
        sub = [r for r in rows if r["is_low_signal"] == key]
        if not sub:
            continue
        v1 = sum(1 for r in sub if r["g16b_v1_status"] != "pass")
        v2 = sum(1 for r in sub if r["g16b_v2_status"] != "pass")
        imp = sum(1 for r in sub if r["g16b_v1_status"] != "pass" and r["g16b_v2_status"] == "pass")
        deg = sum(1 for r in sub if r["g16b_v1_status"] == "pass" and r["g16b_v2_status"] != "pass")
        lines.append(f"| {key} | {len(sub)} | {v1} | {v2} | {imp} | {deg} |")
    lines.append("")

    if improved or degraded:
        lines.append("## Changed Decisions")
        lines.append("")
        lines.append("| dataset | seed | v1 | v2 | branch | low_signal | r2_full | r2_high_signal | |pearson_hs| | |spearman_hs| |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        changed = [r for r in rows if r in improved or r in degraded]
        for r in sorted(changed, key=lambda x: (x["dataset_id"], int(x["seed"]))):
            lines.append(
                f"| {r['dataset_id']} | {r['seed']} | {r['g16b_v1_status']} | {r['g16b_v2_status']} "
                f"| {r['g16b_v2_branch']} | {r['is_low_signal']} | {r['r2_full_recomputed']} | {r['r2_high_signal']} "
                f"| {r['abs_pearson_high_signal']} | {r['abs_spearman_high_signal']} |"
            )
        lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.out_dir.strip():
        out_dir = Path(args.out_dir).resolve()
    else:
        out_dir = (DEFAULT_OUT_SANITY if args.mode == "sanity" else DEFAULT_OUT_PREREG).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root = out_dir / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    if args.strict_prereg:
        enforce_prereg(args)

    profiles = build_profiles(args)
    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        logs.append(msg)

    log("=" * 72)
    log(f"G16b-v2 candidate eval v1 ({args.mode})")
    log(f"start_utc={datetime.utcnow().isoformat()}Z")
    log(f"profiles={len(profiles)}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    for idx, profile in enumerate(profiles, start=1):
        prof_dir = runs_root / profile.tag / "g16"
        prof_dir.mkdir(parents=True, exist_ok=True)
        metric_path = prof_dir / "metric_checks_action.csv"
        action_path = prof_dir / "action.csv"

        log(f"[{idx}/{len(profiles)}] {profile.tag}")
        needs_run = not (args.reuse_existing and metric_path.exists() and action_path.exists())
        if needs_run:
            rc, tail = run_action(profile, prof_dir)
            log(f"  run_action rc={rc}")
            if rc != 0 and tail:
                log("  tail:")
                for line in tail.splitlines():
                    log(f"    {line}")

        metrics = parse_metric_checks(metric_path)
        g11_vals, t11_vals = read_action_vectors(action_path)
        g11_mean, g11_std = mean_std(g11_vals)
        t11_mean, t11_std = mean_std(t11_vals)
        t11_ratio = (t11_std / abs(t11_mean)) if (not math.isnan(t11_std) and not math.isnan(t11_mean) and abs(t11_mean) > 1e-12) else float("inf")

        pear_full = pearson_corr(t11_vals, g11_vals)
        spear_full = spearman_corr(t11_vals, g11_vals)
        r2_full = ols_r2(t11_vals, g11_vals)

        g_hs, t_hs, hs_thr = high_signal_subset(g11_vals, t11_vals, args.high_signal_quantile)
        pear_hs = pearson_corr(t_hs, g_hs)
        spear_hs = spearman_corr(t_hs, g_hs)
        r2_hs = ols_r2(t_hs, g_hs)

        abs_pear_full = abs(pear_full) if not math.isnan(pear_full) else float("nan")
        abs_spear_full = abs(spear_full) if not math.isnan(spear_full) else float("nan")
        abs_pear_hs = abs(pear_hs) if not math.isnan(pear_hs) else float("nan")
        abs_spear_hs = abs(spear_hs) if not math.isnan(spear_hs) else float("nan")

        is_low_signal = t11_ratio > args.low_signal_ratio
        if is_low_signal:
            corr_ok = (abs_pear_hs > args.corr_min) and (abs_spear_hs > args.corr_min)
            r2_ok = r2_hs > args.r2_min
            branch = "high_signal"
        else:
            corr_ok = (abs_pear_full > args.corr_min) and (abs_spear_full > args.corr_min)
            r2_ok = r2_full > args.r2_min
            branch = "full_signal"
        g16b_v2_pass = corr_ok and r2_ok

        g16a_status = metrics.get("G16a", {}).get("status", "").strip().lower() or "fail"
        g16b_v1_status = metrics.get("G16b", {}).get("status", "").strip().lower() or "fail"
        g16c_status = metrics.get("G16c", {}).get("status", "").strip().lower() or "fail"
        g16d_status = metrics.get("G16d", {}).get("status", "").strip().lower() or "fail"

        g16_v1_pass = all(s == "pass" for s in [g16a_status, g16b_v1_status, g16c_status, g16d_status])
        g16_v2_pass = all(s == "pass" for s in [g16a_status, "pass" if g16b_v2_pass else "fail", g16c_status, g16d_status])

        rows.append(
            {
                "dataset_id": profile.dataset_id,
                "seed": profile.seed,
                "phi_scale": f"{profile.phi_scale:.2f}",
                "g16a_status": g16a_status,
                "g16b_v1_status": g16b_v1_status,
                "g16b_v2_status": "pass" if g16b_v2_pass else "fail",
                "g16c_status": g16c_status,
                "g16d_status": g16d_status,
                "g16_v1_status": "pass" if g16_v1_pass else "fail",
                "g16_v2_status": "pass" if g16_v2_pass else "fail",
                "g16b_v2_branch": branch,
                "is_low_signal": "true" if is_low_signal else "false",
                "t11_std_to_abs_mean": f6(t11_ratio),
                "g11_mean": f6(g11_mean),
                "g11_std": f6(g11_std),
                "t11_mean": f6(t11_mean),
                "t11_std": f6(t11_std),
                "pearson_full": f6(pear_full),
                "spearman_full": f6(spear_full),
                "r2_full_recomputed": f6(r2_full),
                "abs_pearson_full": f6(abs_pear_full),
                "abs_spearman_full": f6(abs_spear_full),
                "high_signal_quantile": f6(args.high_signal_quantile),
                "high_signal_count": len(t_hs),
                "high_signal_abs_t11_min": f6(hs_thr),
                "pearson_high_signal": f6(pear_hs),
                "spearman_high_signal": f6(spear_hs),
                "r2_high_signal": f6(r2_hs),
                "abs_pearson_high_signal": f6(abs_pear_hs),
                "abs_spearman_high_signal": f6(abs_spear_hs),
                "corr_min": f6(args.corr_min),
                "r2_min": f6(args.r2_min),
                "low_signal_ratio_threshold": f6(args.low_signal_ratio),
                "run_root": (prof_dir.resolve().relative_to(ROOT.resolve())).as_posix(),
            }
        )

    fieldnames = [
        "dataset_id",
        "seed",
        "phi_scale",
        "g16a_status",
        "g16b_v1_status",
        "g16b_v2_status",
        "g16c_status",
        "g16d_status",
        "g16_v1_status",
        "g16_v2_status",
        "g16b_v2_branch",
        "is_low_signal",
        "t11_std_to_abs_mean",
        "g11_mean",
        "g11_std",
        "t11_mean",
        "t11_std",
        "pearson_full",
        "spearman_full",
        "r2_full_recomputed",
        "abs_pearson_full",
        "abs_spearman_full",
        "high_signal_quantile",
        "high_signal_count",
        "high_signal_abs_t11_min",
        "pearson_high_signal",
        "spearman_high_signal",
        "r2_high_signal",
        "abs_pearson_high_signal",
        "abs_spearman_high_signal",
        "corr_min",
        "r2_min",
        "low_signal_ratio_threshold",
        "run_root",
    ]
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, fieldnames)

    report_md = out_dir / "report.md"
    write_report(report_md, rows, args.mode)

    prereg_manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "strict_prereg": bool(args.strict_prereg),
        "datasets": parse_csv_list(args.datasets),
        "seed_start": args.seed_start,
        "seed_end": args.seed_end,
        "phi_scale": args.phi_scale,
        "low_signal_ratio_threshold": args.low_signal_ratio,
        "corr_min_abs": args.corr_min,
        "r2_min": args.r2_min,
        "high_signal_quantile": args.high_signal_quantile,
        "promotion_rule": PREREG_PROMOTION_RULE,
        "notes": [
            "G16b-v2 candidate only; official gate remains G16b-v1.",
            "No formula/threshold changes in run_qng_action_v1.py.",
            "Use absolute correlations because sign can be convention-dependent.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(prereg_manifest, indent=2), encoding="utf-8")

    (out_dir / "run-log-eval.txt").write_text("\n".join(logs) + "\n", encoding="utf-8")

    print(f"summary_csv:  {summary_csv}")
    print(f"report_md:    {report_md}")
    print(f"manifest:     {out_dir / 'prereg_manifest.json'}")
    print(f"run_log:      {out_dir / 'run-log-eval.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
