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
mlflow.autolog(disable=True)

from zenml import Model, pipeline, step




# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)

@pipeline(
    model=Model(
        # The name uniquely identifies this model
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

    try:
        # Store initial pipeline metadata in MongoDB
        Database.get_collection("pipeline_runs").insert_one(pipeline_metadata)
        logger.info(f"Pipeline {run_id} started for user {user_id}.")

        # Step 1: Data Ingestion
        try:
            raw_data = data_ingestion_step(file_path=file_path)
            logger.info("Data ingestion completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Data ingestion failed: {e}")

        # Step 2: Handle Missing Values
        try:
            filled_data = handle_missing_values_step(raw_data)
            logger.info("Missing values handled successfully.")
        except Exception as e:
            raise RuntimeError(f"Handling missing values failed: {e}")

        # Step 3: Feature Engineering
        try:
            engineered_data = feature_engineering_step(
                filled_data, 
                strategy=feature_strategy, 
                features=feature_columns
            )
            logger.info("Feature engineering completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Feature engineering failed: {e}")

        # Step 4: Outlier Detection
        try:
            clean_data = outlier_detection_step(
                engineered_data, 
                column_name=outlier_column
            )
            logger.info("Outlier detection completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Outlier detection failed: {e}")

        # Step 5: Data Splitting
        try:
            X_train, X_test, y_train, y_test = data_splitter_step(
                clean_data, 
                target_column=target_column
            )
            logger.info("Data splitting completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Data splitting failed: {e}")

        # Step 6: Model Building
        try:
            model = model_building_step(X_train=X_train, y_train=y_train)
            logger.info("Model building completed successfully.")
        except Exception as e:
            raise RuntimeError(f"Model building failed: {e}")

        # Step 7: Model Evaluation

        try:
            # Model Evaluation Step
            evaluation_metrics, mse = model_evaluator_step(
                trained_model=model, X_test=X_test, y_test=y_test
            )

            logger.info("Model evaluation step completed successfully.")
            # Access the evaluation metrics and MSE

        except Exception as e:
            raise RuntimeError(f"Model evaluation failed: {e}")


        # Step 8: Finalize Metadata
        end_time = datetime.utcnow()
        pipeline_metadata.update({
            "end_time": end_time,
            # "metrics": evaluation_metrics,
            # "mse": mse,
            "status": "completed"
        })

        # Update the metadata in MongoDB
        Database.get_collection("pipeline_runs").update_one(
            {"_id": run_id},
            {"$set": pipeline_metadata}
        )
        logger.info(f"Pipeline {run_id} completed successfully.")

        return pipeline_metadata

    except Exception as e:
        # Handle overall pipeline failure
        end_time = datetime.utcnow()
        pipeline_metadata.update({
            "end_time": end_time,
            "status": "failed",
            "error": str(e)
        })
        Database.get_collection("pipeline_runs").update_one(
            {"_id": run_id},
            {"$set": pipeline_metadata}
        )
        logger.error(f"Pipeline {run_id} failed: {e}")
        raise RuntimeError(f"Pipeline execution failed: {e}") from e


if __name__ == "__main__":
    # Running the pipeline
    run = ml_pipeline()