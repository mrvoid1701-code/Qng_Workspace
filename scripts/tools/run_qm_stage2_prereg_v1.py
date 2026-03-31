#!/usr/bin/env python3
"""
Run QM-Stage-2 prereg orchestration package (v1).

Tooling-only scope:
- orchestrates existing QM Stage-1 lane runners over Stage-2 prereg blocks
- optionally runs chunked QM-GR coupling audit v2 per block
- aggregates block reports into one summary.csv / report.md / manifest.json

No physics formulas or thresholds are modified by this script.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "scripts" / "tools"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qm-stage2-prereg-v1"


@dataclass(frozen=True)
class Block:
    block_id: str
    datasets: tuple[str, ...]
    seed_start: int
    seed_end: int


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QM-Stage-2 prereg orchestration package (v1).")
    p.add_argument("--mode", choices=("smoke", "prereg"), default="smoke")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--strict-prereg", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--execute", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--with-coupling-audit", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--resume-qm-lane", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--chunk-size", type=int, default=25)
    p.add_argument("--resume-coupling", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--plots", action=argparse.BooleanOptionalAction, default=False)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=False)
    return p.parse_args()


def make_blocks(mode: str) -> list[Block]:
    if mode == "smoke":
        return [
            Block("primary_ds002_003_006_s3401", ("DS-002", "DS-003", "DS-006"), 3401, 3401),
            Block("attack_ds002_003_006_s3601", ("DS-002", "DS-003", "DS-006"), 3601, 3601),
            Block("holdout_ds004_008_s3401", ("DS-004", "DS-008"), 3401, 3401),
        ]
    return [
        Block("primary_ds002_003_006_s3401_3600", ("DS-002", "DS-003", "DS-006"), 3401, 3600),
        Block("attack_ds002_003_006_s3601_4100", ("DS-002", "DS-003", "DS-006"), 3601, 4100),
        Block("holdout_ds004_008_s3401_3600", ("DS-004", "DS-008"), 3401, 3600),
    ]


def run_cmd(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-10:]) if merged else ""
    return proc.returncode, tail


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def plan_commands(args: argparse.Namespace, blocks: list[Block], out_dir: Path) -> list[dict[str, Any]]:
    plan: list[dict[str, Any]] = []
    for b in blocks:
        block_out = out_dir / b.block_id
        datasets_csv = ",".join(b.datasets)
        qm_out = block_out / "qm_lane"
        eval_out = block_out / "eval"

        plan.append(
            {
                "block_id": b.block_id,
                "step": "run_qm_stage1_prereg_v1",
                "cmd": [
                    sys.executable,
                    str(TOOLS / "run_qm_stage1_prereg_v1.py"),
                    "--mode",
                    "prereg",
                    "--datasets",
                    datasets_csv,
                    "--seed-start",
                    str(b.seed_start),
                    "--seed-end",
                    str(b.seed_end),
                    "--out-dir",
                    str(qm_out),
                    "--resume" if args.resume_qm_lane else "",
                ],
            }
        )
        plan.append(
            {
                "block_id": b.block_id,
                "step": "evaluate_qm_stage1_prereg_v1",
                "cmd": [
                    sys.executable,
                    str(TOOLS / "evaluate_qm_stage1_prereg_v1.py"),
                    "--summary-csv",
                    str(qm_out / "summary.csv"),
                    "--out-dir",
                    str(eval_out),
                    "--eval-id",
                    f"qm-stage2-{b.block_id}-v1",
                    "--strict-datasets",
                    datasets_csv,
                    "--require-zero-rc",
                    "--min-all-pass-rate",
                    "0.0",
                ],
            }
        )
        if args.with_coupling_audit:
            coupling_out = block_out / "coupling_audit"
            plan.append(
                {
                    "block_id": b.block_id,
                    "step": "run_qm_gr_coupling_audit_v2",
                    "cmd": [
                        sys.executable,
                        str(TOOLS / "run_qm_gr_coupling_audit_v2.py"),
                        "--ds-list",
                        datasets_csv,
                        "--seed-min",
                        str(b.seed_start),
                        "--seed-max",
                        str(b.seed_end),
                        "--chunk-size",
                        str(args.chunk_size),
                        "--out-dir",
                        str(coupling_out),
                        "--write-artifacts" if args.write_artifacts else "--no-write-artifacts",
                        "--plots" if args.plots else "--no-plots",
                        "--resume" if args.resume_coupling else "",
                    ],
                }
            )
    # Remove empty placeholders from commands.
    for item in plan:
        item["cmd"] = [x for x in item["cmd"] if x]
    return plan


def enforce_strict_prereg(args: argparse.Namespace, blocks: list[Block]) -> None:
    if not args.strict_prereg:
        return
    if args.mode != "prereg":
        raise RuntimeError("strict-prereg requires --mode prereg")
    expected = make_blocks("prereg")
    if blocks != expected:
        raise RuntimeError("strict-prereg blocks mismatch")


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(str(value))
    except Exception:
        return default


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    blocks = make_blocks(args.mode)
    enforce_strict_prereg(args, blocks)

    plan = plan_commands(args, blocks, out_dir)
    plan_txt = out_dir / "planned_commands.txt"
    plan_txt.write_text(
        "\n".join(" ".join(item["cmd"]) for item in plan) + "\n",
        encoding="utf-8",
    )

    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log("=" * 80)
    log(f"QM-Stage-2 prereg orchestration v1 | mode={args.mode}")
    log(f"execute={str(args.execute).lower()} with_coupling_audit={str(args.with_coupling_audit).lower()}")
    log(f"resume_qm_lane={str(args.resume_qm_lane).lower()} resume_coupling={str(args.resume_coupling).lower()}")
    log(f"out_dir={out_dir}")
    log("=" * 80)

    command_runs: list[dict[str, Any]] = []
    if args.execute:
        for item in plan:
            cmd = item["cmd"]
            step = str(item["step"])
            block_id = str(item["block_id"])
            log(f"[{block_id}] {step}")
            rc, tail = run_cmd(cmd)
            command_runs.append(
                {
                    "block_id": block_id,
                    "step": step,
                    "rc": rc,
                    "cmd": cmd,
                    "tail": tail,
                }
            )
            log(f"  rc={rc}")
            if rc != 0 and tail:
                for line in tail.splitlines():
                    log(f"    {line}")
    else:
        log("execute=false -> plan generated only (no runs executed).")

    rows: list[dict[str, Any]] = []
    for b in blocks:
        block_out = out_dir / b.block_id
        qm_summary = block_out / "qm_lane" / "summary.csv"
        eval_json = block_out / "eval" / "report.json"
        coupling_manifest = block_out / "coupling_audit" / "manifest.json"

        eval_decision = "NOT_RUN"
        profiles = 0
        qm_lane_pass = 0
        all_pass_rate = 0.0
        if eval_json.exists():
            report = read_json(eval_json)
            eval_decision = str(report.get("decision", "HOLD"))
            totals = report.get("totals", {})
            profiles = safe_int(report.get("profiles", 0))
            qm_lane_pass = safe_int(totals.get("qm_lane_pass", 0))
            try:
                all_pass_rate = float(totals.get("all_pass_rate", 0.0))
            except Exception:
                all_pass_rate = 0.0
        elif qm_summary.exists():
            with qm_summary.open("r", encoding="utf-8", newline="") as f:
                q_rows = list(csv.DictReader(f))
            profiles = len(q_rows)
            qm_lane_pass = sum(1 for r in q_rows if str(r.get("all_pass_qm_lane", "")).lower() == "pass")
            all_pass_rate = (qm_lane_pass / profiles) if profiles else 0.0
            eval_decision = "HOLD"

        coupling_profiles = 0
        coupling_g20_pass = 0
        coupling_decision = "NOT_RUN"
        if coupling_manifest.exists():
            m = read_json(coupling_manifest)
            coupling_profiles = safe_int(m.get("profiles_completed", 0))
            coupling_g20_pass = safe_int(m.get("g20_pass", 0))
            pre_ok = bool(m.get("gr_guard_pre_all_pass", False))
            post_ok = bool(m.get("gr_guard_post_all_pass", False))
            chunk_ok = bool(m.get("chunk_decisions_all_pass", False))
            complete = coupling_profiles == safe_int(m.get("profiles_total_expected", -1), default=-1)
            g20_ok = coupling_g20_pass == coupling_profiles
            coupling_decision = "PASS" if (pre_ok and post_ok and chunk_ok and complete and g20_ok) else "HOLD"

        if args.with_coupling_audit:
            combined = "PASS" if (eval_decision == "PASS" and coupling_decision == "PASS") else "HOLD"
        else:
            combined = "PASS" if eval_decision == "PASS" else "HOLD"

        rows.append(
            {
                "block_id": b.block_id,
                "datasets": ",".join(b.datasets),
                "seed_start": b.seed_start,
                "seed_end": b.seed_end,
                "profiles": profiles,
                "qm_lane_pass": qm_lane_pass,
                "all_pass_rate": f"{all_pass_rate:.6f}",
                "eval_decision": eval_decision,
                "coupling_profiles": coupling_profiles,
                "coupling_g20_pass": coupling_g20_pass,
                "coupling_decision": coupling_decision,
                "combined_decision": combined,
            }
        )

    summary_csv = out_dir / "summary.csv"
    if rows:
        write_csv(summary_csv, rows, list(rows[0].keys()))

    pass_blocks = sum(1 for r in rows if str(r.get("combined_decision", "")) == "PASS")
    decision = "PASS" if rows and pass_blocks == len(rows) else "HOLD"

    report_lines = [
        "# QM Stage-2 Prereg Report (v1)",
        "",
        f"- mode: `{args.mode}`",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- execute: `{str(args.execute).lower()}`",
        f"- with_coupling_audit: `{str(args.with_coupling_audit).lower()}`",
        f"- blocks: `{len(rows)}`",
        f"- combined_pass_blocks: `{pass_blocks}/{len(rows)}`",
        f"- decision: `{decision}`",
        "",
        "## Notes",
        "",
        "- This is a tooling orchestration layer that reuses frozen Stage-1 runners.",
        "- No gate formulas or thresholds are changed.",
        "- Promotion requires prereg + non-degradation + coupling stability checks.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "eval_id": "qm-stage2-prereg-v1",
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "execute": bool(args.execute),
        "strict_prereg": bool(args.strict_prereg),
        "with_coupling_audit": bool(args.with_coupling_audit),
        "resume_qm_lane": bool(args.resume_qm_lane),
        "chunk_size": args.chunk_size,
        "resume_coupling": bool(args.resume_coupling),
        "write_artifacts": bool(args.write_artifacts),
        "plots": bool(args.plots),
        "blocks": [
            {
                "block_id": b.block_id,
                "datasets": list(b.datasets),
                "seed_start": b.seed_start,
                "seed_end": b.seed_end,
            }
            for b in blocks
        ],
        "planned_commands_txt": plan_txt.as_posix(),
        "summary_csv": summary_csv.as_posix(),
        "report_md": report_md.as_posix(),
        "decision": decision,
        "command_runs": [
            {
                "block_id": r["block_id"],
                "step": r["step"],
                "rc": r["rc"],
                "cmd": r["cmd"],
            }
            for r in command_runs
        ],
    }
    manifest_json = out_dir / "manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run_log = out_dir / "run-log.txt"
    run_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"planned_commands: {plan_txt}")
    print(f"summary_csv:      {summary_csv}")
    print(f"report_md:        {report_md}")
    print(f"manifest_json:    {manifest_json}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
