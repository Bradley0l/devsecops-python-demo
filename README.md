# 🔄 DevSecOps Pipeline — Sécurité automatisée avec GitHub Actions

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![Python](https://img.shields.io/badge/Python-Flask-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Pipeline](https://img.shields.io/badge/pipeline-5%2F5_passed-brightgreen)

> **Lab 6** de mon parcours *Cloud Security Architect* — **DevSecOps**.
> Objectif : construire un pipeline CI qui **fait échouer le build** dès qu'il détecte ❌ un secret, ❌ une vulnérabilité critique ou ❌ une mauvaise pratique Python, puis corriger le code jusqu'à obtenir un pipeline entièrement vert.

---

## 🏗️ Pipeline

```
 push / pull request
        │
        ├──► 1. Secret Scan ........ Gitleaks
        ├──► 2. SAST ............... Bandit + Semgrep (p/python)
        └──► 3. Dependency Scan .... Trivy fs (CRITICAL, HIGH)
                     │   (les 3 doivent réussir)
                     ▼
             4. Docker Image Scan .. Trivy image (CRITICAL)
                     │
                     ▼
             5. Final Build
```

Workflow : [`.github/workflows/devsecops-pipeline.yml`](.github/workflows/devsecops-pipeline.yml)

| Étape | Outil | Bloque si... |
| :--- | :--- | :--- |
| Secret Scanning | Gitleaks | Clé d'API, mot de passe ou jeton en dur dans l'historique Git |
| SAST | Bandit (`-ll -ii`), Semgrep | Faille Python de sévérité moyenne ou plus (injection, `debug=True`...) |
| Dependency Scan | Trivy `fs` | CVE **CRITICAL** ou **HIGH** dans `requirements.txt` |
| Container Scan | Trivy `image` | CVE **CRITICAL** dans l'image Docker construite |
| Build | — | Ne s'exécute que si tous les contrôles précédents sont verts |

---

## 📁 Structure

```
devsecops-python-demo/
├── .github/workflows/devsecops-pipeline.yml
├── app/
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── requirements.txt
└── images/
```

---

## 1. Code initial volontairement vulnérable

![Dépôt initial](images/Capture%20d%27%C3%A9cran%202026-10-02%20215912.png)

| Fichier | Problème introduit |
| :--- | :--- |
| `app/main.py` | Clé AWS factice codée en dur (`AWS_SECRET_KEY = "AKIA..."`) |
| `app/main.py` | `subprocess.check_output(f"ping -c 1 {host}", shell=True)` → **injection de commande** |
| `app/main.py` | `app.run(host="0.0.0.0", debug=True)` → débogueur exposé |
| `requirements.txt` | `Flask==2.0.1`, `requests==2.25.1` → versions avec CVE connues |
| `Dockerfile` | Image `python:3.9-slim` ancienne, exécution en **root** |

## 2. Premier push : le pipeline bloque ❌

![Pipeline en échec](images/Capture%20d%27%C3%A9cran%202026-10-02%20220937.png)

| Job | Résultat | Raison |
| :--- | :---: | :--- |
| Secret Scanning (Gitleaks) | ✅ | Aucune règle Gitleaks déclenchée sur cette clé factice |
| SAST (Bandit & Semgrep) | ❌ | `shell=True`, `debug=True` |
| Dependency Scan (Trivy) | ❌ | CVE sur Flask 2.0.1 / requests 2.25.1 |
| Docker Image Security Scan | ⏭️ | Annulé : dépend des 3 jobs précédents |
| Final Build | ⏭️ | Annulé : aucune image non sécurisée n'est construite |

> C'est exactement le comportement attendu : **le pipeline refuse de construire un artefact non sûr.**

## 3. Corrections

**`app/main.py`** — secret lu depuis l'environnement, endpoint `/ping` vulnérable supprimé, pas de mode debug, écoute locale uniquement :

```python
import os
from flask import Flask

app = Flask(__name__)

AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")

@app.route("/")
def home():
    return "Application DevSecOps Opérationnelle"

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
```

**`requirements.txt`** — versions corrigées + serveur WSGI de production :

```text
Flask>=3.0.0
requests>=2.31.0
gunicorn>=21.2.0
```

**`Dockerfile`** — image récente et minimale, utilisateur non-root, Gunicorn :

```dockerfile
FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN adduser -D appuser && chown -R appuser /app
USER appuser
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]
```

| Avant | Après |
| :--- | :--- |
| Secret en dur | `os.getenv()` (à terme : Azure Key Vault, voir [azure-key-vault-secrets](https://github.com/Bradley0l/azure-key-vault-secrets)) |
| `subprocess(..., shell=True)` | Fonctionnalité supprimée (surface d'attaque réduite) |
| `debug=True` sur `0.0.0.0` | Serveur de dev local uniquement, **Gunicorn** en production |
| Flask 2.0.1 / requests 2.25.1 | Flask ≥ 3.0 / requests ≥ 2.31 |
| `python:3.9-slim` en root | `python:3.12-alpine` + `USER appuser` |

## 4. Résultat : pipeline 100 % vert ✅

![All checks have passed](images/Capture%20d%27%C3%A9cran%202026-10-02%20221829.png)

**5/5 contrôles réussis** : Secret Scanning, SAST, Dependency Scan, Docker Image Security Scan et Final Build.

![Dépôt après correction](images/Capture%20d%27%C3%A9cran%202026-10-02%20221901.png)

---

## 🧠 Ce que j'ai appris

- Le **Shift-Left** : chaque contrôle tourne à chaque push, le développeur a le retour en quelques secondes au lieu d'un audit en fin de projet.
- Les dépendances entre jobs (`needs:`) évitent de construire une image tant que le code n'est pas propre.
- Corriger n'est pas toujours patcher : supprimer une fonctionnalité dangereuse et inutile est parfois la meilleure remédiation.
- Gitleaks n'a pas détecté la clé d'exemple : un scanner n'est pas infaillible, d'où l'intérêt de **cumuler plusieurs couches** (Gitleaks + Semgrep + revue de code).

## 🚀 Prochaines étapes

- Épingler les actions sur un SHA plutôt que `@master` (supply chain).
- Publier les résultats en SARIF dans l'onglet *Security* de GitHub.
- Ajouter un scan IaC (voir [terraform-security](https://github.com/Bradley0l/terraform-security)) et la signature d'image (Cosign).

---

**Auteur :** André Zami — étudiant en cybersécurité, orienté Cloud Security Architecture.
