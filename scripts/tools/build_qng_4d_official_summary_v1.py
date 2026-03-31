#!/usr/bin/env python3
"""Build a single official 4D gate/metric summary for QNG (G10..G18)."""

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

DEFAULT_GR_GATE_CSV = ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard.csv"
DEFAULT_GR_DETAIL_CSV = ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard_detail.csv"
DEFAULT_G17_CSV = ART / "qng-g17-v2" / "metric_checks_g17_v2.csv"
DEFAULT_G18_CSV = ART / "qng-g18d-v2" / "metric_checks_g18d_v2.csv"
DEFAULT_OUT_DIR = ART / "qng-4d-official-summary-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build QNG official 4D summary (G10..G18).")
    p.add_argument("--gr-gates-csv", default=str(DEFAULT_GR_GATE_CSV))
    p.add_argument("--gr-detail-csv", default=str(DEFAULT_GR_DETAIL_CSV))
    p.add_argument("--g17-csv", default=str(DEFAULT_G17_CSV))
    p.add_argument("--g18-csv", default=str(DEFAULT_G18_CSV))
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


def norm_status(v: str) -> str:
    t = (v or "").strip().lower()
    if t in {"pass", "true", "1", "ok"}:
        return "pass"
    return "fail"


def gate_num(gate_id: str) -> int:
    m = re.match(r"^G(\d+)", gate_id)
    return int(m.group(1)) if m else 999


def subgate_to_gate(subgate: str) -> str:
    m = re.match(r"^(G\d+)", subgate)
    if not m:
        raise ValueError(f"cannot parse gate from subgate: {subgate}")
    return m.group(1)


def main() -> int:
    args = parse_args()

    gr_gates_csv = Path(args.gr_gates_csv).resolve()
    gr_detail_csv = Path(args.gr_detail_csv).resolve()
    g17_csv = Path(args.g17_csv).resolve()
    g18_csv = Path(args.g18_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in (gr_gates_csv, gr_detail_csv, g17_csv, g18_csv):
        if not p.exists():
            raise FileNotFoundError(f"missing required input: {p}")

    gate_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    gr_gates = read_csv(gr_gates_csv)
    for r in gr_gates:
        gate_id = str(r.get("gate", "")).strip()
        if not gate_id:
            continue
        if gate_num(gate_id) > 16:
            continue
        gate_rows.append(
            {
                "gate_id": gate_id,
                "gate_decision": norm_status(str(r.get("status", ""))),
                "lane": "4d",
                "source_file": str(gr_gates_csv),
            }
        )

    gr_detail = read_csv(gr_detail_csv)
    for r in gr_detail:
        subgate = str(r.get("gate", "")).strip()
        if not subgate:
            continue
        gate_id = subgate_to_gate(subgate)
        if gate_num(gate_id) > 16:
            continue
        metric_rows.append(
            {
                "gate_id": gate_id,
                "subgate_id": subgate,
                "metric": str(r.get("metric", "")).strip(),
                "value": str(r.get("value", "")).strip(),
                "threshold": str(r.get("threshold", "")).strip(),
                "status": norm_status(str(r.get("status", ""))),
                "lane": "4d",
                "source_file": str(gr_detail_csv),
            }
        )

    for qm_path in (g17_csv, g18_csv):
        qm_rows = read_csv(qm_path)
        subgate_statuses: dict[str, list[str]] = {}
        for r in qm_rows:
            subgate = str(r.get("gate_id", "")).strip()
            if not subgate or subgate.upper() == "FINAL":
                continue
            gate_id = subgate_to_gate(subgate)
            status = norm_status(str(r.get("status", "") or r.get("pass", "")))
            subgate_statuses.setdefault(gate_id, []).append(status)
            metric_rows.append(
                {
                    "gate_id": gate_id,
                    "subgate_id": subgate,
                    "metric": str(r.get("metric", "")).strip(),
                    "value": str(r.get("value", "")).strip(),
                    "threshold": str(r.get("threshold", "")).strip(),
                    "status": status,
                    "lane": "4d",
                    "source_file": str(qm_path),
                }
            )
        for gate_id, statuses in subgate_statuses.items():
            gate_rows.append(
                {
                    "gate_id": gate_id,
                    "gate_decision": "pass" if all(s == "pass" for s in statuses) else "fail",
                    "lane": "4d",
                    "source_file": str(qm_path),
                }
            )

    # deterministic ordering
    gate_rows = sorted(gate_rows, key=lambda r: gate_num(str(r["gate_id"])))
    metric_rows = sorted(metric_rows, key=lambda r: (gate_num(str(r["gate_id"])), str(r["subgate_id"])))

    write_csv(
        out_dir / "gate_summary_4d.csv",
        gate_rows,
        ["gate_id", "gate_decision", "lane", "source_file"],
    )
    write_csv(
        out_dir / "metric_summary_4d.csv",
        metric_rows,
        ["gate_id", "subgate_id", "metric", "value", "threshold", "status", "lane", "source_file"],
    )

    g18d_rows = [
        r
        for r in metric_rows
        if str(r.get("subgate_id", "")) == "G18d" and str(r.get("metric", "")) == "spectral_dimension_ds"
    ]
    g18d_value = g18d_rows[0]["value"] if g18d_rows else ""
    g18d_threshold = g18d_rows[0]["threshold"] if g18d_rows else ""

    summary = {
        "summary_id": "qng-4d-official-summary-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "4d",
        "gate_count": len(gate_rows),
        "metric_count": len(metric_rows),
        "all_pass": all(str(r.get("gate_decision", "")) == "pass" for r in gate_rows),
        "g18d": {
            "value": g18d_value,
            "threshold": g18d_threshold,
        },
        "inputs": {
            "gr_gates_csv": str(gr_gates_csv),
            "gr_detail_csv": str(gr_detail_csv),
            "g17_csv": str(g17_csv),
            "g18_csv": str(g18_csv),
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    lines = [
        "# QNG 4D Official Summary v1",
        "",
        "This package is the consolidated official 4D lane summary for G10..G18.",
        "",
        f"- Generated: `{summary['generated_at_utc']}`",
        f"- Gates: `{len(gate_rows)}`",
        f"- Metrics: `{len(metric_rows)}`",
        f"- All pass: `{summary['all_pass']}`",
        f"- G18d spectral dimension: `{g18d_value}` with threshold `{g18d_threshold}`",
        "",
        "Inputs:",
        f"- `{gr_gates_csv}`",
        f"- `{gr_detail_csv}`",
        f"- `{g17_csv}`",
        f"- `{g18_csv}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[ok] wrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
