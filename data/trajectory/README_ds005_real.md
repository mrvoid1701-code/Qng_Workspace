# DS-005 Real Trajectory Dataset

This folder contains a real Earth-flyby anomaly compilation used for trajectory tests:

- `flyby_ds005_real.csv`
- `pioneer_ds005_anchor.csv` (deep-space Pioneer anchor values extracted from Anderson 2002 summary equations/tables)

## Scope

- Data type: published mission residual summaries for Earth flybys.
- Primary test targets: `QNG-T-028`, `QNG-T-041`.
- Missions represented: Galileo, NEAR, Cassini, Rosetta, Messenger, EPOXI, Juno, BepiColombo, Solar Orbiter.
- Holdout additions (`2026-02-21`): `JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1` geometry rows from JPL Horizons.

## Baseline Frame

The `delta_v_obs_mm_s` values are taken as published residuals in the mission-analysis frame (i.e., after standard orbit-determination baseline modeling in source publications).  
For reproducibility, non-gravitational correction columns are explicit in the CSV:

- `thermal_corr_mm_s`
- `srp_corr_mm_s`
- `maneuver_corr_mm_s`
- `drag_corr_mm_s`

Current release sets them to `0.0` because source tables provide residual summaries, not per-pass correction decompositions.

## Sources

- Anderson et al. (2008), *Anomalous Orbital-Energy Changes Observed during Spacecraft Flybys of Earth* (Phys. Rev. Lett. 100, 091102; DOI: `10.1103/PhysRevLett.100.091102`):
  - DOI landing: `data/trajectory/sources/anderson_2008_prl_doi_landing.html`
  - Table-I transcription used in this workspace: `data/trajectory/sources/anderson_2008_tableI_transcription.csv`
- Meessen (2017), compiled extended flyby table with additional null/control passes (Table 1):
  - `data/trajectory/sources/meessen_2017_flyby_table.pdf`
- JPL Horizons API mission records and Earth-centered vector extracts for holdout rows:
  - `data/trajectory/sources/horizons/juno_1_summary.txt`
  - `data/trajectory/sources/horizons/juno_1_vectors.txt`
  - `data/trajectory/sources/horizons/bepicolombo_1_summary.txt`
  - `data/trajectory/sources/horizons/bepicolombo_1_vectors.txt`
  - `data/trajectory/sources/horizons/solar_orbiter_1_summary.txt`
  - `data/trajectory/sources/horizons/solar_orbiter_1_vectors.txt`
- Juno Earth-flyby reconstruction (no anomalous velocity change statement):
  - `data/trajectory/sources/juno_2014_reconstruction_hdl.html`
  - `data/trajectory/sources/juno_2014_reconstruction.pdf`
- Additional mission analysis/context papers from Downloads:
  - `data/trajectory/sources/bepicolombo_more_gravity_geodesy_2021_s11214-021-00800-3.pdf`
  - `data/trajectory/sources/juno_mdpi_future_internet_2025_fi17030125.pdf`
  - `data/trajectory/sources/bepicolombo_mission_to_mercury_jehn.pdf`
  - `data/trajectory/sources/lotnav_7th_icatt_2018_low_thrust_navigation_tool.pdf`
  - `data/trajectory/sources/low_thrust_navigation_tools_esoc_mission_analysis.pdf`
- Official online source pulls (2026-02-21) from user-requested links:
  - `data/trajectory/sources/bepicolombo/springer_s11214-021-00800-3_article.html`
  - `data/trajectory/sources/bepicolombo/springer_s11214-021-00800-3.pdf`
  - `data/trajectory/sources/bepicolombo/springer_s11214-021-00861-4_article.html`
  - `data/trajectory/sources/bepicolombo/springer_s11214-021-00861-4.pdf`
  - `data/trajectory/sources/bepicolombo/esa_bepicolombo_earth_flyby_page.html`
  - `data/trajectory/sources/bepicolombo/arxiv_2201.05107.pdf`
  - `data/trajectory/sources/bepicolombo/esa_psa_homepage.html`
  - `data/trajectory/sources/bepicolombo/esa_psa_ftp_index.html`
  - `data/trajectory/sources/bepicolombo/download_manifest_2026-02-21.json`
