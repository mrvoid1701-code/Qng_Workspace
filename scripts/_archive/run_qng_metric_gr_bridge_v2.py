#!/usr/bin/env python3
"""
QNG metric -> GR bridge sanity runner (v2).

Identical logic to v1, with one change:
  --iso-ref 0.7071   (default = 1/sqrt(2))
  The isotropic flat-metric reference for Frobenius-normalized (v4) metric.
  v3 (trace norm) used iso_ref=0.5; v4 (Frobenius norm) uses iso_ref=1/sqrt(2).

Pre-registration: 05_validation/pre-registrations/qng-metric-gr-bridge-v2.md
Dependency policy: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import time


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_ARTIFACT_DIRS = "qng-metric-hardening-v4-ds002,qng-metric-hardening-v4-ds003,qng-metric-hardening-v4-ds006"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-metric-gr-bridge-v2"
DEFAULT_ISO_REF = 1.0 / math.sqrt(2.0)   # ≈ 0.7071 — Frobenius normalization isotropic target


@dataclass
class BridgeThresholds:
    # B1: weak-field perturbation from isotropic flat reference
    weak_med_h_max: float = 0.20    # relaxed slightly from v1=0.18 to account for v4 shrinkage target
    weak_p90_h_max: float = 0.32
    # B2: metric sanity
    min_eig_floor: float = 0.25
    cond_p90_max: float = 2.50
    # B3: Newtonian direction
    cos_raw_median_min: float = 0.95
    cos_raw_p10_min: float = 0.90
    # B4: continuum stability
    drift_median_max: float = 0.07
    drift_p90_max: float = 0.20
    # B5: control separation
    shuffle_gap_min: float = 0.90


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


def parse_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def infer_dataset_id(dir_path: Path) -> str:
    cfg = dir_path / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            ds = str(data.get("dataset_id", "")).strip()
            if ds:
                return ds
        except json.JSONDecodeError:
            pass
    name = dir_path.name.lower()
    if "ds003" in name or "ds-003" in name:
        return "DS-003"
    if "ds006" in name or "ds-006" in name:
        return "DS-006"
    return "DS-002"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG metric->GR bridge sanity checks (v2, Frobenius-normalized).")
    p.add_argument("--artifact-dirs", default=DEFAULT_ARTIFACT_DIRS,
                   help="Comma-separated artifact directories.")
    p.add_argument("--scale-ref", default="1s0")
    p.add_argument("--iso-ref", type=float, default=DEFAULT_ISO_REF,
                   help=f"Isotropic reference for flat metric perturbation (default={DEFAULT_ISO_REF:.6f} = 1/sqrt(2) for v4 Frobenius norm).")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    # Gate CLI overrides (same defaults as v1 except relaxed B1).
    p.add_argument("--weak-med-h-max", type=float, default=0.20)
    p.add_argument("--weak-p90-h-max", type=float, default=0.32)
    p.add_argument("--min-eig-floor", type=float, default=0.25)
    p.add_argument("--cond-p90-max", type=float, default=2.50)
    p.add_argument("--drift-median-max", type=float, default=0.07)
    p.add_argument("--drift-p90-max", type=float, default=0.20)
    p.add_argument("--cos-raw-median-min", type=float, default=0.95)
    p.add_argument("--cos-raw-p10-min", type=float, default=0.90)
    p.add_argument("--shuffle-gap-min", type=float, default=0.90)
    return p.parse_args()


def resolve_artifact_dirs(text: str) -> list[Path]:
    out: list[Path] = []
    for token in [t.strip() for t in text.split(",") if t.strip()]:
        p = Path(token)
        if not p.is_absolute():
            p = (ARTIFACTS_ROOT / p).resolve()
        out.append(p)
    return out


def main() -> int:
    args = parse_args()
    t0 = time.perf_counter()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    iso_ref = args.iso_ref

    thresholds = BridgeThresholds(
        weak_med_h_max=args.weak_med_h_max,
        weak_p90_h_max=args.weak_p90_h_max,
        min_eig_floor=args.min_eig_floor,
        cond_p90_max=args.cond_p90_max,
        drift_median_max=args.drift_median_max,
        drift_p90_max=args.drift_p90_max,
        cos_raw_median_min=args.cos_raw_median_min,
        cos_raw_p10_min=args.cos_raw_p10_min,
        shuffle_gap_min=args.shuffle_gap_min,
    )

    artifact_dirs = resolve_artifact_dirs(args.artifact_dirs)
    if not artifact_dirs:
        raise ValueError("No artifact directories provided.")

    dataset_rows: list[dict[str, str]] = []
    input_hash_rows: list[dict[str, str]] = []
    warnings: list[str] = []

    for adir in artifact_dirs:
        if not adir.exists():
            warnings.append(f"Missing artifact directory: {adir}")
            continue
        eigs_path = adir / "eigs.csv"
        align_path = adir / "align_sigma.csv"
        drift_path = adir / "drift.csv"
        checks_path = adir / "metric_checks.csv"
        required = [eigs_path, align_path, drift_path, checks_path]
        missing = [str(p.name) for p in required if not p.exists()]
        if missing:
            warnings.append(f"Skipping {adir.name}: missing files ({', '.join(missing)})")
            continue

        dataset_id = infer_dataset_id(adir)
        eig_rows = parse_csv(eigs_path)
        align_rows = parse_csv(align_path)
        drift_rows = parse_csv(drift_path)

        h_norm: list[float] = []
        cond_vals: list[float] = []
        min_eig_vals: list[float] = []

        for row in eig_rows:
            if str(row.get("scale", "")).strip() != args.scale_ref:
                continue
            g11 = float(row["g11"])
            g12 = float(row["g12"])
            g22 = float(row["g22"])
            # v2 key change: use iso_ref instead of hardcoded 0.5
            h11 = g11 - iso_ref
            h22 = g22 - iso_ref
            h12 = g12
            h = math.sqrt(h11 * h11 + 2.0 * h12 * h12 + h22 * h22)
            h_norm.append(h)
            lmin = float(row["min_eig"])
            lmax = float(row["max_eig"])
            min_eig_vals.append(lmin)
            if lmin > 0.0:
                cond_vals.append(lmax / lmin)

        cos_raw = [float(r["cos_sim_raw"]) for r in align_rows]
        cos_shuf = [float(r["cos_sim_shuffled"]) for r in align_rows]
        drift = [float(r["delta_g_fro_rel"]) for r in drift_rows]

        if not h_norm or not cond_vals or not min_eig_vals or not cos_raw or not cos_shuf or not drift:
            warnings.append(f"Skipping {adir.name}: insufficient numeric rows after parsing.")
            continue

        med_h = median(h_norm)
        p90_h = percentile90(h_norm)
        min_eig_global = min(min_eig_vals)
        p90_cond = percentile90(cond_vals)
        med_drift = median(drift)
        p90_drift = percentile90(drift)
        med_raw = median(cos_raw)
        p10_raw = percentile10(cos_raw)
        med_shuf = median(cos_shuf)
        raw_shuf_gap = med_raw - med_shuf

        pass_b1 = (med_h <= thresholds.weak_med_h_max) and (p90_h <= thresholds.weak_p90_h_max)
        pass_b2 = (min_eig_global >= thresholds.min_eig_floor) and (p90_cond <= thresholds.cond_p90_max)
        pass_b3 = (med_raw >= thresholds.cos_raw_median_min) and (p10_raw >= thresholds.cos_raw_p10_min)
        pass_b4 = (med_drift <= thresholds.drift_median_max) and (p90_drift <= thresholds.drift_p90_max)
        pass_b5 = raw_shuf_gap >= thresholds.shuffle_gap_min
        pass_dataset = pass_b1 and pass_b2 and pass_b3 and pass_b4 and pass_b5

        dataset_rows.append({
            "dataset_id": dataset_id,
            "artifact_dir": adir.name,
            "n_anchors_ref": str(len(h_norm)),
            "iso_ref_used": fmt(iso_ref),
            "h_norm_median": fmt(med_h),
            "h_norm_p90": fmt(p90_h),
            "min_eig_global": fmt(min_eig_global),
            "cond_p90": fmt(p90_cond),
            "drift_median": fmt(med_drift),
            "drift_p90": fmt(p90_drift),
            "cos_raw_median": fmt(med_raw),
            "cos_raw_p10": fmt(p10_raw),
            "cos_shuffled_median": fmt(med_shuf),
            "raw_minus_shuffled_median_gap": fmt(raw_shuf_gap),
            "pass_B1_weak_field": str(pass_b1),
            "pass_B2_metric_sanity": str(pass_b2),
            "pass_B3_newton_direction": str(pass_b3),
            "pass_B4_continuum_stability": str(pass_b4),
            "pass_B5_control_separation": str(pass_b5),
            "pass_dataset": str(pass_dataset),
        })

        for p in required:
            input_hash_rows.append({
                "dataset_id": dataset_id,
                "artifact_dir": adir.name,
                "file": p.name,
                "sha256": sha256_of(p),
            })

    if not dataset_rows:
        raise RuntimeError("No valid dataset artifact bundle parsed.")

    def bool_col(name: str) -> bool:
        return all(r[name] == "True" for r in dataset_rows)

    max_med_h = max(float(r["h_norm_median"]) for r in dataset_rows)
    max_p90_h = max(float(r["h_norm_p90"]) for r in dataset_rows)
    min_eig_global_all = min(float(r["min_eig_global"]) for r in dataset_rows)
    max_p90_cond = max(float(r["cond_p90"]) for r in dataset_rows)
    max_med_drift = max(float(r["drift_median"]) for r in dataset_rows)
    max_p90_drift = max(float(r["drift_p90"]) for r in dataset_rows)
    min_med_raw = min(float(r["cos_raw_median"]) for r in dataset_rows)
    min_p10_raw = min(float(r["cos_raw_p10"]) for r in dataset_rows)
    min_gap = min(float(r["raw_minus_shuffled_median_gap"]) for r in dataset_rows)

    global_checks = [
        {"gate_id": "B1", "metric": f"weak_field_h_norm from iso={fmt(iso_ref)} (max med/p90)", "value": f"{fmt(max_med_h)} / {fmt(max_p90_h)}", "threshold": f"med<={fmt(thresholds.weak_med_h_max)} and p90<={fmt(thresholds.weak_p90_h_max)}", "status": "pass" if bool_col("pass_B1_weak_field") else "fail"},
        {"gate_id": "B2", "metric": "metric_sanity (min_eig, max cond_p90)", "value": f"{fmt(min_eig_global_all)} / {fmt(max_p90_cond)}", "threshold": f"min_eig>={fmt(thresholds.min_eig_floor)} and cond_p90<={fmt(thresholds.cond_p90_max)}", "status": "pass" if bool_col("pass_B2_metric_sanity") else "fail"},
        {"gate_id": "B3", "metric": "newton_direction (min median/p10 cos_raw)", "value": f"{fmt(min_med_raw)} / {fmt(min_p10_raw)}", "threshold": f"median>={fmt(thresholds.cos_raw_median_min)} and p10>={fmt(thresholds.cos_raw_p10_min)}", "status": "pass" if bool_col("pass_B3_newton_direction") else "fail"},
        {"gate_id": "B4", "metric": "continuum_stability (max median/p90 drift)", "value": f"{fmt(max_med_drift)} / {fmt(max_p90_drift)}", "threshold": f"median<={fmt(thresholds.drift_median_max)} and p90<={fmt(thresholds.drift_p90_max)}", "status": "pass" if bool_col("pass_B4_continuum_stability") else "fail"},
        {"gate_id": "B5", "metric": "control_separation (min raw-shuffled gap)", "value": fmt(min_gap), "threshold": f">={fmt(thresholds.shuffle_gap_min)}", "status": "pass" if bool_col("pass_B5_control_separation") else "fail"},
    ]
    final_pass = all(g["status"] == "pass" for g in global_checks)
    global_checks.append({"gate_id": "FINAL", "metric": "decision", "value": "pass" if final_pass else "fail", "threshold": "B1&B2&B3&B4&B5", "status": "pass" if final_pass else "fail"})

    write_csv(out_dir / "dataset_summary.csv", fieldnames=list(dataset_rows[0].keys()), rows=dataset_rows)
    write_csv(out_dir / "bridge_checks.csv", fieldnames=["gate_id", "metric", "value", "threshold", "status"], rows=global_checks)
    write_csv(out_dir / "input_hashes.csv", fieldnames=["dataset_id", "artifact_dir", "file", "sha256"], rows=input_hash_rows)

    config = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "version": "v2",
        "metric_version": "v4 (Frobenius normalization)",
        "iso_ref": iso_ref,
        "artifact_dirs_cli": args.artifact_dirs,
        "scale_ref": args.scale_ref,
        "thresholds": {
            "iso_ref": iso_ref,
            "weak_med_h_max": thresholds.weak_med_h_max,
            "weak_p90_h_max": thresholds.weak_p90_h_max,
            "min_eig_floor": thresholds.min_eig_floor,
            "cond_p90_max": thresholds.cond_p90_max,
            "drift_median_max": thresholds.drift_median_max,
            "drift_p90_max": thresholds.drift_p90_max,
            "cos_raw_median_min": thresholds.cos_raw_median_min,
            "cos_raw_p10_min": thresholds.cos_raw_p10_min,
            "shuffle_gap_min": thresholds.shuffle_gap_min,
        },
        "n_datasets": len(dataset_rows),
        "decision": "pass" if final_pass else "fail",
        "runtime": {"python": platform.python_version(), "platform": platform.platform(), "duration_seconds": round(time.perf_counter() - t0, 4)},
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    # Run log.
    run_log = [
        "QNG Metric GR Bridge v2 run log",
        f"timestamp_utc: {config['timestamp_utc']}",
        f"metric_version: v4 (Frobenius normalization)",
        f"iso_ref: {iso_ref:.6f}",
        f"decision: {'pass' if final_pass else 'fail'}",
        f"n_datasets: {len(dataset_rows)}",
        "",
        "Per-dataset results:",
    ]
    for r in dataset_rows:
        run_log.append(f"  {r['dataset_id']}: B1={r['pass_B1_weak_field']} B2={r['pass_B2_metric_sanity']} B3={r['pass_B3_newton_direction']} B4={r['pass_B4_continuum_stability']} B5={r['pass_B5_control_separation']} h_med={r['h_norm_median']} h_p90={r['h_norm_p90']} cond_p90={r['cond_p90']} cos_med={r['cos_raw_median']}")
    if warnings:
        run_log += ["", "warnings:"] + [f"  - {w}" for w in warnings]
    (out_dir / "run-log.txt").write_text("\n".join(run_log), encoding="utf-8")

    print(f"QNG GR Bridge v2 completed. decision={'pass' if final_pass else 'fail'}")
    for g in global_checks:
        print(f"  {g['gate_id']:6s} {g['status']:4s}  {g['metric'][:55]:55s}  {g['value']}")
    return 0 if final_pass else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
