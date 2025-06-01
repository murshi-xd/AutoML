# controllers/eda_controller.py

from flask import jsonify, request, session
from datetime import datetime
from bson import ObjectId
import os
import pandas as pd
import plotly.express as px

from utils.db import Database


class EDAController:
    def __init__(self):
        self.datasets_collection = Database.get_collection("datasets")
        self.plots_collection = Database.get_collection("saved_plots")

    def _get_dataset_df(self, dataset_id, user_id=None):
        query = {"$or": [{"dataset_id": dataset_id}, {"_id": ObjectId(dataset_id)}]}
        if user_id:
            query["user_id"] = user_id

        dataset = self.datasets_collection.find_one(query)
        if not dataset:
            return None, "Dataset not found or access denied"

        file_path = dataset.get("processed_file_path")
        if not file_path or not os.path.exists(file_path):
            return None, f"Processed file not found: {file_path}"

        try:
            df = pd.read_csv(file_path)
            return df, None
        except Exception as e:
            return None, f"Failed to load dataset CSV: {str(e)}"

    def generate_plot(self):
        data = request.get_json()
        session_user = session.get("user")
        user_id = session_user.get("_id") if session_user else None

        dataset_id = data.get("dataset_id")
        plot_type = data.get("plot_type")
        column = data.get("column", "")
        column2 = data.get("column2", "")
        top_n = data.get("top_n", 10)

        if not dataset_id or not plot_type:
            return jsonify({"error": "Missing dataset_id or plot_type"}), 400

        df, err = self._get_dataset_df(dataset_id, user_id)
        if err:
            return jsonify({"error": err}), 404

        try:
            fig = None

            if plot_type == "histogram":
                fig = px.histogram(df, x=column)
            elif plot_type == "boxplot":
                fig = px.box(df, y=column)
            elif plot_type == "heatmap":
                fig = px.imshow(df.corr(numeric_only=True))
            elif plot_type == "missing":
                na_series = df.isnull().sum()
                na_series = na_series[na_series > 0]
                fig = px.bar(
                    x=na_series.values, 
                    y=na_series.index, 
                    orientation='h',
                    labels={"x": "Missing Count", "y": "Feature"}
                )
            elif plot_type == "scatter":
                fig = px.scatter(df, x=column, y=column2)
            elif plot_type == "correlation_top_n":
                corr = df.corr(numeric_only=True)
                if column not in corr:
                    return jsonify({"error": f"{column} not found in correlation matrix"}), 400
                top_corr = corr[column].abs().sort_values(ascending=False)[1:top_n + 1]
                fig = px.bar(
                    x=top_corr.values, 
                    y=top_corr.index, 
                    orientation='h',
                    labels={"x": "Correlation", "y": "Feature"}
                )
            elif plot_type == "category_distribution":
                fig = px.histogram(df, x=column)
            elif plot_type == "violin":
                fig = px.violin(df, y=column)
            else:
                return jsonify({"error": f"Unsupported plot type: {plot_type}"}), 400

            fig.update_layout(title=f"{plot_type.replace('_', ' ').title()} Plot")
            return jsonify(fig.to_plotly_json()), 200

        except Exception as e:
            return jsonify({"error": f"Plot generation failed: {str(e)}"}), 500

    def save_plot(self):
        data = request.get_json()
        session_user = session.get("user")
        user_id = session_user.get("_id") if session_user else None

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        required_fields = ["dataset_id", "plot_type", "plot_json"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        plot_data = {
            "user_id": ObjectId(user_id),
            "dataset_id": ObjectId(data["dataset_id"]),
            "plot_type": data["plot_type"],
            "columns": data.get("columns", []),
            "title": data.get("title", ""),
            "plot_json": data["plot_json"],
            "created_at": datetime.utcnow()
        }

        try:
            result = self.plots_collection.insert_one(plot_data)
            return jsonify({"message": "Plot saved", "plot_id": str(result.inserted_id)}), 201
        except Exception as e:
            return jsonify({"error": f"Failed to save plot: {str(e)}"}), 500

    def get_plots(self, user_id):
        try:
            plots = list(self.plots_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))
            for plot in plots:
                plot["_id"] = str(plot["_id"])
                plot["user_id"] = str(plot["user_id"])
                plot["dataset_id"] = str(plot["dataset_id"])
            return jsonify(plots), 200
        except Exception as e:
            return jsonify({"error": f"Failed to fetch plots: {str(e)}"}), 500

    def delete_plot(self, plot_id):
        try:
            result = self.plots_collection.delete_one({"_id": ObjectId(plot_id)})
            if result.deleted_count == 1:
                return jsonify({"message": "Plot deleted"}), 200
            else:
                return jsonify({"error": "Plot not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Deletion failed: {str(e)}"}), 500
