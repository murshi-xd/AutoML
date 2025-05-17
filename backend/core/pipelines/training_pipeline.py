import os
import json
import uuid
import logging
from datetime import datetime
from steps.data_ingestion_step import data_ingestion_step
from steps.data_splitter_step import data_splitter_step
from steps.feature_engineering_step import feature_engineering_step
from steps.handle_missing_values_step import handle_missing_values_step
from steps.model_building_step import model_building_step
from steps.model_evaluator_step import model_evaluator_step
from steps.outlier_detection_step import outlier_detection_step
from utils.db import Database
import mlflow
from zenml import step, log_metadata, get_step_context, Model, pipeline


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_user_runs_directory(file_path):
    # Extract the user directory from the file path
    user_directory = os.path.dirname(os.path.dirname(file_path))
    runs_directory = os.path.join(user_directory, "runs")
    # Create the directory if it doesn't exist
    os.makedirs(runs_directory, exist_ok=True)
    # Convert to a file URI
    return f"file://{os.path.abspath(runs_directory)}"


@pipeline(
    model=Model(
        name="AutoML Model"
    ),
)
def ml_pipeline(
    file_path: str,
    feature_strategy: str,
    feature_columns: list,
    outlier_column: str,
    target_column: str,
    user_id: str,
    dataset_id: str
):
    run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    # Prepare initial pipeline metadata
    pipeline_metadata = {
        "_id": run_id,
        "user_id": user_id,
        "dataset_id": dataset_id,
        "mlflow_tracking_uri": "",
        "params": {
            "file_path": file_path,
            "feature_strategy": feature_strategy,
            "feature_columns": feature_columns,
            "outlier_column": outlier_column,
            "target_column": target_column
        },
        "start_time": start_time,
        "status": "running"
    }

    # # Set up MLflow tracking directory
    # mlflow_tracking_uri = get_user_runs_directory(file_path)
    # mlflow.set_tracking_uri(mlflow_tracking_uri)
    # logger.info(f"✅ MLflow tracking URI set to: {mlflow.get_tracking_uri()}")

    # Set experiment name based on user ID
    experiment_name = f"user_{user_id}_experiments"
    mlflow.set_experiment(experiment_name)

    try:
        # Store initial pipeline metadata in MongoDB
        Database.get_collection("pipeline_runs").insert_one(pipeline_metadata)
        logger.info(f"Pipeline {run_id} started for user {user_id}.")

        with mlflow.start_run(run_name=run_id) as mlflow_run:
            # Log basic params
            mlflow.log_params(pipeline_metadata["params"])

            # Step 1: Data Ingestion
            raw_data = data_ingestion_step(file_path=file_path)
            logger.info("Data ingestion completed successfully.")

            # Step 2: Handle Missing Values
            filled_data = handle_missing_values_step(raw_data)
            logger.info("Missing values handled successfully.")

            # Step 3: Feature Engineering
            engineered_data = feature_engineering_step(
                filled_data, 
                strategy=feature_strategy, 
                features=feature_columns
            )
            logger.info("Feature engineering completed successfully.")

            # Step 4: Outlier Detection
            clean_data = outlier_detection_step(
                engineered_data, 
                column_name=outlier_column
            )
            logger.info("Outlier detection completed successfully.")

            # Step 5: Data Splitting
            X_train, X_test, y_train, y_test = data_splitter_step(
                clean_data, 
                target_column=target_column
            )
            logger.info("Data splitting completed successfully.")

            # Step 6: Model Building
            model = model_building_step(X_train=X_train, y_train=y_train)
            logger.info("Model building completed successfully.")

            # Step 7: Model Evaluation
            evaluation_metrics, mse = model_evaluator_step(
                trained_model=model, 
                X_test=X_test, 
                y_test=y_test
            )
            logger.info("Model evaluation step completed successfully.")



            # Finalize metadata
            pipeline_metadata.update({
                "end_time": datetime.utcnow(),
                "status": "completed",
                "mlflow_tracking_uri" : ""
            })
            Database.get_collection("pipeline_runs").update_one(
                {"_id": run_id},
                {"$set": pipeline_metadata}
            )
            logger.info(f"Pipeline {run_id} completed successfully.")


            return model

    except Exception as e:
        # Handle overall pipeline failure
        pipeline_metadata.update({
            "end_time": datetime.utcnow(),
            "status": "failed",
            "error": str(e)
        })
        Database.get_collection("pipeline_runs").update_one(
            {"_id": run_id},
            {"$set": pipeline_metadata}
        )
        logger.error(f"Pipeline {run_id} failed: {e}")
        raise RuntimeError(f"Pipeline execution failed: {e}") from e
    finally:
        mlflow.end_run()
