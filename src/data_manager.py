# data_manager.py
import csv
import datetime
import json
import logging
import os

logger = logging.getLogger('data_collection')

class DataManager:
    """
    A class to handle data collection and storage for research purposes.
    """
    def __init__(self, csv_filename='game_data.csv', json_filename='game_data.json'):
        self.csv_filename = csv_filename
        self.json_filename = json_filename
        self._initialize_files()

    def _initialize_files(self):
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'role', 'player', 'card', 'clue', 'action', 'vote', 'error'])
            logger.info(f"CSV file initialized: {self.csv_filename}")

        if not os.path.exists(self.json_filename):
            with open(self.json_filename, mode='w') as file:
                json.dump([], file)
            logger.info(f"JSON file initialized: {self.json_filename}")

    def log_data(self, data_entry):
        """
        Log data for research purposes.
        Args:
            data_entry (dict): A dictionary containing the data to be logged.
        """
        data_entry['timestamp'] = datetime.datetime.now().isoformat()

        if not self._validate_data_entry(data_entry):
            logger.error(f"Data entry validation failed: {data_entry}")
            return

        self._write_to_csv(data_entry)
        self._write_to_json(data_entry)

    def _validate_data_entry(self, data_entry):
        required_keys = ['timestamp', 'role', 'player', 'card', 'clue', 'action', 'vote', 'error']
        for key in required_keys:
            if key not in data_entry:
                data_entry[key] = ''
        logger.debug(f"Validated data entry: {data_entry}")
        return True

    def _write_to_csv(self, data_entry):
        try:
            with open(self.csv_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([data_entry.get('timestamp', ''),
                                 data_entry.get('role', ''),
                                 data_entry.get('player', ''),
                                 data_entry.get('card', ''),
                                 data_entry.get('clue', ''),
                                 data_entry.get('action', ''),
                                 data_entry.get('vote', ''),
                                 data_entry.get('error', '')])
            logger.info(f"Data logged to CSV: {data_entry}")
        except Exception as e:
            logger.error(f"Failed to write data to CSV: {e}")

    def _write_to_json(self, data_entry):
        try:
            with open(self.json_filename, mode='r+') as file:
                file_data = json.load(file)
                file_data.append(data_entry)
                file.seek(0)
                json.dump(file_data, file, indent=4)
            logger.info(f"Data logged to JSON: {data_entry}")
        except Exception as e:
            logger.error(f"Failed to write data to JSON: {e}")