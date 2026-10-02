import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# ❌ Mauvaise pratique / Secret en dur (Détecté par Gitleaks / SAST)
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLEKEY"

@app.route("/")
def home():
    return "Application DevSecOps Opérationnelle"

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # ❌ Mauvaise pratique / Command Injection (Détecté par Bandit / Semgrep)
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output.decode("utf-8")

if __name__ == "__main__":
    # ❌ Mauvaise pratique : debug=True en production
    app.run(host="0.0.0.0", port=5000, debug=True)