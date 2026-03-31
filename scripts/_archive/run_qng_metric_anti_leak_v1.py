#!/usr/bin/env python3
"""
QNG metric anti-leak controls (v1).

Adds non-prereg supplementary controls for QNG-T-METRIC-003:
- label permutation control (existing D4-style)
- graph rewire control (degree-preserving edge rewiring)
- graph rewire + label permutation control
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import platform
import random
import sys
import time

import run_qng_metric_hardening_v3 as v3


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-metric-anti-leak-v1"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def edge_list_from_adj(adj: list[list[tuple[int, float]]]) -> tuple[list[tuple[int, int]], list[float]]:
    edges: list[tuple[int, int]] = []
    weights: list[float] = []
    seen = set()
    for i, row in enumerate(adj):
        for j, w in row:
            if i == j:
                continue
            a, b = (i, j) if i < j else (j, i)
            if (a, b) in seen:
                continue
            seen.add((a, b))
            edges.append((a, b))
            weights.append(float(w))
    return edges, weights


def adj_from_edges(n: int, edges: list[tuple[int, int]], weights: list[float]) -> list[list[tuple[int, float]]]:
    out = [[] for _ in range(n)]
    for (a, b), w in zip(edges, weights):
        out[a].append((b, w))
        out[b].append((a, w))
    return out


def degree_preserving_rewire(
    adj: list[list[tuple[int, float]]],
    rng: random.Random,
    swap_factor: int = 6,
) -> list[list[tuple[int, float]]]:
    n = len(adj)
    edges, weights = edge_list_from_adj(adj)
    m = len(edges)
    if m < 4:
        return adj

    edge_set = set(edges)
    swaps_target = max(8, swap_factor * m)
    attempts = 0
    swaps = 0
    max_attempts = swaps_target * 30

    while swaps < swaps_target and attempts < max_attempts:
        attempts += 1
        i = rng.randrange(m)
        j = rng.randrange(m)
        if i == j:
            continue
        a, b = edges[i]
        c, d = edges[j]
        if len({a, b, c, d}) < 4:
            continue

        # Two equivalent switchings; pick one randomly.
        if rng.random() < 0.5:
            n1 = (a, d) if a < d else (d, a)
            n2 = (c, b) if c < b else (b, c)
        else:
            n1 = (a, c) if a < c else (c, a)
            n2 = (d, b) if d < b else (b, d)

        if n1[0] == n1[1] or n2[0] == n2[1]:
            continue
        if n1 in edge_set or n2 in edge_set:
            continue

        edge_set.remove(edges[i])
        edge_set.remove(edges[j])
        edge_set.add(n1)
        edge_set.add(n2)
        edges[i] = n1
        edges[j] = n2
        swaps += 1

    shuffled_weights = weights[:]
    rng.shuffle(shuffled_weights)
    return adj_from_edges(n, edges, shuffled_weights)


def has_inf(dmat: list[list[float]]) -> bool:
    for row in dmat:
        for x in row:
            if not math.isfinite(x):
                return True
    return False


def evaluate_alignment(
    adj: list[list[tuple[int, float]]],
    sigma: list[float],
    samples: int,
    seed: int,
    label_shuffle: bool,
) -> tuple[float, float, int]:
    anchors = v3.choose_anchors(sigma, samples, seed)
    rng = random.Random(seed + 5003)
    cos_vals: list[float] = []
    used = 0

    for anchor in anchors:
        d_anchor = v3.dijkstra(adj, anchor)
        local_nodes = v3.local_nodes_from_anchor(d_anchor, anchor, m=20)
        if len(local_nodes) < 12:
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]
        d_local = v3.local_pairwise_distances(adj, local_nodes)
        if has_inf(d_local):
            continue
        chart = v3.geodesic_tangent_chart(d_local)
        if chart is None:
            continue

        sigma_local = [sigma[n] for n in local_nodes]
        sigma_raw_s0 = v3.smooth_sigma_local(d_local, sigma_local, 1.0)
        gh_raw = v3.estimate_sigma_grad_hessian(chart, sigma_raw_s0)
        if gh_raw is None:
            continue
        grad_raw, _hraw = gh_raw
        a_raw = (-grad_raw[0], -grad_raw[1])

        sigma_work = sigma_local[:]
        if label_shuffle:
            rng.shuffle(sigma_work)
        sigma_work_s0 = v3.smooth_sigma_local(d_local, sigma_work, 1.0)
        gh = v3.estimate_sigma_grad_hessian(chart, sigma_work_s0)
        if gh is None:
            continue
        grad, hess = gh
        g = v3.metric_from_sigma_hessian(hess[0], hess[1], hess[2], floor=1e-6, anisotropy_keep=0.4)
        inv = v3.inv2x2(*g)
        if inv is None:
            continue
        i11, i12, i22 = inv
        a_metric = (-(i11 * grad[0] + i12 * grad[1]), -(i12 * grad[0] + i22 * grad[1]))
        c = v3.cosine(a_metric, a_raw)
        if math.isfinite(c):
            cos_vals.append(c)
            used += 1

    med = v3.median(cos_vals) if cos_vals else float("nan")
    p10 = v3.percentile10(cos_vals) if cos_vals else float("nan")
    return med, p10, used


def evaluate_rewire_against_base(
    base_adj: list[list[tuple[int, float]]],
    test_adj: list[list[tuple[int, float]]],
    sigma: list[float],
    samples: int,
    seed: int,
    label_shuffle: bool,
) -> tuple[float, float, int]:
    anchors = v3.choose_anchors(sigma, samples, seed)
    rng = random.Random(seed + 8009)
    cos_vals: list[float] = []
    used = 0

    for anchor in anchors:
        d_anchor_base = v3.dijkstra(base_adj, anchor)
        local_nodes = v3.local_nodes_from_anchor(d_anchor_base, anchor, m=20)
        if len(local_nodes) < 12:
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]

        # Raw reference is anchored on original/base graph.
        d_local_base = v3.local_pairwise_distances(base_adj, local_nodes)
        if has_inf(d_local_base):
            continue
        chart_base = v3.geodesic_tangent_chart(d_local_base)
        if chart_base is None:
            continue
        sigma_local = [sigma[n] for n in local_nodes]
        sigma_base_s0 = v3.smooth_sigma_local(d_local_base, sigma_local, 1.0)
        gh_base = v3.estimate_sigma_grad_hessian(chart_base, sigma_base_s0)
        if gh_base is None:
            continue
        grad_base, _hbase = gh_base
        a_raw_base = (-grad_base[0], -grad_base[1])

        # Metric-driven direction is extracted on rewired graph for same node subset.
        d_local_test = v3.local_pairwise_distances(test_adj, local_nodes)
        if has_inf(d_local_test):
            continue
        chart_test = v3.geodesic_tangent_chart(d_local_test)
        if chart_test is None:
            continue

        sigma_work = sigma_local[:]
        if label_shuffle:
            rng.shuffle(sigma_work)
        sigma_test_s0 = v3.smooth_sigma_local(d_local_test, sigma_work, 1.0)
        gh_test = v3.estimate_sigma_grad_hessian(chart_test, sigma_test_s0)
        if gh_test is None:
            continue
        grad_test, hess_test = gh_test
        g = v3.metric_from_sigma_hessian(
            hess_test[0], hess_test[1], hess_test[2], floor=1e-6, anisotropy_keep=0.4
        )
        inv = v3.inv2x2(*g)
        if inv is None:
            continue
        i11, i12, i22 = inv
        a_metric = (-(i11 * grad_test[0] + i12 * grad_test[1]), -(i12 * grad_test[0] + i22 * grad_test[1]))
        c = v3.cosine(a_metric, a_raw_base)
        if math.isfinite(c):
            cos_vals.append(c)
            used += 1

    med = v3.median(cos_vals) if cos_vals else float("nan")
    p10 = v3.percentile10(cos_vals) if cos_vals else float("nan")
    return med, p10, used


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG metric anti-leak controls v1.")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--rewire-runs", type=int, default=12)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.rewire_runs < 4:
        print("Error: --rewire-runs must be >= 4", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()

    coords, sigma, adj, med_edge = v3.build_dataset_graph(args.dataset_id, args.seed)
    adj_norm = [[(j, w / med_edge) for j, w in row] for row in adj]

    pos_med, pos_p10, pos_n = evaluate_alignment(adj_norm, sigma, args.samples, args.seed, label_shuffle=False)
    lbl_med, lbl_p10, lbl_n = evaluate_alignment(adj_norm, sigma, args.samples, args.seed + 1, label_shuffle=True)

    rewire_rows: list[dict[str, str]] = []
    rewire_meds: list[float] = []
    rewire_lbl_meds: list[float] = []
    base_rng = random.Random(args.seed + 17001)
    for run_idx in range(args.rewire_runs):
        rrng = random.Random(base_rng.randrange(10**9))
        adj_rw = degree_preserving_rewire(adj_norm, rrng, swap_factor=6)
        med_rw, p10_rw, n_rw = evaluate_rewire_against_base(
            adj_norm,
            adj_rw,
            sigma,
            args.samples,
            args.seed + 100 + run_idx,
            label_shuffle=False,
        )
        med_rw_lbl, p10_rw_lbl, n_rw_lbl = evaluate_rewire_against_base(
            adj_norm,
            adj_rw,
            sigma,
            args.samples,
            args.seed + 200 + run_idx,
            label_shuffle=True,
        )
        if math.isfinite(med_rw):
            rewire_meds.append(med_rw)
        if math.isfinite(med_rw_lbl):
            rewire_lbl_meds.append(med_rw_lbl)
        rewire_rows.append(
            {
                "run_id": str(run_idx + 1),
                "median_cos_rewire": fmt(med_rw),
                "p10_cos_rewire": fmt(p10_rw),
                "anchors_used_rewire": str(n_rw),
                "median_cos_rewire_shuffled": fmt(med_rw_lbl),
                "p10_cos_rewire_shuffled": fmt(p10_rw_lbl),
                "anchors_used_rewire_shuffled": str(n_rw_lbl),
            }
        )

    rewire_med = v3.median(rewire_meds) if rewire_meds else float("nan")
    rewire_lbl_med = v3.median(rewire_lbl_meds) if rewire_lbl_meds else float("nan")

    # supplementary control thresholds (informative, not replacing D1-D4 prereg)
    ctrl_threshold = 0.55
    pass_label_perm = math.isfinite(lbl_med) and (lbl_med < ctrl_threshold)
    pass_rewire = math.isfinite(rewire_med) and (rewire_med < ctrl_threshold)
    pass_rewire_lbl = math.isfinite(rewire_lbl_med) and (rewire_lbl_med < ctrl_threshold)
    pass_all = pass_label_perm and pass_rewire and pass_rewire_lbl

    summary_rows = [
        {"metric": "dataset_id", "value": args.dataset_id},
        {"metric": "seed", "value": str(args.seed)},
        {"metric": "samples", "value": str(args.samples)},
        {"metric": "rewire_runs", "value": str(args.rewire_runs)},
        {"metric": "positive_median_cos", "value": fmt(pos_med)},
        {"metric": "positive_p10_cos", "value": fmt(pos_p10)},
        {"metric": "positive_anchors_used", "value": str(pos_n)},
        {"metric": "label_perm_median_cos", "value": fmt(lbl_med)},
        {"metric": "label_perm_p10_cos", "value": fmt(lbl_p10)},
        {"metric": "label_perm_anchors_used", "value": str(lbl_n)},
        {"metric": "rewire_median_of_medians", "value": fmt(rewire_med)},
        {"metric": "rewire_shuffled_median_of_medians", "value": fmt(rewire_lbl_med)},
        {"metric": "control_threshold", "value": fmt(ctrl_threshold)},
        {"metric": "rule_pass_label_permutation", "value": str(pass_label_perm)},
        {"metric": "rule_pass_graph_rewire", "value": str(pass_rewire)},
        {"metric": "rule_pass_graph_rewire_shuffled", "value": str(pass_rewire_lbl)},
        {"metric": "overall_pass", "value": str(pass_all)},
    ]

    write_csv(out_dir / "control_summary.csv", ["metric", "value"], summary_rows)
    write_csv(
        out_dir / "rewire_runs.csv",
        [
            "run_id",
            "median_cos_rewire",
            "p10_cos_rewire",
            "anchors_used_rewire",
            "median_cos_rewire_shuffled",
            "p10_cos_rewire_shuffled",
            "anchors_used_rewire_shuffled",
        ],
        rewire_rows,
    )

    config_payload = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "samples": args.samples,
        "rewire_runs": args.rewire_runs,
        "control_threshold": ctrl_threshold,
        "metric_lock_dependency": "01_notes/metric/metric-lock-v3.md",
        "base_prereg_dependency": "05_validation/pre-registrations/qng-metric-hardening-v3.md",
    }
    (out_dir / "config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    hash_targets = [
        out_dir / "control_summary.csv",
        out_dir / "rewire_runs.csv",
        out_dir / "config.json",
    ]
    hashes = {p.name: sha256_of(p) for p in hash_targets if p.exists()}
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started
    run_log = [
        "QNG metric anti-leak controls v1 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"seed: {args.seed}",
        f"samples: {args.samples}",
        f"rewire_runs: {args.rewire_runs}",
        f"duration_seconds: {duration:.3f}",
        f"overall_pass: {pass_all}",
        "artifact_hashes_sha256:",
    ]
    for k, v in hashes.items():
        run_log.append(f"- {k}: {v}")
    (out_dir / "run-log.txt").write_text("\n".join(run_log), encoding="utf-8")

    print(
        "QNG metric anti-leak v1 completed: "
        f"overall_pass={pass_all} "
        f"label_perm_pass={pass_label_perm} "
        f"rewire_pass={pass_rewire} "
        f"rewire_shuffle_pass={pass_rewire_lbl}"
    )
    print(f"Artifacts: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
