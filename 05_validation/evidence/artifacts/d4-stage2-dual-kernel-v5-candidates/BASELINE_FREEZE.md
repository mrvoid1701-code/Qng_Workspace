# D4 V5 Baseline Freeze

- Lane: `d4-stage2-dual-kernel-v5-candidates`
- Status: frozen baseline (no further formula/grid/evaluator edits in v5 lane)
- Freeze intent: all exploratory work continues only in `v6` lane artifacts and scripts.

Locked artifacts to preserve:

- `per_seed_candidate_summary.csv`
- `aggregate_summary.csv`
- `manifest.json`
- `evaluation-v1/evaluation_report.json`
- `evaluation-v1/candidate_decisions.csv`

Governance note:

- Any model change after this freeze must run via new prereg lane (`v6+`) with strict lock checks.
