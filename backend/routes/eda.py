# backend/routes/eda.py
from flask import Blueprint, request, jsonify, send_file
import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")  # Use 'Agg' backend for non-GUI environments
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Initialize the blueprint
eda_bp = Blueprint("eda_bp", __name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

@eda_bp.route("/eda_visual", methods=["POST"])
def eda_visual():
    try:
        data = request.json
        file_name = data.get("filename")
        plot_type = data.get("plot_type")
        column = data.get("column", "")
        download_format = data.get("format", "png").lower()
        top_n = int(data.get("top_n", 10))  # for correlation_top_n

        # Validate inputs
        if not file_name:
            return jsonify({"error": "Missing 'filename'"}), 400
        if not plot_type:
            return jsonify({"error": "Missing 'plot_type'"}), 400
        if plot_type in ["histogram", "boxplot", "category_distribution"] and not column:
            return jsonify({"error": f"'column' is required for plot_type '{plot_type}'"}), 400

        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Read data
        df = pd.read_csv(file_path)

        # Set style
        sns.set_theme(style="whitegrid", palette="Blues")

        # Start plot
        plt.figure(figsize=(12, 8) if plot_type == "heatmap" else (10, 6))

        # Plot types
        if plot_type == "histogram":
            missing_count = df[column].isna().sum()
            sns.histplot(df[column], kde=True, color="steelblue", edgecolor="black")
            plt.title(f"Histogram of '{column}' (Missing: {missing_count})", fontsize=14)
            plt.xlabel(column)
            plt.ylabel("Frequency")

        elif plot_type == "boxplot":
            missing_count = df[column].isna().sum()
            sns.boxplot(x=df[column], color="skyblue")
            plt.title(f"Boxplot of '{column}' (Missing: {missing_count})", fontsize=14)
            plt.xlabel(column)
            plt.ylabel("Value")

        elif plot_type == "heatmap":
            corr = df.corr(numeric_only=True)
            sns.heatmap(corr, cmap="Blues", annot=True, fmt=".2f", square=True,
                        linewidths=0.5, cbar_kws={"shrink": 0.8})
            plt.title("Correlation Heatmap", fontsize=16)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)

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
                         download_name=f"{file_name}_{plot_type}.{download_format}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
