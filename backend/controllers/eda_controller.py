# controllers/eda_controller.py

from flask import jsonify, send_file
import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from utils.db import Database
from bson import ObjectId

# generate_eda_visual(dataset_id, plot_type, column="", column2="", download_format="png", top_n=10):

def generate_eda_visual(dataset_id, plot_type, column="", column2="", download_format="png", top_n=10):
    try:
        # Fetch dataset details from MongoDB
        datasets_collection = Database.get_collection("datasets")
        dataset = datasets_collection.find_one({
            "$or": [
                {"dataset_id": dataset_id},
                {"_id": ObjectId(dataset_id)}
            ]
        })

        if not dataset:
            return jsonify({"error": f"Dataset with ID '{dataset_id}' not found"}), 404
        
        # Use the processed file path
        processed_file_path = dataset.get("processed_file_path")
        if not processed_file_path or not os.path.exists(processed_file_path):
            return jsonify({"error": f"Processed file for dataset '{dataset_id}' not found"}), 404

        # Read the data
        df = pd.read_csv(processed_file_path)

        # Set style
        sns.set_theme(style="whitegrid", palette="Blues")
        plt.figure(figsize=(12, 8) if plot_type == "heatmap" else (10, 6))

        # Plot types
        if plot_type == "histogram":
            if column not in df.columns:
                return jsonify({"error": f"'{column}' not found in dataset."}), 400
            sns.histplot(df[column], kde=True, color="steelblue", edgecolor="black")
            plt.title(f"Histogram of '{column}'", fontsize=14)
            plt.xlabel(column)
            plt.ylabel("Frequency")

        elif plot_type == "boxplot":
            if column not in df.columns:
                return jsonify({"error": f"'{column}' not found in dataset."}), 400
            sns.boxplot(x=df[column], color="skyblue")
            plt.title(f"Boxplot of '{column}'", fontsize=14)
            plt.xlabel(column)

        elif plot_type == "heatmap":
            corr = df.corr(numeric_only=True)
            sns.heatmap(corr, cmap="Blues", annot=True, fmt=".2f", square=True,
                        linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title("Correlation Heatmap", fontsize=16)

        elif plot_type == "missing":
            na_counts = df.isna().sum()
            na_counts = na_counts[na_counts > 0].sort_values(ascending=False)
            sns.barplot(x=na_counts.values, y=na_counts.index, color="cornflowerblue", edgecolor="black")
            plt.title("Missing Values Per Column", fontsize=14)
            plt.xlabel("Missing Count")
            plt.ylabel("Columns")

        elif plot_type == "correlation_top_n":
            corr = df.corr(numeric_only=True)
            if column not in corr.columns:
                return jsonify({"error": f"'{column}' not found in numeric columns for correlation."}), 400
            top_corr = corr[column].abs().sort_values(ascending=False)[1:top_n + 1]
            sns.barplot(x=top_corr.values, y=top_corr.index, color="steelblue")
            plt.title(f"Top {top_n} Correlations with '{column}'", fontsize=14)
            plt.xlabel("Correlation")
            plt.ylabel("Features")

        elif plot_type == "category_distribution":
            if column not in df.columns:
                return jsonify({"error": f"'{column}' not found in dataset."}), 400
            value_counts = df[column].value_counts().sort_values(ascending=False)
            sns.barplot(x=value_counts.values, y=value_counts.index, color="cornflowerblue", edgecolor="black")
            plt.title(f"Category Distribution: '{column}'", fontsize=14)
            plt.xlabel("Count")
            plt.ylabel("Category")

        elif plot_type == "pairplot":
            sns.pairplot(df.select_dtypes(include=["number"]))
            plt.title("Pairplot of Numerical Features", fontsize=16)

        elif plot_type == "scatter":
            if column not in df.columns or column2 not in df.columns:
                return jsonify({"error": f"Both '{column}' and '{column2}' must be valid columns."}), 400
            sns.scatterplot(x=df[column], y=df[column2], color="steelblue")
            plt.title(f"Scatter Plot of '{column}' vs '{column2}'", fontsize=14)
            plt.xlabel(column)
            plt.ylabel(column2)

        elif plot_type == "violin":
            if column not in df.columns:
                return jsonify({"error": f"'{column}' not found in dataset."}), 400
            sns.violinplot(x=df[column], color="skyblue")
            plt.title(f"Violin Plot of '{column}'", fontsize=14)

        elif plot_type == "jointplot":
            if column not in df.columns or column2 not in df.columns:
                return jsonify({"error": f"Both '{column}' and '{column2}' must be valid columns."}), 400
            sns.jointplot(x=column, y=column2, data=df, kind="scatter", color="blue", height=8)
            plt.title(f"Jointplot of '{column}' vs '{column2}'", fontsize=16)

        else:
            return jsonify({"error": f"Unsupported plot type: '{plot_type}'"}), 400

        # Finalize and return plot
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format=download_format)
        buf.seek(0)
        plt.close()

        mimetype = "application/pdf" if download_format == "pdf" else "image/png"
        return send_file(buf, mimetype=mimetype, as_attachment=True,
                         download_name=f"{dataset_id}_{plot_type}.{download_format}")

    except Exception as e:
        return jsonify({"error in eda controller": str(e)}), 500