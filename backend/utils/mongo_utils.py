import os
import joblib
import logging
from datetime import datetime
from utils.db import Database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)

def save_pipeline_metadata(run_id, user_id, dataset_id, mlflow_tracking_uri, params, status, error=None):
    """Save or update pipeline metadata in MongoDB."""
    metadata = {
        "_id": run_id,
        "user_id": user_id,
        "dataset_id": dataset_id,
        "mlflow_tracking_uri": mlflow_tracking_uri,
        "params": params,
        "status": status,
        "timestamp": datetime.utcnow()
    }

    if error:
        metadata["error"] = str(error)

    Database.get_collection("pipeline_runs").update_one(
        {"_id": run_id},
        {"$set": metadata},
        upsert=True
    )
    logger.info(f"✅ Pipeline metadata updated for run {run_id}")



def save_model_artifact(model, run_id, file_path):
    # Extract the user directory from the file path
    user_directory = os.path.dirname(os.path.dirname(file_path))
    run_directory = os.path.join(user_directory, "runs", run_id)
    artifacts_directory = os.path.join(run_directory, "artifacts", "model")
    os.makedirs(artifacts_directory, exist_ok=True)

    # Save the model as model.pkl
    model_file_path = os.path.join(artifacts_directory, "model.pkl")
    joblib.dump(model, model_file_path)
    logger.info(f"✅ Model saved at: {model_file_path}")

    return os.path.abspath(model_file_path)
