import logging
import os
import sys
from game_logic import terminal_game_loop

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/game.log', mode='a')
    ]
)

if __name__ == "__main__":
    terminal_game_loop()
