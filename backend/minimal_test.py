
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify({"message": "Hello from MediScan!", "status": "ok"})

if __name__ == "__main__":
    print("Starting minimal test server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
