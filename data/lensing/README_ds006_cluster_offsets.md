# DS-006 Cluster Offset Input (Gold Upgrade)

Use this schema when importing direct cluster lensing-offset catalogs:

- `system_id`: cluster identifier
- `baryon_x`, `baryon_y`: baryonic center coordinates (consistent units)
- `lens_x`, `lens_y`: lensing center coordinates (same units as baryon coordinates)
- `sigma_grad_x`, `sigma_grad_y`: Sigma-gradient components used by memory model
- `sigma`: measurement uncertainty scale for offset fit (must be > 0)

Template file:

- `data/lensing/cluster_offsets_template.csv`

## Import SPT-SZ catalog from downloaded PDF

If you downloaded:
- `C:/Users/tigan/Downloads/GALAXY CLUSTERS DISCOVERED VIA THE SUNYAEV-ZEL’DOVICH EFFECT IN THE.pdf`

Run:

```powershell
.\.venv\Scripts\python.exe scripts\extract_pdf_text.py `
  --input "C:\Users\tigan\Downloads\GALAXY CLUSTERS DISCOVERED VIA THE SUNYAEV-ZEL’DOVICH EFFECT IN THE.pdf" `
  --output "01_notes/source_text/spt-sz-galaxy-clusters.md" `
  --pages-dir "01_notes/page_text/spt-sz-galaxy-clusters"

.\.venv\Scripts\python.exe scripts\extract_spt_sz_table4_catalog.py `
  --input-md "01_notes/source_text/spt-sz-galaxy-clusters.md" `
  --out-csv "data/lensing/spt_sz_table4_catalog.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-spt-sz-catalog-extract.md"
```

Result:
- `data/lensing/spt_sz_table4_catalog.csv` (one SZ/lensing-side center per cluster)
- `05_validation/evidence/artifacts/ds006-spt-sz-catalog-extract.md`

## Import MCXC full X-ray catalog from CDS

Download files:

```powershell
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/534/A109/mcxc.dat" `
  -OutFile "data/lensing/mcxc_full_from_cds.dat"
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/534/A109/ReadMe" `
  -OutFile "data/lensing/mcxc_ReadMe.txt"
```

Convert fixed-width `mcxc.dat` to CSV:

```powershell
.\.venv\Scripts\python.exe scripts\extract_mcxc_cds_catalog.py `
  --input-dat "data/lensing/mcxc_full_from_cds.dat" `
  --out-csv "data/lensing/mcxc_catalog_full.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-mcxc-catalog-extract.md"
```

Result:
- `data/lensing/mcxc_catalog_full.csv` (1743 X-ray baryonic centers)
- `05_validation/evidence/artifacts/ds006-mcxc-catalog-extract.md`

## Import Planck PSZ2 SZ catalog from CDS

Download files:

```powershell
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/594/A27/psz2.dat" `
  -OutFile "data/lensing/psz2_full_from_cds.dat"
Invoke-WebRequest -Uri "https://cdsarc.cds.unistra.fr/ftp/J/A+A/594/A27/ReadMe" `
  -OutFile "data/lensing/psz2_ReadMe.txt"
```

Convert fixed-width `psz2.dat` to CSV:

```powershell
.\.venv\Scripts\python.exe scripts\extract_psz2_cds_catalog.py `
  --input-dat "data/lensing/psz2_full_from_cds.dat" `
  --out-csv "data/lensing/psz2_catalog_full.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-psz2-catalog-extract.md"
```

Result:
- `data/lensing/psz2_catalog_full.csv` (1653 SZ-side centers, 551 MCXC-linked IDs)
- `05_validation/evidence/artifacts/ds006-psz2-catalog-extract.md`

## Auto-build from catalogs (recommended)

Use the builder script to cross-match baryon centers and lensing centers:

```powershell
.\.venv\Scripts\python.exe scripts\build_ds006_cluster_offsets.py `
  --baryon-csv "C:\path\to\baryon_catalog.csv" `
  --lensing-csv "C:\path\to\lensing_catalog.csv" `
  --match-mode hybrid `
  --max-sep-arcmin 5 `
  --out-csv "data/lensing/cluster_offsets_real.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-cluster-offset-build.md"
```

Combined-catalog mode (example: a single file with `role=plasma` and `role=bcg`):

```powershell
.\.venv\Scripts\python.exe scripts\build_ds006_cluster_offsets.py `
  --combined-csv "data/lensing/clowe_2006_table2_positions.csv" `
  --role-col role `
  --group-col component `
  --baryon-role plasma `
  --lensing-role bcg `
  --match-mode id `
  --out-csv "data/lensing/cluster_offsets_real.csv"
```

Direct MCXC x PSZ2 hybrid mode (recommended current DS-006 real pair set):

```powershell
.\.venv\Scripts\python.exe scripts\build_ds006_cluster_offsets.py `
  --baryon-csv "data/lensing/mcxc_catalog_full.csv" `
  --lensing-csv "data/lensing/psz2_catalog_full.csv" `
  --match-mode hybrid `
  --max-sep-arcmin 5 `
  --strict-id-sep `
  --out-csv "data/lensing/cluster_offsets_real.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-cluster-offset-build.md"
```

Direct MCXC x SPT sky-match mode (smaller anchor set):

```powershell
.\.venv\Scripts\python.exe scripts\build_ds006_cluster_offsets.py `
  --baryon-csv "data/lensing/mcxc_catalog_full.csv" `
  --lensing-csv "data/lensing/spt_sz_table4_catalog.csv" `
  --match-mode sky `
  --max-sep-arcmin 5 `
  --out-csv "data/lensing/cluster_offsets_real.csv" `
  --report-out "05_validation/evidence/artifacts/ds006-cluster-offset-build.md"
```

Builder outputs:
- `data/lensing/cluster_offsets_real.csv`
- `data/lensing/cluster_offsets_unmatched_baryon.csv`
- `data/lensing/cluster_offsets_unmatched_lensing.csv`
- `05_validation/evidence/artifacts/ds006-cluster-offset-build.md`

Minimum data gate:
- `scripts/run_qng_t_027_lensing_dark.py --strict-input` requires at least **8 usable lensing rows**.
- Small benchmark sets (for example Clowe-only with 2 pairs) are valid for pipeline checks but not enough for strict DS-006 pass.

## Run DS-006 strict input on real offsets

Run DS-006 strict-input directly with the generated real cluster catalog:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_027_lensing_dark.py `
  --dataset-id DS-006 `
  --model-baseline gr_dm `
  --model-memory qng_sigma_memory `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --seed 42 `
  --strict-input
```

Then run negative controls:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_027_negative_controls.py `
  --lensing-csv "data/lensing/cluster_offsets_real.csv" `
  --rotation-csv "data/rotation/rotation_ds006_rotmod.csv" `
  --out-dir "05_validation/evidence/artifacts/qng-t-027" `
  --n-runs 24 `
  --seed 97
```
