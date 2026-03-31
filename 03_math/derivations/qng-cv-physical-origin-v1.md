# Originea fizică a lui cv_fizic = 0.405 — v1

**Status:** Derivare parțială — consistență demonstrată, origine identificată
**Data:** 2026-03-17
**Dependențe:** qng-vpc-factor4-derivation-v1.md, run_qng_semiclassical_v1.py
**Concluzie:** cv este o constantă fundamentală QNG, CONSISTENTĂ cu modelul la 1.2σ

---

## 1. Întrebarea

Din derivarea anterioară: $\tau_{\text{graph}} = \frac{\lambda}{4} \text{cv}^2$

Inversând: $\text{cv}_{\text{fizic}} = \sqrt{\frac{4\,\tau_{\text{graph}}}{\lambda}} = \sqrt{\frac{4 \times 0.002051}{0.05}} = 0.4051$

**Întrebarea:** De ce are vacuumul fizic solar exact $\text{cv} = 0.405$?

---

## 2. Ce este cv fizic

$\text{cv}(\varepsilon_{\text{vac}}) = \frac{\sigma(\varepsilon_{\text{vac}})}{\mu(\varepsilon_{\text{vac}})}$
unde $\varepsilon_{\text{vac}}(i) = \frac{1}{2}\sum_k \omega_k |\psi_k(i)|^2$ (energia zero-point per nod).

**Interpretare fizică:** cv măsoară **dezordinea spațială a vacuumului cuantic la scara Planck**.
- cv = 0: vacuum perfect uniform (rețea cristalină perfectă) → fără lag, fără Pioneer
- cv = 1: fluctuații comparabile cu media (dezordine maximă)
- cv = 0.405: nivel moderat de dezordine cuantică

Această dezordine vine din **topologia aleatorie a grafului QNG la scara Planck**,
nu din geometria macroscopică a sistemului solar. Dacă spațiul cuantic e un graf
aleatoriu cu $k$ vecini, cv este o caracteristică statistică a acestui ansamblu.

---

## 3. Formula teoretică pentru cv

Din statistica eigenfuncțiilor pe un graf aleatoriu 2D cu $k$ vecini:

$$\text{cv}^2 = \frac{C(k,d)}{K_{\text{eff}}} \cdot (1 + \text{cv}_\omega^2)
\tag{cv-formula}$$

unde:
- $K_{\text{eff}}$ = numărul de moduri cuantice active per celulă Planck
- $\text{cv}_\omega = \sigma(\omega)/\mu(\omega)$ = dispersia relativă a frecvențelor modurilor
- $C(k,d)$ = constantă geometrică a grafului ($C = 2$ pentru Porter-Thomas pur,
  cu corecție numerică $\approx 2.31$ pentru $k=8$, $d=2$)

### Derivarea Eq. (cv-formula)

**Pasul 1: distribuția Porter-Thomas** (statistica valori proprii pe graful aleatoriu)

Eigenfuncțiile pe un graf aleatoriu 2D satisfac statistica Porter-Thomas:
$$\text{var}(|\psi_k(i)|^2) = \frac{2}{N^2}$$

**Pasul 2: varianța energiei locale**

$$\text{var}(\varepsilon_{\text{vac}}(i)) = \sum_k \left(\frac{\omega_k}{2}\right)^2 \text{var}(|\psi_k(i)|^2)
\approx \frac{1}{2N^2} \sum_k \omega_k^2 = \frac{K_{\text{eff}}}{2N^2}\langle\omega^2\rangle$$

**Pasul 3: media energiei locale**

$$\mu(\varepsilon_{\text{vac}}) = \frac{E_0}{N} = \frac{K_{\text{eff}}\langle\omega\rangle}{2N}$$

**Pasul 4: cv²**

$$\text{cv}^2 = \frac{\text{var}}{\mu^2}
= \frac{K_{\text{eff}}\langle\omega^2\rangle/(2N^2)}{K_{\text{eff}}^2\langle\omega\rangle^2/(4N^2)}
= \frac{2\langle\omega^2\rangle}{K_{\text{eff}}\langle\omega\rangle^2}
= \frac{2(1+\text{cv}_\omega^2)}{K_{\text{eff}}}$$

Corecția numerică $C = 2.31$ față de $C_{\text{PT}} = 2$ vine din
**non-Porter-Thomas pe graful 2D** — eigenfuncțiile au cozi mai grele
(comportament multifractal slab).

---

## 4. Predicția ansamblului vs Pioneer

### Parametrii canonici (N=280, k=8, K_eff=19, m_eff²=0.014)

Din 20 de realizări aleatorii:

| Cantitate | Valoare |
|-----------|---------|
| Media cv | $0.3673 \pm 0.0312$ |
| Intervalul 2σ | $[0.305, 0.430]$ |
| cv_ω (dispersia frecvențelor) | $0.331$ |
| cv_teor (Porter-Thomas) | $0.342$ |
| Factor de corecție non-PT | $1.075$ |

### Comparație cu Pioneer

$$\text{cv}_{\text{fizic}} = 0.4051 \quad \Rightarrow \quad z\text{-score} = \frac{0.4051 - 0.3673}{0.0312} = 1.21\sigma$$

**cv_fizic este consistent cu predicția ansamblului la $1.2\sigma$** (fără ajustare).

