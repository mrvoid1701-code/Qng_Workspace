# 07_exports/

Public-facing exports only.

## Use

- final packaged outputs for sharing/release
- reproducibility bundles intended for external consumption

## Do not store

- temporary smoke outputs
- local debug files
- transient logs/config hashes

Local smoke artifacts should go to `07_exports/smoke/` (ignored by Git).