- JPL Horizons exports from Downloads (event-line and short-window vector provenance):
  - `data/trajectory/sources/horizons/juno_vector_table_2011-040A.txt`
  - `data/trajectory/sources/horizons/juno_vector_table_2011-040A_2026-02-21.txt`
  - `data/trajectory/sources/horizons/juno_horizons_results_v2_2013-10-07_12.txt`
  - `data/trajectory/sources/horizons/bepicolombo_vector_table_2018-080A_v2.txt`
  - `data/trajectory/sources/horizons/bepicolombo_vector_table_2018-080A_alt2.txt`
- Additional Horizons export kept for audit context (not used in DS-005 holdout metrics):
  - `data/trajectory/sources/horizons/horizons_results_mars_2026-02-21.txt`
- HELIOWeb trajectory context pulls (mission and mission-minus-Earth):
  - `data/trajectory/sources/helioweb/README.md`
  - `data/trajectory/sources/helioweb/holdout_vs_earth_summary.csv`

## Known Limits

- This dataset is pass-level summary telemetry/residual data, not raw DSN Doppler time series.
- Additional control passes (Rosetta/EPOXI) use conservative uncertainty placeholders (`1.0 mm/s`) where no explicit sigma was reported in the compiled table.
- Current holdout additions (`JUNO_1`, `BEPICOLOMBO_1`, `SOLAR_ORBITER_1`) use Horizons-derived geometry with provisional residual placeholders (`delta_v_obs=0.0 mm/s`, `delta_v_sigma=1.0 mm/s`) pending published OD residual summaries.
- HELIOWeb context files are useful for trajectory covariates but do not replace mission OD residual summary requirements (`delta_v_obs`, `delta_v_sigma`) for holdout-gate decisions.
- New Downloads audit note (2026-02-21 evening): `vector_table_Juno (spacecraft) (2011-040A).txt` and `horizons_results V2 jUNO.txt` confirm Juno flyby timing/altitude metadata plus short-window geocentric vectors; `horizons_results.txt` is Mars osculating-elements output and not used for DS-005 holdout residuals.
- New Downloads audit note (2026-02-21 late evening): `VECTOR_TABLE BepiColombo (Spacecraft) (2018-080A) v2.txt` and `VECTOR_TABLE BepiColombo (Spacecraft) (2018-080A) 2.txt` confirm Earth-flyby metadata (`2020-04-10 04:24:58 UTC`, altitude `19066 km`) and geocentric vector context, but still do not provide published OD residual/sigma values.
- New Downloads audit note (2026-02-21 night): `s11214-021-00800-3.pdf` (BepiColombo MORE) includes Doppler/range residual and orbit-determination context, while `fi17030125` (Juno ML trajectory analysis) provides trajectory-phase context; neither file adds pass-level OD flyby residual table values required to replace DS-005 holdout placeholders.
- New Downloads audit note (2026-02-21 20:13): `Jehn.pdf`, `LOTNAV-7th-ICATT-2018.pdf`, and `paper1.pdf` add low-thrust navigation, flyby, and OD residual-force context (useful methodology support), but do not include direct pass-level `delta_v_obs/sigma` tables for DS-005 holdout replacement.
- Official-source pull note (2026-02-21 20:25): online captures from Springer/ESA/arXiv confirm BepiColombo Earth-flyby no-anomaly wording and Doppler/range performance context, but still do not provide a standalone DS-005-ready per-pass OD residual table (`delta_v_obs`, `delta_v_sigma`) for `BEPICOLOMBO_1`.
- Download audit note (2026-02-21): local BepiColombo kernel bundle (`*.bc`, `*.bds`) and Solar Orbiter PHI L2 archive (`anonymous1771693101915.tar`) provide geometry/science products, not OD residual summary tables.
- Current validation status on this dataset (2026-02-21):
  - `QNG-T-028`: pass (post-horizons rerun; controls and robustness passed).
  - `QNG-T-041` (`C-086a`): pass (post-horizons rerun directional/cross-domain gates).
  - `QNG-T-041` (`C-086b3`): fail on current provisional holdout placeholders.
- For publication-grade gold, upgrade path remains:
  - ingest raw mission tracking arcs,
  - explicit per-pass correction budgets (thermal/SRP/maneuver/drag),
  - independent reprocessing pipeline.
