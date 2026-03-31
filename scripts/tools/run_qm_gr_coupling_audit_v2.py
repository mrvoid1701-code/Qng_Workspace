#!/usr/bin/env python3
"""
Run QM-GR coupling audit package (v2) with chunking + resume.

Engineering goals:
- resumable long runs over dataset/seed grids
- timeout-safe chunk execution
- atomic append/update of a single summary CSV
- optional reduced artifact writes via --no-write-artifacts / --no-plots

Physics logic and thresholds are unchanged.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "scripts" / "tools"
SCRIPTS = ROOT / "scripts"
DEFAULT_DS_LIST = "DS-002,DS-003,DS-006"
DEFAULT_SEED_MIN = 3401
DEFAULT_SEED_MAX = 3600
DEFAULT_CHUNK_SIZE = 25
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qm-gr-coupling-audit-v2"
DEFAULT_GR_BASELINE = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-regression-baseline-v1"
    / "gr_stage3_baseline_official.json"
)
DEFAULT_GR_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-official-v3-rerun-v1"
    / "summary.csv"
)


@dataclass(frozen=True)
class Profile:
    dataset_id: str
    seed: int


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run chunked/resumable QM-GR coupling audit (v2).")
    p.add_argument("--ds-list", default=DEFAULT_DS_LIST)
    p.add_argument("--seed-min", type=int, default=DEFAULT_SEED_MIN)
    p.add_argument("--seed-max", type=int, default=DEFAULT_SEED_MAX)
    p.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--gr-baseline-json", default=str(DEFAULT_GR_BASELINE))
    p.add_argument("--gr-summary-csv", default=str(DEFAULT_GR_SUMMARY))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--plots", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=False)
    return p.parse_args()


def norm_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


def split_key(key: str) -> tuple[str, int]:
    ds, seed = key.split("::", 1)
    return ds, int(seed)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def atomic_write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        env={**os.environ, **{"PYTHONUTF8": "1"}},
    )
    merged = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    tail = "\n".join(merged.splitlines()[-10:]) if merged else ""
    return proc.returncode, tail


def read_metric_final_status(path: Path) -> str:
    if not path.exists():
        return "fail"
    rows = read_csv(path)
    by_gate: dict[str, str] = {}
    for row in rows:
        gid = (row.get("gate_id") or "").strip()
        if gid:
            by_gate[gid] = norm_status(row.get("status", ""))
    if "FINAL" in by_gate:
        return by_gate["FINAL"]
    non_final = [st for gid, st in by_gate.items() if gid != "FINAL"]
    if non_final and all(st == "pass" for st in non_final):
        return "pass"
    return "fail"


def run_gr_guard(baseline_json: Path, summary_csv: Path, out_dir: Path) -> tuple[int, str, Path]:
    cmd = [
        sys.executable,
        str(TOOLS / "run_gr_stage3_regression_guard_v1.py"),
        "--baseline-json",
        str(baseline_json),
        "--summary-csv",
        str(summary_csv),
        "--out-dir",
        str(out_dir),
        "--no-strict-exit",
    ]
    rc, _ = run_cmd(cmd, ROOT)
    report_json = out_dir / "regression_report.json"
    if not report_json.exists():
        return rc, "missing_report", report_json
    report = json.loads(report_json.read_text(encoding="utf-8"))
    return rc, str(report.get("decision", "FAIL")), report_json


def chunked(items: list[Profile], size: int) -> list[list[Profile]]:
    if size <= 0:
        raise ValueError("chunk-size must be > 0")
    return [items[i : i + size] for i in range(0, len(items), size)]


def build_profiles(ds_list: str, seed_min: int, seed_max: int) -> list[Profile]:
    if seed_max < seed_min:
        raise ValueError("seed-max must be >= seed-min")
    datasets = parse_csv_list(ds_list)
    if not datasets:
        raise ValueError("ds-list is empty")
    out: list[Profile] = []
    for ds in datasets:
        for seed in range(seed_min, seed_max + 1):
            out.append(Profile(dataset_id=ds.upper(), seed=seed))
    return out


def relative_or_empty(path: Path, *, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return ""


def summary_fieldnames() -> list[str]:
    return [
        "dataset_id",
        "seed",
        "run_root",
        "g20_status",
        "g20_rc",
        "chunk_id",
    ]


def dataset_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g20_pass": sum(1 for r in sub if str(r["g20_status"]) == "pass"),
                "g20_rc_fail_profiles": sum(1 for r in sub if int(str(r["g20_rc"])) != 0),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    gr_baseline = Path(args.gr_baseline_json).resolve()
    gr_summary = Path(args.gr_summary_csv).resolve()
    if not gr_baseline.exists():
        raise FileNotFoundError(f"gr baseline missing: {gr_baseline}")
    if not gr_summary.exists():
        raise FileNotFoundError(f"gr summary missing: {gr_summary}")

    summary_csv = out_dir / "summary.csv"
    chunk_checks_csv = out_dir / "chunk_checks.csv"
    run_log = out_dir / "run-log.txt"

    all_profiles = build_profiles(args.ds_list, args.seed_min, args.seed_max)
    expected_keys = {key_of(p.dataset_id, p.seed) for p in all_profiles}

    log_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        log_lines.append(msg)

    existing_map: dict[str, dict[str, Any]] = {}
    if summary_csv.exists():
        existing_rows = read_csv(summary_csv)
        for r in existing_rows:
            try:
                ds = str(r.get("dataset_id", "")).strip().upper()
                seed = int(str(r.get("seed", "0")))
            except Exception:
                continue
            k = key_of(ds, seed)
            if k in expected_keys:
                existing_map[k] = {
                    "dataset_id": ds,
                    "seed": seed,
                    "run_root": str(r.get("run_root", "")),
                    "g20_status": norm_status(str(r.get("g20_status", ""))),
                    "g20_rc": int(str(r.get("g20_rc", "1"))),
                    "chunk_id": int(str(r.get("chunk_id", "0")) or "0"),
                }

    if summary_csv.exists() and existing_map and not args.resume:
        raise RuntimeError(f"summary.csv already exists at {summary_csv}; rerun with --resume")

    pending = [p for p in all_profiles if key_of(p.dataset_id, p.seed) not in existing_map]
    chunks = chunked(pending, args.chunk_size) if pending else []

    log("=" * 80)
    log("QM-GR coupling audit v2 (chunked/resumable)")
    log(f"generated_utc={datetime.utcnow().isoformat()}Z")
    log(f"out_dir={out_dir}")
    log(f"profiles_total={len(all_profiles)}")
    log(f"profiles_existing={len(existing_map)}")
    log(f"profiles_pending={len(pending)}")
    log(f"chunk_size={args.chunk_size} chunks={len(chunks)} resume={str(args.resume).lower()}")
    log(f"write_artifacts={str(args.write_artifacts).lower()} plots={str(args.plots).lower()}")
    log("=" * 80)

    rows_map = dict(existing_map)
    chunk_rows: list[dict[str, Any]] = []
    if chunk_checks_csv.exists() and args.resume:
        for r in read_csv(chunk_checks_csv):
            chunk_rows.append(dict(r))

    for idx, chunk in enumerate(chunks, start=1):
        chunk_id = (len(chunk_rows) + 1)
        ctag = f"chunk_{chunk_id:04d}"
        log(f"\n[{ctag}] start profiles={len(chunk)}")

        pre_dir = out_dir / "gr_guard_chunks" / f"{ctag}_pre"
        pre_rc, pre_decision, _ = run_gr_guard(gr_baseline, gr_summary, pre_dir)
        log(f"[{ctag}] guard-pre rc={pre_rc} decision={pre_decision}")

        g20_pass = 0
        g20_rc_fail = 0
        for pidx, p in enumerate(chunk, start=1):
            tag = f"{p.dataset_id.lower()}_seed{p.seed}"
            if args.write_artifacts:
                profile_root = out_dir / "runs" / tag / "g20"
                run_root = relative_or_empty(profile_root, root=ROOT)
            else:
                profile_root = out_dir / "_tmp_runs" / tag / "g20"
                run_root = ""

            cmd = [
                sys.executable,
                str(SCRIPTS / "run_qng_semiclassical_v1.py"),
                "--dataset-id",
                p.dataset_id,
                "--seed",
                str(p.seed),
                "--out-dir",
                str(profile_root),
            ]
            if not args.write_artifacts:
                cmd.append("--no-write-artifacts")
            if not args.plots:
                cmd.append("--no-plots")

            rc, tail = run_cmd(cmd, ROOT)
            status = read_metric_final_status(profile_root / "metric_checks_semi.csv")
            if status == "pass":
                g20_pass += 1
            if rc != 0:
                g20_rc_fail += 1

            rows_map[key_of(p.dataset_id, p.seed)] = {
                "dataset_id": p.dataset_id,
                "seed": p.seed,
                "run_root": run_root,
                "g20_status": status,
                "g20_rc": rc,
                "chunk_id": chunk_id,
            }

            if not args.write_artifacts:
                tmp_tag_root = profile_root.parent.parent
                if tmp_tag_root.exists():
                    shutil.rmtree(tmp_tag_root, ignore_errors=True)

            log(
                f"[{ctag} {pidx}/{len(chunk)}] {tag} rc={rc} status={status}"
            )
            if rc != 0 and tail:
                for line in tail.splitlines():
                    log(f"    {line}")

        post_dir = out_dir / "gr_guard_chunks" / f"{ctag}_post"
        post_rc, post_decision, _ = run_gr_guard(gr_baseline, gr_summary, post_dir)
        log(f"[{ctag}] guard-post rc={post_rc} decision={post_decision}")

        sorted_rows = sorted(rows_map.values(), key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
        atomic_write_csv(summary_csv, sorted_rows, summary_fieldnames())

        chunk_row = {
            "chunk_id": chunk_id,
            "chunk_label": ctag,
            "profiles_in_chunk": len(chunk),
            "g20_pass": g20_pass,
            "g20_rc_fail_profiles": g20_rc_fail,
            "gr_guard_pre_rc": pre_rc,
            "gr_guard_pre_decision": pre_decision,
            "gr_guard_post_rc": post_rc,
            "gr_guard_post_decision": post_decision,
            "chunk_decision": (
                "PASS"
                if (pre_decision == "PASS" and post_decision == "PASS" and g20_rc_fail == 0)
                else "FAIL"
            ),
        }
        chunk_rows.append(chunk_row)
        atomic_write_csv(
            chunk_checks_csv,
            chunk_rows,
            [
                "chunk_id",
                "chunk_label",
                "profiles_in_chunk",
                "g20_pass",
                "g20_rc_fail_profiles",
                "gr_guard_pre_rc",
                "gr_guard_pre_decision",
                "gr_guard_post_rc",
                "gr_guard_post_decision",
                "chunk_decision",
            ],
        )
        run_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    final_rows = sorted(rows_map.values(), key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    atomic_write_csv(summary_csv, final_rows, summary_fieldnames())

    ds_rows = dataset_summary(final_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    atomic_write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()) if ds_rows else ["dataset_id"])

    done_keys = {key_of(str(r["dataset_id"]), int(str(r["seed"]))) for r in final_rows}
    missing_keys = sorted(expected_keys - done_keys)
    missing_profiles = [split_key(k) for k in missing_keys]
    g20_pass_total = sum(1 for r in final_rows if str(r["g20_status"]) == "pass")
    g20_rc_fail_total = sum(1 for r in final_rows if int(str(r["g20_rc"])) != 0)
    pre_all_pass = all(str(r.get("gr_guard_pre_decision", "")) == "PASS" for r in chunk_rows) if chunk_rows else True
    post_all_pass = all(str(r.get("gr_guard_post_decision", "")) == "PASS" for r in chunk_rows) if chunk_rows else True
    chunk_decision_all = all(str(r.get("chunk_decision", "")) == "PASS" for r in chunk_rows) if chunk_rows else True

    report_lines = [
        "# QM-GR Coupling Audit Report (v2)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- out_dir: `{out_dir.as_posix()}`",
        f"- profiles_total_expected: `{len(all_profiles)}`",
        f"- profiles_completed: `{len(final_rows)}`",
        f"- profiles_missing: `{len(missing_profiles)}`",
        f"- chunks_executed: `{len(chunk_rows)}`",
        f"- g20_pass: `{g20_pass_total}/{len(final_rows) if final_rows else 0}`",
        f"- g20_rc_fail_profiles: `{g20_rc_fail_total}`",
        f"- gr_guard_pre_all_pass: `{'true' if pre_all_pass else 'false'}`",
        f"- gr_guard_post_all_pass: `{'true' if post_all_pass else 'false'}`",
        f"- chunk_decisions_all_pass: `{'true' if chunk_decision_all else 'false'}`",
        "",
        "## Notes",
        "",
        "- Each chunk runs G20 profiles plus GR guard pre/post checks.",
        "- Summary CSV is updated atomically after each chunk.",
        "- With `--resume`, already completed profiles in summary.csv are skipped.",
    ]
    if missing_profiles:
        report_lines.extend(
            [
                "",
                "## Missing Profiles",
                "",
                f"- missing_count: `{len(missing_profiles)}`",
                f"- first_missing: `{missing_profiles[0][0]} seed {missing_profiles[0][1]}`",
            ]
        )

    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "policy_id": "qm-gr-coupling-audit-v2",
        "ds_list": parse_csv_list(args.ds_list),
        "seed_min": args.seed_min,
        "seed_max": args.seed_max,
        "chunk_size": args.chunk_size,
        "resume": bool(args.resume),
        "write_artifacts": bool(args.write_artifacts),
        "plots": bool(args.plots),
        "profiles_total_expected": len(all_profiles),
        "profiles_completed": len(final_rows),
        "profiles_missing": len(missing_profiles),
        "g20_pass": g20_pass_total,
        "g20_rc_fail_profiles": g20_rc_fail_total,
        "gr_guard_pre_all_pass": pre_all_pass,
        "gr_guard_post_all_pass": post_all_pass,
        "chunk_decisions_all_pass": chunk_decision_all,
        "gr_baseline_json": gr_baseline.as_posix(),
        "gr_summary_csv": gr_summary.as_posix(),
        "artifacts": {
            "summary_csv": summary_csv.as_posix(),
            "dataset_summary_csv": dataset_csv.as_posix(),
            "chunk_checks_csv": chunk_checks_csv.as_posix(),
            "report_md": report_md.as_posix(),
            "run_log_txt": run_log.as_posix(),
        },
    }
    manifest_json = out_dir / "manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run_log.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print(f"summary_csv:      {summary_csv}")
    print(f"dataset_csv:      {dataset_csv}")
    print(f"chunk_checks_csv: {chunk_checks_csv}")
    print(f"report_md:        {report_md}")
    print(f"manifest_json:    {manifest_json}")

    if args.strict_exit and (
        len(missing_profiles) > 0 or g20_rc_fail_total > 0 or not pre_all_pass or not post_all_pass
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
