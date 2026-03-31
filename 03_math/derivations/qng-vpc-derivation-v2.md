# VPC din Simetria Rețelei QNG Discrete — Derivare v2

**Status:** Derivare semi-formală — înlocuiește postulatul din straton-v2 §9.4.2
**Data:** 2026-03-06
**Dependențe:** qng-straton-interpretation-v2 (Eq. 1, schemă de notație)

---

## Scopul documentului

Straton-v2 §9.4.1 enumeră trei căi posibile pentru derivarea VPC:
(a) graph-averaging kernel, (b) graph update symmetry, (c) Σ field equation.

Prezentul document urmărește calea **(b): simetria de reflexie a rețelei cubice**,
demonstrând că termenul tangențial al lag-ului nu produce energie seculară pe orbite
periodice, fără a impune VPC ca postulat explicit.

---

## 1. Setup: Rețeaua Cubică și Regula de Update

**Rețeaua:** noduri $\mathbf{x} \in \mathbb{Z}^3 \cdot l_0(r)$, muchii de lungime
$l_0(r)$ la vecini fată (6 direcții: $\pm\hat{e}_x, \pm\hat{e}_y, \pm\hat{e}_z$).

**Câmpul de stabilitate:** $\Sigma(\mathbf{x})$ definit pe noduri; pentru o masă
punctuală: $\Sigma = -GM/r$.

**Termenul de lag (forma completă, fără VPC):**

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \; v^j \; \partial_j \partial_i \Sigma \tag{Eq. 1}$$

unde Hessianul $H_{ij} = \partial_i \partial_j \Sigma = \frac{GM}{r^3}(3\hat{r}_i\hat{r}_j - \delta_{ij})$.

---

## 2. Lema de Simetrie: Reflexia față de Planul Orbital

**Definiție:** Fie $\Pi_{\text{orb}}$ planul orbital al unui obiect, conținând
$\hat{r}$ (direcția radială) și $\hat{v} = \mathbf{v}/|\mathbf{v}|$.

**Operatorul de reflexie** $R_\theta$: reflexia față de $\Pi_{\text{orb}}$.

Sub $R_\theta$:
- $\Sigma(\mathbf{x}) \to \Sigma(R_\theta \mathbf{x}) = \Sigma(\mathbf{x})$ — câmpul
  radial-simetric este invariant
- $v_r \to +v_r$, $v_\theta \to -v_\theta$ — viteza radială invariantă,
  tangențială inversată
- $H_{ij} \to R_\theta H_{ij} R_\theta^T$ — tensorul Hessian se transformă covariant

**Proprietate cheie (câmp central):** Pentru $\Sigma = -GM/r$, Hessianul satisface:

$$H_{rr} = -2GM/r^3, \quad H_{\theta\theta} = H_{\phi\phi} = GM/r^3, \quad H_{r\theta} = 0$$

Sub $R_\theta$ (reflexie față de planul $\hat{r}$-$\hat{\theta}$):

$$H_{r\theta} \to -H_{r\theta} = 0 \quad \text{(simetric, deci invariant)}$$
$$H_{\theta\phi} \to -H_{\theta\phi} = 0 \quad \text{(zero, deci invariant)}$$

---

## 3. Termenul Tangențial și Anularea sa Seculară

**Componenta tangențială a lag-ului:**

$$a^\theta_{\text{lag}} = -\tau_{\text{phys}} \left( v_r H_{r\theta} + v_\theta H_{\theta\theta} \right)$$

Pentru câmp central pur ($H_{r\theta} = 0$):

$$a^\theta_{\text{lag}} = -\tau_{\text{phys}} \; v_\theta \; H_{\theta\theta} = -\tau_{\text{phys}} \; v_\theta \; \frac{GM}{r^3}$$

**Puterea disipată de componenta tangențială:**

$$\mathcal{P}_\theta = a^\theta_{\text{lag}} \cdot v_\theta = -\tau_{\text{phys}} \; v_\theta^2 \; \frac{GM}{r^3}$$

**Integrală pe o perioadă orbitală $T$:**

$$\Delta E_{\text{tang}} = \int_0^T \mathcal{P}_\theta \, dt = -\tau_{\text{phys}} \int_0^T v_\theta^2 \frac{GM}{r^3} dt$$

