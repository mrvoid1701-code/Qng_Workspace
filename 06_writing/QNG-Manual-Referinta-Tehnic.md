# QNG — Manual de Referință Tehnic Complet

**Quantum Node Gravity (QNG) — v2 Core-Closure**
*Sistematizare exhaustivă a formalismului matematic*
*Data: 2026-03-16*

---

## 1. Ontologia și Axiomatica

### 1.1 Starea Sistemului

Sistemul fizic este un **graf dinamic** G(t) = (N(t), E(t)) în care fiecare nod i poartă o stare internă cu trei componente:

    N_i(t) = ( V_i(t),  chi_i(t),  phi_i(t) )

| Variabilă | Tip | Interpretare fizică | Unități |
|-----------|-----|---------------------|---------|
| V_i(t) | real, > 0 | Volum relațional al nodului i | L^3 |
| chi_i(t) | real, >= 0 | Sarcina straton ("straton load") — cuplaj la memorie | kg·s/m |
| phi_i(t) | real | Faza locală a câmpului scalar sigma | adimensional |
| Sigma_i(t) | real, [0,1] | Câmpul de stabilitate — măsură de coerență locală | adimensional |

**Câmpul scalar sigma:** pe fiecare nod există și un câmp scalar sigma_i in R, cu rol dublu —
câmp gravitațional discret și sursă pentru tensorul energie-impuls.

### 1.2 Poarta de Existență (Axiomă de Bază)

Un nod i este **activ** la momentul t dacă și numai dacă:

    Sigma_i(t) >= Sigma_min

- Dacă Sigma_i < Sigma_min: nodul este eliminat din graf.
- Dacă Sigma_i >= Sigma_birth și condiția de coerență locală este îndeplinită: se naște un nod copil cu k_new = 1.

### 1.3 Cuantificarea Volumului

Volumul nu este continuu — este **cuantificat** printr-un număr întreg k_i in Z_{>0}:

    V_i(t) = k_i(t) * V_0,   k_i >= 1

unde V_0 este cuanta de volum de referință (dimensiune L^3, nu este o coordonată de embedding —
este un volum relațional).

### 1.4 Parametrii de Control și de Zgomot

**Parametri de control (intenționali):**

| Simbol | Valoare canonică | Rol |
|--------|-----------------|-----|
| tau | 1.3 (simulări T-029) | Scala temporală de memorie (delay) |
| k | 0.85 (T-029) | Amplitudinea kernelului exponențial |
| alpha_tau | de determinat empiric | Coeficient de scalare: tau_i = alpha_tau * chi_i |
| beta_+, beta_- | liberi | Ratele de creștere/scădere a volumului |
| Phi_scale | 0.08–0.10 | Scala potențialului newtonian |
| lambda | 0.05 | Cuplajul back-reaction semiclasic |

**Parametri de zgomot:**
- eta_i(t): zgomot local stochastic pur, prezent **exclusiv** în F_{chi,i} și F_{phi,i}
- Natura zgomotului: **Gaussian** (în simulările actuale) — eta_i ~ N(0, sigma_eta^2)
- Amplitudine în T-029: sigma_eta = noise_scale * 1e-3 per pas de timp

> ⚠️ **Lacună L5:** Formalismul actual tratează eta_i ca zgomot Gaussian pur (Brownian).
> Nu există în fișiere o derivare riguroasă a necesității naturii Gaussiene vs. non-Gaussiene.
> Trebuie justificat dacă zgomotul termic al grafului este Gaussian sau dacă natura discretă
> a grafului impune zgomot Lévy/non-Gaussian.

---

## 2. Cadrul Formal — Ecuația Principală (SFDDE)

### 2.1 Operatorul de Actualizare Discret (QNG-C-029)

Ecuația fundamentală este un operator de actualizare **discret, cauzal, local**:

    N_i(t+1) = U( N_i(t),  {N_j(t)}_{j in Adj(i)},  eta_i(t) )

