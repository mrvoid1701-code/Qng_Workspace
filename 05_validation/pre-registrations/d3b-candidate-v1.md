# Pre-Registration: D3b Candidate Gate v1

**Registered:** 2026-03-05 (înainte de prima rulare)
**Script:** `scripts/run_d3b_candidate_v1.py`
**Seeds:** attack_seed=9999, dataset_seed=3401
**Status:** PRE-REGISTERED

---

## Context

Testul d3-attack-v1 a confirmat că D3 curent este non-discriminant:
- Toate câmpurile (inclusiv zgomot pur) obțin cos_sim ≥ 0.994
- Gap între Sigma QNG și zgomot pur: ~0.002 (neglijabil)

Cauza identificată: `anisotropy_keep=0.4` → 60% blend spre metrică izotropică.
O metrică izotropică dă `g^{-1}·grad ∥ grad` pentru **orice** câmp, indiferent de fizică.

---

## Două Teste Noi

### Test 1: Anisotropy Sweep

Rulează pipeline-ul D3 pe toate câmpurile de control pentru:
- `anisotropy_keep` ∈ {0.4, 0.7, 1.0}

**Predicție:** La `anisotropy_keep=1.0` (fără shrinkage), discriminanța apare —
câmpurile non-Gaussiene și zgomotul vor obține cos_sim semnificativ mai mic.

Gate D3b_sweep trece dacă la `anisotropy_keep=1.0`:
- `cos_sim(QNG) - cos_sim(C5_NOISE) > 0.05`

### Test 2: Cross-Metric Margin

Pentru fiecare anchor:
- `alpha_self = cos_sim(-g_qng^{-1} · grad_qng, -grad_qng)` — metrica din Sigma QNG
- `alpha_cross = cos_sim(-g_ctrl^{-1} · grad_qng, -grad_qng)` — metrica dintr-un câmp random

**Întrebarea:** Metrica QNG aliniază gradientul QNG mai bine decât o metrică străină?

Gate D3b_cross trece dacă:
- `median(alpha_self - alpha_cross) > 0.05`

Dacă gap-ul e < 0.05, înseamnă că orice metrică face la fel pentru Sigma QNG —
câmpul nu are structură specifică față de metrica sa.

---

## Câmpuri Testate
Identice cu d3-attack-v1: BASELINE_QNG, C1-C5.

## Anti-tuning Policy
Thresholdurile (0.05) sunt declarate înainte de rulare și nu vor fi ajustate post-hoc.
