FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sécurité : Création d'un utilisateur non-root
RUN adduser -D appuser && chown -R appuser /app
USER appuser

EXPOSE 5000

# ✅ Lancement via Gunicorn en production :
# -w 2 : 2 processus workers pour gérer la charge
# -b 0.0.0.0:5000 : Écoute sur le port 5000
# app.main:app : Pointe vers le fichier app/main.py et la variable "app"
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.main:app"]