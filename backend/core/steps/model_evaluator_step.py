import logging
from typing import Tuple, Optional

import pandas as pd
from sklearn.pipeline import Pipeline
from src.model_evaluator import ModelEvaluator, RegressionModelEvaluationStrategy
from zenml import step
from utils.db import Database
from bson import ObjectId

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
)
logger = logging.getLogger(__name__)


def update_run_metrics(run_id: str, new_metrics: dict) -> None:
    """
    Updates the mlflow_metrics field in the pipeline_runs collection
    with new evaluation metrics while preserving existing ones.

    Parameters:
    run_id (str): The ID of the pipeline run document.
    new_metrics (dict): The new metrics to add.
    """
    if not run_id:
        logger.warning("No run_id provided. Skipping database update.")
        return

    collection = Database.get_collection("pipeline_runs")

    run = collection.find_one({"_id": run_id})
    if not run:
        logger.error(f"No pipeline run found with _id: {run_id}")
        return

    existing_metrics = run.get("mlflow_metrics", {})
    updated_metrics = {**existing_metrics, **new_metrics}

    result = collection.update_one(
        {"_id": run_id},
        {"$set": {"mlflow_metrics": updated_metrics}}
    )

    if result.modified_count == 1:
        logger.info(f"Successfully updated mlflow_metrics for run_id: {run_id}")
    else:
        logger.warning(f"No changes made to mlflow_metrics for run_id: {run_id}")


@step(enable_cache=False)
def model_evaluator_step(
    trained_model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    run_id: Optional[str] = None
) -> Tuple[dict, float]:
    """
    Evaluates the trained model using ModelEvaluator and RegressionModelEvaluationStrategy.

    Parameters:
    trained_model (Pipeline): The trained pipeline containing the model and preprocessing steps.
    X_test (pd.DataFrame): The test data features.
    y_test (pd.Series): The test data labels/target.
    run_id (Optional[str]): The ID of the pipeline run in the database.

    Returns:
    Tuple[dict, float]: A dictionary of evaluation metrics and the Mean Squared Error.
    """
    if not isinstance(X_test, pd.DataFrame):
        raise TypeError("X_test must be a pandas DataFrame.")
    if not isinstance(y_test, pd.Series):
        raise TypeError("y_test must be a pandas Series.")

    logger.info("Applying the same preprocessing to the test data.")
    X_test_processed = trained_model.named_steps["preprocessor"].transform(X_test)

    evaluator = ModelEvaluator(strategy=RegressionModelEvaluationStrategy())
    evaluation_metrics = evaluator.evaluate(
        trained_model.named_steps["model"], X_test_processed, y_test
    )

    if not isinstance(evaluation_metrics, dict):
        raise ValueError("Evaluation metrics must be returned as a dictionary.")

    test_mse_value = evaluation_metrics.get("Mean Squared Error")
    test_r2_value = evaluation_metrics.get("R-Squared")

    logger.info(f"Test MSE: {test_mse_value}")
    logger.info(f"Test R²: {test_r2_value}")

    # Update the database with the new metrics
    new_metrics = {
        "test_mse": test_mse_value,
        "test_r2": test_r2_value
    }
    update_run_metrics(run_id, new_metrics)

    return evaluation_metrics, test_mse_value
