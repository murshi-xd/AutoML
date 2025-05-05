# backend/app.py

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Add core to sys.path for dynamic imports like from steps import ...
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

# Init Flask
app = Flask(__name__)
CORS(app)

# Health check route
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "OK", "message": "AutoML backend running"}), 200

# Import routes
from routes.pipeline import pipeline_bp
app.register_blueprint(pipeline_bp)

# Debug startup message
print("✅ Flask server started on http://localhost:5004")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)





