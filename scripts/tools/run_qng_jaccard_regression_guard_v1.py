#!/usr/bin/env python3
"""Regression guard for QNG Jaccard freeze v1 (no-degradation + no-missing)."""

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
DEFAULT_INPUTS = {
    "gr_gates": ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard.csv",
    "gr_detail": ART / "qng-gr-jaccard-v1" / "gr_gates_jaccard_detail.csv",
    "g17": ART / "qng-g17-v2" / "metric_checks_g17_v2.csv",
    "g18": ART / "qng-g18d-v2" / "metric_checks_g18d_v2.csv",
    "g19": ART / "qng-g19-jaccard-v1" / "metric_checks_g19_jaccard.csv",
    "g20": ART / "qng-g20-jaccard-v1" / "metric_checks_g20_jaccard.csv",
    "g21": ART / "qng-g21-thermo-v1" / "metric_checks_g21.csv",
}


DEFAULT_BASE_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-jaccard-freeze-v1"
DEFAULT_OUT_DIR = DEFAULT_BASE_DIR / "latest_check"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Jaccard regression guard vs freeze baseline.")
    p.add_argument("--base-dir", default=str(DEFAULT_BASE_DIR))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--no-strict-exit", action="store_true")
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


def subgate_to_gate(subgate: str) -> str:
    m = re.match(r"^(G\d+)", subgate or "")
    return m.group(1) if m else ""


def collect_current(inputs: dict[str, Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    gate_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    gr_gates = read_csv(inputs["gr_gates"])
    for r in gr_gates:
        gate_id = str(r.get("gate", "")).strip()
        if not gate_id:
            continue
        gate_rows.append(
            {"gate_id": gate_id, "decision": norm_status(str(r.get("status", ""))), "source": str(inputs["gr_gates"])}
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
        gate_id = ""
        sub_statuses: list[str] = []
        explicit_final: str | None = None
        for r in rows:
            subgate = str(r.get("gate_id", "")).strip()
            if not subgate:
                continue
            if subgate.upper() == "FINAL":
                explicit_final = norm_status(str(r.get("status", "") or r.get("pass", "")))
                continue
            gate_id = subgate_to_gate(subgate)
            status = norm_status(str(r.get("status", "") or r.get("pass", "")))
            sub_statuses.append(status)
            metric_rows.append(
                {
                    "gate_id": gate_id,
                    "subgate_id": subgate,
                    "metric": str(r.get("metric", "")).strip(),
                    "value": str(r.get("value", "")).strip(),
                    "threshold": str(r.get("threshold", "")).strip(),
                    "status": status,
                    "source": str(inputs[key]),
                }
            )
        if gate_id:
            decision = explicit_final if explicit_final is not None else ("pass" if all(s == "pass" for s in sub_statuses) else "fail")
            gate_rows.append({"gate_id": gate_id, "decision": decision, "source": str(inputs[key])})

    return gate_rows, metric_rows


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    base_gate_csv = base_dir / "gate_status_snapshot.csv"
    base_metric_csv = base_dir / "metric_snapshot.csv"
    for p in (base_gate_csv, base_metric_csv):
        if not p.exists():
            raise FileNotFoundError(f"missing baseline file: {p}")

    baseline_gates = read_csv(base_gate_csv)
    baseline_metrics = read_csv(base_metric_csv)
    current_gates, current_metrics = collect_current(DEFAULT_INPUTS)

    base_gate_map = {str(r["gate_id"]): str(r["decision"]).lower() for r in baseline_gates}
    cur_gate_map = {str(r["gate_id"]): str(r["decision"]).lower() for r in current_gates}

    base_metric_map = {
        str(r["subgate_id"]): str(r["status"]).lower() for r in baseline_metrics
    }
    cur_metric_map = {str(r["subgate_id"]): str(r["status"]).lower() for r in current_metrics}

    missing_gates = sorted(set(base_gate_map) - set(cur_gate_map))
    extra_gates = sorted(set(cur_gate_map) - set(base_gate_map))
    missing_metrics = sorted(set(base_metric_map) - set(cur_metric_map))
    extra_metrics = sorted(set(cur_metric_map) - set(base_metric_map))

    gate_degraded: list[str] = []
    for gate_id, base_dec in base_gate_map.items():
        cur_dec = cur_gate_map.get(gate_id)
        if base_dec == "pass" and cur_dec == "fail":
            gate_degraded.append(gate_id)

    metric_degraded: list[str] = []
    for subgate_id, base_stat in base_metric_map.items():
        cur_stat = cur_metric_map.get(subgate_id)
        if base_stat == "pass" and cur_stat == "fail":
            metric_degraded.append(subgate_id)

    check_rows = [
        {"check": "missing_gates", "count": len(missing_gates), "status": "fail" if missing_gates else "pass"},
        {"check": "extra_gates", "count": len(extra_gates), "status": "fail" if extra_gates else "pass"},
        {"check": "missing_metrics", "count": len(missing_metrics), "status": "fail" if missing_metrics else "pass"},
        {"check": "extra_metrics", "count": len(extra_metrics), "status": "fail" if extra_metrics else "pass"},
        {"check": "gate_degraded", "count": len(gate_degraded), "status": "fail" if gate_degraded else "pass"},
        {"check": "metric_degraded", "count": len(metric_degraded), "status": "fail" if metric_degraded else "pass"},
    ]
    write_csv(out_dir / "checks.csv", check_rows, ["check", "count", "status"])

    details_rows: list[dict[str, str]] = []
    for gid in missing_gates:
        details_rows.append({"kind": "missing_gate", "id": gid})
    for gid in extra_gates:
        details_rows.append({"kind": "extra_gate", "id": gid})
    for sid in missing_metrics:
        details_rows.append({"kind": "missing_metric", "id": sid})
    for sid in extra_metrics:
        details_rows.append({"kind": "extra_metric", "id": sid})
    for gid in gate_degraded:
        details_rows.append({"kind": "gate_degraded", "id": gid})
    for sid in metric_degraded:
        details_rows.append({"kind": "metric_degraded", "id": sid})
    write_csv(out_dir / "details.csv", details_rows, ["kind", "id"])

    pass_guard = not any(
        [missing_gates, extra_gates, missing_metrics, extra_metrics, gate_degraded, metric_degraded]
    )
    report = {
        "guard_id": "qng-jaccard-regression-guard-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_dir": str(base_dir),
        "pass": pass_guard,
        "counts": {
            "missing_gates": len(missing_gates),
            "extra_gates": len(extra_gates),
            "missing_metrics": len(missing_metrics),
            "extra_metrics": len(extra_metrics),
            "gate_degraded": len(gate_degraded),
            "metric_degraded": len(metric_degraded),
        },
    }
    (out_dir / "regression_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QNG Jaccard Regression Guard v1",
        "",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Result: `{'PASS' if pass_guard else 'FAIL'}`",
        "",
        "Counts:",
    ]
    for k, v in report["counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    (out_dir / "regression_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[ok] wrote guard report: {out_dir}")
    return 0 if (pass_guard or args.no_strict_exit) else 1


if __name__ == "__main__":
    raise SystemExit(main())
