import os
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
from zenml import Model, pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)

def get_user_runs_directory(file_path):
    user_directory = os.path.dirname(os.path.dirname(file_path))
    runs_directory = os.path.join(user_directory, "runs")
    os.makedirs(runs_directory, exist_ok=True)
    return f"file://{os.path.abspath(runs_directory)}"

@pipeline(
    model=Model(
        name="AutoML Model"
    ),
)
def ml_pipeline(
    file_path: str,
    feature_strategy: str,
    missing_value_feature_strategy: str,
    feature_columns: list,
    outlier_column: str,
    outlier_strategy: str,
    outlier_method: str,
    outlier_threshold: float,
    target_column: str,
    user_id: str,
    dataset_id: str,
    run_id: str = None
):
    start_time = datetime.utcnow()

    pipeline_metadata = {
        "_id": run_id,
        "user_id": user_id,
        "dataset_id": dataset_id,
        "params": {
            "file_path": file_path,
            "feature_strategy": feature_strategy,
            "missing_value_feature_strategy" : missing_value_feature_strategy,
            "feature_columns": feature_columns,
            "outlier_column": outlier_column,
            "outlier_strategy": outlier_strategy,
            "outlier_method": outlier_method,
            "outlier_threshold": outlier_threshold,
            "target_column": target_column
        },
        "start_time": start_time,
        "status": "running"
    }

    mlflow_tracking_uri = get_user_runs_directory(file_path)
    experiment_name = f"user_{user_id}_experiments"

    try:
        Database.get_collection("pipeline_runs").insert_one(pipeline_metadata)
        logger.info(f"Pipeline {experiment_name} started for user {user_id}.")

        # Step 1: Data Ingestion
        raw_data = data_ingestion_step(file_path=file_path)
        logger.info("Data ingestion completed successfully.")

        # Step 2: Handle Missing Values
        filled_data = handle_missing_values_step(raw_data, strategy=missing_value_feature_strategy)
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
            column_name=outlier_column,
            strategy=outlier_strategy,  
            method=outlier_method,    
            threshold=outlier_threshold       
        )

        logger.info("Outlier detection completed successfully.")

        # Step 5: Data Splitting
        X_train, X_test, y_train, y_test = data_splitter_step(
            clean_data, 
            target_column=target_column
        )
        logger.info("Data splitting completed successfully.")

        # Step 6: Model Building (pass run_id for DB update inside step)
        model = model_building_step(
            X_train=X_train, 
            y_train=y_train,
            mlflow_tracking_uri=mlflow_tracking_uri,
            experiment_name=experiment_name,
            run_id=run_id
        )

        logger.info("Model building completed successfully.")

        # Step 7: Model Evaluation
        evaluation_metrics, mse = model_evaluator_step(
            trained_model=model, 
            X_test=X_test, 
            y_test=y_test,
            run_id=run_id
        )
        logger.info("Model evaluation step completed successfully.")

        pipeline_metadata.update({
            "end_time": datetime.utcnow(),
            "status": "completed",
            "mlflow_tracking_uri": mlflow_tracking_uri
        })
        Database.get_collection("pipeline_runs").update_one(
            {"_id": run_id},
            {"$set": pipeline_metadata}
        )
        logger.info(f"Pipeline run completed with run_id: {run_id}")

        return model

    except Exception as e:
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