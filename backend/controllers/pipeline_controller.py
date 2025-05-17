from controllers.dataset_controller import DatasetController
from core.pipelines.training_pipeline import ml_pipeline
import os
import json
from flask import jsonify
import logging

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

            # Run the pipeline
            pipeline_result = ml_pipeline(
                file_path=file_path,
                feature_strategy=params.get("feature_strategy"),
                feature_columns=params.get("feature_columns"),
                outlier_column=params.get("outlier_column"),
                target_column=params.get("target_column"),
                user_id=user_id,
                dataset_id=dataset_id
            )

            logger.info(f"Pipeline run completed with run_id: {pipeline_result['_id']}")

            # Prepare the response
            response = {
                "message": "Pipeline executed successfully.",
                "status": "success",
                "run_id": pipeline_result['_id'],
                "metrics": pipeline_result.get("metrics", {}),
                "mse": pipeline_result.get("mse", None),
                "start_time": pipeline_result.get("start_time", None),
                "end_time": pipeline_result.get("end_time", None),
                "status": pipeline_result.get("status", "unknown")
            }

            return jsonify(response), 200

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            return jsonify({"message": f"Failed to run pipeline: {str(e)}", "status": "error"}), 500