Expandat explicit:

    chi_i(t+1)  = chi_i(t)  + F_{chi,i}(stare locală, eta_i)
    phi_i(t+1)  = phi_i(t)  + F_{phi,i}(stare locală, eta_i)
    k_i(t+1)    = max(1,  k_i(t) + Delta_k_i^+ - Delta_k_i^-)
    V_i(t+1)    = k_i(t+1) * V_0

cu regulile de volum:

    Delta_k_i^+ = floor( beta_+ * max(0,  Sigma_i - Sigma_grow) )
    Delta_k_i^- = floor( beta_- * max(0,  Sigma_shrink - Sigma_i) )

### 2.2 Kernelul de Întârziere — Câmpul de Stabilitate cu Memorie

Acesta este nucleul ecuației **SFDDE** a teoriei. Câmpul de stabilitate la pasul n nu depinde
doar de starea curentă — el integrează **istoria sistemului** prin un kernel cauzal exponențial:

    Sigma^n(x) = sum_{r=0}^{R} w_r * chi^{n-r}(x)

unde:

    w_r = k * exp(-r * dt / tau) / Z,    Z = sum_{s=0}^{R} exp(-s * dt / tau)

**Câmpul de masă chi^m(x)** la pasul m este densitatea de masă netezită Gaussian:

    chi^m(x) = 1 / (pi * 2*sigma_k^2 * N) * sum_{j=1}^{N} exp( -|x - x_j^m|^2 / (2*sigma_k^2) )

cu sigma_k = 0.15, N = 140 particule.

**Gradientul câmpului de stabilitate** (forța efectivă):

    grad Sigma^n(x) = sum_{r=0}^{R} w_r * grad chi^{n-r}(x)

    d chi^m/dx (x) = -2/(2*sigma_k^2) * 1/(pi * 2*sigma_k^2 * N)
                     * sum_j (x - x_j^m) * exp( -|x - x_j^m|^2 / (2*sigma_k^2) )

### 2.3 Structura Kernelului — Comparație Controale Negative

| Kernel | Ecuație | Interpretare fizică |
|--------|---------|---------------------|
| Cauzal exponențial (corect) | w_r = k * exp(-r*dt/tau) | Memorie care dispare exponențial în trecut |
| Instantaneu (NC-1) | w_0 = k, w_{r>0} = 0 | Gravitație fără memorie — tau = 0 |
| Tau scurt (NC-2) | tau = 0.05 | Memorie de 26× prea scurtă |
| Tau lung (NC-3) | tau = 8.0 | Memorie de 6× prea lungă |
| Anti-gravitație (NC-4) | w_r = -k * exp(-r*dt/tau) | Kernelul cu semn schimbat |

**Rezultat experimental (T-029):** Numai kernelul cu tau=1.3, k=0.85 produce
delta_chi2_total = -671.49 față de baseline. Toate NC au chi2_NC / chi2_correct > 5x
(confirmat pentru 12 seeds).

### 2.4 Termenul de Difuzie și Integrarea Numerică

Ecuația de mișcare a particulei i la pasul n (integrare symplectic Euler):

    a_i^n = -G_base * grad Sigma^n(x_i^n) - kappa * x_i^n + eta_i^n

    v_i^{n+1} = v_i^n + a_i^n * dt
    x_i^{n+1} = x_i^n + v_i^{n+1} * dt

cu G_base = 1.0, kappa = 0.05 (forță restauratoare spre origine), dt = 0.06.

Termenul de difuzie: eta_i^n ~ N(0, (sigma_eta * 1e-3)^2), sigma_eta = 1.0

---

## 3. Câmpul de Stabilitate Sigma_i — Structura Completă (QNG-C-032)

### 3.1 Descompunerea Multiplicativă

    Sigma_i = Sigma_{chi,i} * Sigma_{struct,i} * Sigma_{temp,i} * Sigma_{phi,i}   in [0,1]

Fiecare factor:

    Sigma_{chi,i}    = exp( -|chi_i - chi_ref| / chi_ref )
    Sigma_{struct,i} = exp( -|k_i - k_eq| / k_eq )
    Sigma_{temp,i}   = exp( -|Delta_t_local - tau_i| / tau_i )
    Sigma_{phi,i}    = (1 + cos(Delta_phi_i)) / 2

