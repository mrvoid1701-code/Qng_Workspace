#!/usr/bin/env bash
set -euo pipefail

echo "[repro] Starting Linux reproduce pipeline"

run_py() {
  echo "[repro] python $*"
  python "$@"
}

run_py scripts/lint_workspace.py

run_py scripts/run_qng_metric_hardening_v3.py \
  --dataset-id DS-002 \
  --scales "s0,1.25s0,1.5s0" \
  --samples 72 \
  --seed 3401 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3"

run_py scripts/run_qng_metric_hardening_v3.py \
  --dataset-id DS-003 \
  --scales "s0,1.25s0,1.5s0" \
  --samples 72 \
  --seed 3401 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003"

run_py scripts/run_qng_metric_hardening_v3.py \
  --dataset-id DS-006 \
  --scales "s0,1.25s0,1.5s0" \
  --samples 72 \
  --seed 3401 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006"

run_py scripts/run_qng_metric_anti_leak_v1.py \
  --dataset-id DS-002 \
  --samples 72 \
  --seed 3401 \
  --rewire-runs 12 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1"

run_py scripts/run_qng_metric_anti_leak_v1.py \
  --dataset-id DS-003 \
  --samples 72 \
  --seed 3401 \
  --rewire-runs 12 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds003"

run_py scripts/run_qng_metric_anti_leak_v1.py \
  --dataset-id DS-006 \
  --samples 72 \
  --seed 3401 \
  --rewire-runs 12 \
  --out-dir "05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds006"

run_py scripts/run_qng_t_028_trajectory_real.py \
  --test-id QNG-T-028 \
  --dataset-id DS-005 \
  --flyby-csv data/trajectory/flyby_ds005_real.csv \
  --use-pioneer-anchor \
  --pioneer-csv data/trajectory/pioneer_ds005_anchor.csv \
  --out-dir "05_validation/evidence/artifacts/qng-t-028" \
  --seed 20260220

run_py scripts/run_qng_t_027_lensing_dark.py \
  --test-id QNG-T-039 \
  --dataset-id DS-006 \
  --model-baseline gr_dm \
  --model-memory qng_sigma_memory \
  --lensing-csv "data/lensing/cluster_offsets_real.csv" \
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" \
  --out-dir "05_validation/evidence/artifacts/qng-t-039-direct" \
  --seed 142 \
  --strict-input

run_py scripts/run_qng_t_027_negative_controls.py \
  --lensing-csv "data/lensing/cluster_offsets_real.csv" \
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" \
  --out-dir "05_validation/evidence/artifacts/qng-t-039-direct" \
  --n-runs 48 \
  --seed 197

run_py scripts/run_qng_t_039_rotation_baseline_upgrade.py \
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" \
  --out-dir "05_validation/evidence/artifacts/qng-t-039-baseline-upgrade" \
  --seed 20260221

required=(
  "05_validation/evidence/artifacts/qng-metric-hardening-v3/metric_checks.csv"
  "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds003/metric_checks.csv"
  "05_validation/evidence/artifacts/qng-metric-hardening-v3-ds006/metric_checks.csv"
  "05_validation/evidence/artifacts/qng-metric-anti-leak-v1/control_summary.csv"
  "05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds003/control_summary.csv"
  "05_validation/evidence/artifacts/qng-metric-anti-leak-v1-ds006/control_summary.csv"
  "05_validation/evidence/artifacts/qng-t-028/fit-summary.csv"
  "05_validation/evidence/artifacts/qng-t-039-direct/fit-summary.csv"
  "05_validation/evidence/artifacts/qng-t-039-direct/negative-controls-summary.csv"
  "05_validation/evidence/artifacts/qng-t-039-baseline-upgrade/fit-summary.csv"
)

echo "[repro] Checking required artifacts"
for p in "${required[@]}"; do
  if [[ ! -f "$p" ]]; then
    echo "[repro][error] Missing expected artifact: $p"
    exit 1
  fi
done

echo "[repro] Reproduce pipeline completed successfully"
