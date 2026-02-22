#!/usr/bin/env python3
"""
Generate QNG derivation files from 02_claims/claims-register.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "02_claims" / "claims-register.md"
OUT_DIR = ROOT / "03_math" / "derivations"

ROW_RE = re.compile(
    r"^\|\s*(QNG-C-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)


@dataclass
class Claim:
    claim_id: str
    statement: str
    status: str
    confidence: str
    pages: str
    deriv_path: str


EQUATIONS: dict[str, list[str]] = {
    "004": ["persist_i(t+1) = H(Sigma_i(t) - Sigma_min)", "Node exists <=> Sigma_i >= Sigma_min"],
    "007": ["N_i = (V_i, chi_i, phi_i)", "N_i(t+1) = U(N_i(t), neighbors, eta_i(t))"],
    "012": ["chi = m / c", "m = c * chi"],
    "014": ["tau(chi) = alpha_tau * chi (first-order closure)", "d tau / d chi > 0"],
    "018": ["G = (N, E)", "d_G(i,j) = min_path(i->j) edge_count"],
    "019": ["kappa_i ~ avg_{j in Adj(i)}(k_j) - k_i", "Curvature proxy from graph-topology imbalance"],
    "020": ["T_C = t_R + tau(chi) + (nablaSigma)*tau"],
    "021": ["T_C = t_R + v*tau(chi) + deltaSigma", "DeltaL = v*tau(chi)"],
    "024": ["DeltaL = v * tau"],
    "025": ["a_res ~ -tau * (v . nabla) nablaSigma"],
    "026": ["a_res ~ -tau * (v . nabla) nablaSigma", "Flyby/Pioneer residual follows first-order lag term"],
    "027": ["DeltaSigma_DM = Sigma_hist - Sigma_now", "Sigma(x,t) = integral K(t-t')*chi(x,t') dt'"],
    "029": ["N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))"],
    "032": ["Sigma_i = Sigma_chi * Sigma_struct * Sigma_temp * Sigma_phi", "0 <= Sigma_i <= 1"],
    "033": ["Node removed if Sigma_i < Sigma_min"],
    "036": ["g(x,t) = -nablaSigma(x,t)", "F_grav = m_test * g"],
    "037": ["Sigma(x,t) = integral_{-inf}^{t} K(t-t')*chi(x,t') dt'", "K(Delta t)=(1/tau)exp(-Delta t/tau)"],
    "038": ["a_res ~ -tau*(v.nabla)nablaSigma", "a_total = -nablaSigma + a_res"],
    "040": ["d(DeltaSigma_DM)/dt = -(1/tau_h)DeltaSigma_DM + source", "source=0 => DeltaSigma_DM~exp(-t/tau_h)"],
    "042": ["m = m_0 * Sigma_temp"],
    "044": ["I_eff ~ chi * tau"],
    "048": ["P_persist = 1/(1+exp(-beta_q*(Sigma_i-Sigma_min)))"],
    "051": ["g(x,t) = -nablaSigma(x,t)"],
    "054": ["nablaSigma(t-tau)=nablaSigma(t)-tau*d/dt[nablaSigma(t)]+O(tau^2)"],
    "055": ["|a_res| ~ tau*|v|*|partial_parallel nablaSigma|"],
    "056": ["a_total = -nablaSigma - tau*(v.nabla)nablaSigma + O(tau^2)", "tau->0 => a_total = -nablaSigma"],
    "058": ["Phi_lens ~ Sigma", "alpha_hat ~ nabla_perp Phi_lens ~ nabla_perp Sigma"],
    "060": ["a_res ~ -tau*(v.nabla)nablaSigma"],
    "062": ["Sigma^n = sum_{m<=n} w_{n-m}*chi^m, w_r~exp(-r*dt/tau)", "a_k^n = -nablaSigma^n(x_k^n)"],
    "064": ["T_C = t_R + DeltaL", "DeltaL = v*tau(chi)"],
    "066": ["a_lag ~ -chi * nabla(dSigma/dt)"],
    "069": ["T_C = t_R + v*tau(chi) + deltaSigma"],
    "072": ["chi = 70/(3e8) = 2.33e-7 kg*s/m"],
    "073": ["a = -nablaSigma + tau*(v.nabla)nablaSigma"],
    "074": ["rho_chi(t) = integral_{-inf}^{t} chi(t')*K(t-t') dt'"],
    "077": ["e_a <= e_b if dependency path exists from e_a to e_b"],
    "078": ["r <= c*(t - tau(chi))"],
    "081": ["G^{mu nu} = 8*pi*G_N*(T_matter^{mu nu} + T_chi^{mu nu})"],
    "082": ["v_c(r)^2/r = g_baryon(r) + g_memory(r)", "g_memory(r) = -partial_r Sigma_memory(r)"],
    "085": ["Sigma = K*chi", "g=-nablaSigma", "a_res~ -tau*(v.nabla)nablaSigma"],
    "086": ["|a_res| in [1e-10,1e-8] m/s^2 near perigee (claimed band)"],
    "090": ["delta_t_TOA ~ integral a_lag_parallel(t') dt' / c"],
    "091": ["Delta h ~ A_asym * tau(chi) * f_ringdown(t)"],
    "093": ["a_total = -nablaSigma - tau*(v.nabla)nablaSigma + O(tau^2)", "tau->0 => classical limit"],
    "094": ["Coarse-grained fast-response limit maps to Einstein-form closure"],
    "095": ["N_i(t+1)=U(...,eta_i)", "psi = ensemble_map({phi_i})", "d psi/dt ~ H_eff psi"],
    "096": ["Phi(x,t)=sum_i phi_i(t) delta(x-x_i)", "Box Phi + V'(Phi)=0 (effective)"],
    "100": ["G=(N,E), no predefined metric g_{mu nu}", "Geometry from adjacency/update history"],
    "101": ["T_C = t_R + v*tau = t_R + DeltaL"],
    "103": ["a(t) proportional to |N(t)|^(1/3)"],
    "104": ["a(t) = (|N(t)|/|N(t0)|)^(1/3)"],
    "107": ["J = -mu_s * nablaSigma", "partial_t rho + nabla.J = source/sink"],
    "108": ["C_phi(x,t) = |<exp(i*phi)>_local|", "Filament corridor: C_phi >= C_min and tau(x,t) <= tau_max"],
    "109": ["H_obs(t) = H_geom(t) + d/dt[ln U(t)] - d/dt[ln C_sync(t)]", "q_obs = -1 - (dH_obs/dt)/H_obs^2"],
    "110": [
        "DeltaT/T = (DeltaT/T)_G + epsilon_coh * M(n_hat)",
        "Non-Gaussian marker: f_NL_eff != 0; axis marker: A_axis != 0",
    ],
    "111": ["S(t) = k_S * log(Omega(t))"],
    "112": ["R(t) = |(1/|N|) * sum_i exp(i*phi_i)|", "dR/dt = gamma_sync*R*(1-R) - gamma_dec*R"],
    "113": ["m_eff(x) = c * chi(x)", "Delta m_eff = c * Delta chi"],
    "114": ["T_C = t_R + v*tau", "Delta T_C = v*Delta tau"],
    "115": ["g_art(x,t) = -nablaSigma_art(x,t)", "alpha_hat_art ~ (2/c^2) * integral g_art,perp dl"],
    "116": ["N(t+1) = U_theta(N(t))", "Resonance condition: arg(lambda_k(U_theta)) = 2*pi*m/T"],
    "117": ["Z_total = sum_i w_i * z_i", "Pass set: z_flyby<z0, z_lensing<z0, z_cmb<z0, z_lss<z0"],
    "118": ["Falsify if any gate fails: F = 1[g_taufail or g_lensfail or g_GRfail]", "QNG valid only if F = 0"],
}

DERIV_NOTES: dict[str, list[str]] = {
    "025": ["Derived with first-order Taylor expansion of delayed field evaluation."],
    "026": ["Same operator as QNG-C-025, applied to mission-specific trajectories."],
    "040": ["Predicts measurable halo fading timescale tau_h in isolated systems."],
    "056": ["This is the key reduction used to recover Newton/GR-like behavior."],
    "062": ["Use the same kernel tau as observational fits for consistency checks."],
    "081": ["T_chi^{mu nu} must preserve total covariant conservation constraints."],
    "094": ["Requires explicit coarse-graining map from graph variables to continuum fields."],
    "095": ["Effective Schrodinger-like form is regime-dependent, not exact at all scales."],
    "096": ["Continuum form is valid only after coarse graining of node excitations."],
    "108": ["Corridor criterion is operational and should be calibrated against filament catalogs."],
    "109": ["Acceleration claim is effective/phenomenological and does not assume Lambda by construction."],
    "110": ["Prediction targets summary statistics (f_NL, cold-spot significance, axis alignment), not a single map feature."],
    "112": ["Coherence-burst acts as a synchronization mechanism; quantify burst width and amplitude in simulations."],
    "113": ["Speculative engineering claim; include explicit control-energy and stability-cost terms before hardware interpretation."],
    "114": ["Treat tau engineering as a controllability hypothesis; separate signal-speed from processing-delay semantics."],
    "115": ["Lensing analogue should be benchmarked first in simulation/graph-lab setups before astrophysical scaling."],
    "116": ["Programmable-physics interpretation requires a reproducible control map theta -> U_theta and error bounds."],
    "117": ["Priority-test aggregator is for planning; production acceptance still uses per-test pass/fail gates."],
    "118": ["Falsification logic should remain binary and pre-registered to avoid post-hoc threshold tuning."],
}


def parse_claims() -> list[Claim]:
    claims: list[Claim] = []
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        claims.append(
            Claim(
                claim_id=m.group(1),
                statement=m.group(2),
                status=m.group(3),
                confidence=m.group(4),
                pages=m.group(5),
                deriv_path=m.group(6),
            )
        )
    return claims


def default_equation(claim: Claim) -> list[str]:
    return [
        "Formal relation to be finalized from claim text:",
        claim.statement,
    ]


def render(claim: Claim) -> str:
    cid = claim.claim_id[-3:]
    eqs = EQUATIONS.get(cid, default_equation(claim))
    notes = DERIV_NOTES.get(cid, [])

    lines: list[str] = []
    lines.append(f"# {claim.claim_id} Derivation")
    lines.append("")
    lines.append(f"- Claim statement: {claim.statement}")
    lines.append(f"- Source page(s): {claim.pages}")
    lines.append(f"- Claim status/confidence: {claim.status} / {claim.confidence}")
    lines.append("- Math maturity: v1")
    lines.append("")
    lines.append("## Definitions")
    lines.append("")
    lines.append("- Sigma: stability field scalar.")
    lines.append("- chi: straton load (chi = m/c).")
    lines.append("- tau: relaxation/memory delay.")
    lines.append("- nabla: spatial gradient operator.")
    lines.append("")
    lines.append("## Equations")
    lines.append("")
    lines.append("```text")
    lines.extend(eqs)
    lines.append("```")
    lines.append("")
    lines.append("## Derivation Steps")
    lines.append("")
    lines.append("1. Start from the canonical QNG definitions used in this claim.")
    lines.append("2. Substitute chi/tau/Sigma relationships from source pages.")
    lines.append("3. Apply first-order closure (or coarse-graining) where explicit dynamics are not fully specified.")
    lines.append("4. Keep only terms required for the claim-level observable.")
    lines.append("")
    lines.append("## Result")
    lines.append("")
    lines.append(f"- {claim.statement}")
    lines.append("- The equations above are the operational form to carry into validation/tests.")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("- Verify dimensional consistency after selecting model calibration constants.")
    lines.append("- Verify sign convention against g = -nablaSigma definition.")
    lines.append("- Compare limiting behavior as tau -> 0.")
    if notes:
        lines.append("")
        lines.append("## Claim-Specific Notes")
        lines.append("")
        for n in notes:
            lines.append(f"- {n}")
    lines.append("")
    lines.append("## Next Action")
    lines.append("")
    lines.append(f"- Link {claim.claim_id} to 05_validation/test-plan.md with explicit dataset and threshold.")
    lines.append("")
    return "\n".join(lines)


def write_index(claims: list[Claim]) -> None:
    lines = [
        "# QNG Derivations Index",
        "",
        "| Claim ID | File | Status | Confidence | Source page(s) |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in sorted(claims, key=lambda x: x.claim_id):
        lines.append(f"| {c.claim_id} | {c.deriv_path} | {c.status} | {c.confidence} | {c.pages} |")
    lines.append("")
    lines.append("- Generated by scripts/generate_derivations.py.")
    lines.append("")
    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    claims = parse_claims()
    targets = [c for c in claims if c.deriv_path.startswith("03_math/derivations/")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for claim in targets:
        path = ROOT / claim.deriv_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(claim), encoding="utf-8")
    write_index(targets)
    print(f"Generated derivations: {len(targets)}")
    print("Index: 03_math/derivations/README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
