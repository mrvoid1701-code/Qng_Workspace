# VPC: Structura Disipativă și Justificarea (P-UPD) — Derivare v4

**Status:** Corectare critică a v3 + derivare (P-UPD) din teoria informației
**Data:** 2026-03-17
**Dependențe:** qng-vpc-derivation-v3.md (Eq. 13 — incorectă, corectată aici)

---

## 1. Corecție: Acțiunea din v3 Eq. (13) nu dă VPC

v3 a propus (Eq. 13) că VPC ar putea fi derivat din:

$$S_{\text{lag}} = -\int \frac{\tau_{\text{phys}}}{2} \frac{(d\Sigma/d\tau)^2}{|\nabla\Sigma|^2} \, d\tau
= -\frac{\tau}{2}\int (v \cdot \hat{n})^2 \, d\tau \tag{1}$$

unde $\hat{n} = \hat{\nabla}\Sigma(x)$ depinde de poziție, nu de viteză.

### 1.1 Ecuația Euler-Lagrange din (1)

Fie $\mathcal{L}_{\text{lag}} = -\frac{\tau}{2}(v\cdot\hat{n})^2$. Calculăm:

$$\frac{\partial\mathcal{L}}{\partial v^i} = -\tau(v\cdot\hat{n})\hat{n}_i \tag{2}$$

$$\frac{d}{d\tau}\frac{\partial\mathcal{L}}{\partial v^i}
= -\tau(\dot{v}\cdot\hat{n})\hat{n}_i
- \tau(v^j v^k\partial_k\hat{n}_j)\hat{n}_i
- \tau(v\cdot\hat{n})\,v^k\partial_k\hat{n}_i \tag{3}$$

$$\frac{\partial\mathcal{L}}{\partial x^i} = -\tau(v\cdot\hat{n})\,v^j\partial_i\hat{n}_j \tag{4}$$

Ecuația EL $= (3) - (4) = 0$ conține termeni de forma
$(v\cdot\hat{n})v^j(\partial_i\hat{n}_j - \partial_j\hat{n}_i)$.

Folosind $\hat{n}_j = \partial_j\Sigma/N$ cu $N = |\nabla\Sigma|$:

$$\partial_i\hat{n}_j - \partial_j\hat{n}_i
= \hat{n}_i\,\partial_j\log N - \hat{n}_j\,\partial_i\log N \tag{5}$$

Rezultatul final EL nu se simplifică la forma VPC. El conține $\partial_i\log N$
și termeni pătratici în viteză care **nu apar în VPC**.

**Concluzie: Eq. (13) din v3 este greșită ca derivare a VPC.**

Acțiunea (1) descrie o *modificare relativistă-tip a energiei cinetice*
(restricționând contribuția energetică la componenta paralelă), nu o forță de lag.

---

## 2. De ce VPC nu provine dintr-o funcție Rayleigh standard

O forță disipativă derivabilă dintr-o funcție Rayleigh $\mathcal{R}(v)$:

$$F_i = -\frac{\partial\mathcal{R}}{\partial v^i}$$

implică un tensor de disipație **simetric** $\gamma_{ij}$:

$$\mathcal{R} = \frac{1}{2}\gamma_{ij}v^i v^j \;\Rightarrow\; F_i = -\gamma_{ij}v^j,
\quad \gamma_{ij} = \gamma_{ji} \tag{6}$$

**Tensorul VPC:**

$$F_i^{\text{VPC}} = -\tau(v\cdot\hat{n})\underbrace{H_{ij}\hat{n}^j}_{\equiv w_i}
= -\tau\,w_i\,(\hat{n}_j\,v^j)
\;\Rightarrow\; \gamma_{ij}^{\text{VPC}} = \tau\,w_i\,\hat{n}_j \tag{7}$$

Verificăm simetria:

$$\gamma_{ij}^{\text{VPC}} = \tau\,H_{ik}\hat{n}^k\,\hat{n}_j$$
$$\gamma_{ji}^{\text{VPC}} = \tau\,H_{jk}\hat{n}^k\,\hat{n}_i$$

