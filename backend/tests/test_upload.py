# backend/tests/test_upload.py
# python -m unittest tests.test_upload

import os
import unittest
import shutil
import pandas as pd
import io
import tempfile
import zipfile
from app import app
from utils.db import Database
from werkzeug.datastructures import FileStorage


class TestUploadFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use a temporary directory for uploads
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.base_upload_dir = cls.temp_dir.name

        # Create a test user directory
        cls.test_user_dir = os.path.join(cls.base_upload_dir, "test_user")
        os.makedirs(cls.test_user_dir, exist_ok=True)

        # Create a sample CSV file for testing
        cls.sample_data = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "City": ["New York", "Los Angeles", "Chicago"]
        })

        cls.test_file_name = "test_file.csv"
        cls.test_file_path = os.path.join(cls.test_user_dir, cls.test_file_name)
        cls.sample_data.to_csv(cls.test_file_path, index=False)

        print(f"✅ Test setup completed. Sample file created at {cls.test_file_path}")

    @classmethod
    def tearDownClass(cls):
        # Clean up MongoDB test data
        db = Database.get_database()
        db["files"].delete_many({"user_id": "test_user"})
        db["eda_results"].delete_many({"user_id": "test_user"})
        print(f"✅ MongoDB test data cleaned up for user test_user")

        # Close the MongoDB client
        Database.close()

        # Cleanup the temporary directory
        cls.temp_dir.cleanup()
        print(f"✅ Temporary directory {cls.base_upload_dir} cleaned up.")

    def simulate_file_upload(self, filename, content_type="text/csv"):
        """Simulate a file upload similar to a real API call."""
        with open(filename, "rb") as f:
            # Use FileStorage to correctly simulate the Flask file upload
            file_data = FileStorage(
                stream=io.BytesIO(f.read()),
                filename=os.path.basename(filename),
                content_type=content_type
            )
            return file_data

    def test_save_file(self):
        # Ensure the test file exists
        self.assertTrue(os.path.exists(self.test_file_path))
        print(f"✅ Test file exists: {self.test_file_path}")

    def test_invalid_file_extension(self):
        # Test invalid file extension
        invalid_file_path = self.test_file_path.replace(".csv", ".txt")
        with open(invalid_file_path, "w") as f:
            f.write("This is a test file with an invalid extension.")

        with app.test_client() as client:
            file_data = self.simulate_file_upload(invalid_file_path, content_type="text/plain")
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Only ZIP and CSV files are allowed", response.get_data(as_text=True))
            print(f"✅ Invalid file extension test passed for {invalid_file_path}")

        # Clean up
        os.remove(invalid_file_path)

    def test_empty_file_upload(self):
        # Create an empty file
        empty_file_path = os.path.join(self.test_user_dir, "empty_file.csv")
        with open(empty_file_path, "w") as f:
            pass

        with app.test_client() as client:
            file_data = self.simulate_file_upload(empty_file_path)
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("No columns to parse from file", response.get_data(as_text=True))
            print(f"✅ Empty file test passed for {empty_file_path}")

    def test_corrupt_csv_file(self):
        # Create a corrupt CSV file
        corrupt_file_path = os.path.join(self.test_user_dir, "corrupt_file.csv")
        with open(corrupt_file_path, "w") as f:
            f.write("Name,Age,City\nAlice,25\nBob,30,New York,ExtraColumn\nCharlie,35,Los Angeles")

        with app.test_client() as client:
            file_data = self.simulate_file_upload(corrupt_file_path)
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Error tokenizing data", response.get_data(as_text=True))
            print(f"✅ Corrupt CSV file test passed for {corrupt_file_path}")

    def test_multiple_csv_files_in_zip(self):
        # Create a zip file with multiple CSV files
        zip_file_path = os.path.join(self.test_user_dir, "multi_csv.zip")
        with zipfile.ZipFile(zip_file_path, "w") as zipf:
            # Add two CSV files to the zip
            zipf.writestr("file1.csv", self.sample_data.to_csv(index=False))
            zipf.writestr("file2.csv", self.sample_data.to_csv(index=False))

        with app.test_client() as client:
            file_data = self.simulate_file_upload(zip_file_path, content_type="application/zip")
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 400)
            self.assertIn("Multiple CSV files found", response.get_data(as_text=True))
            print(f"✅ Multiple CSV files in ZIP test passed for {zip_file_path}")

    def test_large_file_upload(self):
        # Simulate a large CSV file (1 million rows)
        large_file_path = os.path.join(self.test_user_dir, "large_file.csv")
        large_data = pd.DataFrame({
            "Name": ["TestUser"] * 1000000,
            "Age": [30] * 1000000,
            "City": ["TestCity"] * 1000000
        })
        large_data.to_csv(large_file_path, index=False)

        with app.test_client() as client:
            file_data = self.simulate_file_upload(large_file_path)
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 200)
            print(f"✅ Large file test passed for {large_file_path}")

    def test_successful_upload(self):
        with app.test_client() as client:
            file_data = self.simulate_file_upload(self.test_file_path)
            response = client.post("/upload_file", data={"file": file_data, "user_id": "test_user"})
            self.assertEqual(response.status_code, 200)
            response_data = response.get_json()
            self.assertEqual(response_data["message"], "File uploaded and analyzed successfully")
            print(f"✅ Successful file upload test passed for {self.test_file_path}")


if __name__ == "__main__":
    unittest.main()
