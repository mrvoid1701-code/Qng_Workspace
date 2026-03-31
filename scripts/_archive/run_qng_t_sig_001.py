#!/usr/bin/env python3
"""
QNG-T-SIG-001/002: Generalized Poisson + metric convergence check.
Implements prereg in 05_validation/pre-registrations/qng-t-sig-001.md.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts"
OUT_DIR_DEFAULT = ARTIFACTS_ROOT / "qng-t-sig-001"


def spd_from_hessian(h: np.ndarray, clip: float = 1e-3) -> np.ndarray:
    # h shape (..., 2, 2)
    w, v = np.linalg.eigh(h)
    w_clipped = np.clip(-w, clip, None)  # -H to get attractive metric; keep positive
    return (v * w_clipped[..., None, :]) @ np.swapaxes(v, -1, -2)


def variable_poisson_step(ginv: np.ndarray, rhs: np.ndarray, dx: float) -> np.ndarray:
    # simple Gauss-Seidel with variable coefficients (only diagonal terms for speed)
    nx, ny = rhs.shape
    sigma = np.zeros_like(rhs)
    for _ in range(200):  # inner relax
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                gx = ginv[i, j, 0, 0]
                gy = ginv[i, j, 1, 1]
                denom = 2 * (gx + gy)
                if denom == 0:
                    continue
                sigma[i, j] = (
                    gx * (sigma[i + 1, j] + sigma[i - 1, j])
                    + gy * (sigma[i, j + 1] + sigma[i, j - 1])
                    - rhs[i, j] * dx * dx
                ) / denom
    return sigma


def laplacian(u: np.ndarray, dx: float) -> np.ndarray:
    return (
        -4 * u
        + np.roll(u, 1, 0)
        + np.roll(u, -1, 0)
        + np.roll(u, 1, 1)
        + np.roll(u, -1, 1)
    ) / (dx * dx)


def hessian(u: np.ndarray, dx: float) -> np.ndarray:
    u_xx = (np.roll(u, -1, 0) - 2 * u + np.roll(u, 1, 0)) / (dx * dx)
    u_yy = (np.roll(u, -1, 1) - 2 * u + np.roll(u, 1, 1)) / (dx * dx)
    u_xy = (
        np.roll(np.roll(u, -1, 0), -1, 1)
        - np.roll(np.roll(u, -1, 0), 1, 1)
        - np.roll(np.roll(u, 1, 0), -1, 1)
        + np.roll(np.roll(u, 1, 0), 1, 1)
    ) / (4 * dx * dx)
    h = np.zeros(u.shape + (2, 2))
    h[..., 0, 0] = u_xx
    h[..., 1, 1] = u_yy
    h[..., 0, 1] = u_xy
    h[..., 1, 0] = u_xy
    return h


def run(grid_n: int, domain: float, max_iter: int, tol_g: float):
    L = domain
    dx = (2 * L) / grid_n
    rhs = np.zeros((grid_n, grid_n))
    cx = cy = grid_n // 2
    rhs[cx, cy] = 4 * np.pi / (dx * dx)  # delta source scaled

    g = np.zeros((grid_n, grid_n, 2, 2))
    g[..., 0, 0] = 1.0
    g[..., 1, 1] = 1.0
    history = []

    sigma = np.zeros_like(rhs)
    final_iter = max_iter
    for n in range(max_iter):
        ginv = np.linalg.inv(g)
        sigma = variable_poisson_step(ginv, rhs, dx)
        H = hessian(sigma, dx)
        g_next = spd_from_hessian(H)

        rel = np.linalg.norm(g_next - g) / max(np.linalg.norm(g), 1e-12)
        lap = laplacian(sigma, dx)
        resid = np.abs(lap - rhs) / (np.abs(rhs).max() + 1e-12)
        max_resid = np.quantile(resid, 0.9)
        history.append((n, rel, float(max_resid)))
        g = g_next
        if rel < tol_g:
            final_iter = n
            break

    lap = laplacian(sigma, dx)
    resid = np.abs(lap - rhs) / (np.abs(rhs).max() + 1e-12)
    p90_resid = float(np.quantile(resid, 0.9))
    return sigma, resid, history, p90_resid, final_iter


def save_png(path: Path, arr: np.ndarray, title: str):
    plt.figure(figsize=(4, 4))
    plt.imshow(arr, origin="lower", cmap="viridis")
    plt.colorbar()
    plt.title(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="QNG-T-SIG-001/002 generalized Poisson test")
    ap.add_argument("--grid", type=int, default=100)
    ap.add_argument("--domain", type=float, default=5.0)
    ap.add_argument("--max-iter", type=int, default=50)
    ap.add_argument("--tol-g", type=float, default=1e-2)
    ap.add_argument("--out-dir", default=str(OUT_DIR_DEFAULT))
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    sigma, resid, history, p90_resid, final_iter = run(args.grid, args.domain, args.max_iter, args.tol_g)

    g1_pass = p90_resid < 0.10
    g2_pass = final_iter < args.max_iter
    final = g1_pass and g2_pass

    # outputs
    save_png(out_dir / "sigma_field.png", sigma, "Sigma field")
    save_png(out_dir / "residual_map.png", resid, "Residual |ΔΣ| normalized")

    hist_path = out_dir / "convergence_history.csv"
    np.savetxt(hist_path, np.array(history), delimiter=",", header="iter,rel_change_g,p90_residual", comments="")

    gate_rows = [
        {"gate": "G1", "metric": "p90_residual", "value": f"{p90_resid:.6e}", "threshold": "<1.0e-1", "status": "pass" if g1_pass else "fail"},
        {"gate": "G2", "metric": "iter_converged", "value": str(final_iter), "threshold": f"<= {args.max_iter-1}", "status": "pass" if g2_pass else "fail"},
        {"gate": "FINAL", "metric": "decision", "value": "pass" if final else "fail", "threshold": "G1 & G2", "status": "pass" if final else "fail"},
    ]
    gate_path = out_dir / "gate_summary.csv"
    import csv

    with gate_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=gate_rows[0].keys())
        w.writeheader()
        w.writerows(gate_rows)

    (out_dir / "run-log.txt").write_text(
        json.dumps(
            {
                "grid": args.grid,
                "domain": args.domain,
                "max_iter": args.max_iter,
                "tol_g": args.tol_g,
                "p90_residual": p90_resid,
                "final_iter": final_iter,
                "g1_pass": g1_pass,
                "g2_pass": g2_pass,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(json.dumps({"decision": final, "p90_residual": p90_resid, "final_iter": final_iter}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
