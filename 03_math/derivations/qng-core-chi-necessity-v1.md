# QNG Core Derivation - Physical Necessity of chi (v1)

- Scope: fundamental closure task (P8)
- Date: 2026-02-21
- Related claims: `QNG-C-012`, `QNG-C-014`, `QNG-C-029`, `QNG-C-032`
- Status: formalized

## Objective

Show that `chi` is not a redundant re-labeling, but a physically necessary parameter in the memory-lag sector.

## Setup

Node-level memory coupling:

```text
tau_i = alpha_tau * chi_i
a_lag = -tau_i * (v . nabla) nablaSigma
chi_i = m_i / c
```

Comparison baseline without `chi`:

```text
tau_i = tau_0 (constant, independent of node load)
a_lag = -tau_0 * (v . nabla) nablaSigma
```

## Non-Redundancy Argument

1. In QNG closure, node state includes `chi_i` and update timing uses `tau_i`.
2. If `chi` were removable, then replacing `tau_i = alpha_tau * chi_i` with a constant `tau_0` would preserve all observables.
3. But observables depend on `tau_i` through directional lag amplitude:

```text
A_i := |a_lag,i| / |(v . nabla) nablaSigma| = tau_i
```

4. Under QNG mapping:

```text
A_i = alpha_tau * chi_i = alpha_tau * (m_i / c)
```

5. Therefore, if two classes `i, j` have different effective `chi` support (`chi_i != chi_j`), QNG predicts:

```text
A_i / A_j = chi_i / chi_j
```

Constant-lag baseline predicts:

```text
A_i / A_j = 1
```

6. These predictions are mutually incompatible unless `chi_i = chi_j` for all tested classes (degenerate case).

Conclusion: `chi` is physically necessary for the memory sector whenever cross-class lag amplitudes are non-degenerate.

## Identifiability Form

From measurable lag amplitude:

```text
tau_i = A_i
chi_i = m_i / c
alpha_tau = tau_i / chi_i
```

Consistency condition for one-parameter closure:

```text
alpha_tau(i) ~= alpha_tau(j) ~= const
```

If this holds across domains, `chi` acts as identifiable physical coupling, not a free gauge variable.

## Falsifier

`chi`-necessity is falsified if both hold:

1. Cross-class lag amplitudes satisfy constant-lag model (`A_i / A_j ~= 1`) within uncertainty.
2. Inferred `alpha_tau(i)` shows no stable collapse under `tau_i = alpha_tau * chi_i`.

In that case, `chi` is not needed for lag dynamics.

## Practical Test Hooks

- Trajectory real: compare inferred `tau` across mission classes with different effective `chi` supports.
- Timing/wave: repeat consistency check using independent residual channels.
- Hold closure rule fixed; do not retune gates after seeing fit.

## Output Class

This document is a theoretical closure proof target (`pipeline-level formalization`), not direct real-world confirmation.

