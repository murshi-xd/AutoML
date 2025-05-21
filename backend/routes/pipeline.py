from flask import Blueprint, request, jsonify
from controllers.pipeline_controller import PipelineController
from utils.db import Database
import logging

pipeline_bp = Blueprint("pipeline", __name__)

@pipeline_bp.route("/run_pipeline", methods=["POST"])
def run_pipeline_route():
    logging.info("Received request to run pipeline")

    try:
        # Extract parameters from request
        data = request.get_json()
        dataset_id = data.get("dataset_id")
        user_id = data.get("user_id")
        params = data.get("params", {})

        # Set defaults if not provided
        params.setdefault("outlier_strategy", "iqr")
        params.setdefault("outlier_method", "remove")
        params.setdefault("outlier_threshold", 3.0)

        # Run the pipeline using the class method
        response = PipelineController.run_pipeline(user_id, dataset_id, params)
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@pipeline_bp.route('/list_experiments/<string:user_id>', methods=['GET'])
def list_experiments_route(user_id):
    return PipelineController.list_experiments(user_id)

@pipeline_bp.route('/list_runs/<string:experiment_id>', methods=['GET'])
def list_runs_route(experiment_id):
    return PipelineController.list_runs(experiment_id)

@pipeline_bp.route('/experiment_info/<string:run_id>', methods=['GET'])
def experiment_info_route(run_id):
    return PipelineController.get_experiment_info(run_id)



# @pipeline_bp.route('/delete_experiment/<string:experiment_id>', methods=['DELETE'])
# def delete_experiment_route(experiment_id):
#     return PipelineController.delete_experiment(experiment_id)
# @pipeline_bp.route('/delete_run/<string:run_id>', methods=['DELETE'])
# def delete_run_route(run_id):
#     return PipelineController.delete_run(run_id)