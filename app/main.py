import os
from flask import Flask

app = Flask(__name__)

# Variable récupérée de manière sécurisée
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")

@app.route("/")
def home():
    return "Application DevSecOps Opérationnelle"

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # Exécution simple sans option debug à risque
    app.run(host="127.0.0.1", port=5000)