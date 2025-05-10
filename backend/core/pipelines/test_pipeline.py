from core.steps.data_splitter_step import data_splitter_step
from core.steps.feature_engineering_step import feature_engineering_step
from core.steps.handle_missing_values_step import handle_missing_values_step
from core.steps.model_building_step import model_building_step
from core.steps.model_evaluator_step import model_evaluator_step
from core.steps.outlier_detection_step import outlier_detection_step

import logging
import os
import pandas as pd
from core.pipelines.training_pipeline import ml_pipeline

# Configure logging for standalone testing
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    # Test the pipeline
    test_file_path = "uploads/AmesHousing.csv"
    target_column = "SalePrice"

    run = ml_pipeline(
        file_path="uploads/AmesHousing.csv",
        feature_strategy="retain",
        target_column=target_column,
        model_type="RandomForestRegressor",
        model_params={"n_estimators": 100, "max_depth": 10},
        scaler_type="StandardScaler",
        feature_selector_type="SelectKBest",
        feature_selector_params={"k": 10},
        use_grid_search=True,
        grid_search_params={
            "n_estimators": [50, 100, 150],
            "max_depth": [5, 10, 15]
        },
        custom_metrics=["r2_score", "mean_squared_error", "mean_absolute_error"],
        use_cross_validation=True,
        cv_folds=5
    )

    print("✅ Pipeline test run completed successfully.")