Acestea sunt egale **doar** dacă $H_{ij} \propto \delta_{ij}$ (câmp izotrop), caz
particular care nu se aplică câmpului Kepler.

**Concluzie: VPC este o forță de frecare ne-reciprocă. Nu provine dintr-o
funcție Rayleigh, deci nu dintr-un principiu variațional standard.**

---

## 3. Ce este frecarea ne-reciprocă în context fizic

Forțele disipative ne-reciproce apar natural în:
- Sisteme active (particule cu propulsie internă)
- Fluide cu vâscozitate "odd" (sisteme chirале)
- Sisteme cuantice deschise (kernel Lindblad non-simetric)

**În QNG:** lag-ul nu este o frecare Stokes (care ar fi $F_i = -\gamma v_i$,
reciprocă). Este o frecare *direcțională*:

- **Direcția forței:** $w = H\hat{n}$ — cum se modifică gradientul câmpului local
- **Sensibilitatea la mișcare:** $v\cdot\hat{n}$ — viteza de penetrare în câmp

Aceste două direcții sunt, în general, **diferite** ($H\hat{n} \neq \lambda\hat{n}$
dacă $\hat{n}$ nu e vector propriu al Hessianului).

Aceasta este o proprietate distinctivă a QNG față de orice teorie cu frecare
Stokes sau fricțiune scalară. Poate fi testată: frecarea Stokes ar fi izotropă
în v, VPC este anizotropă.

---

## 4. Derivarea (P-UPD) din teoria informației grafului

(P-UPD) spune că rata de update a rețelei QNG este:

$$\nu_{\text{update}} = \frac{|d\Sigma/dt|}{\delta\Sigma_{\text{nod}}} \tag{P-UPD}$$

### 4.1 Codificarea informației în graful QNG

Un nod al grafului QNG la poziția $\mathbf{x}$ stochează configurația metrică
locală, determinată de valoarea câmpului $\Sigma(\mathbf{x})$. Două noduri cu
aceeași valoare $\Sigma$ au aceeași configurație metrică — sunt *echivalente
informațional*.

**Definiție (stare distinctă a nodului):** Nodul $\mathbf{x}$ are o stare
distinctă față de nodul $\mathbf{y}$ dacă și numai dacă $\Sigma(\mathbf{x}) \neq \Sigma(\mathbf{y})$.

**Corolarul nodurilor echivalente:** Un obiect care se mișcă pe o suprafață
$\Sigma = \text{const}$ traversează exclusiv noduri echivalente. Rețeaua nu
primește informație nouă. Nicio actualizare nu este necesară.

### 4.2 Rata de noduri distincte traversate

La rezoluție $\delta\Sigma_{\text{nod}}$ (diferența minimă de câmp rezolvabilă),
numărul de stări distincte traversate pe unitate de timp este:

$$\nu_{\text{update}} = \frac{|d\Sigma/dt|_{\text{traiectorie}}}{\delta\Sigma_{\text{nod}}}
= \frac{|\mathbf{v}\cdot\nabla\Sigma|}{\delta\Sigma_{\text{nod}}} \tag{8}$$

Aceasta este (P-UPD). Derivarea folosește o singură ipoteză:

> **(H1): Configurația metrică a unui nod QNG este determinată complet de $\Sigma(\mathbf{x})$.*

(H1) urmează direct din construcția QNG: nodul este definit ca o celulă de
coarse-graining a câmpului scalar $\Sigma$, nu a coordonatelor spațiale.

### 4.3 Entropia produsă de update

Fiecare update consumă energie de relaxare proporțională cu mismatch-ul metric
local. Rata de producție de entropie de-a lungul traiectoriei:

$$\dot{S}_{\text{graph}} = k_B \,\nu_{\text{update}} \cdot s_{\text{nod}}
\propto |\mathbf{v}\cdot\nabla\Sigma| \tag{9}$$

