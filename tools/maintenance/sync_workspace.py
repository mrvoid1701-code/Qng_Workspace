#!/usr/bin/env python3
"""
Regenerate workspace artifacts from claims register as source of truth.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def python_bin() -> str:
    venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def run_step(step_name: str, args: list[str]) -> None:
    cmd = [python_bin(), *args]
    print(f"[sync] {step_name}: {' '.join(args)}")
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr.strip():
            print(result.stderr.strip())
        raise RuntimeError(f"Step failed: {step_name}")


def main() -> int:
    try:
        run_step("claim-files", ["scripts/generate_claim_files.py", "--force"])
        run_step("derivations", ["scripts/generate_derivations.py"])
        run_step("validation-plan", ["scripts/generate_validation_plan.py"])
        run_step("results-log", ["scripts/generate_results_log.py"])
        run_step("evidence-stubs", ["scripts/generate_evidence_stubs.py"])
        run_step("dataset-manifest", ["scripts/generate_dataset_manifest.py"])
        run_step("run-manifests", ["scripts/generate_run_manifests.py"])
        run_step("writing-export", ["scripts/export_validated_writing.py"])
    except RuntimeError as exc:
        print(str(exc))
        return 1

    print("[sync] complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

