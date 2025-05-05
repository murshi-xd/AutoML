# backend/routes/pipeline.py


from zenml.client import Client
import threading

from flask import Blueprint, request, jsonify
from core.pipelines.training_pipeline import ml_pipeline

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/run_pipeline", methods=["POST"])
def run_pipeline():
    try:
        # Get user input from frontend/Postman
        data = request.get_json()

        file_path = data["file_path"]
        feature_strategy = data["feature_strategy"]
        feature_columns = data["feature_columns"]
        outlier_column = data["outlier_column"]
        target_column = data["target_column"]

        # Run the pipeline with the parameters
        run = ml_pipeline(
            file_path=file_path,
            feature_strategy=feature_strategy,
            feature_columns=feature_columns,
            outlier_column=outlier_column,
            target_column=target_column
        )

        # Return success response
        return jsonify({
            "status": "success",
            "message": "Pipeline executed successfully.",
            "dashboard_url": "http://127.0.0.1:8237/runs"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
