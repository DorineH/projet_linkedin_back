# projet_linkedin_back
Le projet permet d’obtenir les dernières offres d’emploi publiées sur LinkedIn. Le backend, développé en Python, se connecte à une base de données PostgreSQL. Celle-ci est alimentée automatiquement grâce à un service N8N, qui récupère et enregistre les nouvelles offres publiées sur LinkedIn.
# Jobs Visualizer API — FastAPI (async)


## Prérequis
- Python 3.11+ (recommandé)
- PostgreSQL en local ou distant


## Installation (PowerShell)
```powershell
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Édite .env et mets ta DATABASE_URL
uvicorn app.main:app --reload
