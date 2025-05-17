from flask import Blueprint, request, jsonify
from controllers.upload_controller import save_file, generate_eda, store_metadata, store_dataset
from core.src.ingest_data import DataIngestorFactory
import os

upload_bp = Blueprint("upload", __name__)

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
            "file_path": save_path
        }), 200

    except ValueError as ve:
        print(f"❌ Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        print(f"❌ General error: {str(e)}")
        return jsonify({"error": str(e)}), 500