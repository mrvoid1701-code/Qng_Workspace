# QNG Rotation Winner V1 (M8c)

## Definition

Frozen winner formula (used in D7/D9b and imported in D4-v8 strict):

`v_pred^2 = bt + r * k * sqrt(g_bar * g_dag) * exp(-g_bar / g_dag)`

with:
- `g_bar = bt / r`
- `k >= 0`
- `g_dag > 0`

## Units

- `v`: `km/s`
- `r`: `kpc`
- `bt`: `km^2/s^2`
- `g_bar`, `g_dag`: `km^2/s^2/kpc`

## Physical Limits

- Deep low-acceleration regime (`g_bar << g_dag`):
  - extra term scales as `sqrt(g_bar * g_dag)` (MOND-like geometric mean regime)
- High-acceleration regime (`g_bar >> g_dag`):
  - exponential suppression drives extra term to zero
  - model tends to baryonic baseline `v^2 ~ bt`

## Fit Contract

The formula is fixed as `WINNER_V1_M8C`.
Only `(k, g_dag)` are fitted per split; equation and units are locked.
