import os
import unittest
import mongomock
from flask import Flask
from dotenv import load_dotenv
from utils.db import Database
from routes.eda_routes import eda_bp

class TestEDARoutes(unittest.TestCase):

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

        # Setup Flask test client
        app = Flask(__name__)
        app.register_blueprint(eda_bp)
        cls.client = app.test_client()

        # Prepare test data directory
        test_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
        os.makedirs(test_data_dir, exist_ok=True)
        
        # Create a sample CSV file
        sample_file_path = os.path.join(test_data_dir, "sample.csv")
        with open(sample_file_path, "w") as f:
            f.write("Lot Area,SalePrice,MS Zoning\n")
            f.write("8450,208500,RL\n")
            f.write("9600,181500,RL\n")
            f.write("11250,223500,RL\n")
            f.write("9550,140000,RL\n")
            f.write("14260,250000,RL\n")
            f.write("14115,143000,RL\n")
            f.write("10084,307000,RL\n")
            f.write("10382,200000,RL\n")
            f.write("6120,129900,RM\n")
            f.write("7420,118000,RM\n")

        # Insert test dataset
        cls.dataset_id = "test_dataset_id"
        cls.db["datasets"].insert_one({
            "dataset_id": cls.dataset_id,
            "custom_name": "test_dataset",
            "processed_file_path": sample_file_path,
            "uploaded_at": "2025-01-01T00:00:00Z"
        })
        print("✅ Test dataset inserted.")

        # Prepare directory to save plots
        cls.plot_dir = os.path.join(test_data_dir, "plots")
        os.makedirs(cls.plot_dir, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        # Close the mock connection
        cls.mock_client.close()
        print("✅ Mock MongoDB connection closed.")

    def save_plot(self, response, plot_name):
        with open(os.path.join(self.plot_dir, plot_name), "wb") as f:
            f.write(response.data)
        print(f"✅ Plot saved: {plot_name}")

    def test_histogram(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "histogram",
            "column": "SalePrice",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "histogram.png")

    def test_boxplot(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "boxplot",
            "column": "SalePrice",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "boxplot.png")

    def test_heatmap(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "heatmap",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "heatmap.png")

    def test_missing(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "missing",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "missing.png")

    def test_correlation_top_n(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "correlation_top_n",
            "column": "SalePrice",
            "top_n": 5,
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "correlation_top_n.png")

    def test_category_distribution(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "category_distribution",
            "column": "MS Zoning",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "category_distribution.png")

    def test_pairplot(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "pairplot",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "pairplot.png")

    def test_scatter(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "scatter",
            "column": "Lot Area",
            "column2": "SalePrice",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "scatter.png")

    def test_violin(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "violin",
            "column": "SalePrice",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "violin.png")

    def test_jointplot(self):
        response = self.client.post("/eda_visual", json={
            "dataset_id": self.dataset_id,
            "plot_type": "jointplot",
            "column": "Lot Area",
            "column2": "SalePrice",
            "format": "png"
        })
        self.assertEqual(response.status_code, 200)
        self.save_plot(response, "jointplot.png")


if __name__ == "__main__":
    unittest.main()
