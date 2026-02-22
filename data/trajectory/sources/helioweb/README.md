# HELIOWeb Command-Line Notes (NASA/SPDF)

Source page references:
- `https://omniweb.gsfc.nasa.gov/helios/heli.html`
- `C:\Users\tigan\Downloads\Heliocentric Trajectories for Selected Spacecraft,Planets, and Comets.htm`

## Why this is useful

HELIOWeb gives heliocentric trajectory/context data you can fetch in batch loops.
It is useful for trajectory context features, but **not** a direct substitute for OD residual anomaly tables (`delta_v_obs`, `sigma`) used by DS-005 holdout gates.

## Quick command examples (Windows PowerShell)

### 1) Direct NASA-style POST with `curl.exe`

```powershell
curl.exe -d "activity=retrieve&object=04&coordinate=1&start_year=2000&start_day=001&stop_year=2000&stop_day=366&resolution=001&equinox=2&object2=" `
  "https://omniweb.gsfc.nasa.gov/cgi/models/helios1.cgi" `
  -o test_curl.txt
```

### 2) Scripted fetch with manifest (recommended)

```powershell
.\.venv\Scripts\python.exe scripts\fetch_helioweb_data.py `
  --url https://omniweb.gsfc.nasa.gov/cgi/models/helios1.cgi `
  --activity retrieve `
  --object 46 `
  --coordinate 1 `
  --start-year 2021 `
  --start-day 001 `
  --stop-year 2021 `
  --stop-day 365 `
  --resolution 001 `
  --equinox 2 `
  --object2 "" `
  --out data/trajectory/sources/helioweb/solar_orbiter_2021_helios1.txt
```

The script also writes:
- `...txt.manifest.json` with payload, endpoint, output hash, and status.

### 3) If endpoint/form needs extra params

Use repeatable `--param key=value`, e.g.:

```powershell
.\.venv\Scripts\python.exe scripts\fetch_helioweb_data.py `
  --url https://omniweb.gsfc.nasa.gov/cgi/models/helios2_h.cgi `
  --activity retrieve `
  --object 37 `
  --coordinate 3 `
  --start-year 2020 `
  --start-day 001 `
  --stop-year 2020 `
  --stop-day 366 `
  --resolution Hourly `
  --equinox 2 `
  --precn 2 `
  --out data/trajectory/sources/helioweb/bepicolombo_2020_helios2.txt `
  --param object2=
```

## Object codes used in this workspace

See `data/trajectory/sources/helioweb/object_codes_subset.csv`.

## Current fetched files (2026-02-21)

- Daily/compact pulls (`helios1.cgi`):
  - `bepicolombo_2020_101_helios1.txt`
  - `juno_2013_282_helios1.txt`
  - `solar_orbiter_2021_331_helios1.txt`
- Hourly mission-minus-Earth pulls (`helios2_h.cgi`, `object2=04`, `precn=4`):
  - `bepicolombo_2020_101_helios2h_vs_earth.txt`
  - `juno_2013_282_helios2h_vs_earth.txt`
  - `solar_orbiter_2021_331_helios2h_vs_earth.txt`

Parsed outputs:
- Detail: `data/trajectory/sources/helioweb/holdout_vs_earth_hourly.csv`
- Summary: `data/trajectory/sources/helioweb/holdout_vs_earth_summary.csv`

Parser command:

```powershell
.\.venv\Scripts\python.exe scripts\parse_helioweb_vs_earth.py
```
