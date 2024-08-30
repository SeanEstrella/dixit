import logging
from logging_config import LOGGING_CONFIG
from game_logic import terminal_game_loop

logger = logging.getLogger('game_logic')

if __name__ == "__main__":
    try:
        logger.info("Starting Dixit Bot Game...")
        terminal_game_loop()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
