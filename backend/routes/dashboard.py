# backend/routes/dashboard.py
from flask import Blueprint, jsonify
import os
import yaml
from datetime import datetime
from uuid import UUID

dashboard_bp = Blueprint("dashboard_bp", __name__)
MLRUNS_PATH = os.path.join(os.getcwd(), "core", "mlruns", "0")  # Adjusted for your structure

def parse_run_details(run_dir):
    run_id = os.path.basename(run_dir)
    metrics_dir = os.path.join(run_dir, "metrics")
    model_dir = os.path.join(run_dir, "artifacts", "model")
    mlmodel_path = os.path.join(model_dir, "MLmodel")

    # Time details
    created = os.path.getctime(run_dir)
    modified = os.path.getmtime(run_dir)
    duration = round(modified - created, 2)

    run_info = {
        "run_id": run_id,
        "pipeline": "ml_pipeline",
        "timestamp": datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": duration,
        "status": "completed" if os.path.exists(metrics_dir) else "failed",
        "metrics": {},
        "model": {}
    }

    # Load metrics
    if os.path.exists(metrics_dir):
        for file in os.listdir(metrics_dir):
            try:
                with open(os.path.join(metrics_dir, file)) as f:
                    run_info["metrics"][file] = float(f.readline().strip())
            except:
                continue

    # Load model info
    if os.path.exists(mlmodel_path):
        try:
            with open(mlmodel_path, "r") as f:
                mlmodel_data = yaml.safe_load(f)

            # Compute model size
            total_size = sum(
                os.path.getsize(os.path.join(dp, file))
                for dp, _, files in os.walk(model_dir)
                for file in files
            )

            run_info["model"] = {
                "flavor": list(mlmodel_data.get("flavors", {}).keys())[0],
                "run_id": mlmodel_data.get("run_id"),
                "artifact_path": model_dir,
                "size_kb": round(total_size / 1024, 2),
            }
        except:
            pass

    return run_info

@dashboard_bp.route("/runs", methods=["GET"])
def list_pipeline_runs():
    runs = []
    for run_id in os.listdir(MLRUNS_PATH):
        run_path = os.path.join(MLRUNS_PATH, run_id)
        if os.path.isdir(run_path):
            try:
                UUID(run_id)  # Ensure it's a valid run ID
                runs.append(parse_run_details(run_path))
            except:
                continue
    return jsonify(sorted(runs, key=lambda x: x["timestamp"], reverse=True))
