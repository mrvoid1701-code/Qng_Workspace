# Task for Codex

## Obiectiv

Adaugă infrastructure de reproducibilitate automată:
1. Un fișier `requirements.lock` complet (toate dependențele exacte cu versiuni fixate)
2. Un `Dockerfile` care rulează `reproduce_all.ps1` echivalent pe Linux
3. Un GitHub Actions workflow (`.github/workflows/reproduce.yml`) care rulează pipeline-ul la fiecare push pe `main`

---

## Context

Proiectul are un pipeline de validare științifică reproducibil descris în:
- `07_exports/repro-pack-v1/reproduce_all.ps1` — lista completă de comenzi de rulat (în ordine)
- `requirements.txt` — conține doar `pypdf>=4.0.0` (incomplet, trebuie completat)
- Toate scripturile sunt în `scripts/` și rulează cu Python 3.10+

Dependențele reale folosite în scripturi (din importuri): `numpy`, `pandas`, `matplotlib`, `scipy` (optional), `pypdf`. Restul sunt din stdlib.

---

## Task 1 — `requirements.lock`

Creează `requirements.lock` cu versiuni fixate pentru toate pachetele de mai jos, compatibile cu Python 3.10:

```
numpy
pandas
matplotlib
pypdf
```

Formatul dorit (exemplu):
```
numpy==1.26.4
pandas==2.2.1
matplotlib==3.8.3
pypdf==4.2.0
```

---

## Task 2 — `Dockerfile`

Creează `Dockerfile` la rădăcina repo-ului care:
- Pornește de la `python:3.10-slim`
- Instalează dependențele din `requirements.lock`
- Copiază tot repo-ul în `/workspace`
- Rulează echivalentul Linux al pașilor din `reproduce_all.ps1` (înlocuiește `.venv\Scripts\python.exe` cu `python`)
- La final verifică existența artifact-elor critice (lista din `reproduce_all.ps1` secțiunea `$required`)

---

## Task 3 — GitHub Actions workflow

Creează `.github/workflows/reproduce.yml` care:
- Se declanșează la `push` pe branch-ul `main`
- Rulează pe `ubuntu-latest`
- Instalează Python 3.10
- Instalează dependențele din `requirements.lock`
- Rulează toți pașii din `reproduce_all.ps1` (tradus în bash)
- Verifică că artifact-ele critice există la final
- Dacă un pas eșuează, workflow-ul eșuează clar cu mesaj

Toate comenzile Python să folosească argparse exact ca în scripturi (argumentele sunt identice cu cele din `reproduce_all.ps1`).

---

## Ce NU trebuie modificat

- Niciun script din `scripts/`
- Niciun fișier din `05_validation/`
- Niciun fișier din `07_exports/`
- Logica de validare sau gate-urile din scripturi

---

## Livrabile

- `requirements.lock`
- `Dockerfile`
- `.github/workflows/reproduce.yml`

---

---

# Taskuri noi adăugate — 2026-02-25T13:19 UTC

> Adăugate de Claude Sonnet 4.6 după sesiunea de validare din 2026-02-25.
> Motivul: limitele identificate în CURL-002 și T-SIG pending — necesită continuare numerică.

---

## TASK-A — QNG-T-CURL-003-v2: Curl cu metrică spatially-varying

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** ÎNALTĂ — deblochează C2/C3 din CURL-002
**Pre-registration:** `05_validation/pre-registrations/qng-t-curl-002.md` (C2/C3 FAIL la constant-metric)

### Problem

CURL-002 a demonstrat că în aproximarea **constant-metric** (`g = g(anchor)`), termenul lag `a_lag = −τ g⁻¹ H v` produce un vector constant → curl = 0 exact. C2 și C3 FAILuiesc structural, nu numeric.

### Soluție

Evaluarea metricii **per-punct** în chart-ul local:
- Pentru fiecare punct `(x_k, y_k)` din chart (nu doar la ancoră), calculează `g(x_k, y_k)` folosind Hessianul local la acel punct
- Metodă: interpolare bilineară a câmpului Σ în vecinătatea fiecărui nod din chart; Hessian numeric din diferențe finite pe grid local
- Termenul lag devine: `a_lag(x_k) = −τ · g⁻¹(x_k) · H(x_k) · v` — acum spatially-varying → curl ≠ 0 în general

### Implementare sugerată

