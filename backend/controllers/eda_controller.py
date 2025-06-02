# controllers/eda_controller.py

from flask import jsonify, request, session, Response
from datetime import datetime
from bson import ObjectId
import os
import pandas as pd
import plotly.express as px
import plotly
from flask import jsonify, request, session
from datetime import datetime
from bson import ObjectId, json_util
import json

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
                if column not in df:
                    return jsonify({"error": f"Column '{column}' not found"}), 400
                fig = px.histogram(df, x=column)

            elif plot_type == "boxplot":
                if column not in df:
                    return jsonify({"error": f"Column '{column}' not found"}), 400
                fig = px.box(df, y=column)

            elif plot_type == "heatmap":
                numeric_df = df.select_dtypes(include="number")
                if numeric_df.shape[1] < 2:
                    return jsonify({"error": "Not enough numeric columns for heatmap"}), 400
                fig = px.imshow(numeric_df.corr())

            elif plot_type == "missing":
                na_series = df.isnull().sum()
                na_series = na_series[na_series > 0]

                if na_series.empty:
                    return jsonify({"error": "No missing values found in dataset"}), 400

                # Sort missing values descending
                na_series = na_series.sort_values(ascending=True)

                x_vals = [int(v) for v in na_series.values]
                y_labels = [str(k) for k in na_series.index]

                fig = px.bar(
                    x=x_vals,
                    y=y_labels,
                    orientation='h',
                    labels={"x": "Missing Count", "y": "Feature"},
                    title="Missing Values"
                )

            elif plot_type == "scatter":
                if column not in df or column2 not in df:
                    return jsonify({"error": "Both columns must be selected"}), 400
                fig = px.scatter(df, x=column, y=column2)

            elif plot_type == "correlation_top_n":
                corr = df.corr(numeric_only=True)
                if column not in corr.columns:
                    return jsonify({"error": f"{column} not found in correlation matrix"}), 400
                top_corr = corr[column].drop(column).abs().sort_values(ascending=False).head(top_n)
                fig = px.bar(
                    x=top_corr.values,
                    y=top_corr.index,
                    orientation='h',
                    labels={"x": "Correlation", "y": "Feature"}
                )

            elif plot_type == "category_distribution":
                if column not in df:
                    return jsonify({"error": f"Column '{column}' not found"}), 400
                fig = px.histogram(df, x=column, color=column)

            elif plot_type == "violin":
                if column not in df:
                    return jsonify({"error": f"Column '{column}' not found"}), 400
                fig = px.violin(df, y=column, box=True, points="all")

            elif plot_type == "pairplot":
                num_cols = df.select_dtypes(include="number").columns.tolist()
                if len(num_cols) < 2:
                    return jsonify({"error": "Not enough numeric columns for pairplot"}), 400
                fig = px.scatter_matrix(df, dimensions=num_cols[:5])

            elif plot_type == "jointplot":
                if column not in df or column2 not in df:
                    return jsonify({"error": "Both columns must be selected for jointplot"}), 400
                fig = px.density_contour(df, x=column, y=column2)

            else:
                return jsonify({"error": f"Unsupported plot type: {plot_type}"}), 400

            fig.update_layout(title=f"{plot_type.replace('_', ' ').title()} Plot")
            return Response(
                plotly.utils.PlotlyJSONEncoder().encode(fig.to_plotly_json()),
                mimetype='application/json'
            ), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Plot generation failed: {str(e)}"}), 500

    def save_plot(self):
        data = request.get_json()
        session_user = session.get("user")
        user_id = session_user.get("_id") if session_user else None

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        required_fields = ["dataset_id", "plot_type", "plot_json"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            plot_json = json.loads(json_util.dumps(data["plot_json"]))
        except Exception as e:
            return jsonify({"error": f"Failed to sanitize plot JSON: {str(e)}"}), 500

        plot_data = {
            "user_id": ObjectId(user_id),
            "dataset_id": ObjectId(data["dataset_id"]),
            "plot_type": data["plot_type"],
            "columns": data.get("columns", []),
            "title": data.get("title", ""),
            "plot_json": plot_json,
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
