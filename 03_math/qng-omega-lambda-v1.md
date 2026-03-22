# QNG: Problema Omega_Lambda — De ce Modul Constant Nu Produce 68% Energie Intunecata

**Status**: OPEN_PROBLEM
**Versiune**: v1
**Data**: 2026-03-22
**Legatura**: G37e (gate diagnostic FAIL)

---

## 1. Identificarea Curenta: Modul Constant = Dark Energy

In QNG, dark energy este identificata cu **modul constant** al operatorului cinetic K:

```
phi_0(i) = 1/sqrt(N)   pentru orice nod i
lambda_0 = M_EFF_SQ = 0.014
omega_0  = sqrt(lambda_0) = 0.1183
```

Energia modului constant in aproximatia half-quantum:

```
E_DE = omega_0 / 2 = sqrt(M_EFF_SQ) / 2 ≈ 0.0592
```

Aceasta identificare este **corecta calitativ**: modul constant este uniform pe tot graful,
fara structura spatiala, exact ca un fond cosmologic. El nu poate fi "vazut" local.

---

## 2. De ce Omega_DE << 0.68

### 2.1 Calculul energiei totale

Pentru un graf cu N = 280 noduri si spectrul K cu valori proprii {lambda_k}:

```
E_total = sum_{k=0}^{N-1} omega_k / 2 = (1/2) sum_k sqrt(lambda_k)
```

Estimat prin momente de urma:

```
E_total ~ (N/2) * omega_mean
```

unde `omega_mean = sqrt(mean(lambda)) * (1 - Var(lambda)/(8*mean(lambda)^2))`.

Pentru graful Jaccard cu N=280, k=8:
- `mean_lambda ~ 4.5`
- `omega_mean ~ 2.1`
- `E_total ~ 280/2 * 2.1 = 294`

### 2.2 Fractia energiei modului constant

```
Omega_DE_QNG = E_DE / E_total = (omega_0/2) / (N/2 * omega_mean)
             = omega_0 / (N * omega_mean)
             = 0.1183 / (280 * 2.1)
             ~ 0.00020
```

Valoarea numerica (G37): `Omega_DE_QNG ≈ 0.000380`

**Factor discrepanta: 0.6847 / 0.000380 ≈ 1800x**

### 2.3 Structura problemei

Problema este **structurala**, nu numerica:

```
Omega_DE_QNG = omega_0 / (N * omega_mean) ~ 1/N   (pentru omega_0 ~ omega_mean)
```

Cu N = 280 si Omega_Lambda_obs = 0.6847:

```
Necesar: N_eff_DE ~ omega_0 / (Omega_Lambda_obs * omega_mean) ~ 1 / 0.68 ~ 1.5 moduri echivalente
```

Dar modul constant contribuie efectiv 1 mod. Diferenta este factor ~1.5 * 280 / 1 ~ 420x in numar de moduri echivalente, compusă cu diferenta de omega.

---

## 3. Ce Ar Trebui sa Faca Teoria

Pentru a reproduce `Omega_Lambda = 0.6847`, identificarea modului constant trebuie extinsa.
Exista cateva directii posibile:

### 3.1 Degenerare Exponentiala (Cosmological Constant Problem Analog)

Daca exista `g(lambda_0)` moduri cu aceeasi eigenvaloare `lambda_0`:

```
E_DE = g(lambda_0) * omega_0 / 2
Omega_DE = g(lambda_0) * omega_0 / (N * omega_mean)
```

Pentru Omega_DE = 0.68:
```
g(lambda_0) ~ 0.68 * N * omega_mean / omega_0 ~ 0.68 * 280 * 2.1 / 0.1183 ~ 3380 moduri
```

Aceasta ar necesita o degenerare de ~3380x a modului constant — neverosimil pentru un graf finit.

### 3.2 Condensat de Vacuum (Vacuum Energy Density)

O alternativa: dark energy nu provine din modul constant individual, ci dintr-un **condensat**:
energia de punct zero a grafului Jaccard, integrata pe toate modurile:

```
E_vacuum = (1/2) sum_{k=0}^{N-1} omega_k
```

In aceasta interpretare, dark energy este proportionala cu E_vacuum total, si Omega_Lambda
este un parametru liber al teoriei (ca in Lambda-CDM).

**Problema**: Aceasta abandoneaza identificarea dynamica a DE cu modul constant.

### 3.3 Mecanism de Renormalizare

Poate energia modului constant trebuie renormalizata la scara cosmologica:

```
E_DE_ren = E_DE * Z(N, k_conn)
```

unde `Z` este un factor de renormalizare dependent de structura grafului. Dar nu avem
o derivare din primele principii.

### 3.4 Interpretare Diferita a Omega

Poate ca `Omega_Lambda` nu corespunde **fractiei din energia totala**, ci unui alt raport:
- ex. fractia din **energia de interactie** (off-diagonal K)
- sau fractia din **energia de masa** (modul constant e pur masa, nu cinetic)

Aceasta ar necesita o derivare a ecuatiilor Friedmann din QNG.

---

## 4. Concluzie

**Starea curenta**: G37 demonstreaza corect ca modul constant este candidatul natural
pentru dark energy in QNG (uniform, non-local, stabil). Dar **valoarea absoluta**
a energiei sale este de ~1800x mai mica decat Omega_Lambda observat.

**Aceasta este o problema deschisa (P1) a teoriei QNG.** Nu este un bug numeric
si nu are o rezolvare ad-hoc corecta. Necesita:

1. O derivare a ecuatiilor Friedmann din spectrul Jaccard
2. Un mecanism fizic care amplifica contributia modului constant
3. Sau o redefinire a identificarii Dark Energy in QNG

**Gates afectate**: G37e — FAIL (OPEN_PROBLEM)
**Impact**: Relatiile relative (G37a-d) raman valide; numai Omega_Lambda absolut este problema.

---

## 5. Estimare Simpla a Discrepantei

```
discrepanta = Omega_Lambda_obs / Omega_DE_QNG
            = 0.6847 / (omega_0 / (N * omega_mean))
            = 0.6847 * N * omega_mean / omega_0
            = 0.6847 * 280 * omega_mean / sqrt(M_EFF_SQ)
```

Pentru `omega_mean ~ 2.1` si `sqrt(0.014) = 0.1183`:

```
discrepanta ~ 0.6847 * 280 * 2.1 / 0.1183 ~ 3408
```

Numeric (G37 run): factor = 1802x (diferenta de la estimare din cauza distributiei reale a eigenvalorilor).

---

*Document generat automat de sesiunea Claude Code pe baza rezultatelor G37e.*
