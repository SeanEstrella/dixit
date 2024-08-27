import os
import logging.config

def ensure_log_directories():
    log_directories = ['logs']
    for directory in log_directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

def configure_logging(env='development'):
    ensure_log_directories()
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'logging_config.ini')
    logging.config.fileConfig(config_file_path)
