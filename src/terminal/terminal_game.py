import logging
import os
import sys
from game_logic import terminal_game_loop

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils.logger import configure_logging

configure_logging(env='development')

# Now, you can use logging in your module
import logging
logger = logging.getLogger('game_logic')

logger.debug('Game logic started.')


if __name__ == "__main__":
    try:
        logger.debug('Game logic started.')
        terminal_game_loop()
    except Exception as e:
        logger.exception("An error occurred during the game session: %s", e) 