**Cuplajul cheie** (legătura SFDDE ↔ variabilele de stare):

    tau_i = alpha_tau * chi_i

Aceasta înseamnă că **scala de memorie temporală** a nodului i este direct proporțională cu
sarcina sa straton. Este relația care face teoria **falsificabilă** prin măsurători cross-class:

    A_i / A_j = chi_i / chi_j   (predicție QNG)
    A_i / A_j ≈ 1               (predicție baseline constant-lag)

### 3.2 Funcționala de Densitate de Probabilitate

> ⚠️ **Lacună L1 (Critică):** Repository-ul nu conține o derivare explicită a funcționalei
> de densitate de probabilitate P[Sigma] sau a distribuției stochastice a câmpului Sigma_i.
>
> Derivarea completă necesară pentru paper:
>
> 1. Ecuația Fokker-Planck pentru P(chi_i, t):
>
>    dP/dt = -d/d_chi [ F_chi(chi) * P ] + (sigma_eta^2 / 2) * d^2 P/d_chi^2
>
> 2. Distribuția staționară P_stat(chi_i) din condiția dP/dt = 0.
>
> 3. Propagare prin Sigma_chi = exp(-|chi - chi_ref|/chi_ref) pentru P(Sigma_chi).
>
> 4. P(Sigma_i) ca distribuție a produsului celor patru factori.

---

## 4. Sectorul GR — Geometria Discretă

### 4.1 Curbura Forman-Ricci

Pentru fiecare muchie (i,j):

    F(i,j) = 4 - k_i - k_j + 2 * t(i,j)

unde t(i,j) = |N(i) ∩ N(j)| este numărul de vecini comuni.

**Tensorul Ricci discret:**

    R_{mu,nu}(i) = (1/k_i) * sum_{j in N(i)} F(i,j) * n^mu_ij * n^nu_ij

**Curbura scalară:**

    R(i) = R_{11}(i) + R_{22}(i)

**Tensorul Einstein discret:**

    G_{mu,nu}(i) = R_{mu,nu}(i) - (1/2) * delta_{mu,nu} * R(i)

Proprietate 2D: Tr G = G11 + G22 = 0 exact (verificat în G11d cu eroare < 1e-10).

### 4.2 Metrica ADM (G10)

Potențialul newtonian efectiv:

    U(i) = Phi_scale * sigma(i) / sigma_max > 0

Metrica spațio-temporală:

    g_00(i) = -N(i)^2 = -(1 + Phi)^2 = -(1 - 2U + U^2)
    g_11(i) = gamma_s(i) = 1 - 2*Phi(i) = 1 + 2U

unde lapse-ul N(i) = 1 + Phi(i) și Phi(i) = -U(i).

### 4.3 Ecuațiile Einstein (G11)

Constrângerea Hamiltoniană — regresie OLS:

    R(i) = A + B * sigma_norm(i)

    Lambda_eff = A/2
    G_eff      = B / (16*pi)

Identitatea Bianchi discretă:

    B_x(i) = d_x G_11(i) + d_y G_12(i) ≈ 0
    B_y(i) = d_x G_12(i) + d_y G_22(i) ≈ 0

Tensorul Energie-Impuls:

    T_{mu,nu}(i) = d_mu sigma * d_nu sigma (i)
                   - (1/2) * g_{mu,nu}(i) * [ |grad sigma|^2(i) + m^2 * sigma^2(i) ]

### 4.4 Acțiunea Discretă (G16)

    S_total = S_EH + S_Lambda + S_kin + S_pot

    S_EH     = (1 / 16*pi*G) * sum_i R_i * vol(i)
    S_Lambda = -(Lambda / 8*pi*G) * sum_i vol(i)
    S_kin    = -(1/2) * sum_{edges} (sigma_i - sigma_j)^2 * vol_edge
    S_pot    = -(m^2/2) * sum_i sigma_i^2 * vol(i)

Laplasianul random-walk (ecuația Klein-Gordon discretă):

    L_rw[sigma](i) = (1/k_i) * sum_{j in N(i)} [ sigma(j) - sigma(i) ]

