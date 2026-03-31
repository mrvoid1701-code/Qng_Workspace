# 05_validation/

Validation planning, execution logs, and evidence registry.

## Expected contents

- `test-plan.md` claim-to-test matrix
- `results-log.md` append-only execution journal
- `evidence/` public evidence narratives and artifacts
- `run-manifests/` reproducibility manifests
- `pre-registrations/` locked plans and thresholds

## Artifact policy

- Keep public evidence tables/figures versioned.
- Generated runtime files (`run-log*`, `config*`, `artifact-hashes*`) are ignored by default via `.gitignore`.
- Do not delete evidence in `evidence/artifacts/`; archive instead when cleanup is needed.
