# scripts/

This directory contains executable QNG run pipelines only.

## What belongs here

- `run_qng_*.py` gate/test runners
- `_common.py` shared stdlib helper for runner CLI/output housekeeping

## What does not belong here

- dataset import/export helpers
- report generation scripts
- linting, sync, or UI maintenance utilities

Those utilities are maintained under `tools/maintenance/` and `tools/powershell/`.
