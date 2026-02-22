# QNG-C-086 Derivation

- Claim statement: Flyby anomaly signature is split into directional signature (`C-086a`) plus numeric amplitude tracks (`C-086b v1` falsified, `C-086b2` calibration/holdout, `C-086b3` scaling-law holdout).
- Source page(s): page-063
- Claim status/confidence: predicted / medium
- Math maturity: v2 (split-claim form)

## Definitions

- `Sigma`: stability field scalar.
- `tau`: relaxation/memory delay.
- `v`: trajectory velocity vector.
- `r_p`: perigee radius.
- `f_io`: inbound/outbound geometry factor.

## Equations

```text
a_res = -tau * (v . grad) grad(Sigma)
```

```text
C-086a (directional): sign(a_res_parallel) = sign(v . grad(Sigma))
```

```text
C-086b2 (scaling law):
|a_res| = A0 * (|v|/v0)^p * (r_p/r0)^(-q) * (|grad(Sigma)|/g0)^s * f_io
```

```text
C-086b3 (covariate scaling law):
log(A_obs + eps) = b0 + b1*log(v_p/v0) + b2*log((h_p+h0)/h0)
                 + b3*log(|grad_g|/g0) + b4*log(1+geom_io)
                 + b5*log(1+non_grav/ng0) + e
```

## Derivation Steps

1. Start from first-order delayed-response expansion of the QNG acceleration operator.
2. Project the lag term on trajectory direction to obtain a sign-predictive directional observable (`C-086a`).
3. Factor amplitude into separable kinematic/geometry/field terms for pre-registration (`C-086b`/`C-086b2`).
4. Upgrade numeric branch to covariate scaling (`C-086b3`) with explicit systematics-control proxy and disjoint holdout policy.
5. Keep numeric evaluation external to directional pass/fail to prevent post-hoc coupling.

## Result

- `C-086a` yields a robust directional signature testable with fixed sign/directionality gates.
- `C-086b v1` is falsified under its locked band.
- `C-086b2` is the current numeric calibration branch and remains pending until strict holdout passes.
- `C-086b3` defines a defensible covariate-scaling framework and is currently blocked on missing disjoint holdout rows.

## Checks

- Unit check: `|a_res|` stays in acceleration units.
- Sign check: directional term follows `v . grad(Sigma)` convention.
- Limit check: `tau -> 0` implies `a_res -> 0` and recovers baseline dynamics.
- Workflow check: amplitude calibration cannot be tuned after seeing target-run outcomes.

## Next Action

- Use `QNG-T-041` for `C-086a` decision with amplitude gate in report-only mode.
- Track amplitude branches separately through:
- `05_validation/pre-registrations/qng-c-086b-amplitude-band-v1.md`
- `05_validation/pre-registrations/qng-c-086b-amplitude-band-v2.md`
- `05_validation/pre-registrations/qng-c-086b2-holdout-v1.md`
- `05_validation/pre-registrations/qng-c-086b3-scaling-law-v1.md`
- `05_validation/pre-registrations/holdout-registry.csv`
