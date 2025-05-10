# backend/routes/upload.py

from flask import Blueprint, request, jsonify
import os
import pandas as pd
import uuid
from datetime import datetime
from core.src.ingest_data import DataIngestorFactory
from utils.db import Database
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

# Set the upload folder relative to the backend directory
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "backend", "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = [".zip", ".csv"]

def is_allowed_file(filename):
    """Check if the uploaded file has a supported extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext[1:] for ext in ALLOWED_EXTENSIONS]


def save_file(file, user_id):
    """Save the uploaded file to the user directory."""
    try:
        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()

        # Validate file extension
        if not is_allowed_file(filename):
            raise ValueError("Only ZIP and CSV files are allowed")

        # Create user directory if it doesn't exist
        user_dir = os.path.join(UPLOAD_FOLDER, user_id)
        os.makedirs(user_dir, exist_ok=True)

        # Save the file
        save_path = os.path.join(user_dir, f"{file_id}_{filename}")
        file.save(save_path)
        print(f"✅ File saved at: {save_path}")

        return file_id, filename, save_path, file_extension

    except Exception as e:
        print(f"❌ Failed to save file: {str(e)}")
        raise e


def generate_eda(file_id, user_id, filename, file_path, df):
    """Generate basic EDA for the uploaded file."""
    try:
        eda = {
            "file_id": file_id,
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary": df.describe(include='all').fillna("").to_dict(),
            "head": df.head(5).fillna("").to_dict(orient="records"),
            "uploaded_at": datetime.utcnow().isoformat()
        }
        print(f"✅ EDA generated successfully for file: {filename}")
        return eda

    except Exception as e:
        print(f"❌ Failed to create EDA: {str(e)}")
        raise e


def store_metadata(file_id, user_id, filename, file_path):
    """Store file metadata in MongoDB."""
    try:
        files_collection = Database.get_collection("files")
        files_collection.insert_one({
            "file_id": file_id,
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path,
            "status": "processed",
            "uploaded_at": datetime.utcnow().isoformat()
        })
        print(f"✅ File metadata stored in MongoDB for file: {filename}")

    except Exception as e:
        print(f"❌ Failed to store file metadata: {str(e)}")
        raise e


def store_eda(file_id, user_id, eda):
    """Store EDA results in MongoDB."""
    try:
        eda_results_collection = Database.get_collection("eda_results")
        eda_results_collection.insert_one({
            "file_id": file_id,
            "user_id": user_id,
            "eda": eda,
        })
        print(f"✅ EDA results stored in MongoDB for file ID: {file_id}")

    except Exception as e:
        print(f"❌ Failed to store EDA results: {str(e)}")
        raise e


@upload_bp.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        # Check for file
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file provided"}), 400
        
        # Get or generate user ID
        user_id = request.form.get('user_id', 'default_user')
        
        # Save the file
        file_id, filename, save_path, file_extension = save_file(file, user_id)

        # Ingest the data
        data_ingestor = DataIngestorFactory.get_data_ingestor(file_extension)
        df = data_ingestor.ingest(save_path)
        print(f"✅ Data ingested successfully for file: {filename}")

        # Generate EDA
        eda = generate_eda(file_id, user_id, filename, save_path, df)

        # Store metadata and EDA results
        store_metadata(file_id, user_id, filename, save_path)
        store_eda(file_id, user_id, eda)

        # Return response
        print(f"✅ File upload completed successfully for file: {filename}")
        return jsonify({
            "message": "File uploaded and analyzed successfully",
            "file_id": file_id,
            "user_id": user_id,
            "file_path": save_path,
            "eda": eda
        }), 200

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        print(f"❌ General error: {str(e)}")
        return jsonify({"error": str(e)}), 500