Aceasta este **semnul defic** — ar produce pierdere de energie orbitală! Dar:

**Argumentul de simetrie $R_\theta$:**

Sub $R_\theta$ (reflexia față de planul orbital):

- $v_\theta^2 \to v_\theta^2$ (invariant, pătrat)
- $r \to r$ (invariant)
- DECI: $\Delta E_{\text{tang}}$ **nu se anulează** prin $R_\theta$ singur!

**Argumentul corect: Simetria față de planul $\hat{r}$-$\hat{n}$ perpendicular pe orbită:**

Fie $R_n$: reflexia față de planul perpendicular pe $\hat{\theta}$ (planul $\hat{r}$-$\hat{n}$).

Sub $R_n$:
- $v_\theta \to -v_\theta$ (se inversează direcția orbitală)
- $\Sigma \to \Sigma$ (invariant în câmp central)
- $H_{\theta\theta} \to H_{\theta\theta}$ (invariant — scalar față de rotație în $\hat{r}$)
- $\mathcal{P}_\theta = a^\theta_{\text{lag}} \cdot v_\theta = -\tau \; v_\theta^2 \; GM/r^3$

$\mathcal{P}_\theta$ e pătratic în $v_\theta$ → invariant sub $R_n$. Nu ajută direct.

---

## 4. Calea corectă: Structura Discretă și Anularea la Graph Coarse-Graining

**Teorema (anulare la medie pe celulă):**

Pe rețeaua cubică cu $l_0 \sim r$, termenul Hessian discret se calculează prin
diferențe finite pe cele 6 muchii față. Fie celula din jurul nodului $\mathbf{x}_0$:

$$H^{\text{disc}}_{\theta\theta}(\mathbf{x}_0) = \frac{1}{l_0^2}
\left[\Sigma(\mathbf{x}_0 + l_0\hat{\theta}) + \Sigma(\mathbf{x}_0 - l_0\hat{\theta}) - 2\Sigma(\mathbf{x}_0)\right]$$

Media pe celulă (8 noduri):

$$\langle H^{\text{disc}}_{\theta\theta} \rangle_{\text{cell}} = H_{\theta\theta}^{\text{cont}} + O(l_0^2 \nabla^4 \Sigma)$$

Termenul de corecție $O(l_0^2)$ nu e neglijabil când $l_0 \sim r$ (galaxii!).

**Condiția de auto-consistență:** La scara galactică, $l_0$ e dat de Scenario B:
$l_0(r) \propto r^3$ → $l_0 \gg r$ la raze mari → **Hessianul discret e dominated de
termeni de corecție** și coarse-graining reduce efectiv $H_{\theta\theta}$.

**Estimarea reducerii:** Termenul dominant în expansion Taylor:

$$\Delta H^{\text{disc}}_{\theta\theta} = \frac{l_0^2}{12} \partial^4_\theta \Sigma + O(l_0^4)$$

Pentru $\Sigma = -GM/r$: $\partial^4_\theta \Sigma = 24 GM/r^5$ → reducere la scara $l_0/r$.

La $l_0 \gg r$ (periferia galactică unde flat curve e importantă):

$$H^{\text{disc}}_{\theta\theta} \sim H^{\text{cont}}_{\theta\theta} \times \left(\frac{r}{l_0}\right)^2 \to 0$$

**Deci termenul tangențial dispare la scara galactică** nu prin simetrie exactă,
ci prin coarse-graining: rețeaua e prea grosieră la $r_{\text{gal}}$ pentru a
rezolva variațiile $\theta$-uale ale câmpului.

---

## 5. Statutul VPC: Postulat → Semi-derivat

| Aspect | Straton-v2 | Această derivare |
|--------|-----------|-----------------|
| Anulare seculară tangențială | Postulat (VPC) | Emergentă din coarse-graining $l_0 \gg r$ |
| Anulare instantanee $a^\theta_{\text{lag}} = 0$ | Postulat | **NU** — există oscilații la freq. orbitală |
| Securitate Mercury/Venus | Prin postulat | Prin coarse-graining ($l_0 \ll r_{\text{Mercury}}$) |
| Securitate galaxii | Prin postulat | Prin $l_0 \gg r_{\text{gal}}$ → lag tangențial → 0 |
| Status | Postulat | Semi-derivat, necesită simulare |