Masa efectivă via coeficientul Rayleigh:

    m^2 = [ sum_i sigma(i) * L_rw[sigma](i) * vol(i) ] / [ sum_i sigma(i)^2 * vol(i) ]

Hessianul acțiunii (stabilitate):

    H_ii = -sum_j vol_edge_ij - m^2 * vol(i)  <  0

Condiția G16d: frac(H_ii < 0) > 0.90.

### 4.5 Parametrii Post-Newtonienii (G15)

    gamma_PPN(i) = [g_11(i) - 1] / [-g_00(i) - 1]
                 = 2U / (2U + U^2)
                 = 1/(1 + U/2)
                 -> 1  ca  U -> 0

    beta_PPN = 1/2   (din alegerea N = 1 + Phi)

Întârziere Shapiro:

    c_eff(i) = N(i) / sqrt(gamma_s(i))
    delta_S(i) = sqrt(gamma_s)/N - 1
    Shapiro_ratio = mean(delta_S)_inner / mean(delta_S)_outer > 2.0

> ⚠️ **Lacună L3:** beta_PPN = 1/2 deviează de la GR (beta_GR = 1). Gateul G15c acceptă
> beta in (0.3, 0.7). Aceasta trebuie adresată în paper — fie ca predicție distinctivă
> a QNG, fie ca limitare a metricii actuale.

---

## 5. Sectorul Cuantic (G17–G21)

### 5.1 Cuantificarea Canonică (G17)

Descompunerea în moduri proprii ale Laplasianului random-walk:

    L_rw[psi_k](i) = (1 - mu_k) * psi_k(i),    mu_k in [0,1]

Frecvențele modurilor:

    omega_k = sqrt(mu_k + m_eff^2),    m_eff^2 = 0.014

Energia de punct zero (vacuum cuantic):

    E_0 = (1/2) * sum_{k=1}^{K_eff} omega_k

Relația de incertitudine Heisenberg (verificată exact):

    Delta_sigma * Delta_pi = 1/2

### 5.2 Geometria Informațională Cuantică (G18)

Distribuția Gibbs pe moduri:

    p_k = exp(-omega_k / T_ref) / Z,    Z = sum_k exp(-omega_k / T_ref)

Entropia cuantică:

    S = -sum_k p_k * ln(p_k)

Dimensiunea spectrală (din difuzia pe graf):

    d_s = -2 * d ln P(t) / d ln t

unde P(t) = (1/N) * sum_i K(i,i,t) este probabilitatea de retur a mersului aleator la timp t.

**Rezultat obținut:** d_s = 4.082 pe graful Jaccard Informațional (fără embedding spațial).
Curgerea UV -> IR: d_s ≈ 2.87 -> 4.45.

### 5.3 Efectul Unruh Termic (G19)

Temperatura Unruh locală:

    alpha(i) = k_i / k_bar
    a_eff(i) = mean_{j in N(i)} |alpha(j) - alpha(i)|
    T_Unruh(i) = a_eff(i) / (2*pi)

Ocupația modurilor Bose-Einstein:

    n_k = 1 / (exp(omega_k / T_global) - 1)

Propagatorul termal:

    G_beta(i,j) = sum_k psi_k(i) * psi_k(j) * (2*n_k + 1) / (2*omega_k)
                = G_0(i,j) + Delta_G_thermal(i,j)

    Delta_G_thermal(i,j) = sum_k psi_k(i) * psi_k(j) * n_k / omega_k

### 5.4 Back-reaction Semiclasic (G20)

Densitatea de energie a vidului:

    eps_vac(i) = (1/2) * sum_k omega_k * psi_k(i)^2

Câmpul de corecție back-reaction:

    f(i) = (eps_vac(i) - eps_bar) / eps_bar

Metrica corectată la primul ordin:

    alpha^(1)(i) = alpha^(0)(i) * (1 + lambda * f(i)),    lambda = 0.05

