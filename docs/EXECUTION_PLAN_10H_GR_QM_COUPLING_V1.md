# 10h Execution Plan: GR + QM + Coupling (v1)

Date: 2026-03-04  
Policy: anti post-hoc (`prereg -> run -> decide`), no threshold/formula edits in official lanes.

## 1) Freeze + control (0:00-0:45)

- lock references used for official checks
- define sprint stop conditions
- confirm branch + baseline paths

## 2) Coupling first (0:45-3:30)

- run / resume coupling audit v2 on:
  - primary (`DS-002/003/006`, `3401..3600`)
  - attack (`DS-002/003/006`, `3601..4100`)
  - holdout (`DS-004/008`, `3401..3600`)
- require:
  - `profiles_missing = 0`
  - `G20 pass = completed`
  - `GR guard pre/post = PASS`
- bundle outputs into one package:
  - `qm-gr-coupling-audit-v2/bundle-v1`

## 3) GR timeboxed closure (3:30-6:00)

- target only remaining Stage-3 G11 fail signatures
- decision rule:
  - if clear uplift with `degraded=0`: candidate switch lane
  - else stop and mark as `known limitation` (no rabbit-hole tuning)

## 4) QM finish realistic (6:00-8:30)

- Stage-1:
  - run regression guard
  - refresh strict taxonomy
- Stage-2:
  - run strict taxonomy on prereg blocks
  - identify dominant failing gate/signature
  - prepare one candidate gate lane (not full redesign)

## 5) Consolidation (8:30-10:00)

- update reproducibility commands
- write result note + status note (EN)
- push all tooling/evidence updates

## Hard constraints

- no destructive cleanup of evidence
- no formula/threshold changes in official gates
- each governance move is a separate, explicit step
