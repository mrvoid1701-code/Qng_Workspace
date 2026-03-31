#!/usr/bin/env python3
"""
Run stability convergence v6 extended audit v1 (post-freeze).

This orchestrates:
- stress generation for primary/attack/shifted-holdout blocks
- legacy v5-like convergence gate
- official v6 convergence gate
- aggregated promotion-style evaluator

Supports --resume to skip completed block stages.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "scripts" / "tools"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v6-extended-v1"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v6-extended-v1.md"


@dataclass(frozen=True)
class Block:
    block_id: str
    dataset_id: str
    seed_min: int
    seed_max: int
    n_nodes_list: str
    steps_list: str
    holdout_shifted: bool = False

    def seed_list_csv(self) -> str:
        return ",".join(str(s) for s in range(self.seed_min, self.seed_max + 1))


BLOCKS = [
    Block(
        block_id="primary_s3401_3600",
        dataset_id="STABILITY-CONVERGENCE-V6-EXT-PRIMARY",
        seed_min=3401,
        seed_max=3600,
        n_nodes_list="24,28,32,36,40,44,48",
        steps_list="60",
    ),
    Block(
        block_id="attack_s3601_3800",
        dataset_id="STABILITY-CONVERGENCE-V6-EXT-ATTACK",
        seed_min=3601,
        seed_max=3800,
        n_nodes_list="24,28,32,36,40,44,48",
        steps_list="60",
    ),
    Block(
        block_id="holdout_shifted_s3801_4000",
        dataset_id="STABILITY-CONVERGENCE-V6-EXT-HOLDOUT",
        seed_min=3801,
        seed_max=4000,
        n_nodes_list="30,36,42,48",
        steps_list="80",
        holdout_shifted=True,
    ),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence v6 extended audit v1.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--prereg-doc", default=str(DEFAULT_PREREG))
    p.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def cmd_str(cmd: list[str]) -> str:
    out: list[str] = []
    for c in cmd:
        if " " in c:
            out.append(f"\"{c}\"")
        else:
            out.append(c)
    return " ".join(out)


def run_cmd(cmd: list[str], log_path: Path) -> tuple[int, float]:
    started = time.time()
    with log_path.open("a", encoding="utf-8") as logf:
        logf.write(f"\n$ {cmd_str(cmd)}\n")
        logf.flush()
        proc = subprocess.run(cmd, cwd=str(ROOT), stdout=logf, stderr=logf, text=True)
    elapsed = time.time() - started
    return proc.returncode, elapsed


def should_skip(path: Path, resume: bool) -> bool:
    return resume and path.exists()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    prereg_doc = Path(args.prereg_doc).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "run-log.txt"

    manifest: dict[str, object] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "out_dir": out_dir.as_posix(),
        "prereg_doc": prereg_doc.as_posix() if prereg_doc.exists() else "",
        "resume": bool(args.resume),
        "blocks": [],
        "steps": [],
        "decision": "PASS",
        "failures": [],
    }

    for block in BLOCKS:
        block_root = out_dir / block.block_id
        raw_dir = block_root / "raw"
        legacy_dir = block_root / "legacy_v5like"
        v6_dir = block_root / "v6_candidate"
        raw_summary = raw_dir / "summary.csv"
        legacy_report = legacy_dir / "report.json"
        v6_report = v6_dir / "report.json"

        manifest["blocks"].append(
            {
                "block_id": block.block_id,
                "dataset_id": block.dataset_id,
                "seed_min": block.seed_min,
                "seed_max": block.seed_max,
                "n_nodes_list": block.n_nodes_list,
                "steps_list": block.steps_list,
                "holdout_shifted": block.holdout_shifted,
            }
        )

        stress_cmd = [
            sys.executable,
            str(TOOLS / "run_stability_stress_v1.py"),
            "--dataset-id",
            block.dataset_id,
            "--seed-list",
            block.seed_list_csv(),
            "--n-nodes-list",
            block.n_nodes_list,
            "--steps-list",
            block.steps_list,
            "--out-dir",
            str(raw_dir),
            "--no-strict-exit",
        ]
        if block.holdout_shifted:
            stress_cmd.extend(
                [
                    "--edge-prob-grid",
                    "0.05,0.12,0.25",
                    "--chi-scale-grid",
                    "0.40,1.00,1.80",
                    "--noise-grid",
                    "0.00,0.02,0.05",
                    "--phi-shock-grid",
                    "0.00,0.60",
                ]
            )

        if not should_skip(raw_summary, bool(args.resume)):
            rc, elapsed = run_cmd(stress_cmd, log_path)
            manifest["steps"].append(
                {"block_id": block.block_id, "stage": "stress", "rc": rc, "elapsed_sec": round(elapsed, 3), "cmd": cmd_str(stress_cmd)}
            )
            if rc != 0:
                manifest["decision"] = "FAIL"
                manifest["failures"].append(f"{block.block_id}:stress")
                if args.strict_exit:
                    break
        else:
            manifest["steps"].append({"block_id": block.block_id, "stage": "stress", "skipped": True, "reason": "resume_summary_exists"})

        legacy_cmd = [
            sys.executable,
            str(TOOLS / "run_stability_convergence_gate_v4.py"),
            "--summary-csv",
            str(raw_summary),
            "--out-dir",
            str(legacy_dir),
            "--prereg-doc",
            str(ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v5.md"),
            "--full-metric-field",
            "delta_energy_rel",
            "--bulk-metric-field",
            "delta_energy_rel",
            "--step-tol",
            "0.002",
            "--full-step-fraction-min",
            "0.75",
            "--bulk-step-fraction-min",
            "0.85",
            "--overall-improvement-min",
            "0.005",
            "--support-worsen-factor-max",
            "1.25",
            "--rho-full-max",
            "-0.60",
            "--full-seed-pass-fraction-min",
            "0.85",
            "--bulk-seed-pass-fraction-min",
            "0.85",
            "--bulk-min-profiles-per-level",
            "5",
            "--bulk-core-size-min",
            "6",
            "--bulk-core-ratio-min",
            "0.10",
            "--bulk-bootstrap-reps",
            "400",
            "--bulk-ci-alpha",
            "0.05",
            "--no-strict-exit",
        ]
        if not should_skip(legacy_report, bool(args.resume)):
            rc, elapsed = run_cmd(legacy_cmd, log_path)
            manifest["steps"].append(
                {"block_id": block.block_id, "stage": "legacy_gate", "rc": rc, "elapsed_sec": round(elapsed, 3), "cmd": cmd_str(legacy_cmd)}
            )
            if rc != 0:
                manifest["decision"] = "FAIL"
                manifest["failures"].append(f"{block.block_id}:legacy_gate")
                if args.strict_exit:
                    break
        else:
            manifest["steps"].append({"block_id": block.block_id, "stage": "legacy_gate", "skipped": True, "reason": "resume_report_exists"})

        v6_cmd = [
            sys.executable,
            str(TOOLS / "run_stability_convergence_gate_v6.py"),
            "--summary-csv",
            str(raw_summary),
            "--out-dir",
            str(v6_dir),
            "--prereg-doc",
            str(ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v6.md"),
            "--full-metric-field",
            "delta_energy_rel",
            "--bulk-metric-field",
            "delta_energy_rel",
            "--bulk-core-size-min",
            "6",
            "--bulk-core-ratio-min",
            "0.10",
            "--bulk-min-profiles-per-level",
            "5",
            "--bootstrap-reps",
            "2000",
            "--ci-alpha",
            "0.05",
            "--no-strict-exit",
        ]
        if not should_skip(v6_report, bool(args.resume)):
            rc, elapsed = run_cmd(v6_cmd, log_path)
            manifest["steps"].append(
                {"block_id": block.block_id, "stage": "v6_gate", "rc": rc, "elapsed_sec": round(elapsed, 3), "cmd": cmd_str(v6_cmd)}
            )
            if rc != 0:
                manifest["decision"] = "FAIL"
                manifest["failures"].append(f"{block.block_id}:v6_gate")
                if args.strict_exit:
                    break
        else:
            manifest["steps"].append({"block_id": block.block_id, "stage": "v6_gate", "skipped": True, "reason": "resume_report_exists"})

    eval_cmd = [
        sys.executable,
        str(TOOLS / "evaluate_stability_convergence_v6_promotion_v1.py"),
        "--audit-root",
        str(out_dir),
        "--blocks",
        ",".join(b.block_id for b in BLOCKS),
        "--out-dir",
        str(out_dir),
        "--eval-id",
        "stability-convergence-v6-extended-promotion-eval-v1",
        "--no-strict-exit",
    ]
    rc, elapsed = run_cmd(eval_cmd, log_path)
    manifest["steps"].append({"stage": "aggregate_eval", "rc": rc, "elapsed_sec": round(elapsed, 3), "cmd": cmd_str(eval_cmd)})
    if rc != 0:
        manifest["decision"] = "FAIL"
        manifest["failures"].append("aggregate_eval")

    report_json = out_dir / "promotion_report.json"
    if report_json.exists():
        try:
            rep = json.loads(report_json.read_text(encoding="utf-8"))
            manifest["aggregate_decision"] = rep.get("decision", "")
            if str(rep.get("decision", "")).upper() != "PASS":
                manifest["decision"] = "FAIL"
        except Exception:
            pass

    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"out_dir:       {out_dir.as_posix()}")
    print(f"promotion:     {(out_dir / 'promotion_report.json').as_posix()}")
    print(f"manifest_json: {manifest_path.as_posix()}")
    print(f"run_log:       {log_path.as_posix()}")

    if args.strict_exit and str(manifest.get("decision", "PASS")) != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
