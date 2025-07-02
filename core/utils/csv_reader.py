import csv
import os
from .logger import get_logger

LOGGER = get_logger(__name__)

class CsvReader:
    @staticmethod
    def read_csv(file_path: str) -> list[dict]:
        """
        Reads data from a CSV file.
        Returns a list of dictionaries, where each dict represents a row.
        """
        if not os.path.exists(file_path):
            LOGGER.error(f"CSV file not found: {file_path}")
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        results = []
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as csvfile: # utf-8-sig handles BOM
                reader = csv.DictReader(csvfile) # Assumes first row is headers
                for row in reader:
                    results.append(row)
            LOGGER.info(f"Successfully read CSV file: {file_path}. Rows: {len(results)}")
            return results
        except Exception as e:
            LOGGER.error(f"Error reading CSV file {file_path}: {e}")
            raise