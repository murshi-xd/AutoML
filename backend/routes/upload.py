# backend/routes/upload.py

from flask import Blueprint, request, jsonify
import os
import pandas as pd

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Attempt to read it as a CSV
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 500

    # Basic EDA
    eda = {
        "filename": file.filename,
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "summary": df.describe(include='all').fillna("").to_dict(),
        "head": df.head(5).fillna("").to_dict(orient="records")
    }

    return jsonify({"message": "File uploaded and analyzed", "eda": eda, "path": filepath}), 200
