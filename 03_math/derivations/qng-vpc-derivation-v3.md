# VPC din Rata de Schimbare a Câmpului — Derivare v3

**Status:** Derivare completă — înlocuiește postulatul din straton-v2 §9.4.2
**Data:** 2026-03-16
**Dependențe:** qng-straton-interpretation-v2, qng-vpc-derivation-v1, qng-vpc-addendum-v1
**Metodă:** Calea (a)+(c) din straton-v2 §9.4.2 — postulat de update + câmp Σ

---

## 1. Problema

Straton-v2 impune VPC ca postulat:

> *Termenul de lag cuplează doar componenta vitezei de-a lungul gradientului câmpului.*

Derivările anterioare:
- v1: valid sub simetrie sferică (coordonate sferice) — limitat
- v2: anulare prin coarse-graining la scară galactică — nu acoperă Mercury
- addendum: VPC exact în coordonate sferice, dar coordinate-dependent

Această derivare elimină dependența de coordonate și de simetria sferică, printr-un
postulat mai fundamental: **rata de update a rețelei**.

---

## 2. Postulatul de Update (P-UPD)

**Postulat (P-UPD).** *Rețeaua QNG se actualizează (produce lag) cu o rată
proporțională cu rata de schimbare a câmpului de stabilitate Σ de-a lungul traiectoriei:*

$$\nu_{\text{update}} \;=\; \frac{|d\Sigma/dt|_{\text{traiectorie}}}{\delta\Sigma_{\text{nod}}}
\;=\; \frac{|\mathbf{v} \cdot \nabla\Sigma|}{\delta\Sigma_{\text{nod}}} \tag{P-UPD}$$

unde $\delta\Sigma_{\text{nod}}$ este diferența de câmp între noduri adiacente
(constantă la rezoluție dată a rețelei).

**Motivație fizică:**

Un obiect care se mișcă pe o suprafață echi-potențială ($\Sigma = \text{const}$)
nu traversează noduri cu valori de câmp diferite. Rețeaua din jurul lui se află
deja în configurația de echilibru pentru acea valoare de Σ. Nu apare niciun lag.

Un obiect care traversează suprafețe de Σ diferite descoperă configurații noi
ale rețelei. Rețeaua trebuie să se relaxeze la fiecare trecere. Rata de trecere
este exact $\nu_{\text{update}}$ din (P-UPD).

**Notă:** (P-UPD) este mai fundamental decât VPC. VPC urmează ca teoremă.

---

## 3. Derivarea VPC din (P-UPD)

### 3.1 Forma generală a lag-ului

Ecuația de mișcare QNG cu termenul de lag complet (formă naivă, fără VPC):

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \; v^j \; \partial_j\partial^i \Sigma \tag{1}$$

Aceasta se poate scrie ca:

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \; H^i_{\ j} \; v^j \tag{2}$$

unde $H^i_{\ j} = \partial^i\partial_j\Sigma$ este Hessianul câmpului.

### 3.2 Proiecția pe gradientul câmpului

Descompunem viteza în componentele paralele și perpendiculare la $\nabla\Sigma$:

$$\mathbf{v} = v_\parallel \,\hat{\nabla}\Sigma \;+\; \mathbf{v}_\perp$$

unde:

$$v_\parallel \;\equiv\; \mathbf{v} \cdot \hat{\nabla}\Sigma \;=\; \frac{\mathbf{v} \cdot \nabla\Sigma}{|\nabla\Sigma|}
\qquad\quad
\mathbf{v}_\perp \;\equiv\; \mathbf{v} - v_\parallel\,\hat{\nabla}\Sigma \tag{3}$$

### 3.3 Contribuția componentei perpendiculare

Prin definiție, $\mathbf{v}_\perp \cdot \nabla\Sigma = 0$, deci:

$$\frac{d\Sigma}{dt}\bigg|_{\mathbf{v}_\perp} = \mathbf{v}_\perp \cdot \nabla\Sigma = 0 \tag{4}$$

Din (P-UPD): $\nu_{\text{update}}|_{\mathbf{v}_\perp} = 0$.

Rețeaua nu se actualizează pentru mișcarea perpendiculară pe gradient.
Deci componenta perpendiculară a vitezei **nu produce lag**:

$$a^i_{\text{lag}}\big|_{\mathbf{v}_\perp} = 0 \tag{5}$$

### 3.4 Contribuția componentei paralele

$$\frac{d\Sigma}{dt}\bigg|_{v_\parallel} = v_\parallel \; |\nabla\Sigma| \neq 0 \tag{6}$$

Aceasta produce update-uri cu rata $\nu \propto |v_\parallel|$.

Forța de lag de la componenta paralelă:

$$a^i_{\text{lag}}\big|_{v_\parallel} = -\tau_{\text{phys}} \; H^i_{\ j} \; (v_\parallel \,\hat{\nabla}\Sigma^j)
\;=\; -\tau_{\text{phys}} \; v_\parallel \; H^i_{\ j} \; \hat{\nabla}\Sigma^j \tag{7}$$

### 3.5 Forma VPC finală

Combinând (5) și (7):

$$\boxed{a^i_{\text{lag}} = -\tau_{\text{phys}} \;(\mathbf{v} \cdot \hat{\nabla}\Sigma)\; H^i_{\ j} \;\hat{\nabla}\Sigma^j} \tag{VPC}$$

Aceasta este exact forma postulată în straton-v2 (Eq. 2), acum **derivată** din (P-UPD).

---

## 4. Verificare: recuperarea rezultatelor anterioare

### 4.1 Orbite circulare

Pe orbită circulară în câmp central: $\mathbf{v} \perp \hat{r} = \hat{\nabla}\Sigma$.

