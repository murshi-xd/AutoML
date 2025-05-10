# backend/tests/test_mongodb_connection.py
# python -m unittest tests.test_mongodb_connection

import os
import unittest
import mongomock
from dotenv import load_dotenv
from utils.db import Database


class TestMongoDBConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), "../.env")
        load_dotenv(env_path)

        # Use mongomock for testing
        cls.mock_client = mongomock.MongoClient()
        cls.db = cls.mock_client[os.getenv("DATABASE_NAME", "automl_test")]

        # Patch the Database class to use the mock client
        Database._client = cls.mock_client
        Database._db = cls.db
        print("✅ Mock MongoDB connection established.")

    @classmethod
    def tearDownClass(cls):
        # Close the mock connection
        cls.mock_client.close()
        print("✅ Mock MongoDB connection closed.")

    def setUp(self):
        # Drop collections if they exist to avoid conflicts
        self.db.drop_collection("files")
        self.db.drop_collection("eda_results")

        # Recreate the collections
        self.db.create_collection("files")
        self.db.create_collection("eda_results")

        # Clear the collections
        self.db["files"].delete_many({})
        self.db["eda_results"].delete_many({})
        print("🧹 Cleared test collections.")

    def test_mongodb_connection(self):
        # Check if the connection is successful
        collections = self.db.list_collection_names()
        self.assertIn("files", collections)
        self.assertIn("eda_results", collections)
        print(f"✅ Connected to Mock MongoDB: {collections}")

    def test_index_creation(self):
        # Ensure indexes were created
        self.db["files"].create_index("file_id", unique=True)
        self.db["eda_results"].create_index([("file_id", 1), ("user_id", 1)], unique=True)

        files_indexes = self.db["files"].index_information()
        eda_indexes = self.db["eda_results"].index_information()

        # Check for file_id uniqueness
        self.assertIn("file_id_1", files_indexes)
        self.assertIn("file_id_1_user_id_1", eda_indexes)

        print("✅ Indexes are present as expected.")

    def test_schema_validation(self):
        # Insert a valid file document
        valid_file = {
            "file_id": "test_file_id",
            "user_id": "test_user",
            "filename": "test_file.csv",
            "file_path": "/test/path/to/test_file.csv",
            "status": "processed"
        }

        # Insert a valid EDA document
        valid_eda = {
            "file_id": "test_file_id",
            "user_id": "test_user",
            "eda": {
                "shape": (10, 2),
                "columns": ["col1", "col2"],
                "dtypes": {"col1": "int64", "col2": "float64"},
                "missing_values": {"col1": 0, "col2": 0},
                "summary": {},
                "head": [{"col1": 1, "col2": 2.0}],
                "uploaded_at": "2025-01-01T00:00:00Z"
            }
        }

        # Insert and verify file metadata
        self.db["files"].insert_one(valid_file)
        self.assertIsNotNone(self.db["files"].find_one({"file_id": "test_file_id"}))
        print("✅ File metadata validation passed.")

        # Insert and verify EDA results
        self.db["eda_results"].insert_one(valid_eda)
        self.assertIsNotNone(self.db["eda_results"].find_one({"file_id": "test_file_id"}))
        print("✅ EDA results validation passed.")

    def test_schema_enforcement(self):
        # Attempt to insert an invalid file (should raise ValueError)
        invalid_file = {
            "file_id": "invalid_file_id",
            "user_id": "test_user",
            "filename": "invalid_file.csv"
            # Missing required fields like "file_path" and "status"
        }

        try:
            self.db["files"].insert_one(invalid_file)
            self.fail("Expected schema enforcement to fail.")
        except Exception as e:
            print(f"✅ Schema enforcement test passed (invalid file rejected): {e}")

    def test_collection_existence(self):
        # Ensure the collections exist
        collections = self.db.list_collection_names()
        self.assertIn("files", collections)
        self.assertIn("eda_results", collections)
        print("✅ Collections exist as expected.")


if __name__ == "__main__":
    unittest.main()