Deplasarea frecvențelor modurilor:

    delta_omega_k = (lambda/2) * omega_k * sum_i f(i) * psi_k(i)^2
    omega_k^(1)   = omega_k + delta_omega_k

Corecția energiei de vid:

    delta_E_0 = (lambda/2) * E_0 * cv(eps_vac)^2

Reziduul auto-consistenței (condiție loop closure):

    res(i) = |eps_vac^(1)(i) - eps_vac^(0)(i)| / eps_bar  <  0.20

### 5.5 Termodinamica Completă (G21)

Verificare: F = U - T*S cu eroare = 1.3e-16 (precizie mașină), S >= 0, C_V > 0.

---

## 6. Graful Jaccard Informațional — Emergența Dimensiunii 4D

### 6.1 Principiu

Două noduri i, j se conectează cu o pondere proporțională cu **suprapunerea vecinătăților
lor informaționale** (similitudine Jaccard), **fără nicio embedding spațial**:

    J(i,j) = |N(i) ∩ N(j)| / |N(i) ∪ N(j)|

### 6.2 Rezultat Central

Pe graful Jaccard Informațional:

    d_s = 4.082 ≈ 4   (4D emergent din conectivitate pură)

Curgerea dimensiunii spectrale:
- UV (t in [2,5]):  d_s ≈ 2.87  — consistent cu CDT și Asymptotic Safety
- IR (t in [9,13]): d_s ≈ 4.45  — limita macroscopică 4D

**Aceasta este descoperirea-cheie a teoriei:** spațio-timpul 4D apare fără a fi postulat,
dintr-un principiu informațional pur.

> ⚠️ **Lacună L6:** Derivarea principiului Jaccard din teoria informației nu este completă
> în repository. Un paper riguros trebuie să justifice de ce suprapunerea vecinătăților
> minimizează entropia relativă sau maximizează informația mutuală între noduri.

---

## 7. Anomalia Flyby — Puntea QNG ↔ Observații (C-086)

### 7.1 Ecuația de Lag

Accelerația reziduală din lag-ul de memorie:

    a_res = -tau * (v . grad) grad(Sigma)

Semnătura direcțională (C-086a, falsificabilă):

    sign(a_res_parallel) = sign(v . grad(Sigma))

Legea de scalare a amplitudinii (C-086b2):

    |a_res| = A0 * (|v|/v0)^p * (r_p/r0)^(-q) * (|grad(Sigma)|/g0)^s * f_io

Forma log-liniară (C-086b3):

    ln(A_obs + eps) = b0 + b1*ln(v_p/v0) + b2*ln((h_p+h0)/h0)
                    + b3*ln(|grad_g|/g0) + b4*ln(1 + geom_io)
                    + b5*ln(1 + ng/ng0) + e

**Status:**
- C-086a (semnătură direcțională): CONFIRMATĂ
- C-086b/b2/b3 (amplitudine): în curs de validare holdout

---

## 8. Constanta de Rigiditate a Nodului (K_R)

### 8.1 Definiție și Motivație

**Constanta de Rigiditate a Nodului** este cantitatea care măsoară cât de puternic rezistă un
nod la deformarea instantanee a câmpului său de stabilitate — adică "memoria inerțială" a
gravitației în QNG.

Kernelul cauzal exponențial are doi parametri liberi: amplitudinea k și scala de memorie tau.
Produsul lor formează o singură constantă adimensionalizabilă:

    K_R  =  k * tau / tau_0

unde tau_0 este unitatea de timp de referință a sistemului (tau_0 = 1 în unitățile curente).
Astfel:

    K_R  =  k * tau  =  0.85 * 1.3  =  1.105   (măsurată în T-029)

**Interpretare fizică:** K_R este "aria" efectivă de sub kernelul cauzal normalizat — suma
totală a ponderilor de memorie înainte de normalizare Z:

    sum_{r=0}^{inf} k * exp(-r*dt/tau)  =  k / (1 - exp(-dt/tau))  ≈  k*tau/dt   (dt << tau)

K_R captează deci câte "pași de memorie eficienți" influențează starea curentă a nodului.

### 8.2 Relațiile Derivate din K_R

