import os
import uuid
import pandas as pd
from datetime import datetime
from utils.db import Database
from werkzeug.utils import secure_filename

# Set the upload folder relative to the backend directory
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Supported file extensions
ALLOWED_EXTENSIONS = [".zip", ".csv"]

def is_allowed_file(filename):
    """Check if the uploaded file has a supported extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in [ext[1:] for ext in ALLOWED_EXTENSIONS]

def save_file(file, user_id, custom_name=None):
    try:
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = os.path.splitext(filename)[1].lower()

        if custom_name:
            filename = secure_filename(custom_name) + file_extension

        if not is_allowed_file(filename):
            raise ValueError("Only ZIP and CSV files are allowed")

        user_dir = os.path.join(UPLOAD_FOLDER, user_id)
        os.makedirs(user_dir, exist_ok=True)

        save_path = os.path.join(user_dir, f"{file_id}_{filename}")
        file.save(save_path)
        print(f"✅ File saved at: {save_path}")

        return file_id, filename, save_path, file_extension

    except Exception as e:
        print(f"❌ Failed to save file: {str(e)}")
        raise e

def generate_eda(file_id, user_id, filename, file_path, df):
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
    try:
        dataset_id = str(uuid.uuid4())
        processed_dir = os.path.join(UPLOAD_FOLDER, user_id, "datasets")
        os.makedirs(processed_dir, exist_ok=True)

        processed_file_path = os.path.join(processed_dir, f"{dataset_id}_{custom_name or eda['filename']}.csv")
        df.to_csv(processed_file_path, index=False)
        print(f"✅ Processed data saved at: {processed_file_path}")

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
