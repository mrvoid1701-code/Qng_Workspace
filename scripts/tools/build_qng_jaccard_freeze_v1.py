#!/usr/bin/env python3
"""Build freeze package for QNG Jaccard lane (G10..G21)."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"

DEFAULT_INPUTS = {
    "gr_gates": ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard.csv",
    "gr_detail": ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard_detail.csv",
    "g17": ART / "qng-g17-v2" / "metric_checks_g17_v2.csv",
    "g18": ART / "qng-g18d-v2" / "metric_checks_g18d_v2.csv",
    "g19": ART / "qng-g19-jaccard-v1" / "metric_checks_g19_jaccard.csv",
    "g20": ART / "qng-g20-jaccard-v1" / "metric_checks_g20_jaccard.csv",
    "g21": ART / "qng-g21-thermo-v1" / "metric_checks_g21.csv",
}
DEFAULT_OUT_DIR = ART / "qng-jaccard-freeze-v1"


@dataclass
class Collected:
    gate_rows: list[dict[str, Any]]
    metric_rows: list[dict[str, Any]]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build QNG Jaccard freeze package v1.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--freeze-id", default="qng-jaccard-freeze-v1")
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


def gate_num(g: str) -> int:
    m = re.match(r"^G(\d+)", g or "")
    return int(m.group(1)) if m else 999


def subgate_to_gate(subgate: str) -> str:
    m = re.match(r"^(G\d+)", subgate or "")
    return m.group(1) if m else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def collect_current(inputs: dict[str, Path]) -> Collected:
    gate_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    gr_gates = read_csv(inputs["gr_gates"])
    for r in gr_gates:
        gate_id = str(r.get("gate", "")).strip()
        if not gate_id:
            continue
        gate_rows.append(
            {
                "gate_id": gate_id,
                "decision": norm_status(str(r.get("status", ""))),
                "source": str(inputs["gr_gates"]),
            }
        )

    gr_detail = read_csv(inputs["gr_detail"])
    for r in gr_detail:
        subgate = str(r.get("gate", "")).strip()
        gate_id = subgate_to_gate(subgate)
        if not gate_id:
            continue
        metric_rows.append(
            {
                "gate_id": gate_id,
                "subgate_id": subgate,
                "metric": str(r.get("metric", "")).strip(),
                "value": str(r.get("value", "")).strip(),
                "threshold": str(r.get("threshold", "")).strip(),
                "status": norm_status(str(r.get("status", ""))),
                "source": str(inputs["gr_detail"]),
            }
        )

    for key in ("g17", "g18", "g19", "g20", "g21"):
        rows = read_csv(inputs[key])
        sub_statuses: list[str] = []
        gate_id = ""
        explicit_final: str | None = None

        for r in rows:
            raw_sub = str(r.get("gate_id", "")).strip()
            if not raw_sub:
                continue
            if raw_sub.upper() == "FINAL":
                explicit_final = norm_status(str(r.get("status", "") or r.get("pass", "")))
                continue
            gate_id = subgate_to_gate(raw_sub)
            status = norm_status(str(r.get("status", "") or r.get("pass", "")))
            sub_statuses.append(status)
            metric_rows.append(
                {
                    "gate_id": gate_id,
                    "subgate_id": raw_sub,
                    "metric": str(r.get("metric", "")).strip(),
                    "value": str(r.get("value", "")).strip(),
                    "threshold": str(r.get("threshold", "")).strip(),
                    "status": status,
                    "source": str(inputs[key]),
                }
            )

        if gate_id:
            decision = explicit_final if explicit_final is not None else ("pass" if all(s == "pass" for s in sub_statuses) else "fail")
            gate_rows.append(
                {
                    "gate_id": gate_id,
                    "decision": decision,
                    "source": str(inputs[key]),
                }
            )

    gate_rows = sorted(gate_rows, key=lambda r: gate_num(str(r["gate_id"])))
    metric_rows = sorted(metric_rows, key=lambda r: (gate_num(str(r["gate_id"])), str(r["subgate_id"])))
    return Collected(gate_rows=gate_rows, metric_rows=metric_rows)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in DEFAULT_INPUTS.values():
        if not p.exists():
            raise FileNotFoundError(f"missing input: {p}")

    collected = collect_current(DEFAULT_INPUTS)

    gate_csv = out_dir / "gate_status_snapshot.csv"
    metric_csv = out_dir / "metric_snapshot.csv"
    write_csv(gate_csv, collected.gate_rows, ["gate_id", "decision", "source"])
    write_csv(metric_csv, collected.metric_rows, ["gate_id", "subgate_id", "metric", "value", "threshold", "status", "source"])

    all_pass = all(str(r.get("decision", "")) == "pass" for r in collected.gate_rows)
    failing_gates = [str(r["gate_id"]) for r in collected.gate_rows if str(r.get("decision", "")) != "pass"]

    summary = {
        "freeze_id": args.freeze_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate_count": len(collected.gate_rows),
        "metric_count": len(collected.metric_rows),
        "all_pass": all_pass,
        "failing_gates": failing_gates,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    manifest_inputs: list[dict[str, Any]] = []
    for name, p in DEFAULT_INPUTS.items():
        manifest_inputs.append(
            {
                "name": name,
                "path": str(p.relative_to(ROOT)),
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
            }
        )

    manifest_outputs: list[dict[str, Any]] = []
    for p in (gate_csv, metric_csv, summary_path):
        manifest_outputs.append(
            {
                "path": str(p.relative_to(ROOT)),
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
            }
        )

    manifest = {
        "freeze_id": args.freeze_id,
        "generated_at_utc": summary["generated_at_utc"],
        "inputs": manifest_inputs,
        "outputs": manifest_outputs,
        "script": str(Path(__file__).relative_to(ROOT)),
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report_lines = [
        f"# {args.freeze_id}",
        "",
        "Operational freeze package for QNG Jaccard lane.",
        "",
        f"- Generated: `{summary['generated_at_utc']}`",
        f"- Gates: `{summary['gate_count']}`",
        f"- Metrics: `{summary['metric_count']}`",
        f"- All pass: `{summary['all_pass']}`",
        "",
        "Included gates: G10..G21",
        "",
        "Files:",
        f"- `{gate_csv.relative_to(ROOT)}`",
        f"- `{metric_csv.relative_to(ROOT)}`",
        f"- `{summary_path.relative_to(ROOT)}`",
        f"- `{manifest_path.relative_to(ROOT)}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"[ok] wrote freeze package: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
