#!/usr/bin/env python3
"""
G17 diagnosis runner (v1) for DS-003 fragility analysis.

Scope:
- run G17 over a seed block (default DS-003, 3401..3430)
- collect gate metrics into one summary CSV
- compute diagnostic feature set (multi-peak, low-signal, spectral health)
- assign fail taxonomy classes (diagnostic only; no threshold changes)
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
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "g17-diagnosis-ds003-v1"


@dataclass(frozen=True)
class G17Metrics:
    g17a_status: str
    g17b_status: str
    g17c_status: str
    g17d_status: str
    g17_status: str
    spectral_gap: float
    propagator_slope: float
    e0_per_mode: float
    heisenberg_dev: float


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G17 diagnosis batch and taxonomy (v1).")
    p.add_argument("--dataset-id", default="DS-003")
    p.add_argument("--seed-start", type=int, default=3401)
    p.add_argument("--seed-end", type=int, default=3430)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=False)
    return p.parse_args()


def parse_float(v: str, default: float = 0.0) -> float:
    try:
        return float(str(v).strip())
    except Exception:
        return default


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-10:]) if merged else ""
    return proc.returncode, tail


def parse_metric_checks(path: Path) -> G17Metrics:
    by_gate: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        gid = (row.get("gate_id") or "").strip()
        if gid:
            by_gate[gid] = row

    return G17Metrics(
        g17a_status=norm_status(by_gate.get("G17a", {}).get("status", "")),
        g17b_status=norm_status(by_gate.get("G17b", {}).get("status", "")),
        g17c_status=norm_status(by_gate.get("G17c", {}).get("status", "")),
        g17d_status=norm_status(by_gate.get("G17d", {}).get("status", "")),
        g17_status=norm_status(by_gate.get("FINAL", {}).get("status", "")),
        spectral_gap=parse_float(by_gate.get("G17a", {}).get("value", "0")),
        propagator_slope=parse_float(by_gate.get("G17b", {}).get("value", "0")),
        e0_per_mode=parse_float(by_gate.get("G17c", {}).get("value", "0")),
        heisenberg_dev=parse_float(by_gate.get("G17d", {}).get("value", "0")),
    )


def compute_sigma_features(local_rows: list[dict[str, str]]) -> dict[str, float]:
    if not local_rows:
        return {
            "n_vertices": 0.0,
            "sigma_mean": 0.0,
            "sigma_var": 0.0,
            "sigma_p90_mean": 0.0,
            "sigma_peak1": 0.0,
            "sigma_peak2": 0.0,
            "sigma_peak2_to_peak1": 0.0,
            "peak12_distance": 0.0,
            "peak12_distance_norm": 0.0,
            "multi_peak_score": 0.0,
        }

    sigma_vals = [parse_float(r.get("sigma_norm", "0")) for r in local_rows]
    xs = [parse_float(r.get("x", "0")) for r in local_rows]
    ys = [parse_float(r.get("y", "0")) for r in local_rows]
    n = len(sigma_vals)
    sigma_sorted_idx = sorted(range(n), key=lambda i: sigma_vals[i], reverse=True)
    i1 = sigma_sorted_idx[0]
    i2 = sigma_sorted_idx[1] if n > 1 else i1
    p1 = sigma_vals[i1]
    p2 = sigma_vals[i2]
    ratio = p2 / p1 if p1 > 1e-12 else 0.0
    d12 = math.hypot(xs[i1] - xs[i2], ys[i1] - ys[i2])
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    diag = math.hypot(dx, dy)
    d12_norm = d12 / diag if diag > 1e-12 else 0.0
    q = max(1, int(0.1 * n))
    p90_mean = sum(sorted(sigma_vals, reverse=True)[:q]) / q
    mean = sum(sigma_vals) / n
    var = sum((v - mean) ** 2 for v in sigma_vals) / n

    return {
        "n_vertices": float(n),
        "sigma_mean": mean,
        "sigma_var": var,
        "sigma_p90_mean": p90_mean,
        "sigma_peak1": p1,
        "sigma_peak2": p2,
        "sigma_peak2_to_peak1": ratio,
        "peak12_distance": d12,
        "peak12_distance_norm": d12_norm,
        "multi_peak_score": ratio * d12_norm,
    }


def compute_spectral_features(mode_rows: list[dict[str, str]]) -> dict[str, float]:
    mus = [parse_float(r.get("mu_k", "0")) for r in mode_rows]
    prods = [parse_float(r.get("ds_dp_product", "0")) for r in mode_rows]
    if not mus:
        return {
            "n_modes": 0.0,
            "mu_min_spacing": 0.0,
            "mu_12_spacing": 0.0,
            "mu_23_spacing": 0.0,
            "mu_degenerate_pairs_eps1e3": 0.0,
            "prod_mean": 0.0,
            "prod_max_dev_from_half": 0.0,
        }
    mus_sorted = sorted(mus)
    spacings = [mus_sorted[i + 1] - mus_sorted[i] for i in range(len(mus_sorted) - 1)]
    mu_min_spacing = min(spacings) if spacings else 0.0
    deg_pairs = sum(1 for s in spacings if s < 1e-3)
    mu12 = mus_sorted[1] - mus_sorted[0] if len(mus_sorted) > 1 else 0.0
    mu23 = mus_sorted[2] - mus_sorted[1] if len(mus_sorted) > 2 else 0.0
    prod_mean = sum(prods) / len(prods) if prods else 0.0
    prod_dev = max((abs(p - 0.5) for p in prods), default=0.0)

    return {
        "n_modes": float(len(mus_sorted)),
        "mu_min_spacing": mu_min_spacing,
        "mu_12_spacing": mu12,
        "mu_23_spacing": mu23,
        "mu_degenerate_pairs_eps1e3": float(deg_pairs),
        "prod_mean": prod_mean,
        "prod_max_dev_from_half": prod_dev,
    }


def classify_fail(row: dict[str, Any]) -> str:
    if row["g17_status"] == "pass":
        return "pass"
    if row["g17d_status"] == "fail" or row["prod_max_dev_from_half"] > 0.01:
        return "normalization_break"

    # Diagnostic-only signatures (not decision thresholds).
    multi_peak = row["sigma_peak2_to_peak1"] >= 0.90 and row["peak12_distance_norm"] <= 0.25
    low_signal = row["sigma_mean"] <= 0.45 or row["sigma_p90_mean"] <= 0.65
    spectral_deg = row["mu_12_spacing"] < 0.005 or row["mu_degenerate_pairs_eps1e3"] >= 2

    if row["g17a_status"] == "fail" and multi_peak:
        return "multipeak_mode_mixing"
    if row["g17a_status"] == "fail" and spectral_deg:
        return "spectral_degeneracy"
    if row["g17a_status"] == "fail" and low_signal:
        return "low_signal_mode_instability"
    return "other_gap_fail"


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n == 0 or len(ys) != n:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-30 or vy <= 1e-30:
        return 0.0
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return cov / math.sqrt(vx * vy)


def main() -> int:
    args = parse_args()
    if args.seed_end < args.seed_start:
        raise ValueError("seed-end must be >= seed-start")

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root = out_dir / "runs"
    runs_root.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    seeds = list(range(args.seed_start, args.seed_end + 1))
    log("=" * 72)
    log(
        f"G17 diagnosis v1 | dataset={args.dataset_id} "
        f"seeds={args.seed_start}..{args.seed_end} n={len(seeds)}"
    )
    log(f"out_dir={out_dir}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    for idx, seed in enumerate(seeds, start=1):
        tag = f"{args.dataset_id.lower()}_seed{seed}"
        g17_out = runs_root / tag / "g17"
        g17_out.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(SCRIPTS / "run_qng_qm_bridge_v1.py"),
            "--dataset-id",
            args.dataset_id,
            "--seed",
            str(seed),
            "--out-dir",
            str(g17_out),
        ]
        rc, tail = run_cmd(cmd, ROOT)

        metrics_csv = g17_out / "metric_checks_qm.csv"
        modes_csv = g17_out / "qm_modes.csv"
        local_csv = g17_out / "local_fluctuations.csv"
        if not metrics_csv.exists():
            raise RuntimeError(f"missing metric_checks_qm.csv for {tag}")

        g = parse_metric_checks(metrics_csv)
        sigma_feats = compute_sigma_features(read_csv(local_csv) if local_csv.exists() else [])
        spec_feats = compute_spectral_features(read_csv(modes_csv) if modes_csv.exists() else [])

        row: dict[str, Any] = {
            "dataset_id": args.dataset_id,
            "seed": seed,
            "run_root": g17_out.resolve().relative_to(ROOT.resolve()).as_posix(),
            "runner_rc": rc,
            "g17_status": g.g17_status,
            "g17a_status": g.g17a_status,
            "g17b_status": g.g17b_status,
            "g17c_status": g.g17c_status,
            "g17d_status": g.g17d_status,
            "spectral_gap": g.spectral_gap,
            "propagator_slope": g.propagator_slope,
            "e0_per_mode": g.e0_per_mode,
            "heisenberg_dev": g.heisenberg_dev,
            **sigma_feats,
            **spec_feats,
        }
        row["fail_class"] = classify_fail(row)
        rows.append(row)

        log(
            f"[{idx}/{len(seeds)}] {tag}: rc={rc} g17={row['g17_status']} "
            f"g17a={row['g17a_status']} gap={row['spectral_gap']:.6f} "
            f"class={row['fail_class']}"
        )
        if rc != 0 and tail:
            for line in tail.splitlines():
                log(f"    {line}")

    rows.sort(key=lambda r: int(r["seed"]))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, list(rows[0].keys()))

    fail_rows = [r for r in rows if r["g17_status"] == "fail"]
    class_counts: dict[str, int] = {}
    for r in fail_rows:
        cls = str(r["fail_class"])
        class_counts[cls] = class_counts.get(cls, 0) + 1
    class_rows = [{"fail_class": k, "count": v} for k, v in sorted(class_counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    class_csv = out_dir / "class_summary.csv"
    if class_rows:
        write_csv(class_csv, class_rows, ["fail_class", "count"])
    else:
        write_csv(class_csv, [{"fail_class": "none", "count": 0}], ["fail_class", "count"])

    feature_names = [
        "spectral_gap",
        "mu_12_spacing",
        "mu_min_spacing",
        "mu_degenerate_pairs_eps1e3",
        "sigma_mean",
        "sigma_var",
        "sigma_p90_mean",
        "sigma_peak2_to_peak1",
        "peak12_distance_norm",
        "multi_peak_score",
        "heisenberg_dev",
    ]
    y = [1.0 if r["g17_status"] == "fail" else 0.0 for r in rows]
    corr_rows = []
    for f in feature_names:
        xs = [float(r[f]) for r in rows]
        fail_vals = [float(r[f]) for r in rows if r["g17_status"] == "fail"]
        pass_vals = [float(r[f]) for r in rows if r["g17_status"] == "pass"]
        fail_mean = sum(fail_vals) / len(fail_vals) if fail_vals else 0.0
        pass_mean = sum(pass_vals) / len(pass_vals) if pass_vals else 0.0
        corr_rows.append(
            {
                "feature": f,
                "corr_fail_indicator": f"{pearson(xs, y):.6f}",
                "delta_fail_minus_pass": f"{(fail_mean - pass_mean):.6f}",
            }
        )
    corr_rows.sort(key=lambda r: abs(parse_float(r["corr_fail_indicator"])), reverse=True)
    corr_csv = out_dir / "feature_correlations.csv"
    write_csv(corr_csv, corr_rows, ["feature", "corr_fail_indicator", "delta_fail_minus_pass"])

    n = len(rows)
    n_fail = len(fail_rows)
    n_pass = n - n_fail
    g17a_fail = sum(1 for r in rows if r["g17a_status"] == "fail")
    g17b_fail = sum(1 for r in rows if r["g17b_status"] == "fail")
    g17c_fail = sum(1 for r in rows if r["g17c_status"] == "fail")
    g17d_fail = sum(1 for r in rows if r["g17d_status"] == "fail")

    report_lines = [
        "# G17 Diagnosis Report (v1)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- dataset_id: `{args.dataset_id}`",
        f"- seed_range: `{args.seed_start}..{args.seed_end}`",
        f"- profiles: `{n}`",
        f"- g17_pass: `{n_pass}/{n}`",
        f"- g17_fail: `{n_fail}/{n}`",
        "",
        "## Gate Component Fails",
        "",
        f"- G17a fail count: `{g17a_fail}`",
        f"- G17b fail count: `{g17b_fail}`",
        f"- G17c fail count: `{g17c_fail}`",
        f"- G17d fail count: `{g17d_fail}`",
        "",
        "## Fail Taxonomy",
        "",
    ]
    if class_rows and class_rows[0]["fail_class"] != "none":
        for r in class_rows:
            report_lines.append(f"- `{r['fail_class']}`: `{r['count']}`")
    else:
        report_lines.append("- no fail profiles in batch")

    report_lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Taxonomy is diagnostic only and does not change gate thresholds or formulas.",
            "- DS-003 mini-sprint output is intended for deciding whether G17-v2 candidate is needed.",
        ]
    )
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "dataset_id": args.dataset_id,
        "seed_start": args.seed_start,
        "seed_end": args.seed_end,
        "profiles": n,
        "runner": "run_g17_diagnosis_v1.py",
        "source_script": "scripts/run_qng_qm_bridge_v1.py",
        "notes": [
            "Diagnostic batch for G17 only.",
            "No gate thresholds or formulas were changed.",
        ],
    }
    manifest_json = out_dir / "diagnosis_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "run-log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"class_csv:   {class_csv}")
    print(f"corr_csv:    {corr_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")

    if args.strict_exit and n_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
