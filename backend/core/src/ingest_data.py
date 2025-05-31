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

# ✅ Excel Ingestor
class ExcelDataIngestor(DataIngestor):
    def ingest(self, file_path: str) -> pd.DataFrame:
        if not file_path.endswith((".xlsx", ".xls")):
            raise ValueError("The provided file is not an Excel file.")
        df = pd.read_excel(file_path)
        print(f"✅ Ingested Excel file: {file_path}")
        return df

# ✅ CSV Ingestor
class CSVDataIngestor(DataIngestor):
    def ingest(self, file_path: str) -> pd.DataFrame:
        if not file_path.endswith(".csv"):
            raise ValueError("The provided file is not a CSV file.")
        df = pd.read_csv(file_path)
        print(f"✅ Ingested CSV file: {file_path}")
        return df

# ✅ ZIP Ingestor (handles multiple CSV/Excel files)
class ZipDataIngestor(DataIngestor):
    def ingest(self, file_path: str) -> pd.DataFrame:
        if not file_path.endswith(".zip"):
            raise ValueError("The provided file is not a .zip file.")

        extracted_dir = "backend/extracted_data"
        os.makedirs(extracted_dir, exist_ok=True)
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extracted_dir)

        # Filter out CSV and Excel files
        extracted_files = os.listdir(extracted_dir)
        valid_files = [f for f in extracted_files if f.endswith((".csv", ".xlsx", ".xls"))]

        if len(valid_files) == 0:
            raise FileNotFoundError("No valid CSV or Excel files found in the zip archive.")

        dfs = []
        for file in valid_files:
            full_path = os.path.join(extracted_dir, file)
            ext = os.path.splitext(file)[1].lower()

            ingestor = DataIngestorFactory.get_data_ingestor(ext)
            df = ingestor.ingest(full_path)
            df["__source_file__"] = file  # Track which file each row came from (optional)
            dfs.append(df)

        # Merge all DataFrames into one
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"✅ Ingested {len(dfs)} file(s) from ZIP")
        return combined_df

# ✅ Ingestor Factory
class DataIngestorFactory:
    @staticmethod
    def get_data_ingestor(file_extension: str) -> DataIngestor:
        file_extension = file_extension.lower()
        if file_extension == ".zip":
            return ZipDataIngestor()
        elif file_extension == ".csv":
            return CSVDataIngestor()
        elif file_extension in [".xlsx", ".xls"]:
            return ExcelDataIngestor()
        else:
            raise ValueError(f"No ingestor available for file extension: {file_extension}")


# Example usage:
if __name__ == "__main__":
# ✅ Example usage (Uncomment to test directly)
# if __name__ == "__main__":
#     file_path = "example.zip"  # Can also be .csv or .xlsx
#     ext = os.path.splitext(file_path)[1]
#     ingestor = DataIngestorFactory.get_data_ingestor(ext)
#     df = ingestor.ingest(file_path)
#     print(df.head())

    pass
