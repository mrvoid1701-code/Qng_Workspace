#!/usr/bin/env python3
"""
Run G17 candidate-v2 hybrid evaluation on frozen QM lane summaries.

Policy (diagnostic/governance layer):
- keep G17-v1 unchanged (legacy baseline)
- preserve all existing gate formulas/thresholds in runners
- use robust hybrid for G17a only:
  - if G17a-v1 passes -> keep pass
  - if G17a-v1 fails and multi-peak mixing is detected:
    evaluate local basin gap and apply same gap threshold (0.01)
  - else keep fail
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import random
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import run_qng_qm_bridge_v1 as g17v1  # noqa: E402


DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-g17-candidate-v2"
    / "primary_ds002_003_006_s3401_3600"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G17 candidate-v2 hybrid evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--mix-ratio-threshold", type=float, default=0.90)
    p.add_argument("--mix-distance-threshold", type=float, default=0.25)
    p.add_argument("--basin-quantile", type=float, default=0.15)
    p.add_argument("--local-gap-threshold", type=float, default=0.01)
    p.add_argument("--local-gap-max-modes", type=int, default=12)
    p.add_argument("--local-gap-iters", type=int, default=300)
    return p.parse_args()


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def parse_float(v: str, default: float = 0.0) -> float:
    try:
        return float(str(v).strip())
    except Exception:
        return default


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def resolve_run_root(raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    return (ROOT / raw).resolve()


def parse_g17_metric_checks(path: Path) -> dict[str, Any]:
    rows = read_csv(path)
    by_gate: dict[str, dict[str, str]] = {}
    for r in rows:
        gid = (r.get("gate_id") or "").strip()
        if gid:
            by_gate[gid] = r
    return {
        "g17a_status_v1": norm_status(by_gate.get("G17a", {}).get("status", "")),
        "g17b_status": norm_status(by_gate.get("G17b", {}).get("status", "")),
        "g17c_status": norm_status(by_gate.get("G17c", {}).get("status", "")),
        "g17d_status": norm_status(by_gate.get("G17d", {}).get("status", "")),
        "g17_status_v1": norm_status(by_gate.get("FINAL", {}).get("status", "")),
        "g17a_gap_global": parse_float(by_gate.get("G17a", {}).get("value", "0")),
        "g17b_slope": parse_float(by_gate.get("G17b", {}).get("value", "0")),
        "g17c_e0_per_mode": parse_float(by_gate.get("G17c", {}).get("value", "0")),
        "g17d_heisenberg_dev": parse_float(by_gate.get("G17d", {}).get("value", "0")),
    }


def induced_largest_component(neighbours: list[list[int]], node_ids: list[int]) -> list[list[int]]:
    node_set = set(node_ids)
    map_idx = {old: i for i, old in enumerate(node_ids)}
    sub = [[] for _ in node_ids]
    for old in node_ids:
        i = map_idx[old]
        for nb in neighbours[old]:
            if nb in node_set:
                sub[i].append(map_idx[nb])

    # keep largest connected component to avoid isolated-node artifacts
    n = len(sub)
    seen = [False] * n
    best: list[int] = []
    for i in range(n):
        if seen[i]:
            continue
        stack = [i]
        seen[i] = True
        comp: list[int] = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in sub[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        if len(comp) > len(best):
            best = comp

    if not best:
        return []
    keep = set(best)
    remap = {old: i for i, old in enumerate(sorted(best))}
    out = [[] for _ in range(len(best))]
    for old in sorted(best):
        i = remap[old]
        out[i] = [remap[v] for v in sub[old] if v in keep]
    return out


def compute_multi_peak_and_local_gap(
    dataset_id: str,
    seed: int,
    basin_quantile: float,
    mix_ratio_threshold: float,
    mix_distance_threshold: float,
    local_gap_max_modes: int,
    local_gap_iters: int,
) -> dict[str, Any]:
    coords, sigma, neighbours = g17v1.build_dataset_graph(dataset_id, seed)
    n = len(sigma)
    idx = sorted(range(n), key=lambda i: sigma[i], reverse=True)
    i1 = idx[0]
    i2 = idx[1] if n > 1 else i1
    p1 = sigma[i1]
    p2 = sigma[i2]
    ratio = (p2 / p1) if p1 > 1e-12 else 0.0
    d12 = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
    d12_norm = d12 / diag if diag > 1e-12 else 0.0
    mixing = (ratio >= mix_ratio_threshold) and (d12_norm <= mix_distance_threshold)

    # primary basin = top-q sigma nodes
    qn = max(8, int(round(basin_quantile * n)))
    basin_ids = idx[:qn]
    local_neighbours = induced_largest_component(neighbours, basin_ids)
    local_n = len(local_neighbours)
    local_gap = 0.0
    if local_n >= 3:
        n_modes = max(3, min(local_gap_max_modes, local_n))
        rng = random.Random(seed + 991)
        mus, _ = g17v1.compute_eigenmodes(local_neighbours, n_modes, local_gap_iters, rng)
        if len(mus) > 1:
            local_gap = max(0.0, float(mus[1]))

    return {
        "sigma_peak2_to_peak1": ratio,
        "peak12_distance_norm": d12_norm,
        "multi_peak_mixing": "true" if mixing else "false",
        "local_basin_nodes": local_n,
        "g17a_gap_local": local_gap,
    }


def summarize_by_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g17_v1_pass": sum(1 for r in sub if r["g17_status_v1"] == "pass"),
                "g17_v2_pass": sum(1 for r in sub if r["g17_status_v2"] == "pass"),
                "qm_lane_v1_pass": sum(1 for r in sub if r["all_pass_qm_lane_v1"] == "pass"),
                "qm_lane_v2_pass": sum(1 for r in sub if r["all_pass_qm_lane_v2"] == "pass"),
                "improved_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass"
                ),
                "degraded_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail"
                ),
                "improved_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
                ),
                "degraded_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
                ),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    source_summary = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source_summary.exists():
        raise FileNotFoundError(f"source summary not found: {source_summary}")

    source_rows = read_csv(source_summary)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for srow in source_rows:
        dataset_id = str(srow.get("dataset_id", ""))
        seed = int(str(srow.get("seed", "0")))
        run_root = resolve_run_root(str(srow.get("run_root", "")))
        g17_dir = run_root / "g17"
        mc_csv = g17_dir / "metric_checks_qm.csv"
        if not mc_csv.exists():
            raise FileNotFoundError(f"missing g17 metric file: {mc_csv}")

        base = parse_g17_metric_checks(mc_csv)
        feats = compute_multi_peak_and_local_gap(
            dataset_id=dataset_id,
            seed=seed,
            basin_quantile=args.basin_quantile,
            mix_ratio_threshold=args.mix_ratio_threshold,
            mix_distance_threshold=args.mix_distance_threshold,
            local_gap_max_modes=args.local_gap_max_modes,
            local_gap_iters=args.local_gap_iters,
        )

        # Hybrid G17a-v2 policy with explicit non-degradation guard.
        g17a_v1 = base["g17a_status_v1"]
        if g17a_v1 == "pass":
            g17a_v2 = "pass"
            g17a_v2_rule = "accept_v1_pass"
        else:
            mixing = feats["multi_peak_mixing"] == "true"
            if mixing and feats["g17a_gap_local"] > args.local_gap_threshold:
                g17a_v2 = "pass"
                g17a_v2_rule = "local_gap_recovery"
            else:
                g17a_v2 = "fail"
                g17a_v2_rule = "retain_v1_fail"

        g17_v2 = (
            "pass"
            if g17a_v2 == "pass"
            and base["g17b_status"] == "pass"
            and base["g17c_status"] == "pass"
            and base["g17d_status"] == "pass"
            else "fail"
        )

        g18 = norm_status(srow.get("g18_status", ""))
        g19 = norm_status(srow.get("g19_status", ""))
        g20 = norm_status(srow.get("g20_status", ""))
        lane_v1 = norm_status(srow.get("all_pass_qm_lane", ""))
        lane_v2 = "pass" if (g17_v2 == "pass" and g18 == "pass" and g19 == "pass" and g20 == "pass") else "fail"

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": run_root.resolve().relative_to(ROOT.resolve()).as_posix(),
                "g17_status_v1": base["g17_status_v1"],
                "g17_status_v2": g17_v2,
                "g17a_status_v1": g17a_v1,
                "g17a_status_v2": g17a_v2,
                "g17a_v2_rule": g17a_v2_rule,
                "g17b_status": base["g17b_status"],
                "g17c_status": base["g17c_status"],
                "g17d_status": base["g17d_status"],
                "g17a_gap_global": base["g17a_gap_global"],
                "g17a_gap_local": feats["g17a_gap_local"],
                "sigma_peak2_to_peak1": feats["sigma_peak2_to_peak1"],
                "peak12_distance_norm": feats["peak12_distance_norm"],
                "multi_peak_mixing": feats["multi_peak_mixing"],
                "local_basin_nodes": feats["local_basin_nodes"],
                "g17b_slope": base["g17b_slope"],
                "g17c_e0_per_mode": base["g17c_e0_per_mode"],
                "g17d_heisenberg_dev": base["g17d_heisenberg_dev"],
                "g18_status": g18,
                "g19_status": g19,
                "g20_status": g20,
                "all_pass_qm_lane_v1": lane_v1,
                "all_pass_qm_lane_v2": lane_v2,
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g17_v1_pass = sum(1 for r in out_rows if r["g17_status_v1"] == "pass")
    g17_v2_pass = sum(1 for r in out_rows if r["g17_status_v2"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v2_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v2"] == "pass")
    improved_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass")
    degraded_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
    )

    report_lines = [
        "# QM G17 Candidate-v2 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G17 v1 -> v2: `{g17_v1_pass}/{n} -> {g17_v2_pass}/{n}`",
        f"- QM lane v1 -> v2: `{lane_v1_pass}/{n} -> {lane_v2_pass}/{n}`",
        f"- improved_g17: `{improved_g17}`",
        f"- degraded_g17: `{degraded_g17}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- G17a-v1 global-gap diagnostic is treated as valid in single-well/single-peak regimes.",
        "- G17-v2 preserves v1 behavior in that regime and applies local-gap recovery only under multi-peak mixing.",
        "- No threshold tuning was applied in core runners; this is an observable-definition hardening at governance layer.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g17-candidate-v2-hybrid",
        "mix_ratio_threshold": args.mix_ratio_threshold,
        "mix_distance_threshold": args.mix_distance_threshold,
        "basin_quantile": args.basin_quantile,
        "local_gap_threshold": args.local_gap_threshold,
        "local_gap_max_modes": args.local_gap_max_modes,
        "local_gap_iters": args.local_gap_iters,
        "notes": [
            "Hybrid uses G17a local gap only under multi-peak mixing signature.",
            "No threshold/formula edits in core gate scripts.",
        ],
    }
    manifest_json = out_dir / "candidate_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
