#!/usr/bin/env python3
"""
Bundle per-block QM-GR coupling audit v2 outputs into one package.

Tooling-only:
- reads existing block manifests + dataset summaries
- writes combined block summary/report/manifest
- does not change any gate formulas or thresholds
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_BASE_DIR = ART / "qm-gr-coupling-audit-v2"
DEFAULT_OUT_DIR = DEFAULT_BASE_DIR / "bundle-v1"

DEFAULT_BLOCK_DIRS = [
    DEFAULT_BASE_DIR / "primary_ds002_003_006_s3401_3600",
    DEFAULT_BASE_DIR / "attack_seed500_ds002_003_006_s3601_4100",
    DEFAULT_BASE_DIR / "holdout_ds004_008_s3401_3600",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bundle QM-GR coupling audit v2 per-block artifacts.")
    p.add_argument(
        "--block-dirs",
        default=",".join(str(p) for p in DEFAULT_BLOCK_DIRS),
        help="Comma-separated coupling block directories (each must contain manifest.json).",
    )
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--bundle-id", default="qm-gr-coupling-audit-v2-bundle")
    return p.parse_args()


def parse_csv_list(text: str) -> list[Path]:
    out: list[Path] = []
    for tok in text.split(","):
        token = tok.strip()
        if token:
            out.append(Path(token).resolve())
    return out


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(str(value))
    except Exception:
        return default


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    block_dirs = parse_csv_list(args.block_dirs)
    if not block_dirs:
        raise RuntimeError("no block dirs provided")

    block_rows: list[dict[str, Any]] = []
    dataset_rows: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, str]] = {}

    total_expected = 0
    total_completed = 0
    total_missing = 0
    total_g20_pass = 0
    total_g20_rc_fail = 0

    all_pre = True
    all_post = True
    all_chunks = True

    for bdir in block_dirs:
        manifest_path = bdir / "manifest.json"
        dataset_path = bdir / "dataset_summary.csv"
        report_path = bdir / "report.md"
        summary_path = bdir / "summary.csv"
        chunk_path = bdir / "chunk_checks.csv"

        if not manifest_path.exists():
            raise FileNotFoundError(f"missing manifest: {manifest_path}")
        if not dataset_path.exists():
            raise FileNotFoundError(f"missing dataset summary: {dataset_path}")

        m = read_json(manifest_path)
        block_id = bdir.name

        expected = safe_int(m.get("profiles_total_expected", 0))
        completed = safe_int(m.get("profiles_completed", 0))
        missing = safe_int(m.get("profiles_missing", max(0, expected - completed)))
        g20_pass = safe_int(m.get("g20_pass", 0))
        g20_rc_fail = safe_int(m.get("g20_rc_fail_profiles", 0))
        pre = bool(m.get("gr_guard_pre_all_pass", False))
        post = bool(m.get("gr_guard_post_all_pass", False))
        chunk_ok = bool(m.get("chunk_decisions_all_pass", False))

        total_expected += expected
        total_completed += completed
        total_missing += missing
        total_g20_pass += g20_pass
        total_g20_rc_fail += g20_rc_fail
        all_pre = all_pre and pre
        all_post = all_post and post
        all_chunks = all_chunks and chunk_ok

        block_rows.append(
            {
                "block_id": block_id,
                "seed_min": safe_int(m.get("seed_min", 0)),
                "seed_max": safe_int(m.get("seed_max", 0)),
                "profiles_total_expected": expected,
                "profiles_completed": completed,
                "profiles_missing": missing,
                "g20_pass": g20_pass,
                "g20_rc_fail_profiles": g20_rc_fail,
                "gr_guard_pre_all_pass": "true" if pre else "false",
                "gr_guard_post_all_pass": "true" if post else "false",
                "chunk_decisions_all_pass": "true" if chunk_ok else "false",
                "write_artifacts": str(m.get("write_artifacts", "")),
                "plots": str(m.get("plots", "")),
                "manifest_path": manifest_path.as_posix(),
                "summary_csv_path": summary_path.as_posix(),
                "dataset_summary_csv_path": dataset_path.as_posix(),
                "chunk_checks_csv_path": chunk_path.as_posix(),
                "report_md_path": report_path.as_posix(),
            }
        )

        artifacts[block_id] = {
            "manifest_json": manifest_path.as_posix(),
            "summary_csv": summary_path.as_posix(),
            "dataset_summary_csv": dataset_path.as_posix(),
            "chunk_checks_csv": chunk_path.as_posix(),
            "report_md": report_path.as_posix(),
        }

        for dr in read_csv(dataset_path):
            dataset_rows.append(
                {
                    "block_id": block_id,
                    "dataset_id": dr.get("dataset_id", ""),
                    "n_profiles": safe_int(dr.get("n_profiles", 0)),
                    "g20_pass": safe_int(dr.get("g20_pass", 0)),
                    "g20_rc_fail_profiles": safe_int(dr.get("g20_rc_fail_profiles", 0)),
                }
            )

    block_rows.sort(key=lambda r: str(r["block_id"]))
    dataset_rows.sort(key=lambda r: (str(r["block_id"]), str(r["dataset_id"])))

    write_csv(
        out_dir / "block_summary.csv",
        block_rows,
        [
            "block_id",
            "seed_min",
            "seed_max",
            "profiles_total_expected",
            "profiles_completed",
            "profiles_missing",
            "g20_pass",
            "g20_rc_fail_profiles",
            "gr_guard_pre_all_pass",
            "gr_guard_post_all_pass",
            "chunk_decisions_all_pass",
            "write_artifacts",
            "plots",
            "manifest_path",
            "summary_csv_path",
            "dataset_summary_csv_path",
            "chunk_checks_csv_path",
            "report_md_path",
        ],
    )
    write_csv(
        out_dir / "dataset_summary.csv",
        dataset_rows,
        ["block_id", "dataset_id", "n_profiles", "g20_pass", "g20_rc_fail_profiles"],
    )

    overall_pass = (
        total_missing == 0
        and total_completed == total_expected
        and total_g20_pass == total_completed
        and total_g20_rc_fail == 0
        and all_pre
        and all_post
        and all_chunks
    )
    overall_decision = "PASS" if overall_pass else "HOLD"

    generated_utc = datetime.now(timezone.utc).isoformat()
    lines: list[str] = []
    lines.append("# QM-GR Coupling Audit v2 Bundle")
    lines.append("")
    lines.append(f"- generated_utc: `{generated_utc}`")
    lines.append(f"- bundle_id: `{args.bundle_id}`")
    lines.append(f"- blocks: `{len(block_rows)}`")
    lines.append(f"- profiles_total_expected: `{total_expected}`")
    lines.append(f"- profiles_completed: `{total_completed}`")
    lines.append(f"- profiles_missing: `{total_missing}`")
    lines.append(f"- g20_pass: `{total_g20_pass}/{total_completed}`")
    lines.append(f"- g20_rc_fail_profiles: `{total_g20_rc_fail}`")
    lines.append(f"- gr_guard_pre_all_pass: `{'true' if all_pre else 'false'}`")
    lines.append(f"- gr_guard_post_all_pass: `{'true' if all_post else 'false'}`")
    lines.append(f"- chunk_decisions_all_pass: `{'true' if all_chunks else 'false'}`")
    lines.append(f"- overall_decision: `{overall_decision}`")
    lines.append("")
    lines.append("## Blocks")
    lines.append("")
    for r in block_rows:
        lines.append(
            f"- `{r['block_id']}`: completed `{r['profiles_completed']}/{r['profiles_total_expected']}`, "
            f"g20 `{r['g20_pass']}/{r['profiles_completed']}`, missing `{r['profiles_missing']}`, "
            f"pre `{r['gr_guard_pre_all_pass']}`, post `{r['gr_guard_post_all_pass']}`"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Bundle is tooling/aggregation only.")
    lines.append("- No thresholds/formulas changed.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": generated_utc,
        "bundle_id": args.bundle_id,
        "overall_decision": overall_decision,
        "totals": {
            "blocks": len(block_rows),
            "profiles_total_expected": total_expected,
            "profiles_completed": total_completed,
            "profiles_missing": total_missing,
            "g20_pass": total_g20_pass,
            "g20_rc_fail_profiles": total_g20_rc_fail,
            "gr_guard_pre_all_pass": all_pre,
            "gr_guard_post_all_pass": all_post,
            "chunk_decisions_all_pass": all_chunks,
        },
        "artifacts": {
            "block_summary_csv": (out_dir / "block_summary.csv").as_posix(),
            "dataset_summary_csv": (out_dir / "dataset_summary.csv").as_posix(),
            "report_md": (out_dir / "report.md").as_posix(),
            "source_blocks": artifacts,
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(f"block_summary_csv: {out_dir / 'block_summary.csv'}")
    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:          {out_dir / 'report.md'}")
    print(f"manifest_json:      {out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

