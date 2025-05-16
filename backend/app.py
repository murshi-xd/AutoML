# backend/app.py

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Add core to sys.path for dynamic imports like from steps import ...
sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Health check route
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "OK", "message": "AutoML backend running"}), 200

# Import the centralized DB connection
from utils.db import Database
Database.connect()

# Import routes
from routes.pipeline import pipeline_bp
app.register_blueprint(pipeline_bp)

from routes.upload_routes import upload_bp
app.register_blueprint(upload_bp)

from routes.dataset_routes import dataset_bp
app.register_blueprint(dataset_bp)

from routes.eda_routes import eda_bp
app.register_blueprint(eda_bp)

from routes.config import config_bp
app.register_blueprint(config_bp)

from routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

from routes.model import model_bp
app.register_blueprint(model_bp)

# Debug startup message
print("✅ Flask server started on http://localhost:5004")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5004)
