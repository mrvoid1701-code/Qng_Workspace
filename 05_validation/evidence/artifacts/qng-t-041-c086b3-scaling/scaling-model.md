# C-086b3 Scaling Audit

## Model Form

```text
log(A_obs + eps) = b0 + b1*log(v_p/v0) + b2*log((h_p+h0)/h0) + b3*log(|grad_g|/g0) + b4*log(1+geom) + b5*log(1+non_grav/ng0) + e
```

## Covariates

- `h_p`: perigee altitude (`r_perigee_km - R_earth_km`)
- `v_p`: perigee speed from hyperbolic-energy closure
- `|grad_g|` proxy: `mu_earth / r_perigee^3`
- `geom`: `|cos(delta_in)-cos(delta_out)|`
- `non_grav`: acceleration-equivalent from explicit correction columns (thermal/SRP/maneuver/drag)

## Split

- calibration rows: `13`
- holdout rows present: `3`
- missing holdout IDs: `none`
- holdout status: `fail`

## Metrics

- calibration rmse_log: `3.831984`
- holdout rmse_log: `15.382645`
- holdout median_ratio: `1.178824e+08`
- holdout coverage_95: `0.333333`

## Coefficients

| term | beta | std_error |
| --- | --- | --- |
| `intercept` | `6.079488` | `9.381292e-07` |
| `log_v_perigee` | `-5.990773` | `3.822959e-07` |
| `log_altitude` | `-34.881671` | `1.383960e-06` |
| `log_grad_g_proxy` | `-11.289131` | `5.022636e-07` |
| `log_geom_proxy` | `15.932134` | `1.019903e-06` |
| `log_non_grav_proxy` | `0.000000` | `5222.113684` |
