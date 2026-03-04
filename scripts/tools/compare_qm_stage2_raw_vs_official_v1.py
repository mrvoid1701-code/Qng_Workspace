#!/usr/bin/env python3
"""
Compare QM Stage-2 prereg raw summaries vs QM Stage-1 official-v5 summaries.

Purpose:
- quantify raw->official policy uplift/degrade at profile and dataset level
- expose whether Stage-2 HOLD is dominated by raw policy or residual true fails
- tooling only; no gate/formula/threshold changes
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_OUT_DIR = ART / "qm-stage2-raw-vs-official-v5-v1"
DEFAULT_RAW_CSVS = [
    ART / "qm-stage2-prereg-v1" / "primary_ds002_003_006_s3401_3600" / "qm_lane" / "summary.csv",
    ART / "qm-stage2-prereg-v1" / "attack_ds002_003_006_s3601_4100" / "qm_lane" / "summary.csv",
    ART / "qm-stage2-prereg-v1" / "holdout_ds004_008_s3401_3600" / "qm_lane" / "summary.csv",
]
DEFAULT_OFFICIAL_CSVS = [
    ART / "qm-stage1-official-v5" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-stage1-official-v5" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-stage1-official-v5" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]

GATES = ("g17_status", "g18_status", "g19_status", "g20_status")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare QM Stage-2 raw prereg vs official-v5 summaries.")
    p.add_argument("--raw-summary-csvs", default=",".join(str(p) for p in DEFAULT_RAW_CSVS))
    p.add_argument("--official-summary-csvs", default=",".join(str(p) for p in DEFAULT_OFFICIAL_CSVS))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def parse_csv_list(text: str) -> list[Path]:
    out: list[Path] = []
    for token in text.split(","):
        t = token.strip()
        if t:
            out.append(Path(t).resolve())
    return out


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
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def detect_block_id(path: Path) -> str:
    s = path.as_posix().lower()
    if "primary_ds002_003_006_s3401_3600" in s:
        return "primary"
    if "attack_ds002_003_006_s3601_4100" in s or "attack_seed500_ds002_003_006_s3601_4100" in s:
        return "attack"
    if "holdout_ds004_008_s3401_3600" in s or "attack_holdout_ds004_008_s3401_3600" in s:
        return "holdout"
    return path.parent.name


def key_of(block_id: str, ds: str, seed: int) -> str:
    return f"{block_id}::{ds.upper()}::{seed}"


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_paths = parse_csv_list(args.raw_summary_csvs)
    off_paths = parse_csv_list(args.official_summary_csvs)
    if not raw_paths or not off_paths:
        raise RuntimeError("raw/off csv path lists must be non-empty")
    for p in raw_paths + off_paths:
        if not p.exists():
            raise FileNotFoundError(f"missing csv: {p}")

    raw_map: dict[str, dict[str, Any]] = {}
    off_map: dict[str, dict[str, Any]] = {}

    for p in raw_paths:
        block = detect_block_id(p)
        for r in read_csv(p):
            ds = str(r.get("dataset_id", "")).strip()
            seed = int(str(r.get("seed", "0")))
            key = key_of(block, ds, seed)
            raw_map[key] = {
                "block_id": block,
                "dataset_id": ds,
                "seed": seed,
                "all_pass_qm_lane_raw": norm_status(str(r.get("all_pass_qm_lane", ""))),
                "g17_status_raw": norm_status(str(r.get("g17_status", ""))),
                "g18_status_raw": norm_status(str(r.get("g18_status", ""))),
                "g19_status_raw": norm_status(str(r.get("g19_status", ""))),
                "g20_status_raw": norm_status(str(r.get("g20_status", ""))),
                "run_root_raw": str(r.get("run_root", "")),
            }

    for p in off_paths:
        block = detect_block_id(p)
        for r in read_csv(p):
            ds = str(r.get("dataset_id", "")).strip()
            seed = int(str(r.get("seed", "0")))
            key = key_of(block, ds, seed)
            off_map[key] = {
                "block_id": block,
                "dataset_id": ds,
                "seed": seed,
                "all_pass_qm_lane_official": norm_status(str(r.get("all_pass_qm_lane", ""))),
                "g17_status_official": norm_status(str(r.get("g17_status", ""))),
                "g18_status_official": norm_status(str(r.get("g18_status", ""))),
                "g19_status_official": norm_status(str(r.get("g19_status", ""))),
                "g20_status_official": norm_status(str(r.get("g20_status", ""))),
                "policy_id_official": str(r.get("policy_id", "")),
            }

    keys_raw = set(raw_map.keys())
    keys_off = set(off_map.keys())
    missing_in_off = sorted(keys_raw - keys_off)
    extra_in_off = sorted(keys_off - keys_raw)

    joined_rows: list[dict[str, Any]] = []
    for key in sorted(keys_raw & keys_off):
        rr = raw_map[key]
        oo = off_map[key]
        row: dict[str, Any] = {
            "block_id": rr["block_id"],
            "dataset_id": rr["dataset_id"],
            "seed": rr["seed"],
            "all_pass_qm_lane_raw": rr["all_pass_qm_lane_raw"],
            "all_pass_qm_lane_official": oo["all_pass_qm_lane_official"],
            "transition": f"{rr['all_pass_qm_lane_raw']}->{oo['all_pass_qm_lane_official']}",
            "policy_id_official": oo["policy_id_official"],
        }
        changed_gates: list[str] = []
        for g in GATES:
            raw_col = f"{g}_raw"
            off_col = f"{g}_official"
            row[raw_col] = rr[raw_col]
            row[off_col] = oo[off_col]
            if rr[raw_col] != oo[off_col]:
                changed_gates.append(g)
        row["changed_gate_list"] = ",".join(changed_gates) if changed_gates else "none"
        joined_rows.append(row)

    write_csv(
        out_dir / "profile_deltas.csv",
        joined_rows,
        [
            "block_id",
            "dataset_id",
            "seed",
            "all_pass_qm_lane_raw",
            "all_pass_qm_lane_official",
            "transition",
            "g17_status_raw",
            "g17_status_official",
            "g18_status_raw",
            "g18_status_official",
            "g19_status_raw",
            "g19_status_official",
            "g20_status_raw",
            "g20_status_official",
            "changed_gate_list",
            "policy_id_official",
        ],
    )

    trans_counter = Counter(str(r["transition"]) for r in joined_rows)
    change_gate_counter = Counter()
    for r in joined_rows:
        for g in str(r["changed_gate_list"]).split(","):
            t = g.strip()
            if t and t != "none":
                change_gate_counter[t] += 1

    summary_rows: list[dict[str, Any]] = []
    for block in ("primary", "attack", "holdout", "ALL"):
        for ds in sorted({str(r["dataset_id"]) for r in joined_rows}) + ["ALL"]:
            sub = joined_rows
            if block != "ALL":
                sub = [r for r in sub if str(r["block_id"]) == block]
            if ds != "ALL":
                sub = [r for r in sub if str(r["dataset_id"]) == ds]
            total = len(sub)
            if total == 0:
                continue
            pass_raw = sum(1 for r in sub if r["all_pass_qm_lane_raw"] == "pass")
            pass_off = sum(1 for r in sub if r["all_pass_qm_lane_official"] == "pass")
            improved = sum(1 for r in sub if r["transition"] == "fail->pass")
            degraded = sum(1 for r in sub if r["transition"] == "pass->fail")
            summary_rows.append(
                {
                    "block_id": block,
                    "dataset_id": ds,
                    "profiles_total": total,
                    "pass_raw": pass_raw,
                    "pass_official": pass_off,
                    "improved_fail_to_pass": improved,
                    "degraded_pass_to_fail": degraded,
                    "pass_rate_raw": f"{(pass_raw / total):.6f}",
                    "pass_rate_official": f"{(pass_off / total):.6f}",
                }
            )

    write_csv(
        out_dir / "summary_transition.csv",
        summary_rows,
        [
            "block_id",
            "dataset_id",
            "profiles_total",
            "pass_raw",
            "pass_official",
            "improved_fail_to_pass",
            "degraded_pass_to_fail",
            "pass_rate_raw",
            "pass_rate_official",
        ],
    )

    missing_rows = [{"key": k, "side": "missing_in_official"} for k in missing_in_off] + [
        {"key": k, "side": "extra_in_official"} for k in extra_in_off
    ]
    write_csv(out_dir / "profile_mismatch_keys.csv", missing_rows, ["key", "side"])

    total = len(joined_rows)
    pass_raw_all = sum(1 for r in joined_rows if r["all_pass_qm_lane_raw"] == "pass")
    pass_off_all = sum(1 for r in joined_rows if r["all_pass_qm_lane_official"] == "pass")
    improved_all = trans_counter.get("fail->pass", 0)
    degraded_all = trans_counter.get("pass->fail", 0)

    lines: list[str] = []
    lines.append("# QM Stage-2 Raw vs Official-v5 Comparison (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- profiles_joined: `{total}`")
    lines.append(f"- missing_in_official: `{len(missing_in_off)}`")
    lines.append(f"- extra_in_official: `{len(extra_in_off)}`")
    lines.append("")
    lines.append("## Lane Transition Summary (ALL)")
    lines.append("")
    lines.append(f"- raw pass: `{pass_raw_all}/{total}`")
    lines.append(f"- official pass: `{pass_off_all}/{total}`")
    lines.append(f"- improved (fail->pass): `{improved_all}`")
    lines.append(f"- degraded (pass->fail): `{degraded_all}`")
    lines.append("")
    lines.append("## Transition Counts")
    lines.append("")
    for k, c in trans_counter.most_common():
        lines.append(f"- `{k}`: `{c}`")
    lines.append("")
    lines.append("## Gate Status Deltas")
    lines.append("")
    for g, c in change_gate_counter.most_common():
        lines.append(f"- `{g}` changed on `{c}` profiles")
    if not change_gate_counter:
        lines.append("- none")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Tooling-only comparison over frozen artifacts.")
    lines.append("- No gate thresholds/formulas were changed.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"profile_deltas:       {(out_dir / 'profile_deltas.csv').as_posix()}")
    print(f"summary_transition:   {(out_dir / 'summary_transition.csv').as_posix()}")
    print(f"profile_mismatches:   {(out_dir / 'profile_mismatch_keys.csv').as_posix()}")
    print(f"report_md:            {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
