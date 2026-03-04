#!/usr/bin/env python3
"""
Build chi-sigma phase diagram table from stability sweep summaries.

Diagnostic-only:
- no formula/threshold changes
- aggregates pass/fail structure across chi_scale and sigma bands
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-dual-sweep-v1" / "summary.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-phase-diagram-chi-sigma-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze stability phase diagram in chi-sigma coordinates.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--sigma-field", default="max_abs_sigma_seen")
    p.add_argument("--sigma-bins", default="0.20,0.40,0.60,0.80,1.00")
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


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(str(v))
    except Exception:
        return default


def is_pass(v: Any) -> bool:
    return str(v or "").strip().lower() == "pass"


def parse_bins(text: str) -> list[float]:
    vals = [float(x.strip()) for x in text.split(",") if x.strip()]
    vals = sorted(vals)
    if not vals:
        raise ValueError("sigma-bins is empty")
    return vals


def sigma_bin_label(x: float, bins: list[float]) -> str:
    low = 0.0
    for high in bins:
        if x <= high:
            return f"[{low:.2f},{high:.2f}]"
        low = high
    return f">{bins[-1]:.2f}"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary csv not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    bins = parse_bins(args.sigma_bins)
    table: dict[tuple[str, str], dict[str, int]] = {}
    for r in rows:
        chi = f"{to_float(r.get('chi_scale', 0.0), 0.0):.2f}"
        sigma = to_float(r.get(args.sigma_field, 0.0), 0.0)
        sb = sigma_bin_label(sigma, bins)
        key = (chi, sb)
        cell = table.setdefault(
            key,
            {
                "n": 0,
                "all_pass": 0,
                "energy_pass": 0,
                "struct_pass": 0,
            },
        )
        cell["n"] += 1
        if is_pass(r.get("all_pass", "")):
            cell["all_pass"] += 1
        if is_pass(r.get("gate_energy_drift", "")):
            cell["energy_pass"] += 1
        if (
            is_pass(r.get("gate_sigma_bounds", ""))
            and is_pass(r.get("gate_metric_positive", ""))
            and is_pass(r.get("gate_metric_cond", ""))
            and is_pass(r.get("gate_runaway", ""))
            and is_pass(r.get("gate_variational_residual", ""))
            and is_pass(r.get("gate_alpha_drift", ""))
            and is_pass(r.get("gate_no_signalling", ""))
        ):
            cell["struct_pass"] += 1

    phase_rows: list[dict[str, Any]] = []
    for (chi, sb) in sorted(table.keys(), key=lambda x: (float(x[0]), x[1])):
        c = table[(chi, sb)]
        n = max(1, c["n"])
        phase_rows.append(
            {
                "chi_scale": chi,
                "sigma_bin": sb,
                "n_profiles": c["n"],
                "all_pass_rate": f"{(c['all_pass'] / n):.6f}",
                "energy_pass_rate": f"{(c['energy_pass'] / n):.6f}",
                "structural_pass_rate": f"{(c['struct_pass'] / n):.6f}",
            }
        )

    write_csv(
        out_dir / "phase_diagram.csv",
        phase_rows,
        ["chi_scale", "sigma_bin", "n_profiles", "all_pass_rate", "energy_pass_rate", "structural_pass_rate"],
    )

    lines = [
        "# Stability Phase Diagram chi-sigma (v1)",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- source_summary_csv: `{summary_csv.as_posix()}`",
        f"- sigma_field: `{args.sigma_field}`",
        f"- sigma_bins: `{','.join(f'{b:.2f}' for b in bins)}`",
        f"- cells: `{len(phase_rows)}`",
        "",
        "## Notes",
        "",
        "- `all_pass_rate` is full gate conjunction.",
        "- `energy_pass_rate` isolates energetic channel (S1 proxy).",
        "- `structural_pass_rate` isolates structural channel (S2 proxy).",
        "- Diagnostic-only aggregation; no gate thresholds/formulas changed.",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"phase_diagram_csv: {out_dir / 'phase_diagram.csv'}")
    print(f"report_md:         {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

