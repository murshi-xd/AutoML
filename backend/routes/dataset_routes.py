from flask import Blueprint, request, jsonify
from controllers.dataset_controller import DatasetController

dataset_bp = Blueprint("dataset_bp", __name__)

# List all datasets
@dataset_bp.route("/datasets", methods=["GET"])
def list_datasets():
    try:
        datasets = DatasetController.list_datasets()
        return jsonify({"datasets": datasets}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get details of a single dataset
@dataset_bp.route("/datasets/<dataset_id>", methods=["GET"])
def get_dataset_details(dataset_id):
    try:
        dataset = DatasetController.get_dataset_details(dataset_id)
        if not dataset:
            return jsonify({"error": "Dataset not found"}), 404
        return jsonify({"dataset": dataset}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a dataset
@dataset_bp.route("/datasets/<dataset_id>", methods=["DELETE"])
def delete_dataset(dataset_id):
    try:
        deleted = DatasetController.delete_dataset(dataset_id)
        if not deleted:
            return jsonify({"error": "Dataset not found"}), 404
        return jsonify({"message": "Dataset deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
