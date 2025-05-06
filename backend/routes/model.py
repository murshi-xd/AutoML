# backend/routes/model.py
from flask import Blueprint, jsonify
import os
import yaml
from datetime import datetime

model_bp = Blueprint("model_bp", __name__)
MLRUNS_PATH = os.path.join(os.getcwd(), "core", "mlruns", "0")


@model_bp.route("/model/<run_id>", methods=["GET"])
def get_model_info(run_id):
    try:
        run_dir = os.path.join(MLRUNS_PATH, run_id)
        artifact_path = os.path.join(run_dir, "artifacts", "model")
        mlmodel_path = os.path.join(artifact_path, "MLmodel")
        metrics_path = os.path.join(run_dir, "metrics")
        params_path = os.path.join(run_dir, "params")
        run_time = datetime.fromtimestamp(os.path.getmtime(run_dir)).strftime("%Y-%m-%d %H:%M:%S")

        if not os.path.exists(artifact_path):
            return jsonify({"error": "Model artifact not found"}), 404

        # Load MLmodel YAML
        mlmodel_info = {}
        if os.path.exists(mlmodel_path):
            with open(mlmodel_path, "r") as f:
                mlmodel_info = yaml.safe_load(f)

        # Load metrics
        metrics = {}
        if os.path.exists(metrics_path):
            for metric_file in os.listdir(metrics_path):
                with open(os.path.join(metrics_path, metric_file)) as f:
                    try:
                        metrics[metric_file] = float(f.readline().strip())
                    except:
                        continue

        # Load parameters (hyperparameters)
        parameters = {}
        if os.path.exists(params_path):
            for param_file in os.listdir(params_path):
                with open(os.path.join(params_path, param_file)) as f:
                    parameters[param_file] = f.read().strip()

        # Compose final response
        response = {
            "run_id": run_id,
            "status": "completed",
            "timestamp": run_time,
            "artifact_path": artifact_path,
            "model_files": os.listdir(artifact_path),
            "mlmodel_info": {
                "flavors": list(mlmodel_info.get("flavors", {}).keys()),
                "signature": mlmodel_info.get("signature", {}),
                "input_example": mlmodel_info.get("input_example", {}),
                "run_id": mlmodel_info.get("run_id", run_id)
            },
            "metrics": metrics,
            "parameters": parameters
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
