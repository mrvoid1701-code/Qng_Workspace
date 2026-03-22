# QNG: Numarul Optim de Moduri n_eff — Derivare Teoretica

**Status**: DERIVARE PRELIMINARA (justificata partial)
**Versiune**: v1
**Data**: 2026-03-22
**Legatura**: G47 (convergenta gamma), fereastra fizica 25-35 moduri

---

## 1. Problema

In G47, analiza convergentei lui gamma necesita alegerea unui numar de moduri
`n_modes` pentru calculul propagatorului. Empiric, pentru N=280 noduri, s-a
observat o platou stabila in γ(n_modes) in regiunea 25-35 moduri.

**Intrebare**: Exista o justificare teoretica pentru aceasta fereastra?

---

## 2. Argument: n_eff ~ 2 * sqrt(N)

### 2.1 Analogia cu Grafuri Aleatoare

Pentru un graf Erdos-Renyi G(N, p) cu grad mediu `<k> = p*(N-1) ~ k_mean`,
spectrul Laplacianului Jaccard are o structura cunoscuta:

- **Banda de baza** (bulk): N - O(sqrt(N)) eigenvalori concentrate in jurul `<k>`
- **Moduri de margine** (edge modes): O(sqrt(N)) eigenvalori mici/mari, separate de bulk
- **Modul constant**: exact 1 eigenvaloare la lambda=0 (sau M_EFF_SQ)

Argumentul clasic Wigner pentru matrici random: fluctuatiile spectrale au magnitudine
`sigma_lambda ~ sqrt(N) * delta_lambda` unde `delta_lambda` este spacing-ul mediu.

### 2.2 Moduri Fizice vs Moduri de Rumore

Un mod este "fizic" (contribuie la propagatorul pe distante lungi) daca:
- Eigenvaloarea este **semnificativ separata** de bulk: `lambda_k < lambda_bulk / sqrt(N)`
- Sau eigenvaloarea este **semnificativ mai mare** decat bulk: `lambda_k > lambda_bulk * sqrt(N)`

Numarul de moduri care satisfac aceasta conditie:

```
n_eff = numarul de eigenvalori in coada spectrala = O(sqrt(N))
```

Pentru N = 280:
```
n_eff ~ 2 * sqrt(280) ~ 2 * 16.7 ~ 33
```

Factorul 2 vine din faptul ca luam **ambele cozi** (bottom si top).

### 2.3 Justificare Fizica — Localizare Anderson

Modurile cu eigenvaloare mica (`lambda << <lambda>`) sunt delocalizate pe tot graful —
acestea propagariu pe distante lungi si contribuie la C(r) pe scari mari (cosmologice).

Modurile cu eigenvaloare mare (`lambda >> <lambda>`) sunt localizate — contribuie
la structuri locale (materie barionica).

**Modurile din bulk** (`lambda ~ <lambda>`) sunt "generic delocalizate" cu lungime
de localizare `xi ~ N^{1/2}` — contribuie la propagator pe distante intermediare,
dar cu o putere totala O(N) mai slaba decat coada.

Deci **fizica pe distante lungi** este controlata de O(sqrt(N)) moduri.

---

## 3. Estimarea Explicita

### 3.1 Spacing spectral in coada

Spectrul Jaccard pentru G(N, k_mean) are o densitate de stari aproximativa:

```
rho(lambda) ~ (1 / (2*pi)) * sqrt(4*k_mean - (lambda - k_mean)^2) / k_mean
```

(legea semicirculara Wigner, valida pentru bulk)

Numarul de stari in coada `[0, lambda_c]`:

```
N_tail(lambda_c) ~ N * integral_0^{lambda_c} rho(lambda) d lambda
```

Pentru `lambda_c = M_EFF_SQ + delta_lambda_bulk / sqrt(N)`:

```
N_tail ~ N * (delta_lambda / (2*pi*k_mean)) * lambda_c^{1/2}
```

Aceasta da `N_tail ~ sqrt(N)` pentru alegeri naturale ale `lambda_c`.

### 3.2 Calcul numeric (N=280, k=8)

```
<k> ~ 8 (grad mediu Jaccard)
sqrt(N) = sqrt(280) = 16.73
2*sqrt(N) = 33.5
```

Fereastra observata empiric: **25-35 moduri** — consistent cu `2*sqrt(N) ≈ 33`.

---

## 4. Platoul lui gamma(n_modes)

Cand `n_modes` creste de la 1 la N, gamma(n_modes) trece prin trei regimuri:

```
n_modes << n_eff:  gamma instabil, dominat de 1-2 moduri, varianta mare
n_modes ~ n_eff:   PLATOU — toate modurile fizice sunt incluse, gamma stabil
n_modes >> n_eff:  gamma deriva incet pe masura ce modurile de bulk dilueaza semnalul
```

Platoul este **coerent teoretic cu n_eff ~ 2*sqrt(N) ≈ 33**.

---

## 5. Limitele Argumentului

### 5.1 Graful Jaccard nu este Erdos-Renyi pur

Graful Jaccard QNG este construit prin doua etape (G(N,p) initial + rewiring Jaccard),
ceea ce introduce **corelatie** intre muchii. Spectrul deviaza de la legea Wigner pura.

Totusi, pentru N=280, efectele de corelare sunt O(1/N) — argumentul `sqrt(N)` ramane valid.

### 5.2 n_eff depinde de k_conn si M_EFF_SQ

Factorul 2 in `2*sqrt(N)` nu este derivat exact — este o estimare:

```
n_eff = alpha * sqrt(N)   cu   alpha ~ 1.5..2.5
```

Pentru parametrii canonic (N=280, k=8, M_EFF_SQ=0.014): alpha ~ 2.0 da n_eff ≈ 33.

### 5.3 Mixed vs Bottom propagator

Argumentul de mai sus se aplica modurilor **de coada totala** (bottom + top).
Pentru propagatorul mixed (bottom n/2 + top n/2), fereastra optima este:

```
n_half ~ sqrt(N) = 16.7 per coada   =>   n_total = 2 * sqrt(N) ~ 33
```

---

## 6. Concluzie si Recomandare

**Justificare**: `n_eff ~ 2*sqrt(N)` este derivat din:
1. Structura spectrala a grafurilor random (teoria Wigner)
2. Separarea intre moduri de coada (fizice) si bulk (rumore)
3. Argumentul de localizare Anderson

**Pentru N=280**: `n_eff ≈ 33`, consistent cu fereastra empirica 25-35.

**Recomandare pentru G47**: Folositi `n_modes ∈ [sqrt(N), 3*sqrt(N)]` ca fereastra fizica.
Centrul plateaului trebuie sa cada in aceasta regiune; daca nu, parametrii grafului
(N, k, M_EFF_SQ) nu sunt in regimul valid.

**Status**: Aceasta derivare este **preliminara** — necesita verificare prin:
- Scanare N (ex. N=100,200,280,400,500) si verificare ca platoul se scaleza cu sqrt(N)
- Analiza analitica a spectrului Jaccard (nu Erdos-Renyi pur)

---

*Document generat pe baza analizei G47 si a teoriei spectrelor random.*
