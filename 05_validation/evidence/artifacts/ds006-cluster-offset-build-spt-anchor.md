# DS-006 Cluster Offset Build

- Generated (UTC): 2026-02-16 16:55:00Z
- Input mode: `two-catalog`
- Match mode: `sky`
- Strict ID separation gate: `False`
- Separation window (arcmin): `[0.000, 5.000]`

## Inputs

- Baryon CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\mcxc_catalog_full.csv`
- Lensing CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\spt_sz_table4_catalog.csv`
- Combined CSV: `N/A`

## Column Mapping

- Baryon: id=`system_id`, ra=`ra_deg`, dec=`dec_deg`, grad_x=``, grad_y=``, sigma=``
- Lensing: id=`system_id`, ra=`ra_deg`, dec=`dec_deg`, grad_x=``, grad_y=``, sigma=``

## Match Summary

- Parsed baryon rows: `1743`
- Parsed lensing rows: `101`
- Matched rows: `10`
- Unmatched baryon rows: `1733`
- Unmatched lensing rows: `91`
- Matched by id: `0`
- Matched by sky: `10`

## Separation Stats (arcmin)

- min: `0.064516`
- median: `0.411852`
- p90: `0.717043`
- max: `0.871585`

## Outputs

- Cluster offsets CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_spt_anchor.csv`
- Unmatched baryon CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_baryon.csv`
- Unmatched lensing CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_lensing.csv`

## Warnings

- none

## Next Step

Run DS-006 strict input on this catalog:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_spt_anchor.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --seed 42 `
  --strict-input
```
