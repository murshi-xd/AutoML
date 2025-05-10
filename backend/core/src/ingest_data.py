import os
import zipfile
import pandas as pd
from abc import ABC, abstractmethod


# Define an abstract class for Data Ingestor
class DataIngestor(ABC):
    @abstractmethod
    def ingest(self, file_path: str) -> pd.DataFrame:
        """Abstract method to ingest data from a given file."""
        pass


# Implement a concrete class for ZIP Ingestion
class ZipDataIngestor(DataIngestor):
    def ingest(self, file_path: str) -> pd.DataFrame:
        """Extracts a .zip file and returns the content as a pandas DataFrame."""
        # Ensure the file is a .zip
        if not file_path.endswith(".zip"):
            raise ValueError("The provided file is not a .zip file.")

        # Extract the zip file
        extracted_dir = "backend/extracted_data"
        os.makedirs(extracted_dir, exist_ok=True)
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extracted_dir)

        # Find the extracted CSV file (assuming there is only one CSV file inside the zip)
        extracted_files = os.listdir(extracted_dir)
        csv_files = [f for f in extracted_files if f.endswith(".csv")]

        if len(csv_files) == 0:
            raise FileNotFoundError("No CSV file found in the extracted data.")
        if len(csv_files) > 1:
            raise ValueError("Multiple CSV files found. Please specify which one to use.")

        # Read the CSV into a DataFrame
        csv_file_path = os.path.join(extracted_dir, csv_files[0])
        df = pd.read_csv(csv_file_path)

        # Return the DataFrame
        return df


# Implement a concrete class for CSV Ingestion
class CSVDataIngestor(DataIngestor):
    def ingest(self, file_path: str) -> pd.DataFrame:
        """Reads a .csv file and returns it as a pandas DataFrame."""
        # Ensure the file is a .csv
        if not file_path.endswith(".csv"):
            raise ValueError("The provided file is not a .csv file.")

        # Read the CSV into a DataFrame
        df = pd.read_csv(file_path)
        print(f"✅ Ingested CSV file: {file_path}")
        return df


# Implement a Factory to create DataIngestors
class DataIngestorFactory:
    @staticmethod
    def get_data_ingestor(file_extension: str) -> DataIngestor:
        """Returns the appropriate DataIngestor based on file extension."""
        if file_extension == ".zip":
            return ZipDataIngestor()
        elif file_extension == ".csv":
            return CSVDataIngestor()
        else:
            raise ValueError(f"No ingestor available for file extension: {file_extension}")


# Example usage:
if __name__ == "__main__":
    # Test the factory
    # file_path = "/path/to/your/file.csv"
    # file_extension = os.path.splitext(file_path)[1]
    # data_ingestor = DataIngestorFactory.get_data_ingestor(file_extension)
    # df = data_ingestor.ingest(file_path)
    # print(df.head())
    pass
