import os
import logging.config

def ensure_log_directories():
    log_directories = ['logs']
    for directory in log_directories:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            print(f"Error creating log directory {directory}: {e}")

def configure_logging(env='development'):
    ensure_log_directories()
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'logging_config.ini')

    if not os.path.exists(config_file_path):
        print(f"Logging configuration file not found at {config_file_path}.")
        return

    try:
        logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
        logging.getLogger('game_logic').info(f"Logging configured successfully using {config_file_path}.")
    except Exception as e:
        print(f"Failed to configure logging: {e}")
