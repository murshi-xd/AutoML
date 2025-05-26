# routes/eda_routes.py

from flask import Blueprint, request, jsonify, session
from controllers.eda_controller import generate_eda_visual

eda_bp = Blueprint("eda_bp", __name__)

@eda_bp.route("/eda_visual", methods=["POST"])
def eda_visual():
    try:
        data = request.json
        dataset_id = data.get("dataset_id")
        plot_type = data.get("plot_type")
        column = data.get("column", "")
        column2 = data.get("column2", "")
        download_format = str(data.get("format", "png")).lower()
        top_n = int(data.get("top_n", 10))

        if not dataset_id:
            return jsonify({"error": "Missing 'dataset_id'"}), 400
        if not plot_type:
            return jsonify({"error": "Missing 'plot_type'"}), 400
        if plot_type in ["histogram", "boxplot", "category_distribution", "violin"] and not column:
            return jsonify({"error": f"'column' is required for plot_type '{plot_type}'"}), 400

        # ✅ Ensure user is logged in
        user = session.get("user")
        if not user:
            return jsonify({"error": "Not authenticated"}), 401
        current_user_id = user.get("_id")

        return generate_eda_visual(
            dataset_id, plot_type, column, column2, download_format, top_n, current_user_id
        )

    except Exception as e:
        print(f"❌ Error in eda_visual route: {e}")
        return jsonify({"error": str(e)}), 500
