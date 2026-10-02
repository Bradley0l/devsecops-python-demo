import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

@app.route("/")
def home():
    return "Application DevSecOps Opérationnelle"

@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # ✅ Exécution sécurisée sans shell=True
    output = subprocess.check_output(["ping", "-c", "1", host])
    return output.decode("utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)