# Dataset Manifest

Generated from `05_validation/test-plan.md`.

| Dataset ID | Name | Type | Highest Priority | Tests | Claims | Source URL | License | Local Path | Version | Last Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS-001 | Analytical + symbolic limit analysis | analytical | P3 | QNG-T-038, QNG-T-044, QNG-T-045 | QNG-C-081, QNG-C-093, QNG-C-094 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-002 | Cosmological toy simulation / synthetic catalogs | simulation | P2 | QNG-T-050, QNG-T-051, QNG-T-052, QNG-T-053 | QNG-C-103, QNG-C-104, QNG-C-107, QNG-C-111 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-003 | Discrete/N-body simulation environment | simulation | P1 | QNG-T-029 | QNG-C-062 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-004 | Ensemble update simulation + operator fitting | simulation | P3 | QNG-T-046, QNG-T-047 | QNG-C-095, QNG-C-096 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-005 | Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer) | spacecraft | P1 | QNG-T-010, QNG-T-011, QNG-T-025, QNG-T-028, QNG-T-041 | QNG-C-025, QNG-C-026, QNG-C-055, QNG-C-060, QNG-C-086 | https://doi.org/10.1103/PhysRevLett.100.091102; local sources in data/trajectory/sources/ | Derived numeric summaries from published literature | data/trajectory/flyby_ds005_real.csv | ds005-real-v1 | 2026-02-17 |
| DS-006 | Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs) | astronomy | P1 | QNG-T-012, QNG-T-017, QNG-T-018, QNG-T-019, QNG-T-027, QNG-T-039 | QNG-C-027, QNG-C-037, QNG-C-038, QNG-C-040, QNG-C-058, QNG-C-082 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-007 | Symbolic math + dimensional analysis | other | P3 | QNG-T-001, QNG-T-002, QNG-T-003, QNG-T-004, QNG-T-005, QNG-T-006, QNG-T-007, QNG-T-008, QNG-T-009, QNG-T-013, QNG-T-014, QNG-T-015, QNG-T-016, QNG-T-020, QNG-T-021, QNG-T-022, QNG-T-023, QNG-T-024, QNG-T-026, QNG-T-030, QNG-T-033, QNG-T-034, QNG-T-035, QNG-T-036, QNG-T-040, QNG-T-048, QNG-T-049 | QNG-C-004, QNG-C-007, QNG-C-012, QNG-C-014, QNG-C-018, QNG-C-019, QNG-C-020, QNG-C-021, QNG-C-024, QNG-C-029, QNG-C-032, QNG-C-033, QNG-C-036, QNG-C-042, QNG-C-044, QNG-C-048, QNG-C-051, QNG-C-054, QNG-C-056, QNG-C-064, QNG-C-072, QNG-C-073, QNG-C-074, QNG-C-077, QNG-C-085, QNG-C-100, QNG-C-101 | TODO | TODO | TODO | TODO | YYYY-MM-DD |
| DS-008 | Timing/waveforms (GPS residuals, binary pulsars, LIGO/Virgo/KAGRA) | timing-waveform | P1 | QNG-T-031, QNG-T-032, QNG-T-037, QNG-T-042, QNG-T-043 | QNG-C-066, QNG-C-069, QNG-C-078, QNG-C-090, QNG-C-091 | TODO | TODO | TODO | TODO | YYYY-MM-DD |

## Dataset Notes

### DS-001 - Analytical + symbolic limit analysis
- Type: analytical
- Highest priority linked: P3
- Tests: QNG-T-038, QNG-T-044, QNG-T-045
- Claims: QNG-C-081, QNG-C-093, QNG-C-094
- Notes: TODO

### DS-002 - Cosmological toy simulation / synthetic catalogs
- Type: simulation
- Highest priority linked: P2
- Tests: QNG-T-050, QNG-T-051, QNG-T-052, QNG-T-053
- Claims: QNG-C-103, QNG-C-104, QNG-C-107, QNG-C-111
- Notes: TODO

### DS-003 - Discrete/N-body simulation environment
- Type: simulation
- Highest priority linked: P1
- Tests: QNG-T-029
- Claims: QNG-C-062
- Notes: TODO

### DS-004 - Ensemble update simulation + operator fitting
- Type: simulation
- Highest priority linked: P3
- Tests: QNG-T-046, QNG-T-047
- Claims: QNG-C-095, QNG-C-096
- Notes: TODO

### DS-005 - Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer)
- Type: spacecraft
- Highest priority linked: P1
- Tests: QNG-T-010, QNG-T-011, QNG-T-025, QNG-T-028, QNG-T-041
- Claims: QNG-C-025, QNG-C-026, QNG-C-055, QNG-C-060, QNG-C-086
- Notes: Published pass-level Earth-flyby residual compilation (Anderson 2008 + Meessen 2017) with Pioneer deep-space anchor file from Anderson 2002 summary equations/tables. Non-gravitational correction columns are explicit and currently zeroed where source tables provide residual-only summaries.

### DS-006 - Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs)
- Type: astronomy
- Highest priority linked: P1
- Tests: QNG-T-012, QNG-T-017, QNG-T-018, QNG-T-019, QNG-T-027, QNG-T-039
- Claims: QNG-C-027, QNG-C-037, QNG-C-038, QNG-C-040, QNG-C-058, QNG-C-082
- Notes: TODO

### DS-007 - Symbolic math + dimensional analysis
- Type: other
- Highest priority linked: P3
- Tests: QNG-T-001, QNG-T-002, QNG-T-003, QNG-T-004, QNG-T-005, QNG-T-006, QNG-T-007, QNG-T-008, QNG-T-009, QNG-T-013, QNG-T-014, QNG-T-015, QNG-T-016, QNG-T-020, QNG-T-021, QNG-T-022, QNG-T-023, QNG-T-024, QNG-T-026, QNG-T-030, QNG-T-033, QNG-T-034, QNG-T-035, QNG-T-036, QNG-T-040, QNG-T-048, QNG-T-049
- Claims: QNG-C-004, QNG-C-007, QNG-C-012, QNG-C-014, QNG-C-018, QNG-C-019, QNG-C-020, QNG-C-021, QNG-C-024, QNG-C-029, QNG-C-032, QNG-C-033, QNG-C-036, QNG-C-042, QNG-C-044, QNG-C-048, QNG-C-051, QNG-C-054, QNG-C-056, QNG-C-064, QNG-C-072, QNG-C-073, QNG-C-074, QNG-C-077, QNG-C-085, QNG-C-100, QNG-C-101
- Notes: TODO

### DS-008 - Timing/waveforms (GPS residuals, binary pulsars, LIGO/Virgo/KAGRA)
- Type: timing-waveform
- Highest priority linked: P1
- Tests: QNG-T-031, QNG-T-032, QNG-T-037, QNG-T-042, QNG-T-043
- Claims: QNG-C-066, QNG-C-069, QNG-C-078, QNG-C-090, QNG-C-091
- Notes: TODO
