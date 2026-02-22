# QNG Core Derivation - Metric to GR Bridge (v1)

- Scope: P8 GR bridge hardening
- Date: 2026-02-21
- Related claims: `QNG-C-093`, `QNG-C-094`
- Inputs:
  - `03_math/derivations/qng-core-emergent-metric-v1.md`
  - `01_notes/metric/metric-lock-v3.md`
- Status: formalized (pipeline-level bridge)

## Objective

Define a non-poetic bridge from emergent spatial metric `g_ij` (from Sigma-Hessian method) to a weak-field GR-compatible form, with explicit sanity gates.

## 1) Spatial Metric Split

In v3 conformal gauge (`trace(g)=1` in 2D), use Euclidean reference:

```text
g0_ij = (1/2) delta_ij
```

and perturbation:

```text
h_ij = g_ij - g0_ij
```

Weak-field regime is interpreted as `||h||_F << 1`.

## 2) Newtonian Direction Bridge

QNG acceleration proxy:

```text
a_QNG^i = -g^{ij} partial_j Sigma
```

Linearized around `g0`:

```text
g^{ij} = g0^{ij} - h^{ij} + O(h^2)
```

so

```text
a_QNG^i = -g0^{ij} partial_j Sigma + h^{ij} partial_j Sigma + O(h^2)
```

This is the bridge form: leading Newtonian-like term plus curvature correction from `h`.

## 3) Effective Potential Identification

Define effective weak-field potential:

```text
Phi_eff = Sigma / 2
```

then baseline acceleration is:

```text
a_Newton^i = -2 g0^{ij} partial_j Phi_eff
```

Hence `a_QNG` reduces to Newtonian-gradient direction when:

```text
h -> 0
```

and when `partial_j Sigma` is smooth under coarse-grain.

## 4) Continuum/GR-Limit Link

For `tau -> 0` and coarse-grain smoothing:

```text
a_total = -nabla Sigma + O(h, tau)
```

which is consistent with the v1 claim-level GR bridge used in `QNG-C-093` and `QNG-C-094` (pipeline interpretation, not uniqueness proof).

## 5) Auditable Bridge Gates (v1)

Bridge gate family for artifact-level checks:

1. `B1` weak-field perturbation:
   - `median(||h||_F)` and `p90(||h||_F)` bounded.
2. `B2` metric sanity:
   - SPD floor and bounded condition number.
3. `B3` Newtonian-direction compatibility:
   - high cosine between `a_QNG` direction and raw `-nabla Sigma`.
4. `B4` continuum stability:
   - bounded drift across scales (`s0 -> 1.25s0 -> 1.5s0`).
5. `B5` control separation:
   - strong median gap between raw and shuffled alignment.

## Falsifier

Bridge v1 is falsified at pipeline level if any of `B1..B5` fails consistently under locked v3 artifacts without gate edits.

## Interpretation Discipline

- This bridge validates consistency/discriminability in the pipeline.
- It is not, by itself, a REAL-data uniqueness proof of GR replacement.
