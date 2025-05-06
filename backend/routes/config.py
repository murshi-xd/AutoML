# backend/routes/config.py
from flask import Blueprint, jsonify

config_bp = Blueprint("config_bp", __name__)

@config_bp.route("/preprocessing_options", methods=["GET"])
def preprocessing_options():
    options = {
        "missing_value_strategies": ["mean", "median", "mode"],
        "feature_engineering_strategies": ["log", "normalize", "standardize"],
        "outlier_detection_methods": ["zscore", "iqr"],
        "data_split_strategies": ["train_test_split", "k_fold"]
    }
    return jsonify(options), 200
