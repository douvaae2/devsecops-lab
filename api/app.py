from flask import Flask, request, jsonify
import sqlite3
import subprocess
import bcrypt
import os
import ast
import re

app = Flask(__name__)

# SECRET_KEY lu depuis une variable d'environnement
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

# ---------------------------
# UTILITAIRES
# ---------------------------
def is_valid_hostname(hostname):
    # Validation simple : lettres, chiffres, tirets, points
    return re.match(r'^[a-zA-Z0-9.-]+$', hostname) is not None

def safe_eval(expr):
    # N'accepte que les opérations math simples
    try:
        return ast.literal_eval(expr)
    except:
        return None

# ---------------------------
# ROUTES
# ---------------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # ✅ Requête SQL paramétrée pour éviter SQL Injection
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"status": "success", "user": username})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")
    if not is_valid_hostname(host):
        return jsonify({"error": "Invalid host"}), 400

    # ✅ subprocess sécurisé
    try:
        output = subprocess.check_output(["ping", "-n", "1", host], shell=False)
        return jsonify({"output": output.decode()})
    except subprocess.CalledProcessError:
        return jsonify({"error": "Ping failed"}), 500

@app.route("/compute", methods=["POST"])
def compute():
    expression = request.json.get("expression", "1+1")
    result = safe_eval(expression)
    if result is None:
        return jsonify({"error": "Invalid expression"}), 400
    return jsonify({"result": result})

@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "admin")
    # ✅ bcrypt hash
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    return jsonify({"bcrypt": hashed.decode()})

@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "test.txt")
    # ✅ Protection contre path traversal
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Invalid filename"}), 400
    try:
        with open(filename, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

@app.route("/debug", methods=["GET"])
def debug():
    # ❌ Ne pas exposer les secrets dans prod
    return jsonify({"debug": True, "environment": "hidden"})

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Welcome to the DevSecOps secured API"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