Forța de lag este gradientul acestei producții de entropie față de deplasare
(termodinamica ne-echilibrului liniar):

$$F_i^{\text{lag}} = -T\,\frac{\partial \dot{S}}{\partial \dot{x}^i}\bigg|_{\text{forță}}
\propto -\frac{\partial}{\partial \dot{x}^i}|\dot{x}^j\partial_j\Sigma| \cdot (\text{direcție lag}) \tag{10}$$

Termenul de direcție vine din cum se propagă mismatch-ul metric: de-a lungul
$\nabla\Sigma$ (câmpul e radial), modificând gradientul — deci $H_{ij}\hat{n}^j$.

**Rezultat:** (P-UPD) este o consecință a **ipotezei de completitudine (H1)**,
care este o ipoteză despre natura grafului QNG, nu o ipoteză separată despre VPC.

---

## 5. Formularea corectă a VPC

VPC este o **relație constitutivă** a grafului QNG (nu variațională):

$$\boxed{a^i_{\text{lag}} = -\tau_{\text{phys}}\,(\mathbf{v}\cdot\hat{\nabla}\Sigma)\,
H^i_{\ j}\,\hat{\nabla}\Sigma^j} \tag{VPC}$$

derivată din:
1. **(H1)** — completitudinea câmpului scalar: starea nodului ↔ $\Sigma(\mathbf{x})$
2. **(P-UPD)** — rata de update ∝ $|d\Sigma/dt|$ **(teoremă din H1)**
3. **Direcția lag** = $H\hat{n}$ — propagarea mismatch-ului metric **(constitutivă)**

Punctul (3) rămâne o ipoteză constitutivă. Ea spune că forța de lag acționează
în direcția în care se modifică gradientul câmpului, nu în direcția câmpului însuși.

---

## 6. Structura ipotezelor — starea finală

| Nivel | Ipoteza | Status | Derivabilă din? |
|-------|---------|--------|-----------------|
| Fundamental | **(H1)** Starea nodului ↔ $\Sigma(\mathbf{x})$ | **Postulat de bază QNG** | Definiția grafului |
| Derivat | **(P-UPD)** $\nu \propto |d\Sigma/dt|$ | **Teoremă din (H1)** | Demonstrat §4 |
| Derivat | **VPC (direcție forță ∥ ∇Σ)** | **Teoremă din (P-UPD)** | Demonstrat v3 §3 |
| Constitutiv | **Direcția lag = $H\hat{n}$** | **Ipoteză constitutivă** | Deschis |

---

## 7. Falsificatorul structural

Dacă frecarea VPC este ne-reciprocă ($\gamma_{ij} \neq \gamma_{ji}$), există o
predicție testabilă: **rotația planului orbital** pe o orbită excentrică.

Frecarea standard Stokes ($\gamma \propto \delta_{ij}$) produce decay radial
uniform. VPC produce **cuplaj asimetric** între oscilațiile radiale și tangențiale:

$$\Delta\phi_{\text{VPC}} \sim \tau_{\text{phys}} \int_0^T H_{r\theta}\,v_r\,v_\theta\,dt$$

Pentru câmp Kepler: $H_{r\theta} = 0$ exact (diagonal în sferice) → no rotation.
Dar pentru un câmp asimetric (sistemul binar aproape): $H_{r\theta} \neq 0$ →
rotație detectabilă.

**Test:** Pulsari binari cu câmp compozit non-sferic. Dacă VPC e prezent și
ne-reciproc, predicție: drift orbital distinct de GR.

---

## 8. Rezumat corecții față de v3

| Element | v3 | v4 (corect) |
|---------|-----|-------------|
| Acțiunea Eq. (13) | Propusă ca derivare VPC | **Greșită** — nu dă VPC prin EL |
| Natura VPC | Nemenționată | **Frecare ne-reciprocă** |
| Baza (P-UPD) | Motivație fizică intuitivă | **Derivat din (H1)** via teoria informației |
| Ipoteza rămasă | Acțiunea | **(H1) + direcția lag = $H\hat{n}$** |
