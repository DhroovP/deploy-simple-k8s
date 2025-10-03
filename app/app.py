from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/status/<int:code>")
def status_code(code):
    if 100 <= code <= 504:
        response = jsonify({"status": code, "message": f"Returning HTTP {code}"})
        response.status_code = code
        return response
    else:
        abort(400, description="Provide a code with constraints: 100 <= code <= 504")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
