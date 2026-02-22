#!/usr/bin/env python3
"""
Build a reproducibility freeze package for Gold Pack v1.

Outputs:
- 07_exports/gold-pack-v1/gold-pack-v1-manifest.json
- 07_exports/gold-pack-v1/gold-pack-v1-artifact-hashes.csv
- 07_exports/gold-pack-v1/gold-pack-v1-freeze-status.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"
RUN_MANIFEST_DIR = ROOT / "05_validation" / "run-manifests"
OUT_DIR = ROOT / "07_exports" / "gold-pack-v1"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def split_md_row(line: str) -> list[str]:
    raw = line.strip()
    if not raw.startswith("|") or not raw.endswith("|"):
        return []
    body = raw[1:-1]
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            cur.append(body[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def parse_results_rows() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    lines = RESULTS_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    in_table = False
    for line in lines:
        if line.strip().startswith("| Test ID | Priority | Claim | Exec status |"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = split_md_row(line)
            if len(cells) < 12:
                continue
            test_id = cells[0].strip()
            if not TEST_ID_RE.match(test_id):
                continue
            claim_match = CLAIM_HEAD_RE.match(cells[2].strip())
            if not claim_match:
                continue
            rows[test_id] = {
                "test_id": test_id,
                "priority": cells[1].strip(),
                "claim_id": claim_match.group(1),
                "claim_statement": claim_match.group(2),
                "exec_status": cells[3].strip().lower(),
                "last_run": cells[4].strip(),
                "evidence_path": cells[5].strip(),
                "metric_value": cells[6].strip(),
                "decision_note": cells[7].strip(),
                "next_action": cells[8].strip(),
                "authenticity": cells[9].strip().lower(),
                "leakage_risk": cells[10].strip().lower(),
                "negative_control": cells[11].strip().lower(),
            }
    return rows


def read_run_manifest(test_id: str) -> dict:
    path = RUN_MANIFEST_DIR / f"{test_id.lower()}.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing run manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def csv_metric_map(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:
                continue
            if i == 0 and row[0].strip().lower() == "metric":
                continue
            if len(row) < 2:
                continue
            key = row[0].strip()
            val = row[1].strip()
            if key:
                out[key] = val
    return out


def normalize_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def path_from_manifest_entry(entry: str) -> Path | None:
    try:
        p = Path(entry)
    except Exception:
        return None
    if p.is_absolute():
        try:
            p.resolve().relative_to(ROOT.resolve())
            return p
        except Exception:
            return None
    return (ROOT / p).resolve()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_path(rel_path: str) -> str:
    if rel_path.startswith("05_validation/evidence/artifacts/"):
        return "artifact"
    if rel_path.startswith("05_validation/run-manifests/"):
        return "run-manifest"
    if rel_path.startswith("05_validation/"):
        return "validation-core"
    if rel_path.startswith("scripts/"):
        return "script"
    if rel_path.startswith("data/"):
        return "dataset"
    if rel_path.startswith("06_writing/") or rel_path.startswith("07_exports/"):
        return "writing-export"
    return "workspace"


def run_lint() -> tuple[bool, str]:
    lint_path = ROOT / "scripts" / "lint_workspace.py"
    if not lint_path.exists():
        return False, "lint script missing"
    proc = subprocess.run(
        [sys.executable, str(lint_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    output = (proc.stdout or "").strip()
    if proc.stderr:
        output = (output + "\n" + proc.stderr.strip()).strip()
    return proc.returncode == 0, output


def build_hash_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for p in sorted(paths, key=lambda x: normalize_rel(x)):
        rel = normalize_rel(p)
        exists = p.exists() and p.is_file()
        size = p.stat().st_size if exists else 0
        sha = sha256_file(p) if exists else ""
        mtime = (
            datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            if exists
            else ""
        )
        rows.append(
            {
                "path": rel,
                "category": classify_path(rel),
                "exists": "true" if exists else "false",
                "size_bytes": str(size),
                "sha256": sha,
                "mtime_utc": mtime,
            }
        )
    return rows


def write_hash_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["path", "category", "exists", "size_bytes", "sha256", "mtime_utc"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_status_md(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Gold Pack v1 freeze bundle.")
    p.add_argument("--tests", default="QNG-T-027,QNG-T-039", help="Comma-separated test ids")
    p.add_argument("--out-dir", default=str(OUT_DIR), help="Output folder")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    test_ids = [t.strip().upper() for t in args.tests.split(",") if t.strip()]
    if not test_ids:
        raise SystemExit("No test ids provided.")

    results_rows = parse_results_rows()
    run_manifests: dict[str, dict] = {}
    selected_rows: dict[str, dict] = {}
    missing: list[str] = []
    for test_id in test_ids:
        row = results_rows.get(test_id)
        if not row:
            missing.append(f"Missing results row for {test_id}")
            continue
        selected_rows[test_id] = row
        try:
            run_manifests[test_id] = read_run_manifest(test_id)
        except Exception as exc:
            missing.append(str(exc))

    if missing:
        raise SystemExit("Cannot build freeze package:\n- " + "\n- ".join(missing))

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    fixed_paths: list[Path] = [
        ROOT / "TASKS.md",
        ROOT / "05_validation" / "test-plan.md",
        ROOT / "05_validation" / "results-log.md",
        ROOT / "05_validation" / "dataset-manifest.json",
        ROOT / "05_validation" / "dataset-manifest.md",
        ROOT / "scripts" / "run_qng_t_027_lensing_dark.py",
        ROOT / "scripts" / "run_qng_t_027_negative_controls.py",
        ROOT / "scripts" / "import_ds006_downloads.py",
        ROOT / "scripts" / "lint_workspace.py",
        ROOT / "05_validation" / "evidence" / "qng-t-027-lensing_dark.md",
        ROOT / "05_validation" / "evidence" / "qng-t-039-lensing_dark.md",
    ]

    for test_id in test_ids:
        rm_path = RUN_MANIFEST_DIR / f"{test_id.lower()}.json"
        fixed_paths.append(rm_path)
        rm = run_manifests[test_id]
        for entry in rm.get("outputs", []):
            p = path_from_manifest_entry(str(entry))
            if p is not None:
                fixed_paths.append(p)
        ev_rel = selected_rows[test_id]["evidence_path"]
        if ev_rel:
            fixed_paths.append((ROOT / ev_rel).resolve())

    # Include direct artifacts for QNG-T-039 promotion path used in final evidence.
    if "QNG-T-039" in test_ids:
        direct_paths = [
            ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-direct" / "fit-summary.csv",
            ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-direct" / "model-comparison.md",
            ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-direct" / "robustness-checks.csv",
            ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-direct" / "negative-controls-summary.csv",
            ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-039-direct" / "promotion-gold.md",
        ]
        fixed_paths.extend(direct_paths)

    # Unique file paths.
    uniq: dict[str, Path] = {}
    for p in fixed_paths:
        rel = normalize_rel(p)
        uniq[rel.lower()] = p
    hash_rows = build_hash_rows(list(uniq.values()))

    hash_csv_path = out_dir / "gold-pack-v1-artifact-hashes.csv"
    write_hash_csv(hash_csv_path, hash_rows)

    lint_ok, lint_output = run_lint()
    no_git = not (ROOT / ".git").exists()

    test_entries: list[dict] = []
    for test_id in test_ids:
        row = selected_rows[test_id]
        rm = run_manifests[test_id]

        fit_summary_candidates = []
        for out in rm.get("outputs", []):
            out_text = str(out).replace("\\", "/")
            if out_text.endswith("/fit-summary.csv"):
                fit_summary_candidates.append((ROOT / out_text).resolve())
        if test_id == "QNG-T-039":
            fit_summary_candidates.insert(
                0,
                (ROOT / "05_validation/evidence/artifacts/qng-t-039-direct/fit-summary.csv").resolve(),
            )

        fit_metrics: dict[str, str] = {}
        fit_path = None
        for cand in fit_summary_candidates:
            if cand.exists():
                fit_path = cand
                fit_metrics = csv_metric_map(cand)
                break

        test_entries.append(
            {
                "test_id": test_id,
                "claim_id": row["claim_id"],
                "claim_statement": row["claim_statement"],
                "status": row["exec_status"],
                "authenticity": row["authenticity"],
                "leakage_risk": row["leakage_risk"],
                "negative_control": row["negative_control"],
                "last_run": row["last_run"],
                "metric_value_results_log": row["metric_value"],
                "evidence_path": row["evidence_path"],
                "run_manifest_path": f"05_validation/run-manifests/{test_id.lower()}.json",
                "seeds": {
                    "primary_seed": rm.get("parameters", {}).get("seed", rm.get("parameters", {}).get("primary_seed")),
                    "negative_control_seed": 97 if test_id == "QNG-T-027" else 197,
                },
                "fit_summary_path": normalize_rel(fit_path) if fit_path else "",
                "fit_metrics": {
                    "delta_chi2": fit_metrics.get("delta_chi2", ""),
                    "delta_aic": fit_metrics.get("delta_aic", ""),
                    "delta_bic": fit_metrics.get("delta_bic", ""),
                    "delta_chi2_per_point_total": fit_metrics.get("delta_chi2_per_point_total", ""),
                    "pass_recommendation": fit_metrics.get("pass_recommendation", ""),
                },
                "commands": rm.get("commands", []),
                "parameters": rm.get("parameters", {}),
            }
        )

    manifest = {
        "schema_version": "1.0",
        "pack_id": "gold-pack-v1",
        "generated_utc": now_utc(),
        "workspace_root": str(ROOT),
        "git": {
            "is_repo": not no_git,
            "tag_status": "blocked_no_git_repo" if no_git else "ready_for_tag",
            "requested_tag": "gold-pack-v1",
            "note": "Workspace has no .git directory; create/init repo before applying real git tag."
            if no_git
            else "Git repository detected.",
        },
        "alignment": {
            "lint_ok": lint_ok,
            "lint_output": lint_output,
            "results_and_manifests_targeted_tests": test_ids,
        },
        "global_parameters": {
            "dataset_id": "DS-006",
            "model_baseline": "gr_dm",
            "model_memory": "qng_sigma_memory",
            "strict_input": True,
            "same_sample_same_sigma_same_likelihood_policy": True,
        },
        "tests": test_entries,
        "hash_inventory_path": "07_exports/gold-pack-v1/gold-pack-v1-artifact-hashes.csv",
        "hash_file_count": len(hash_rows),
    }

    manifest_path = out_dir / "gold-pack-v1-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    status_lines = [
        "# Gold Pack v1 Freeze Status",
        "",
        f"- Generated (UTC): `{manifest['generated_utc']}`",
        f"- Pack manifest: `07_exports/gold-pack-v1/{manifest_path.name}`",
        f"- Hash inventory: `07_exports/gold-pack-v1/{hash_csv_path.name}`",
        f"- Target tests: `{', '.join(test_ids)}`",
        "",
        "## Alignment",
        f"- lint_workspace: `{'pass' if lint_ok else 'fail'}`",
        f"- lint output: `{lint_output if lint_output else '(no output)'}`",
        "",
        "## Git Tag",
        f"- is_repo: `{str(not no_git)}`",
        f"- tag_status: `{manifest['git']['tag_status']}`",
        f"- note: {manifest['git']['note']}",
        "",
        "## Test Snapshot",
    ]
    for t in test_entries:
        status_lines.extend(
            [
                f"- `{t['test_id']}` ({t['claim_id']}): status=`{t['status']}`, authenticity=`{t['authenticity']}`, leakage=`{t['leakage_risk']}`, negative_control=`{t['negative_control']}`",
                f"  metric: `{t['metric_value_results_log']}`",
                f"  fit summary: `{t['fit_summary_path']}`",
            ]
        )

    write_status_md(out_dir / "gold-pack-v1-freeze-status.md", status_lines)

    print(f"Gold pack manifest: {manifest_path}")
    print(f"Gold pack hashes: {hash_csv_path}")
    print(f"Gold pack status: {out_dir / 'gold-pack-v1-freeze-status.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
