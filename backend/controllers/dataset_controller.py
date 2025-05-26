import os
import pandas as pd
from utils.db import Database
from bson.objectid import ObjectId

# Controller for:
# - Listing datasets (optionally filtered by user)
# - Getting dataset details
# - Deleting datasets

class DatasetController:
    DATASETS_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "datasets"))

    @staticmethod
    def list_datasets(user_id=None):
        try:
            datasets_collection = Database.get_collection("datasets")
            query = {"user_id": user_id} if user_id else {}

            datasets = list(datasets_collection.find(
                query,
                {
                    "_id": 1,
                    "custom_name": 1,
                    "processed_file_path": 1,
                    "uploaded_at": 1,
                    "user_id": 1  # ✅ include user_id in projection
                }
            ))

            # Convert ObjectId and user_id to string for frontend compatibility
            for dataset in datasets:
                dataset["_id"] = str(dataset["_id"])
                if "user_id" in dataset:
                    dataset["user_id"] = str(dataset["user_id"])

            return datasets

        except Exception as e:
            raise Exception(f"Failed to list datasets: {str(e)}")

    @staticmethod
    def get_dataset_details(dataset_id):
        try:
            datasets_collection = Database.get_collection("datasets")
            dataset = datasets_collection.find_one({"_id": ObjectId(dataset_id)})
            if dataset:
                dataset["_id"] = str(dataset["_id"])
                if "user_id" in dataset:
                    dataset["user_id"] = str(dataset["user_id"])
            return dataset
        except Exception as e:
            raise Exception(f"Failed to get dataset details: {str(e)}")

    @staticmethod
    def delete_dataset(dataset_id):
        try:
            datasets_collection = Database.get_collection("datasets")
            result = datasets_collection.delete_one({"_id": ObjectId(dataset_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Failed to delete dataset: {str(e)}")
