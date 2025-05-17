from flask import Blueprint, request, jsonify
from controllers.pipeline_controller import PipelineController  # Class import
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

        # Run the pipeline using the class method
        response = PipelineController.run_pipeline(user_id, dataset_id, params)
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# @pipeline_bp.route("/run_pipeline/data/<pipeline_id>", methods=["GET"])
# def get_pipeline_data(pipeline_id):
#     try:
#         # Load pipeline metadata from MongoDB
#         pipeline_metadata = Database.get_collection("pipeline_runs").find_one({"pipeline_id": pipeline_id})
#         if not pipeline_metadata:
#             return jsonify({"status": "error", "message": "Pipeline metadata not found"}), 404
#         pipeline_metadata["_id"] = str(pipeline_metadata["_id"])
#         return jsonify({"status": "success", "data": pipeline_metadata}), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
