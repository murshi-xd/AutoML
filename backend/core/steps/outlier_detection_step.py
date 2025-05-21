import logging

import pandas as pd
from src.outlier_detection import OutlierDetector, ZScoreOutlierDetection, IQROutlierDetection
from zenml import step


@step
def outlier_detection_step(
    df: pd.DataFrame,
    column_name: str,
    strategy: str = "zscore",   # "zscore" or "iqr"
    method: str = "remove",     # "remove" or "cap"
    threshold: float = 3.0      # Only used for zscore
) -> pd.DataFrame:
    """Detects and handles outliers using the specified strategy, method, and threshold."""
    logging.info(f"Starting outlier detection step with DataFrame of shape: {df.shape}")

    if df is None:
        logging.error("Received a NoneType DataFrame.")
        raise ValueError("Input df must be a non-null pandas DataFrame.")

    if not isinstance(df, pd.DataFrame):
        logging.error(f"Expected pandas DataFrame, got {type(df)} instead.")
        raise ValueError("Input df must be a pandas DataFrame.")

    if column_name not in df.columns:
        logging.error(f"Column '{column_name}' does not exist in the DataFrame.")
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame.")

    df_numeric = df.select_dtypes(include=[int, float])

    # Select strategy
    if strategy == "zscore":
        detector_strategy = ZScoreOutlierDetection(threshold=threshold)
    elif strategy == "iqr":
        detector_strategy = IQROutlierDetection()
    else:
        logging.error(f"Unknown strategy '{strategy}'.")
        raise ValueError(f"Unknown strategy '{strategy}'.")

    outlier_detector = OutlierDetector(detector_strategy)
    df_cleaned = outlier_detector.handle_outliers(df_numeric, method=method)
    return df_cleaned