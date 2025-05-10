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
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = [".zip", ".csv"]

def is_allowed_file(filename):
    """Check if the uploaded file has a supported extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext[1:] for ext in ALLOWED_EXTENSIONS]


def save_file(file, user_id, custom_name=None):
    """Save the uploaded file to the user directory."""
    try:
        # Generate a unique file ID
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()

        # Use custom name if provided
        if custom_name:
            # Ensure the custom name doesn't include the extension
            filename = secure_filename(custom_name) + file_extension

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


def store_metadata(file_id, user_id, filename, file_path, custom_name=None):
    """Store file metadata in MongoDB."""
    try:
        files_collection = Database.get_collection("files")
        files_collection.insert_one({
            "file_id": file_id,
            "user_id": user_id,
            "filename": filename,
            "custom_name": custom_name or filename,
            "file_path": file_path,
            "status": "processed",
            "uploaded_at": datetime.utcnow().isoformat()
        })
        print(f"✅ File metadata stored in MongoDB for file: {filename}")

    except Exception as e:
        print(f"❌ Failed to store file metadata: {str(e)}")
        raise e


def store_dataset(file_id, user_id, eda, df, custom_name=None):
    """Store dataset metadata and save the processed CSV."""
    try:
        # Create dataset ID
        dataset_id = str(uuid.uuid4())
        
        # Prepare dataset directory
        processed_dir = os.path.join(UPLOAD_FOLDER, user_id, "datasets")
        os.makedirs(processed_dir, exist_ok=True)

        # Save the processed CSV
        processed_file_path = os.path.join(processed_dir, f"{dataset_id}_{custom_name or eda['filename']}.csv")
        df.to_csv(processed_file_path, index=False)
        print(f"✅ Processed data saved at: {processed_file_path}")

        # Store dataset metadata
        datasets_collection = Database.get_collection("datasets")
        datasets_collection.insert_one({
            "dataset_id": dataset_id,
            "file_id": file_id,
            "user_id": user_id,
            "custom_name": custom_name or eda["filename"],
            "processed_file_path": processed_file_path,
            "eda": eda,
            "uploaded_at": datetime.utcnow().isoformat()
        })

        print(f"✅ Dataset metadata stored in MongoDB for dataset ID: {dataset_id}")

    except Exception as e:
        print(f"❌ Failed to store dataset metadata: {str(e)}")
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
        
        # Get the custom file name (optional)
        custom_name = request.form.get('custom_name', None)

        # Save the file
        file_id, filename, save_path, file_extension = save_file(file, user_id, custom_name)

        # Ingest the data
        data_ingestor = DataIngestorFactory.get_data_ingestor(file_extension)
        df = data_ingestor.ingest(save_path)
        print(f"✅ Data ingested successfully for file: {filename}")

        # Generate EDA
        eda = generate_eda(file_id, user_id, filename, save_path, df)

        # Store metadata and dataset
        store_metadata(file_id, user_id, filename, save_path, custom_name)
        store_dataset(file_id, user_id, eda, df, custom_name)

        # Return response
        print(f"✅ File upload completed successfully for file: {filename}")
        return jsonify({
            "message": "File uploaded and analyzed successfully",
            "file_id": file_id,
            "user_id": user_id,
            "custom_name": custom_name or filename,
            "file_path": save_path,
            "eda": eda
        }), 200

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        print(f"❌ General error: {str(e)}")
        return jsonify({"error": str(e)}), 500
