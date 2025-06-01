# controllers/plot_controller.py

from flask import Blueprint, request, jsonify
from utils.db import Database
from bson import ObjectId
from datetime import datetime

plot_blueprint = Blueprint("plot", __name__)
plots_collection = Database.get_collection("saved_plots")

@plot_blueprint.route("/save_plot", methods=["POST"])
def save_plot():
    data = request.get_json()
    required_fields = ["user_id", "dataset_id", "plot_type", "plot_json"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    plot_data = {
        "user_id": ObjectId(data["user_id"]),
        "dataset_id": ObjectId(data["dataset_id"]),
        "plot_type": data["plot_type"],
        "columns": data.get("columns", []),
        "title": data.get("title", ""),
        "plot_json": data["plot_json"],
        "created_at": datetime.utcnow()
    }

    inserted = plots_collection.insert_one(plot_data)
    return jsonify({"message": "Plot saved", "plot_id": str(inserted.inserted_id)}), 201


@plot_blueprint.route("/get_plots/<user_id>", methods=["GET"])
def get_user_plots(user_id):
    plots = list(plots_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
    for plot in plots:
        plot["_id"] = str(plot["_id"])
        plot["user_id"] = str(plot["user_id"])
        plot["dataset_id"] = str(plot["dataset_id"])
    return jsonify(plots)


@plot_blueprint.route("/delete_plot/<plot_id>", methods=["DELETE"])
def delete_plot(plot_id):
    result = plots_collection.delete_one({"_id": ObjectId(plot_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Plot deleted"}), 200
    return jsonify({"error": "Plot not found"}), 404
