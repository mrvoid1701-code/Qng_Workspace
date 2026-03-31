#!/usr/bin/env python3
"""Compare legacy 2D gate summary against consolidated 4D official summary (G10..G18)."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"

DEFAULT_LEGACY_GATES_CSV = ROOT / "gates_summary.csv"
DEFAULT_LANE4D_GATE_CSV = ART / "qng-4d-official-summary-v1" / "gate_summary_4d.csv"
DEFAULT_LANE4D_METRIC_CSV = ART / "qng-4d-official-summary-v1" / "metric_summary_4d.csv"
DEFAULT_OUT_DIR = ART / "qng-2d-vs-4d-comparator-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare QNG 2D legacy vs 4D official (G10..G18).")
    p.add_argument("--legacy-gates-csv", default=str(DEFAULT_LEGACY_GATES_CSV))
    p.add_argument("--lane4d-gate-csv", default=str(DEFAULT_LANE4D_GATE_CSV))
    p.add_argument("--lane4d-metric-csv", default=str(DEFAULT_LANE4D_METRIC_CSV))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
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


def gate_num(gate_id: str) -> int:
    m = re.match(r"^G(\d+)", gate_id)
    return int(m.group(1)) if m else 999


def norm_status(v: str) -> str:
    t = (v or "").strip().lower()
    if t in {"pass", "true", "1", "ok"}:
        return "pass"
    return "fail"


def to_float(x: str) -> float | None:
    try:
        return float((x or "").strip())
    except Exception:
        return None


def main() -> int:
    args = parse_args()

    legacy_gates_csv = Path(args.legacy_gates_csv).resolve()
    lane4d_gate_csv = Path(args.lane4d_gate_csv).resolve()
    lane4d_metric_csv = Path(args.lane4d_metric_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in (legacy_gates_csv, lane4d_gate_csv, lane4d_metric_csv):
        if not p.exists():
            raise FileNotFoundError(f"missing required input: {p}")

    legacy_rows = read_csv(legacy_gates_csv)
    lane4d_gate_rows = read_csv(lane4d_gate_csv)
    lane4d_metric_rows = read_csv(lane4d_metric_csv)

    legacy_gate_decision: dict[str, str] = {}
    legacy_metric_map: dict[str, dict[str, str]] = {}
    for r in legacy_rows:
        gate_id = str(r.get("gate_id", "")).strip()
        if gate_num(gate_id) > 18:
            continue
        # Gate decision from any row for this gate.
        if gate_id and gate_id not in legacy_gate_decision:
            legacy_gate_decision[gate_id] = norm_status(str(r.get("gate_decision", "")))
        subgate = str(r.get("sub_gate", "")).strip()
        if subgate:
            legacy_metric_map[subgate] = {
                "gate_id": gate_id,
                "metric": str(r.get("metric", "")).strip(),
                "value": str(r.get("value", "")).strip(),
                "threshold": str(r.get("threshold", "")).strip(),
                "status": norm_status(str(r.get("status", ""))),
                "source": str(legacy_gates_csv),
            }

    lane4d_gate_decision: dict[str, str] = {}
    for r in lane4d_gate_rows:
        gate_id = str(r.get("gate_id", "")).strip()
        if gate_id:
            lane4d_gate_decision[gate_id] = norm_status(str(r.get("gate_decision", "")))

    lane4d_metric_map: dict[str, dict[str, str]] = {}
    for r in lane4d_metric_rows:
        subgate = str(r.get("subgate_id", "")).strip()
        if not subgate:
            continue
        lane4d_metric_map[subgate] = {
            "gate_id": str(r.get("gate_id", "")).strip(),
            "metric": str(r.get("metric", "")).strip(),
            "value": str(r.get("value", "")).strip(),
            "threshold": str(r.get("threshold", "")).strip(),
            "status": norm_status(str(r.get("status", ""))),
            "source": str(r.get("source_file", "")).strip(),
        }

    all_gates = sorted(set(legacy_gate_decision) | set(lane4d_gate_decision), key=gate_num)
    gate_cmp_rows: list[dict[str, Any]] = []
    for gate_id in all_gates:
        d2 = legacy_gate_decision.get(gate_id, "missing")
        d4 = lane4d_gate_decision.get(gate_id, "missing")
        gate_cmp_rows.append(
            {
                "gate_id": gate_id,
                "decision_2d_legacy": d2,
                "decision_4d_official": d4,
                "changed": "yes" if d2 != d4 else "no",
            }
        )

    subgate_overlap = sorted(set(legacy_metric_map) & set(lane4d_metric_map), key=lambda s: (gate_num(s), s))
    metric_cmp_rows: list[dict[str, Any]] = []
    for subgate in subgate_overlap:
        m2 = legacy_metric_map[subgate]
        m4 = lane4d_metric_map[subgate]
        v2 = to_float(m2["value"])
        v4 = to_float(m4["value"])
        delta = ""
        if v2 is not None and v4 is not None:
            delta = f"{(v4 - v2):.6g}"
        metric_cmp_rows.append(
            {
                "gate_id": m4["gate_id"] or m2["gate_id"],
                "subgate_id": subgate,
                "metric_2d": m2["metric"],
                "metric_4d": m4["metric"],
                "value_2d": m2["value"],
                "value_4d": m4["value"],
                "delta_4d_minus_2d": delta,
                "threshold_2d": m2["threshold"],
                "threshold_4d": m4["threshold"],
                "status_2d": m2["status"],
                "status_4d": m4["status"],
                "source_2d": m2["source"],
                "source_4d": m4["source"],
            }
        )

    write_csv(
        out_dir / "gate_comparison.csv",
        gate_cmp_rows,
        ["gate_id", "decision_2d_legacy", "decision_4d_official", "changed"],
    )
    write_csv(
        out_dir / "metric_comparison.csv",
        metric_cmp_rows,
        [
            "gate_id",
            "subgate_id",
            "metric_2d",
            "metric_4d",
            "value_2d",
            "value_4d",
            "delta_4d_minus_2d",
            "threshold_2d",
            "threshold_4d",
            "status_2d",
            "status_4d",
            "source_2d",
            "source_4d",
        ],
    )

    g18d = next((r for r in metric_cmp_rows if r["subgate_id"] == "G18d"), None)
    summary = {
        "summary_id": "qng-2d-vs-4d-comparator-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate_count": len(gate_cmp_rows),
        "gate_changed_count": sum(1 for r in gate_cmp_rows if r["changed"] == "yes"),
        "metric_overlap_count": len(metric_cmp_rows),
        "g18d_comparison": g18d,
        "inputs": {
            "legacy_gates_csv": str(legacy_gates_csv),
            "lane4d_gate_csv": str(lane4d_gate_csv),
            "lane4d_metric_csv": str(lane4d_metric_csv),
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# QNG 2D vs 4D Comparator v1",
        "",
        "Single-protocol comparison for G10..G18 using legacy 2D summary vs official 4D summary.",
        "",
        f"- Generated: `{summary['generated_at_utc']}`",
        f"- Gates compared: `{len(gate_cmp_rows)}` (changed: `{summary['gate_changed_count']}`)",
        f"- Metric overlap: `{len(metric_cmp_rows)}`",
    ]
    if g18d:
        lines += [
            "",
            "G18d spotlight:",
            f"- 2D legacy: `{g18d['value_2d']}` with threshold `{g18d['threshold_2d']}`",
            f"- 4D official: `{g18d['value_4d']}` with threshold `{g18d['threshold_4d']}`",
        ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[ok] wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