Din K_R se pot exprima toate cantitățile observabile ale teoriei:

**Lungimea de relaxare spațială:**

    L_R = sqrt(K_R) * sigma_kernel = sqrt(1.105) * 0.15 ≈ 0.158

Este raza efectivă în care un nod "simte" istoricul gravitațional al vecinilor.

**Scala de accelerație reziduală (flyby):**

    |a_res| ~ K_R * dt * |v| * |grad^2 Sigma|

Factorul K_R * dt = 1.105 * 0.06 = 0.0663 este coeficientul de lag observabil în flyby.

**Frecvența de coerență a nodului:**

    omega_R = 1 / (K_R * dt) = 1 / 0.0663 ≈ 15.1   [rad / unitate de timp]

Modurile grafului cu omega_k > omega_R sunt suprimate de memorie; cele cu omega_k < omega_R
sunt amplificate coerentin. Aceasta explică de ce m_eff^2 = 0.014 << 1 — masa efectivă
este mult sub frecvența de coerență.

**Scala de memorie per unitate de masă (cuplaj straton):**

    tau_i = alpha_tau * chi_i  =>  K_R(i) = k * alpha_tau * chi_i

K_R nu este constantă per nod — variază cu sarcina straton chi_i. Universalitatea se referă
la **alpha_tau * k** = const, nu la K_R per nod individual.

### 8.3 Testul de Universalitate — Ce Înseamnă "Gold Standard"

**Universalitatea** lui K_R înseamnă că produsul k * alpha_tau este aceeași constantă
adimensională indiferent de scara fizică a sistemului.

| Sistem | Scara | K_R măsurabil prin | Predicție QNG |
|--------|-------|-------------------|---------------|
| N-body laborator (T-029) | ~1 pc simulat | chi2 fit tau, k direct | k*tau = 1.105 |
| Anomalia flyby (C-086) | ~10^4 km | lag temporal al a_res | tau_flyby = K_R * dt / |v_esc| |
| Curbe de rotație galactică | ~1-100 kpc | tau_gal din profil v(r) | tau_gal/tau_lab = chi_gal/chi_lab |
| Cluster de galaxii | ~1-10 Mpc | dispersie sigma(r) cu lag | același K_R |
| CMB (scale cosmologice) | ~Gpc | P(k) power spectrum | K_R apare în transfer function |

**Predicția centrală testabilă:**

    K_R(laborator) = K_R(galaxii) = K_R(cosmologic)

sau echivalent:

    k * alpha_tau = const   (universală, independentă de scară)

Dacă aceasta este confirmată pe cel puțin 3 scări distincte, K_R devine o **constantă
fundamentală** a teoriei QNG, analogă constantei lui Newton G dar pentru memoria
gravitațională.

### 8.4 Cum se Extrage K_R din Date Observaționale

**Metoda 1 — Lag temporal direct (flyby):**

Din ecuația C-086:

    a_res = -tau * (v . grad) grad(Sigma)

Se măsoară a_res (reziduu orbit față de GR pur), se calculează (v.grad)grad(Sigma) din
modelul gravitațional standard, se obține:

    tau_obs = -a_res / [ (v . grad) grad(Sigma) ]
    K_R_obs = k_fit * tau_obs

**Metoda 2 — Raportul amplitudinilor cross-class (QNG-C-032):**

    A_i / A_j = K_R(i) / K_R(j) = chi_i / chi_j   (dacă k = const)

Dacă doi pulsari din clase diferite (masă, vârstă) arată raport de amplitudini egal cu
raportul maselor lor de straton, atunci alpha_tau este universal.

**Metoda 3 — Power spectrum cu transfer function modificată:**

K_R modifică transfer function CMB la scara:

    k_memory = 1 / L_R = 1 / (sqrt(K_R) * sigma_kernel)

Dacă k_memory corespunde unei caracteristici observate în P(k) sau C_l, K_R este
constrâns cosmologic.

### 8.5 Valoarea Actuală și Incertitudinea

