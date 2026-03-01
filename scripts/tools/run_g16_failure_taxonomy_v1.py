#!/usr/bin/env python3
"""
Build G16 failure taxonomy from a profile summary (housekeeping only).

Purpose:
- Diagnose when/why G16 fails without changing thresholds or formulas.
- Produce structured pass/fail case tables and an explanatory report.

Inputs:
- summary CSV containing dataset_id, seed, phi_scale (+ optional gate statuses)

Outputs (under --out-dir):
- g16_fail_cases.csv
- g16_pass_cases.csv
- g16_failure_taxonomy.md
- run-log-g16-taxonomy.txt
- per-profile reruns in runs/<dataset_seed_phi>/g16/
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import math
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_qng_action_v1 import build_adjacency, build_dataset_graph  # noqa: E402


DEFAULT_SUMMARY_CSV = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-regression-baseline-v1"
    / "source_runs_grid20"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16-failure-taxonomy-v1"
)

ACTION_SCRIPT = ROOT / "scripts" / "run_qng_action_v1.py"
ACTION_METRIC_CSV = "metric_checks_action.csv"
ACTION_CONFIG_JSON = "config_action.json"

SUBGATES = ["G16a", "G16b", "G16c", "G16d"]


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int
    phi_scale: str
    source_row: dict[str, str]

    @property
    def tag(self) -> str:
        phi_tag = self.phi_scale.replace(".", "p")
        return f"{self.dataset_id.lower()}_seed{self.seed}_phi{phi_tag}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G16 taxonomy diagnostics over summary profiles.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--reuse-existing", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--max-profiles", type=int, default=0, help="0 means all profiles.")
    p.add_argument("--top-patterns", type=int, default=5)
    p.add_argument("--peak-ratio-threshold", type=float, default=0.98)
    p.add_argument("--peak-distance-threshold", type=float, default=0.10)
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


def parse_profiles(rows: list[dict[str, str]]) -> list[Profile]:
    profiles: dict[tuple[str, int, str], Profile] = {}
    for row in rows:
        key = (
            row["dataset_id"].strip(),
            int(row["seed"]),
            f"{float(row['phi_scale']):.2f}",
        )
        if key not in profiles:
            profiles[key] = Profile(
                dataset_id=key[0],
                seed=key[1],
                phi_scale=key[2],
                source_row=row,
            )
    out = list(profiles.values())
    out.sort(key=lambda p: (p.dataset_id, p.seed, float(p.phi_scale)))
    return out


def read_metric_checks(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def parse_metric_checks(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        gate_id = row.get("gate_id", "").strip()
        if gate_id:
            out[gate_id] = row
    return out


def status_is_pass(value: str) -> bool:
    return value.strip().lower() == "pass"


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def run_action(profile: Profile, out_dir: Path) -> tuple[int, str]:
    cmd = [
        sys.executable,
        str(ACTION_SCRIPT),
        "--dataset-id",
        profile.dataset_id,
        "--seed",
        str(profile.seed),
        "--phi-scale",
        profile.phi_scale,
        "--no-plots",
        "--out-dir",
        str(out_dir),
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONUTF8": "1", **dict(**__import__("os").environ)},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-8:]) if merged else ""
    return proc.returncode, tail


def euclidean(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def sigma_features(
    dataset_id: str,
    seed: int,
    *,
    peak_ratio_threshold: float,
    peak_distance_threshold: float,
) -> dict[str, Any]:
    coords, sigma, adj_list = build_dataset_graph(dataset_id, seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / float(n) if n else float("nan")

    sigma_max = max(sigma) if sigma else 1.0
    sigma_norm = [s / sigma_max for s in sigma]
    sigma_mean = statistics.mean(sigma_norm) if sigma_norm else float("nan")
    sigma_std = statistics.pstdev(sigma_norm) if len(sigma_norm) > 1 else 0.0
    sigma_cv = sigma_std / sigma_mean if sigma_mean and not math.isnan(sigma_mean) else float("nan")

    sorted_idx = sorted(range(n), key=lambda i: sigma_norm[i], reverse=True)
    i1 = sorted_idx[0] if sorted_idx else 0
    i2 = sorted_idx[1] if len(sorted_idx) > 1 else i1
    peak1 = sigma_norm[i1] if sorted_idx else float("nan")
    peak2 = sigma_norm[i2] if len(sorted_idx) > 1 else peak1
    peak_ratio = (peak2 / peak1) if peak1 and not math.isnan(peak1) else float("nan")
    d12 = euclidean(coords[i1], coords[i2]) if len(sorted_idx) > 1 else 0.0

    xs = [x for x, _ in coords]
    ys = [y for _, y in coords]
    span_diag = math.hypot((max(xs) - min(xs)) if xs else 0.0, (max(ys) - min(ys)) if ys else 0.0)
    d12_norm = d12 / span_diag if span_diag > 1e-12 else 0.0

    p90 = percentile(sigma_norm, 0.90)
    p10 = percentile(sigma_norm, 0.10)

    is_multi_peak = bool(
        (not math.isnan(peak_ratio))
        and peak_ratio >= peak_ratio_threshold
        and d12_norm >= peak_distance_threshold
    )

    return {
        "n_nodes": n,
        "mean_degree": mean_degree,
        "sigma_mean": sigma_mean,
        "sigma_std": sigma_std,
        "sigma_cv": sigma_cv,
        "sigma_p90": p90,
        "sigma_p10": p10,
        "peak1_sigma": peak1,
        "peak2_sigma": peak2,
        "peak2_to_peak1": peak_ratio,
        "peak12_distance": d12,
        "peak12_distance_norm": d12_norm,
        "multi_peak_flag_default": "true" if is_multi_peak else "false",
    }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    pos = (len(vals) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    f = pos - lo
    return vals[lo] * (1.0 - f) + vals[hi] * f


def f6(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.6f}"


def fail_signature(sub_status: dict[str, str]) -> str:
    failed = [g for g in SUBGATES if sub_status.get(g, "").lower() != "pass"]
    return "+".join(failed) if failed else "NONE"


def summarize_fail_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    out = {g: 0 for g in SUBGATES}
    for row in rows:
        for g in SUBGATES:
            if row.get(f"{g.lower()}_status", "").lower() != "pass":
                out[g] += 1
    return out


def group_count(rows: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, "")).strip()
        counts[value] = counts.get(value, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def mean_of(rows: list[dict[str, Any]], key: str) -> float:
    vals = []
    for row in rows:
        v = to_float(str(row.get(key, "")))
        if v is not None:
            vals.append(v)
    return statistics.mean(vals) if vals else float("nan")


def write_report(
    path: Path,
    *,
    all_rows: list[dict[str, Any]],
    fail_rows: list[dict[str, Any]],
    pass_rows: list[dict[str, Any]],
    fail_counts: dict[str, int],
    top_patterns: int,
) -> None:
    lines: list[str] = []
    lines.append("# G16 Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- profiles_total: `{len(all_rows)}`")
    lines.append(f"- g16_fail: `{len(fail_rows)}`")
    lines.append(f"- g16_pass: `{len(pass_rows)}`")
    lines.append("- thresholds/formulas: unchanged (diagnostic-only run)")
    lines.append("")
    lines.append("## Sub-Gate Failure Counts")
    lines.append("")
    lines.append("| subgate | fail_count |")
    lines.append("| --- | --- |")
    for g in SUBGATES:
        lines.append(f"| {g} | {fail_counts[g]} |")
    lines.append("")

    lines.append("## Failure Signatures")
    lines.append("")
    lines.append("| signature | count |")
    lines.append("| --- | --- |")
    for sig, cnt in group_count(fail_rows, "fail_signature")[:top_patterns]:
        lines.append(f"| {sig} | {cnt} |")
    lines.append("")

    lines.append("## Dataset Fail Split")
    lines.append("")
    lines.append("| dataset | fail_count | pass_count | fail_rate |")
    lines.append("| --- | --- | --- | --- |")
    by_ds_fail = dict(group_count(fail_rows, "dataset_id"))
    by_ds_pass = dict(group_count(pass_rows, "dataset_id"))
    for ds in sorted(set(list(by_ds_fail.keys()) + list(by_ds_pass.keys()))):
        fcnt = by_ds_fail.get(ds, 0)
        pcnt = by_ds_pass.get(ds, 0)
        denom = fcnt + pcnt
        rate = (fcnt / float(denom)) if denom else float("nan")
        lines.append(f"| {ds} | {fcnt} | {pcnt} | {f6(rate)} |")
    lines.append("")

    lines.append("## Pass vs Fail Feature Means")
    lines.append("")
    lines.append("| feature | fail_mean | pass_mean |")
    lines.append("| --- | --- | --- |")
    for feature in [
        "mean_degree",
        "sigma_std",
        "sigma_cv",
        "peak2_to_peak1",
        "peak12_distance_norm",
        "closure_rel",
        "r2_G11_T11",
        "m_sq_abs",
        "hessian_frac_neg",
    ]:
        lines.append(f"| {feature} | {f6(mean_of(fail_rows, feature))} | {f6(mean_of(pass_rows, feature))} |")
    lines.append("")

    lines.append("## Pattern Notes")
    lines.append("")
    pattern_rows = group_count(fail_rows, "fail_signature")[:top_patterns]
    if not pattern_rows:
        lines.append("- No G16 failures in analyzed profiles.")
    else:
        for idx, (sig, cnt) in enumerate(pattern_rows, start=1):
            sample = [r for r in fail_rows if r.get("fail_signature") == sig][:2]
            example = ", ".join(f"{r['dataset_id']}/seed{r['seed']}" for r in sample) if sample else "n/a"
            lines.append(f"{idx}. `{sig}` occurs `{cnt}` times; examples: `{example}`.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    runs_root = out_dir / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    runs_root.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        print(f"[error] summary CSV not found: {summary_csv}")
        return 2

    profiles = parse_profiles(read_csv(summary_csv))
    if args.max_profiles > 0:
        profiles = profiles[: args.max_profiles]

    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 72)
    log("G16 failure taxonomy v1")
    log(f"start_utc={datetime.utcnow().isoformat()}Z")
    log(f"profiles={len(profiles)}")
    log("=" * 72)

    rows: list[dict[str, Any]] = []
    for idx, profile in enumerate(profiles, start=1):
        prof_dir = runs_root / profile.tag / "g16"
        prof_dir.mkdir(parents=True, exist_ok=True)
        metric_csv = prof_dir / ACTION_METRIC_CSV
        config_json = prof_dir / ACTION_CONFIG_JSON

        log(f"[{idx}/{len(profiles)}] {profile.tag}")
        if not (args.reuse_existing and metric_csv.exists() and config_json.exists()):
            rc, tail = run_action(profile, prof_dir)
            log(f"  run_action rc={rc}")
            if rc != 0 and tail:
                log("  tail:")
                for line in tail.splitlines():
                    log(f"    {line}")

        metric_rows = read_metric_checks(metric_csv)
        metrics = parse_metric_checks(metric_rows)
        cfg = {}
        if config_json.exists():
            cfg = __import__("json").loads(config_json.read_text(encoding="utf-8"))

        sub_status = {g: metrics.get(g, {}).get("status", "").strip().lower() for g in SUBGATES}
        final_status = metrics.get("FINAL", {}).get("status", "").strip().lower()
        if not final_status:
            final_status = "fail"

        features = sigma_features(
            profile.dataset_id,
            profile.seed,
            peak_ratio_threshold=args.peak_ratio_threshold,
            peak_distance_threshold=args.peak_distance_threshold,
        )

        row: dict[str, Any] = {
            "dataset_id": profile.dataset_id,
            "seed": profile.seed,
            "phi_scale": profile.phi_scale,
            "g16_status": final_status,
            "g16a_status": sub_status["G16a"],
            "g16b_status": sub_status["G16b"],
            "g16c_status": sub_status["G16c"],
            "g16d_status": sub_status["G16d"],
            "fail_signature": fail_signature(sub_status),
            "closure_rel": metrics.get("G16a", {}).get("value", ""),
            "r2_G11_T11": metrics.get("G16b", {}).get("value", ""),
            "m_sq_abs": metrics.get("G16c", {}).get("value", ""),
            "hessian_frac_neg": metrics.get("G16d", {}).get("value", ""),
            "n_nodes": cfg.get("n_nodes", features["n_nodes"]),
            "mean_degree": f6(to_float(str(cfg.get("mean_degree", ""))) or features["mean_degree"]),
            "sigma_mean": f6(features["sigma_mean"]),
            "sigma_std": f6(features["sigma_std"]),
            "sigma_cv": f6(features["sigma_cv"]),
            "sigma_p90": f6(features["sigma_p90"]),
            "sigma_p10": f6(features["sigma_p10"]),
            "peak1_sigma": f6(features["peak1_sigma"]),
            "peak2_sigma": f6(features["peak2_sigma"]),
            "peak2_to_peak1": f6(features["peak2_to_peak1"]),
            "peak12_distance": f6(features["peak12_distance"]),
            "peak12_distance_norm": f6(features["peak12_distance_norm"]),
            "multi_peak_flag_default": features["multi_peak_flag_default"],
            "g11_status": profile.source_row.get("g11_status", ""),
            "g12_status": profile.source_row.get("g12_status", ""),
            "g13_status": profile.source_row.get("g13_status", ""),
            "g14_status": profile.source_row.get("g14_status", ""),
            "g15_status": profile.source_row.get("g15_status", ""),
            "g15b_v2_status": profile.source_row.get("g15b_v2_status", ""),
            "all_pass_official": profile.source_row.get("all_pass_official", ""),
            "all_pass_diagnostic": profile.source_row.get("all_pass_diagnostic", profile.source_row.get("all_pass", "")),
            "source_run_root": profile.source_row.get("run_root", ""),
            "action_run_root": (prof_dir.resolve().relative_to(ROOT.resolve())).as_posix(),
        }
        rows.append(row)

    fail_rows = [r for r in rows if r.get("g16_status", "").lower() != "pass"]
    pass_rows = [r for r in rows if r.get("g16_status", "").lower() == "pass"]
    fail_counts = summarize_fail_counts(fail_rows)

    fieldnames = [
        "dataset_id",
        "seed",
        "phi_scale",
        "g16_status",
        "g16a_status",
        "g16b_status",
        "g16c_status",
        "g16d_status",
        "fail_signature",
        "closure_rel",
        "r2_G11_T11",
        "m_sq_abs",
        "hessian_frac_neg",
        "n_nodes",
        "mean_degree",
        "sigma_mean",
        "sigma_std",
        "sigma_cv",
        "sigma_p90",
        "sigma_p10",
        "peak1_sigma",
        "peak2_sigma",
        "peak2_to_peak1",
        "peak12_distance",
        "peak12_distance_norm",
        "multi_peak_flag_default",
        "g11_status",
        "g12_status",
        "g13_status",
        "g14_status",
        "g15_status",
        "g15b_v2_status",
        "all_pass_official",
        "all_pass_diagnostic",
        "source_run_root",
        "action_run_root",
    ]

    fail_csv = out_dir / "g16_fail_cases.csv"
    pass_csv = out_dir / "g16_pass_cases.csv"
    write_csv(fail_csv, fail_rows, fieldnames)
    write_csv(pass_csv, pass_rows, fieldnames)

    report_md = out_dir / "g16_failure_taxonomy.md"
    write_report(
        report_md,
        all_rows=rows,
        fail_rows=fail_rows,
        pass_rows=pass_rows,
        fail_counts=fail_counts,
        top_patterns=max(1, args.top_patterns),
    )

    run_log = out_dir / "run-log-g16-taxonomy.txt"
    run_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"g16_fail_cases: {fail_csv}")
    print(f"g16_pass_cases: {pass_csv}")
    print(f"taxonomy_md:    {report_md}")
    print(f"run_log:        {run_log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