$$\mathbf{v} \cdot \hat{\nabla}\Sigma = 0 \;\Rightarrow\; a^i_{\text{lag}} = 0 \quad \text{(exact)} \tag{8}$$

Nicio pierdere seculară de energie. Planetele sunt în siguranță prin construcție.

### 4.2 Zbor radial (Pioneer)

$\mathbf{v} = v_r \hat{r}$, $\hat{\nabla}\Sigma = \hat{r}$ pentru câmp central.

$$\mathbf{v} \cdot \hat{\nabla}\Sigma = v_r \;\Rightarrow\;
a^r_{\text{lag}} = -\tau_{\text{phys}} \; v_r \; H^r_{\ j} \; \hat{r}^j = -\tau_{\text{phys}} \; v_r \; \frac{d^2\Sigma}{dr^2} \tag{9}$$

Pentru $\Sigma = -GM/r$: $d^2\Sigma/dr^2 = -2GM/r^3$.

$$a^r_{\text{lag}} = \frac{2\tau_{\text{phys}} \; v_r \; GM}{r^3} \tag{10}$$

Identic cu Eq. (2) din straton-v2. ✓

### 4.3 Recuperarea rezultatului addendum-v1

Addendum-v1 a arătat că în coordonate sferice, $H_{\theta\theta}^{\text{sph}} = 0$
exact pentru $\Sigma = \Sigma(r)$.

Din (VPC): pentru $\mathbf{v} = v_\theta \hat{\theta}$:

$$\mathbf{v} \cdot \hat{\nabla}\Sigma = v_\theta \underbrace{(\hat{\theta} \cdot \hat{r})}_{=\,0} = 0
\;\Rightarrow\; a^i_{\text{lag}} = 0 \tag{11}$$

Același rezultat, acum din principiu, nu din alegerea de coordonate. ✓

---

## 5. Generalizare la câmpuri non-sferice

Forma (VPC) este coordinate-invariantă și se aplică oricărui câmp $\Sigma(\mathbf{x})$.

**Câmp general (sisteme binare, clustere):**

$$a^i_{\text{lag}} = -\tau_{\text{phys}} \;(\mathbf{v} \cdot \hat{\nabla}\Sigma)\;
\frac{\nabla^j\Sigma}{|\nabla\Sigma|} \; \partial_j\partial^i\Sigma \tag{12}$$

**Condiție de aplicabilitate:** (P-UPD) se aplică când câmpul $\Sigma$ variază
suficient de lent la scara unui nod ($l_0$) încât Hessianul local este bine definit.
Corecțiile sunt de ordin $O(l_0 |\nabla^3\Sigma| / |\nabla^2\Sigma|)$.

**Domenii unde corecțiile pot fi semnificative:**
- Vecinătatea punctului de șa între două mase ($\nabla\Sigma \to 0$)
- Regiuni de schimbare rapidă a direcției $\hat{\nabla}\Sigma$

---

## 6. Statutul derivării

| Aspect | Straton-v2 | VPC-v1 | VPC-v2 | **VPC-v3 (acesta)** |
|--------|-----------|--------|--------|---------------------|
| Baza | Postulat | Simetrie sferică | Coarse-graining | **(P-UPD) + descompunere** |
| Coordonate | — | Sferice | Orice | **Invariant** |
| Orbite circulare | Impus | Derivat (A1–A3) | Parțial | **Derivat exact** |
| Câmp central solar | Impus | Derivat | Derivat | **Derivat** |
| Câmp general | Postulat | Nu | Nu | **Derivat** |
| Scală galactică | Impus | Nu | Derivat | **Derivat** |
| Status | Postulat | Semi-derivat | Semi-derivat | **Derivat (sub P-UPD)** |

---

## 7. Ce rămâne deschis

**(P-UPD) este acum postulatul de bază, nu VPC.**

(P-UPD) spune că rețeaua răspunde la schimbările câmpului de-a lungul traiectoriei,
nu la deplasarea brută. Aceasta este o afirmație despre **mecanismul fizic al lag-ului**
la nivel de graf discret.

**Derivarea (P-UPD) din acțiunea QNG** (calea (c) completă) rămâne deschisă.
Direcția: termenul de lag în acțiune ar trebui să ia forma:

$$S_{\text{lag}} = -\int \frac{\tau_{\text{phys}}}{2} \left(\frac{d\Sigma}{d\tau}\right)^2
\frac{1}{|\nabla\Sigma|^2} \, d\tau \tag{13}$$

Variind față de $x^i(\tau)$ ar produce (VPC) direct. Această verificare este
pasul următor necesar.

**Falsificator observațional (neschimbat față de straton-v2):**

Orice orbită circulară (Mercury–Saturn) cu drift secular $> 10^{-12}$ m/s²
infirmă (P-UPD) și implicit VPC-v3.

---

## 8. Concluzie

VPC a fost promovat de la **postulat** la **teoremă sub (P-UPD)**.

(P-UPD) este mai fundamental decât VPC: spune că rețeaua discretă nu poate
"simți" o mișcare care nu traversează suprafețe de câmp diferite. Aceasta este
o proprietate naturală a oricărei rețele cu câmp scalar: informația despre
configurația câmpului este encodată în valoarea lui Σ, nu în poziția angulară.

Forma finală a accelerației QNG complete:

$$\boxed{a^i = -g^{ij}\partial_j\Sigma
\;-\; \tau_{\text{phys}}(r) \;(\mathbf{v} \cdot \hat{\nabla}\Sigma)\;
H^i_{\ j} \;\hat{\nabla}\Sigma^j}$$

cu $\tau_{\text{phys}}(r) = \tau_{\text{graph}} \cdot l_{0,\text{1AU}} (r/\text{1AU})^3 / c$
și $C = 6.99 \times 10^{-14}$ s⁻¹ calibrat din Pioneer 10.