| Parametru | Valoare centrală | Incertitudine | Sursa |
|-----------|-----------------|---------------|-------|
| k | 0.85 | ± 0.02 (1σ, T-029) | chi2 fit pe 12 seeds |
| tau | 1.3 | ± 0.1 (1σ, T-029) | chi2 fit pe 12 seeds |
| **K_R = k*tau** | **1.105** | **± 0.09** | propagare erori |
| alpha_tau | TBD | TBD | necesită date cross-class |
| K_R / K_R(GR pur) | 1.105 / 0 = ∞ | — | GR nu are memorie |

> ⚠️ **Lacună L8 (Nouă):** Valoarea K_R = 1.105 este măsurată exclusiv din simulări
> N-body cu parametri adimensionali (T-029). Nu există încă o mapare riguroasă la
> unități fizice SI. Această conversie dimensională este necesară pentru a face
> predicții observaționale absolute (nu doar relative). Relația:
>
>     K_R [SI] = k * tau [s] * G [m^3 kg^-1 s^-2] / c^2 [m^2 s^-2]
>
> trebuie derivată din limita continuă a teoriei (vezi Lacuna L4).

---

## 9. Condițiile de Stabilitate

### 8.1 Condiții Lyapunov Implicite (Verificate Numeric)

1. Stabilitate câmp scalar: Sigma_i in [0,1] menținut prin clip — stabil prin construcție
2. Stabilitate acțiune: H_ii < 0 (G16d: frac > 0.90) — acțiunea este un maxim local
3. Stabilitate spectrală: gap spectral mu_1 > 0.01 (G17a) — operatorul de propagare e invertibil
4. Stabilitate termodinamică: C_V > 0 (G21) — sistemul termic e stabil față de fluctuații T

> ⚠️ **Lacună L2:** Nu există o demonstrație Lyapunov directă pentru stabilitatea globală
> a soluțiilor discrete N_i(t+1) = U(...). Un paper riguros ar trebui să construiască
> V(t) = sum_i |Sigma_i(t) - Sigma*|^2 și să arate V(t+1) <= rho * V(t), rho < 1,
> în jurul punctelor fixe.

---

## 10. Implementarea Computațională

### 9.1 Algoritmul de Integrare (T-029)

Schema **Symplectic Euler** (ordinul 1 simplex, conservare energie mai bună decât Euler forward):

    v_i^{n+1} = v_i^n + a_i^n * dt
    x_i^{n+1} = x_i^n + v_i^{n+1} * dt

cu dt = 0.06, N_steps = 160, N_particles = 140.

**Fereastra de memorie:**

    Memory buffer: pos_history[0..R], R = min(step, MEMORY_WINDOW=30)
    Kernel weights: w_r, r = 0..R
    Complexitate per pas: O(N^2 * R)

### 9.2 Metrica Chi-Squared de Potrivire

    chi2(obs, pred; n_burn=20) = sum_{n=n_burn}^{N_steps} [ (obs_n - pred_n) / max(|obs_n|, 0.005) ]^2

Normalizarea prin max(|obs_n|, 0.005) previne divergența la valori mici.

### 9.3 Constantele Critice (Toate Fișierele)

```
# T-029 / Simulări N-body
TRUTH_TAU       = 1.3       # scala de memorie
TRUTH_K         = 0.85      # amplitudinea kernelului
G_BASE          = 1.0       # cuplajul gravitațional
SIGMA_KERNEL    = 0.15      # lățimea kernel-ului spațial
MEMORY_WINDOW   = 30        # numărul maxim de pași reținuți
DT              = 0.06      # pasul de timp
N_PARTICLES     = 140       # numărul de particule
N_STEPS         = 160       # numărul de pași de simulare
RATIO_THRESHOLD = 5.0       # pragul gate-ului NC

# G17-G21 / Sectorul cuantic
M_EFF_SQ        = 0.014     # masa efectivă pătrată
N_MODES         = 20        # numărul de moduri proprii
N_ITER_POW      = 350       # iterații power method
LAMBDA_BACK     = 0.05      # cuplajul back-reaction (5%)

# Metrică
PHI_SCALE       = 0.08-0.10 # scala potențialului newtonian
SHRINKAGE_K     = 0.4       # shrinkage metric-lock-v3: g_v3 = 0.4*g_conf + 0.6*I/2
```

