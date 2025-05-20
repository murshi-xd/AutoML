import logging
from typing import Optional

import mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from zenml import step, Model
from utils.db import Database
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Define model metadata
model = Model(
    name="AutoML",
    version=None,
    license="Apache 2.0",
    description="Price prediction model for houses.",
)


def update_run_with_mlflow_metadata(run_id: str, run_info: mlflow.entities.RunInfo, tracking_uri: str) -> None:
    """
    Update the pipeline run document in the database with MLflow metadata.

    Args:
        run_id (str): The ID of the pipeline run in the database.
        run_info (mlflow.entities.RunInfo): The MLflow run information.
        tracking_uri (str): MLflow tracking URI.
    """
    try:
        run_data = mlflow.get_run(run_info.run_id).data
        metrics = run_data.metrics
        params = run_data.params

        update_payload = {
            "mlflow_run_id": run_info.run_id,
            "mlflow_experiment_id": run_info.experiment_id,
            "mlflow_tracking_uri": tracking_uri,
            "mlflow_metrics": metrics,
            "mlflow_params": params,
            # "mlflow_artifacts": [f.path for f in mlflow.list_artifacts(run_info.run_id)]
        }

        result = Database.get_collection("pipeline_runs").update_one(
            {"_id": run_id},
            {"$set": update_payload}
        )

        if result.modified_count:
            logger.info(f"Successfully updated MLflow metadata for run_id: {run_id}")
        else:
            logger.warning(f"No changes made to DB for run_id: {run_id}")
    except Exception as e:
        logger.error(f"Failed to update DB with MLflow metadata: {e}")
        raise


@step(enable_cache=False, model=model)
def model_building_step(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    mlflow_tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
    run_id: Optional[str] = None
) -> Pipeline:
    """
    Builds and trains a Linear Regression model using a scikit-learn pipeline,
    and logs training run details to MLflow.

    Args:
        X_train (pd.DataFrame): Training feature set.
        y_train (pd.Series): Training labels.
        mlflow_tracking_uri (Optional[str]): MLflow tracking URI.
        experiment_name (Optional[str]): MLflow experiment name.
        run_id (Optional[str]): ID of the pipeline run in the database.

    Returns:
        Pipeline: Trained scikit-learn pipeline.
    """
    if not isinstance(X_train, pd.DataFrame):
        raise TypeError("X_train must be a pandas DataFrame.")
    if not isinstance(y_train, pd.Series):
        raise TypeError("y_train must be a pandas Series.")

    # Define preprocessing steps
    categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns
    numerical_cols = X_train.select_dtypes(exclude=["object", "category"]).columns

    logger.info(f"Categorical columns: {categorical_cols.tolist()}")
    logger.info(f"Numerical columns: {numerical_cols.tolist()}")

    numerical_transformer = SimpleImputer(strategy="mean")
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numerical_transformer, numerical_cols),
        ("cat", categorical_transformer, categorical_cols),
    ])

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", LinearRegression())
    ])

    # Setup MLflow tracking
    if mlflow_tracking_uri:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
    if experiment_name:
        mlflow.set_experiment(experiment_name)

    mlflow.sklearn.autolog()

    try:
        if mlflow.active_run():
            mlflow.end_run()

        with mlflow.start_run() as run:
            logger.info("Training Linear Regression model...")
            pipeline.fit(X_train, y_train)
            logger.info("Model training completed.")

            # Update DB with MLflow metadata
            if run_id:
                update_run_with_mlflow_metadata(
                    run_id=run_id,
                    run_info=run.info,
                    tracking_uri=mlflow.get_tracking_uri()
                )

            logger.info(f"MLflow run ID: {run.info.run_id}")
            logger.info(f"MLflow experiment ID: {run.info.experiment_id}")

    except Exception as e:
        logger.exception("Exception occurred during model training")
        raise

    logger.info("Model building step completed successfully.")
    return pipeline