```python
# Pentru fiecare anchor_i:
#   1. Construiește grid local 5×5 în coordonate chart (x,y) folosind cei 20 noduri locali
#   2. Interpolar bilinear Sigma pe grid din valorile nodurilor
#   3. Calculează Hessian numeric (diff. finite) la fiecare punct din chart
#   4. Calculează g(x,y) = metric_from_sigma_hessian_v4(H(x,y))
#   5. Calculează a_lag(x,y) = −τ · g^{-1}(x,y) · H(x,y) · v
#   6. Fit linear model pe (x,y) → (a_lag_x, a_lag_y), extrage curl = ∂_x a_lag_y − ∂_y a_lag_x
```

### Gates pre-înregistrate (de scris în nou prereg ÎNAINTE de run)

| Gate | Condiție |
|---|---|
| C1 | median(curl_rel_static) < 1e-8 (identic cu CURL-002 C1) |
| C2 | median(curl_rel_lag_iso) > 10 × median(curl_rel_static) |
| C3 | median(curl_rel_rewired) > 10 × median(curl_rel_static) |

### Fișiere de creat

```
05_validation/pre-registrations/qng-t-curl-003-v2.md   ← LOCK BEFORE RUN
scripts/run_qng_t_curl_003_v2.py
05_validation/evidence/qng-t-curl-003-v2.md            ← după run
05_validation/evidence/artifacts/qng-t-curl-003-v2/
```

---

## TASK-B — T-SIG-001: Newtonian Limit Test (Numeric)

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** MEDIE
**Pre-registration:** `05_validation/pre-registrations/qng-sigma-dynamics-prereg-v1.md` (status: Pending)

### Ce trebuie implementat

Solver Poisson generalizat pe grid 2D (100×100), iterație fixă metrică-câmp:

```
Setup:
  - Grid 100×100, domeniu [−5, 5]² (unități adimensionale)
  - Sursă: ρ = M · δ(r) cu M = 1, G = 1, α = 4π
  - Condiție limită: Σ = 0 pe margini (Dirichlet)

Algoritm:
  g_0 = δ_ij (metric flat)
  Pentru n = 0..49:
    Rezolvă ∂_i(g_n^{ij} ∂_j Σ_n) = 4π ρ  (Poisson solver cu coef. variabili)
    g_{n+1} = normalize(SPD(−Hess(Σ_n)))
    Dacă ||g_{n+1} − g_n||_F / ||g_n||_F < 1e-2: STOP (converged)

Măsurare T-SIG-001:
  Rezidual: |∇²Σ_n − 4π ρ| / (4π · ρ_max) la fiecare punct
  Gate: 90th percentile < 0.10
```

### Biblioteci necesare

`scipy.sparse.linalg` pentru solver Poisson cu coeficienți variabili (matrix assembler 5-point stencil cu g variabil).

### Fișiere de creat

```
scripts/run_qng_t_sig_001.py
05_validation/evidence/qng-t-sig-001.md
05_validation/evidence/artifacts/qng-t-sig-001/
  ├── sigma_field.png
  ├── residual_map.png
  ├── convergence_history.csv
  └── gate_summary.csv
```

---

## TASK-C — T-SIG-002: Self-Consistency Convergence Test

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** MEDIE (same script ca T-SIG-001, iterație suplimentară)
**Pre-registration:** `05_validation/pre-registrations/qng-sigma-dynamics-prereg-v1.md` (status: Pending)

### Ce trebuie măsurat

Același algoritm iterativ ca T-SIG-001, dar gate-ul este convergența metricii:

```
Gate T-SIG-002: ||g_{n+1} − g_n||_F / ||g_n||_F < 0.01 atins în ≤ 50 iterații
```

Dacă T-SIG-001 și T-SIG-002 folosesc același script, pot fi în același run.

---

## TASK-D — T-SIG-004: Post-Newtonian Structure (Analytic)

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** SCĂZUTĂ (analytic, nu numeric)
**Pre-registration:** `05_validation/pre-registrations/qng-sigma-dynamics-prereg-v1.md` (status: Pending)

### Ce trebuie demonstrat

Expansiunea la ordinul 1 în `h_ij = g_ij − δ_ij`:

```
∇²Σ + ∇·(h ∇Σ) = αρ

Corecția de forță:
  δa^i = −h^{ij} ∂_j Σ

Forma funcțională așteptată: δa ∝ h · ∇Σ
Comparație cu GR liniarizat: în GR, corecția PN la accelerație are forma −Γ^i_{00} ∝ ∂ h_{00}
```

Se poate face ca document `03_math/derivations/qng-pn-structure-v1.md` (nu necesită script Python).

### Fișier de creat

```
03_math/derivations/qng-pn-structure-v1.md
```

