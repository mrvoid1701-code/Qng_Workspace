# DS-006 Cluster Offset Build

- Generated (UTC): 2026-02-16 16:52:40Z
- Input mode: `two-catalog`
- Match mode: `hybrid`
- Strict ID separation gate: `True`
- Separation window (arcmin): `[0.000, 3.000]`

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
- Matched rows: `485`
- Unmatched baryon rows: `1258`
- Unmatched lensing rows: `1168`
- Matched by id: `484`
- Matched by sky: `1`

## Separation Stats (arcmin)

- min: `0.101450`
- median: `1.134610`
- p90: `2.397148`
- max: `2.984645`

## Outputs

- Cluster offsets CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_psz2_strict3.csv`
- Unmatched baryon CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_baryon.csv`
- Unmatched lensing CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_unmatched_lensing.csv`

## Warnings

- ID match 'MCXC J0011.7-1523' dropped: separation 3.194 arcmin (> 3.000).
- ID match 'MCXC J0040.0+0649' dropped: separation 5.353 arcmin (> 3.000).
- ID match 'MCXC J0051.1-4833' dropped: separation 4.612 arcmin (> 3.000).
- ID match 'MCXC J0056.3-0112' dropped: separation 4.004 arcmin (> 3.000).
- ID match 'MCXC J0108.8-1524' dropped: separation 6.394 arcmin (> 3.000).
- ID match 'MCXC J0115.2+0019' dropped: separation 5.937 arcmin (> 3.000).
- ID match 'MCXC J0125.0+0841' dropped: separation 3.021 arcmin (> 3.000).
- ID match 'MCXC J0152.7+3609' dropped: separation 5.516 arcmin (> 3.000).
- ID match 'MCXC J0212.8-4707' dropped: separation 4.043 arcmin (> 3.000).
- ID match 'MCXC J0236.6-1923' dropped: separation 4.065 arcmin (> 3.000).
- ID match 'MCXC J0328.6-2140' dropped: separation 6.154 arcmin (> 3.000).
- ID match 'MCXC J0330.0-5235' dropped: separation 8.076 arcmin (> 3.000).
- ID match 'MCXC J0346.1-5702' dropped: separation 5.956 arcmin (> 3.000).
- ID match 'MCXC J0408.2-3053' dropped: separation 6.005 arcmin (> 3.000).
- ID match 'MCXC J0438.9-2206' dropped: separation 4.590 arcmin (> 3.000).
- ID match 'MCXC J0501.6+0110' dropped: separation 4.395 arcmin (> 3.000).
- ID match 'MCXC J0515.3+5845' dropped: separation 3.403 arcmin (> 3.000).
- ID match 'MCXC J0516.6+0626' dropped: separation 4.193 arcmin (> 3.000).
- ID match 'MCXC J0631.3-5610' dropped: separation 7.995 arcmin (> 3.000).
- ID match 'MCXC J0728.9+2935' dropped: separation 5.660 arcmin (> 3.000).
- ID match 'MCXC J0745.1-5404' dropped: separation 3.785 arcmin (> 3.000).
- ID match 'MCXC J0800.9+3602' dropped: separation 3.022 arcmin (> 3.000).
- ID match 'MCXC J0811.0+1644' dropped: separation 6.392 arcmin (> 3.000).
- ID match 'MCXC J0820.9-5704' dropped: separation 3.805 arcmin (> 3.000).
- ID match 'MCXC J0825.9+0415' dropped: separation 3.825 arcmin (> 3.000).
- ID match 'MCXC J0909.1-0939' dropped: separation 3.040 arcmin (> 3.000).
- ID match 'MCXC J0956.4-1004' dropped: separation 7.650 arcmin (> 3.000).
- ID match 'MCXC J1013.6-0054' dropped: separation 5.898 arcmin (> 3.000).
- ID match 'MCXC J1039.7-0841' dropped: separation 3.823 arcmin (> 3.000).
- ID match 'MCXC J1113.3+1735' dropped: separation 3.548 arcmin (> 3.000).
- ... (36 more)

## Next Step

Run DS-006 strict input on this catalog:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "C:\Users\tigan\Desktop\qng workspace\data\lensing\cluster_offsets_psz2_strict3.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --seed 42 `
  --strict-input
```
