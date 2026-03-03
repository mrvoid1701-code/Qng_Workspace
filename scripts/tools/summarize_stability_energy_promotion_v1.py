#!/usr/bin/env python3
"""
Aggregate stability energy promotion reports across primary/attack/holdout.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-energy-promotion-eval-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate stability energy promotion reports.")
    p.add_argument("--report-jsons", required=True, help="Comma-separated list of report.json files")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="stability-energy-promotion-bundle-v1")
    return p.parse_args()


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    reports: list[dict[str, Any]] = []
    for raw in parse_csv_list(args.report_jsons):
        p = Path(raw).resolve()
        if not p.exists():
            raise FileNotFoundError(f"missing report json: {p}")
        rep = read_json(p)
        rep["_path"] = p.as_posix()
        reports.append(rep)
    if not reports:
        raise RuntimeError("no report jsons provided")

    overall = all(str(r.get("overall_decision", "")).upper() == "PASS" for r in reports)
    bundle = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "report_jsons": [str(r["_path"]) for r in reports],
        "blocks": [
            {
                "eval_id": r.get("eval_id", ""),
                "overall_decision": r.get("overall_decision", ""),
                "n": r.get("totals", {}).get("n", 0),
                "energy_improved": r.get("totals", {}).get("energy_improved", 0),
                "energy_degraded": r.get("totals", {}).get("energy_degraded", 0),
                "all_improved": r.get("totals", {}).get("all_improved", 0),
                "all_degraded": r.get("totals", {}).get("all_degraded", 0),
                "non_energy_degraded_total": r.get("totals", {}).get("non_energy_degraded_total", 0),
            }
            for r in reports
        ],
        "overall_decision": "PASS" if overall else "HOLD",
    }
    (out_dir / "promotion_decision.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")

    lines = [
        "# Stability Energy Candidate-v2 Promotion Decision",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{bundle['generated_utc']}`",
        f"- overall_decision: `{bundle['overall_decision']}`",
        "",
        "## Blocks",
        "",
    ]
    for b in bundle["blocks"]:
        lines.append(
            f"- `{b['eval_id']}`: decision=`{b['overall_decision']}`, "
            f"n=`{b['n']}`, energy_improved=`{b['energy_improved']}`, energy_degraded=`{b['energy_degraded']}`, "
            f"all_improved=`{b['all_improved']}`, all_degraded=`{b['all_degraded']}`, "
            f"non_energy_degraded_total=`{b['non_energy_degraded_total']}`"
        )
    (out_dir / "promotion_decision.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"promotion_decision_md:   {(out_dir / 'promotion_decision.md').as_posix()}")
    print(f"promotion_decision_json: {(out_dir / 'promotion_decision.json').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
