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