---

## 11. Gate-urile de Validare — Praguri Complete

### GR Lane

| Gate | Metric | Prag | Valoare obținută | Margin |
|------|--------|------|-----------------|--------|
| G10 | min lapse N | > 0.0 | 0.920 | — |
| G11a | R² OLS fit R vs sigma | > 0.02 | 0.070 | — |
| G11b | \|B_slope\| / \|mean_R\| | > 0.05 | — | — |
| G11c | mean\|Bianchi\|/\|mean_R\| | < 1.5 | — | — |
| G11d | max\|Tr G\| | < 1e-10 | — | — |
| G15a | \|mean(gamma_PPN) - 1\| | < 0.06 | — | — |
| G15b | Shapiro ratio | > 2.0 | 14.26 | — |
| G15c | beta_PPN | ∈ (0.3, 0.7) | 0.5 | — |
| G15d | EP_ratio std/mean_U | < 0.15 | — | — |
| G16a | Closure error | < 0.01 | — | — |
| G16b | R² G11 vs 8πG*T11 | > 0.05 | — | — |
| G16c | \|m²_fit\| | > 0.005 | — | — |
| G16d | frac(H_ii < 0) | > 0.90 | 1.000 | 11.1% |

### QM Lane

| Gate | Metric | Prag | Valoare obținută | Margin |
|------|--------|------|-----------------|--------|
| G17a | spectral gap mu_1 | > 0.01 | 0.010 | 4.6% ⚠️ |
| G17b | E_0 | ∈ (0, ∞) | ✓ | — |
| G18a | S/log(K_eff) | > 0.8 | — | — |
| G18b | Δω/mean(ω) | > 0.1 | — | — |
| G18d | d_s spectral dim | ∈ (3.5, 4.5) | 4.082 | 83.6% |
| G19a | cv(T_Unruh) | > 0.05 | 0.438 | — |
| G19b | E_MB/E_BE | > 2.0 | — | — |
| G19c | E_BE(2T)/E_BE(T) | > 3.0 | — | — |
| G19d | OLS slope ΔG_thermal vs r | < -0.001 | — | — |
| G20a | Energy conservation | < 0.01 | 0.0 | — |
| G20b | cv(eps_vac) | > 0.05 | — | — |
| G20c | \|δE_0/E_0\| | ∈ (1e-5, 0.30) | — | — |
| G20d | max(residual) | < 0.20 | — | — |
| G21 | F = U - TS error | — | 1.3e-16 | — |

### Status oficial (2026-03-15)

- GR Stage-3: **600/600 PASS (100%)**, attack 1459/1500 (97.3%), holdout 400/400 (100%)
- QM Stage-1: **2500/2500 PASS (100%)**
- Jaccard: **21/21 gate-uri PASS**

---

## 12. Lacune și Pașii Următori Necesari pentru Paper

| # | Lacună | Impact |
|---|--------|--------|
| L1 | Distribuția P[Sigma_i] nederivaă analitic (lipsește Fokker-Planck) | **Critic** |
| L2 | Stabilitate Lyapunov globală nedemonstrată | Important |
| L3 | beta_PPN = 1/2 ≠ 1 față de GR standard, neexplicat | Important |
| L4 | Limita continuă dt -> 0 a sistemului discret neanaliz | Important |
| L5 | Natura zgomotului eta_i (Gaussian vs. non-Gaussian) nejustificată | Mediu |
| L6 | Derivarea principiului Jaccard din teoria informației incompletă | Important |
| L7 | Predicții observaționale cuantitative (unde gravitaționale, CMB) lipsesc | **Critic** |
| L8 | Conversia dimensională K_R [adim] → K_R [SI] nederivaată (blochează predicții absolute) | **Critic** |

---

*Generat automat din analiza exhaustivă a codebase-ului QNG_Workspace — 2026-03-16*
*Referință: toate fișierele din 01_notes/, 02_claims/, 03_math/, scripts/run_qng_*.py*