---

## 5. Ce determină exact valoarea 0.405

### 5.1 Nu este determinat de geometria sistemului solar

Câmpul gravitațional al Soarelui produce o variație relativă a vacuumului:
$$\frac{\delta\varepsilon_{\text{vac}}}{\varepsilon_{\text{vac}}} \sim \frac{\Phi}{c^2}
= \frac{GM_\odot}{rc^2}$$

La 20 AU: $\delta\varepsilon/\varepsilon \sim 5 \times 10^{-10}$.
La 70 AU: $\delta\varepsilon/\varepsilon \sim 1.4 \times 10^{-10}$.

Acestea sunt cu 9 ordine de mărime mai mici decât $\text{cv} = 0.405$.
**Gravitația solară nu poate explica cv_fizic.** cv vine de la scara Planck.

### 5.2 cv este determinat de K_eff_fizic

Din Eq. (cv-formula), inversând:

$$K_{\text{eff,fizic}} = \frac{C(k,d)\,(1+\text{cv}_\omega^2)}{\text{cv}_{\text{fizic}}^2}
= \frac{2.31 \times 1.110}{0.405^2} \approx 15.6$$

**Predicție: vacuumul fizic solar are $K_{\text{eff}} \approx 16$ moduri cuantice
efective per celulă Planck.**

Această predicție poate fi verificată dacă:
1. Avem o teorie a topologiei grafului QNG la scara Planck
2. Numărăm câte grade de libertate cuantice participă la back-reaction la scara Pioneer

### 5.3 Constantă matematică apropiată

$$\frac{1}{\sqrt{6}} = 0.4082 \approx \text{cv}_{\text{fizic}} = 0.4051 \quad (\text{diferență } 0.8\%)$$

Dacă aceasta nu e coincidență: cv = $1/\sqrt{6}$ implică $K_{\text{eff}} = 6$ pentru
formula Porter-Thomas pură ($C=2$, $\text{cv}_\omega \to 0$):
$$\text{cv} = \sqrt{2/6} = \sqrt{1/3} \neq 1/\sqrt{6}$$

Dar cu corecția non-PT ($C = 2.31$) și dispersia frecvențelor ($\text{cv}_\omega = 0.33$):
$$K_{\text{eff}} = C(1+\text{cv}_\omega^2)/\text{cv}^2 = 2.31 \times 1.11/0.166 = 15.4$$

**Conjectură:** $K_{\text{eff,fizic}} = 16 = 2^4$ (patru dimensiuni spațio-temporale × 4 grade
de libertate per mod?) — dar aceasta necesită verificare din teoria QNG completă.

---

## 6. Statutul epistemologic al lui cv_fizic

| Constantă | Analogie | Teoretic? | Metoda |
|-----------|----------|-----------|--------|
| $\alpha = 1/137$ | Fine structure const | Nu (din QED+renorm.) | Măsurat |
| $\text{cv}_{\text{fizic}} = 0.405$ | Dezordine Planck | Nu (din QG) | Măsurat (Pioneer) |

**cv_fizic este o constantă fundamentală a teoriei QNG**, analogă constantei de structură
fină. Valoarea ei:
- Nu poate fi derivată din QNG fără o teorie completă a gravitației cuantice
- Este CONSISTENTĂ cu predicția ansamblului QNG la $1.2\sigma$
- Poate fi predicută dacă cunoaștem topologia grafului Planck ($k$, $d$, $K_{\text{eff}}$)

---

## 7. Predicții testabile

Dacă cv este universal (aceeași peste tot în univers):

1. **Anomalia Pioneer la alte nave**: aceeași $a_P = \text{const}$ pentru orice navă
   neecranată în spațiul interplanetar (nu doar Pioneer 10/11)

2. **Independența de sistemul stelar**: anomalia similară în jurul altor stele
   (dacă cv este Planck-scale, nu depinde de $M_*$, $r$, etc.)

3. **Relația cu λ**: dacă $\lambda$ se schimbă (alt cuplaj back-reaction),
   $a_P \propto \lambda \cdot \text{cv}^2$ — testabil prin variații temporale

4. **K_eff = 16**: dacă teoria QNG prezice exact 16 moduri per celulă Planck,
   aceasta este o predicție verificabilă (dar necesită quantum gravity complet)

---

## 8. Concluzie și pașii următori

**Starea actuală:** Lanțul cauzal este:
```
Topologia grafului Planck (NECUNOSCUTA)
  ↓ determina
K_eff, k, d, m_eff, cv_omega
  ↓ prin Eq. (cv-formula)
cv = 0.405                    ← CONSISTENT cu ansamblu la 1.2σ
  ↓ prin teorema virialului
τ_graph = λ/4 · cv²
  ↓
VPC → anomalia Pioneer
```

**Ce lipsește:** O teorie a topologiei grafului QNG la scara Planck care să prezică
$K_{\text{eff}} = 16$, $k \approx 8$, $d = 3$.

**Concluzie:** cv_fizic = 0.405 nu poate fi derivat exact din principii mai simple în
cadrul actual. Este o constantă fundamentală, CONSISTENTĂ cu modelul QNG, cu semnificație
fizică clară (dezordine cuantică Planck), și cu o predicție numerică ($K_{\text{eff}} \approx 16$)
care poate fi verificată independent.