---

## TASK-E — Sensitivity Scan (TASKS.md items 77–81)

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** MEDIE
**Referință:** `TASKS.md` secțiunea cu itemii 77–81

### Context

Itemii 77–81 din TASKS.md privesc scanarea sensibilității parametrilor QNG față de variații ale:
- `anisotropy_keep` (k = 0.4 ± 0.2)
- `tau_universal` (τ = 0.4 ± 0.15)
- Praguri de normalizare metrică (frob_floor variabil)

Nu a fost rulat niciodată cu metric v4. Necesită re-run post v4-commit.

---

## TASK-F — Date misiune noi: OD Residuals

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** SCĂZUTĂ (date externe — nu depinde de cod intern)

### Placeholder-uri în `data/trajectory/`

Fișierele existente au valori de 0 sau lipsesc rezidualele OD publicate pentru:

| Misiune | Stare | Acțiune necesară |
|---|---|---|
| JUNO_1 | `residual_mm_s = 0` (placeholder) | Căutare tabelă OD JUNO din articolele publicate (Iess et al. sau JPL IPN) |
| BEPICOLOMBO_1 | Absent din dataset | Adăugare din ESA/JPL OD reports |
| SOLAR_ORBITER_1 | Absent din dataset | Adăugare din ESA Orbit Determination reports |

Notă: datele trebuie să fie publicate în literatura de specialitate — nu interne NASA/ESA.

---

## TASK-G — Pioneer / Voyager / Deep-Space Tests

**Adăugat:** 2026-02-25T13:19 UTC
**Prioritate:** MEDIE-ÎNALTĂ (testele clasice ale anomaliei Pioneer)

### Context

Codex a adăugat `spacecraft_mass_kg` în `flyby_ds005_real.csv`. Asta sugerează că infrastructura pentru teste cu mase specifice este acum prezentă.

Teste propuse (din roadmap QNG):

| Test ID | Descriere | Fișier prereg |
|---|---|---|
| QNG-T-P01 | Pioneer 10: predicție anomalie la 20–70 AU | de creat |
| QNG-T-P02 | Pioneer 11: predicție anomalie | de creat |
| QNG-T-P03 | Verificare dependență radială a_P ~ 8.7×10⁻¹⁰ m/s² | de creat |
| QNG-T-V01 | Voyager 1: comparare cu anomalie Pioneer la aceeași rază | de creat |
| QNG-T-V02 | Voyager 2: idem | de creat |
| QNG-T-DS01 | Deep Space 1: verificare fără MMOD | de creat |

**Important:** Toate testele Pioneer/Voyager necesită pre-registration ÎNAINTE de rulare (anti-gaming policy).

### Update 2026-02-25 (Codex)
- QNG-T-PIONEER-v1 prereg + run executate (simple a = τ·|∇Σ|). Gate FAIL — predicție prea mare și nu respectă controalele interioare.
- Limitare structurală: forma a=τ·GM/r² nu poate produce anomalia constantă Pioneer; niciun τ nu o repară.
- Pentru v2 este nevoie mai întâi de analiză teoretică asupra:
  - unităților/semnificației lui τ (calibrat în T-028 ca coeficient de regresie, nu timp fizic),
  - formei corecte a termenului de lag la distanțe mari: a_lag ≈ −τ (v·∇)(g⁻¹∇Σ) ∝ τ·(GM)·v_r / r³, nu 1/r².
- Acest pas cere input de la autorul teoriei; Codex nu poate fixa formula fără specificație.
***

---

## Starea de după sesiunea 2026-02-25

| Test | Status după sesiune |
|---|---|
| Metric v4 (Frobenius) | ✅ PASS (toate DS) |
| GR-Bridge v2 | ✅ PASS B1–B5 (toate DS) |
| CURL-001 | ✅ PASS C1–C2 |
| CURL-002 | ✅ RUN COMPLET — C1 PASS, C2/C3 FAIL by design (constant-metric) |
| T-SIG-003 | ✅ PASS analytic |
| T-028 v4 | ✅ PASS (Codex, delta_chi2=−5849) |
| T-039 direct-v4 | ✅ PASS (Codex, Δchi2≈−887 000) |
| CURL-003-v2 | ⏳ Pending (TASK-A) |
| T-SIG-001 | ⏳ Pending numeric (TASK-B) |
| T-SIG-002 | ⏳ Pending numeric (TASK-C) |
| T-SIG-004 | ⏳ Pending analytic (TASK-D) |
| Sensitivity scan | ⏳ Pending (TASK-E) |
