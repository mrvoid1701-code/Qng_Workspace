# DS-006 Cluster Offset Build

- Generated (UTC): 2026-02-16 16:52:40Z
- Input mode: `two-catalog`
- Match mode: `hybrid`
- Strict ID separation gate: `True`
- Separation window (arcmin): `[0.000, 4.000]`

## Inputs

- Baryon CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\mcxc_catalog_full.csv`
- Lensing CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\psz2_catalog_full.csv`
- Combined CSV: `N/A`

## Column Mapping

- Baryon: id=`system_id`, ra=`ra_deg`, dec=`dec_deg`, grad_x=``, grad_y=``, sigma=``
- Lensing: id=`system_id`, ra=`ra_deg`, dec=`dec_deg`, grad_x=``, grad_y=``, sigma=``

## Match Summary

- Parsed baryon rows: `1743`
- Parsed lensing rows: `1653`
- Matched rows: `512`
- Unmatched baryon rows: `1231`
- Unmatched lensing rows: `1141`
- Matched by id: `511`
- Matched by sky: `1`

## Separation Stats (arcmin)

- min: `0.101450`
- median: `1.214018`
- p90: `2.654968`
- max: `3.990871`

## Outputs

- Cluster offsets CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_psz2_strict4.csv`
- Unmatched baryon CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_baryon.csv`
- Unmatched lensing CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_lensing.csv`

## Warnings

- ID match 'MCXC J0040.0+0649' dropped: separation 5.353 arcmin (> 4.000).
- ID match 'MCXC J0051.1-4833' dropped: separation 4.612 arcmin (> 4.000).
- ID match 'MCXC J0056.3-0112' dropped: separation 4.004 arcmin (> 4.000).
- ID match 'MCXC J0108.8-1524' dropped: separation 6.394 arcmin (> 4.000).
- ID match 'MCXC J0115.2+0019' dropped: separation 5.937 arcmin (> 4.000).
- ID match 'MCXC J0152.7+3609' dropped: separation 5.516 arcmin (> 4.000).
- ID match 'MCXC J0212.8-4707' dropped: separation 4.043 arcmin (> 4.000).
- ID match 'MCXC J0236.6-1923' dropped: separation 4.065 arcmin (> 4.000).
- ID match 'MCXC J0328.6-2140' dropped: separation 6.154 arcmin (> 4.000).
- ID match 'MCXC J0330.0-5235' dropped: separation 8.076 arcmin (> 4.000).
- ID match 'MCXC J0346.1-5702' dropped: separation 5.956 arcmin (> 4.000).
- ID match 'MCXC J0408.2-3053' dropped: separation 6.005 arcmin (> 4.000).
- ID match 'MCXC J0438.9-2206' dropped: separation 4.590 arcmin (> 4.000).
- ID match 'MCXC J0501.6+0110' dropped: separation 4.395 arcmin (> 4.000).
- ID match 'MCXC J0516.6+0626' dropped: separation 4.193 arcmin (> 4.000).
- ID match 'MCXC J0631.3-5610' dropped: separation 7.995 arcmin (> 4.000).
- ID match 'MCXC J0728.9+2935' dropped: separation 5.660 arcmin (> 4.000).
- ID match 'MCXC J0811.0+1644' dropped: separation 6.392 arcmin (> 4.000).
- ID match 'MCXC J0956.4-1004' dropped: separation 7.650 arcmin (> 4.000).
- ID match 'MCXC J1013.6-0054' dropped: separation 5.898 arcmin (> 4.000).
- ID match 'MCXC J1113.3+0231' dropped: separation 7.684 arcmin (> 4.000).
- ID match 'MCXC J1121.7+0249' dropped: separation 4.171 arcmin (> 4.000).
- ID match 'MCXC J1144.6+1945' dropped: separation 8.598 arcmin (> 4.000).
- ID match 'MCXC J1156.0+7325' dropped: separation 5.604 arcmin (> 4.000).
- ID match 'MCXC J1326.2+1230' dropped: separation 5.006 arcmin (> 4.000).
- ID match 'MCXC J1330.8-0152' dropped: separation 5.794 arcmin (> 4.000).
- ID match 'MCXC J1440.6+0328' dropped: separation 4.075 arcmin (> 4.000).
- ID match 'MCXC J1516.5-0056' dropped: separation 5.022 arcmin (> 4.000).
- ID match 'MCXC J1602.3+1601' dropped: separation 4.306 arcmin (> 4.000).
- ID match 'MCXC J1614.3-6052' dropped: separation 6.365 arcmin (> 4.000).
- ... (9 more)

## Next Step

Run DS-006 strict input on this catalog:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_psz2_strict4.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --seed 42 `
  --strict-input
```
