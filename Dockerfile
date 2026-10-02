# ❌ Mauvaise pratique : Utilisation d'une vieille image avec des vulnérabilités connues
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ❌ Mauvaise pratique : Exécution en tant que root
EXPOSE 5000
CMD ["python", "app/main.py"]