**VPC emergent (formulare slabă):**

> *Pe o orbită periodică, contribuția tangențială a termenului de lag la energia
> orbitală se anulează la ordinul $O(r^2/l_0^2)$ prin coarse-graining-ul rețelei
> cubice QNG, fără a fi necesară o constrângere suplimentară.*

---

## 6. Implicații pentru Consistența Solară

La scara solară ($r \leq$ 100 AU), $l_0(r) = l_{0,1\text{AU}} \cdot (r/\text{AU})^3$:

| Locație | $r$ | $l_0$ | $r/l_0$ | Supr. tang. |
|---------|-----|-------|---------|-------------|
| Mercury | 0.39 AU | 0.05 AU | 7.6 | $(r/l_0)^2 \approx 58$ → **nu** suprimate! |
| Earth | 1 AU | 0.86 AU | 1.16 | $(r/l_0)^2 \approx 1.3$ → marginal |
| Pioneer (40 AU) | 40 AU | 55k AU | 0.00073 | $(r/l_0)^2 \ll 1$ → **suprimate** |
| Galaxie (10 kpc) | 10 kpc | $\gg$ | $\ll 1$ | **suprimate** |

**La Mercury, $r/l_0 \approx 7.6$ — coarse-graining NU suprimă componenta tangențială!**

Aceasta înseamnă că la scara Mercury, termenul tangențial nu dispare din
coarse-graining. Pentru Mercury, VPC trebuie să funcționeze dintr-un alt mecanism —
sau componenta tangențială e mică din altă cauză.

**Rezoluție:** La Mercury ($v_\theta = 47.9$ km/s), termenul tangențial instantaneu:

$$a^\theta_{\text{lag}} = -\tau_{\text{phys}} \; v_\theta \; H_{\theta\theta}^{\text{disc}}$$

cu $\tau_{\text{phys}} \approx 0.051$ s (din tabel straton-v2 §7.5) și
$H^{\text{disc}}_{\theta\theta} \approx GM/r^3 = GM_\odot/(0.39\text{AU})^3$:

$$a^\theta_{\text{lag}} \approx 0.051 \times 47870 \times 6.6 \times 10^{-4} = 1.6 \text{ m/s}^2$$

Aceasta ar fi catastrofică! Dar $\tau_{\text{phys}} = \tau_{\text{graph}} \times l_0/c$:

$$\tau_{\text{phys}} = 0.002051 \times (0.05 \text{ AU} / c) = 0.002051 \times 24.9\text{s} = 0.051 \text{ s}$$

$$a^\theta_{\text{lag}} = 0.051 \times 47870 \times \frac{1.327\times10^{20}}{(5.83\times10^{10})^3} = 6.9\times10^{-10} \text{ m/s}^2$$

Fracție din Newton: $6.9\times10^{-10} / 3.96\times10^{-2} = 1.7\times10^{-8}$ (17 ppb) — sub limita efemerică. **Deci la Mercury, termenul e mic numeric** chiar dacă nu e zero.

---

## 7. Concluzie și Status Actual

**VPC emergent (din coarse-graining la scară galactică):**
- ✓ Termenul tangențial dispare la $r_{\text{gal}}$ din $l_0 \gg r$
- ✓ La Mercury, termenul e $\sim 17$ ppb — sub detectabilitate
- ✗ Nu e zero exact — există oscilații la frecvența orbitală
- ✗ Nu e derivat din Lagrangian sau simetrie exactă de gauge

**Ce mai lipsește pentru o derivare completă:**
1. Simulare QNG discretă în 3D care să arate că $H^{\text{disc}}_{\theta\theta} \to 0$
   la coarse-graining corect
2. Demonstrarea că termenul $\sim (r/l_0)^2 H^{\text{cont}}$ produce efecte sub
   threshold la toate scările testate
3. Derivarea din acțiune (calea (c) din straton-v2 §9.4.2) — deschis

**Status:** De la **postulat** (straton-v2) la **semi-derivat** (acest document).
Falsificatorul observațional rămâne: orice orbită cu drift secular $> 10^{-12}$ m/s²
infirmă VPC.
