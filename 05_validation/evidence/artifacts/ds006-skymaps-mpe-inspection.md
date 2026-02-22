# DS-006 SKYMAPS_052022_MPE Inspection

- Generated (UTC): 2026-02-16 15:13:50Z
- Input FITS: `C:\Users\tigan\Downloads\SKYMAPS_052022_MPE.fits`
- Output CSV: `C:\Users\tigan\Desktop\qng workspace\data\lensing\skymaps_052022_mpe_tiles.csv`

## FITS Structure

- EXTNAME: `SMAPS   `
- Rows: `2447`
- Columns: `24`
- Row length (bytes): `140`

## Column Summary

| Name | TFORM | Unit |
| --- | --- | --- |
| `SRVMAP` | `J` | `` |
| `OWNER` | `I` | `` |
| `RA_MIN` | `D` | `deg` |
| `RA_MAX` | `D` | `deg` |
| `DE_MIN` | `D` | `deg` |
| `DE_MAX` | `D` | `deg` |
| `RA_CEN` | `D` | `deg` |
| `DE_CEN` | `D` | `deg` |
| `ELON_CEN` | `D` | `deg` |
| `ELAT_CEN` | `D` | `deg` |
| `GLON_CEN` | `D` | `deg` |
| `GLAT_CEN` | `D` | `deg` |
| `X_MIN` | `D` | `arcmin` |
| `Y_MIN` | `D` | `arcmin` |
| `N_NBRS` | `I` | `` |
| `FIELD1` | `J` | `` |
| `FIELD2` | `J` | `` |
| `FIELD3` | `J` | `` |
| `FIELD4` | `J` | `` |
| `FIELD5` | `J` | `` |
| `FIELD6` | `J` | `` |
| `FIELD7` | `J` | `` |
| `FIELD8` | `J` | `` |
| `FIELD9` | `J` | `` |

## Numeric Coverage

- RA_MIN range: `0.000000` .. `356.470588` (mean `152.268019`)
- RA_MAX range: `3.428571` .. `360.000000` (mean `156.889928`)
- DE_MIN range: `-90.000000` .. `40.500000` (mean `-26.320801`)
- DE_MAX range: `-88.500000` .. `43.500000` (mean `-23.321414`)
- N_NBRS range: `6` .. `9` (mean `7.352`)

## DS-006 Relevance

- This file is a sky-tiling/index table (map cells and neighbors), not a direct cluster-offset catalog.
- It does not contain explicit baryonic-center vs lensing-center paired measurements per cluster.
- Therefore it can be used as supporting sky-map metadata, but not as final `gold` DS-006 lensing evidence by itself.
