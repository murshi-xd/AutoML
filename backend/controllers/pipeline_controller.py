from controllers.dataset_controller import DatasetController
from core.pipelines.training_pipeline import ml_pipeline
from utils.db import Database

from zenml.integrations.mlflow.mlflow_utils import get_tracking_uri
import os
import json
from flask import jsonify
import logging
import mlflow
import uuid




UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class PipelineController:

    @staticmethod
    def run_pipeline(user_id, dataset_id, params):
        try:
            # Fetch all datasets
            all_datasets = DatasetController.list_datasets()

            # Find the specific dataset by ID
            dataset = next((d for d in all_datasets if d["_id"] == dataset_id), None)

            # Validate the dataset
            if not dataset or 'processed_file_path' not in dataset:
                return jsonify({"message": "Dataset not found or invalid", "status": "error"}), 404
            
            # Use the processed file path
            file_path = dataset['processed_file_path']
            
            # Set up logging
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)

            logger.info(f"User {user_id} is running pipeline on dataset {dataset_id} with params: {params}")
            logger.info(f"Using processed file path: {file_path}")

            run_id=str(uuid.uuid4())

            # Run the pipeline
            pipeline_run = ml_pipeline(
                file_path=file_path,
                feature_strategy=params.get("feature_strategy"),
                missing_value_feature_strategy=params.get("missing_value_feature_strategy"),
                feature_columns=params.get("feature_columns"),
                outlier_column=params.get("outlier_column"),
                outlier_strategy=params.get("outlier_strategy"),
                outlier_method=params.get("outlier_method"),
                outlier_threshold=params.get("outlier_threshold"),
                target_column=params.get("target_column"),
                user_id=user_id,
                dataset_id=dataset_id,
                run_id=run_id
            )



            # Log pipeline details
            logger.info(f"Pipeline run completed with run_id: {run_id}")
            logger.info(f"Pipeline status: {pipeline_run.status}")

            # Return the response
            return jsonify({
                "message": "Pipeline executed successfully.",
                "run_id": run_id,
                "status": pipeline_run.status
            }), 200

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return jsonify({"message": f"Failed to run pipeline: {str(e)}", "status": "error"}), 500


    @staticmethod
    def list_experiments(user_id):
        pipeline_runs = Database.get_collection("pipeline_runs")
        runs = list(pipeline_runs.find({"user_id": user_id}))

        experiments = {}
        for run in runs:
            exp_id = run.get("mlflow_experiment_id")
            dataset_id = run.get("dataset_id")
            if exp_id not in experiments:
                dataset_info = DatasetController.get_dataset_details(dataset_id)
                custom_name = dataset_info.get("custom_name") if dataset_info else "Unknown"
                experiments[exp_id] = {
                    "mlflow_experiment_id": exp_id,
                    "dataset_custom_name": custom_name
                }

        return jsonify(list(experiments.values())), 200

    @staticmethod
    def list_runs(experiment_id):
        pipeline_runs = Database.get_collection("pipeline_runs")

        # Fetch all runs for the given experiment ID
        runs = list(pipeline_runs.find(
            {"mlflow_experiment_id": experiment_id},
            {"mlflow_run_id": 1, "status": 1, "_id": 0}
        ))
        return jsonify(runs), 200

    @staticmethod
    def get_experiment_info(run_id):
        pipeline_runs =  Database.get_collection("pipeline_runs")

        # Fetch the run details using the run_id
        run = pipeline_runs.find_one({"mlflow_run_id": run_id})

        if not run:
            return jsonify({"error": "Run not found"}), 404

        info = {
            "mlflow_run_id": run.get("mlflow_run_id"),
            "start_time": run.get("start_time"),
            "end_time": run.get("end_time"),
            "metrics": run.get("mlflow_metrics"),
            "params": run.get("params"),
            "status": run.get("status")
        }
        return jsonify(info), 200
