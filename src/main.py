import pygame
import argparse
from utils.logger import configure_logging
import logging
import os
from core.game_manager import GameManager
from model.model_manager import ModelManager
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import errorcode

def db_connect():
    print("attempting to connect to db")
    try:
        cnx = mysql.connector.connect(user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      host='dixitdb.cdguq4e4c4jo.us-east-2.rds.amazonaws.com',
                                      database='dixitdb')
        
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

def test_sql(cnx):
    is_bot = False
    name = 'John Doe'

    cursor = cnx.cursor()

    insert_query = """
        INSERT INTO Player (is_bot, name)
        VALUES (%s, %s)
        """

    cursor.execute(insert_query, (is_bot, name))

    cnx.commit()

    print(f"Inserted player ID: {cursor.lastrowid}")
    
    cursor.close()


def parse_arguments():
    """Parse command-line arguments for game configuration."""
    parser = argparse.ArgumentParser(description="Dixit Game Configuration")
    parser.add_argument("--width", type=int, default=1024, help="Screen width")
    parser.add_argument("--height", type=int, default=768, help="Screen height")
    parser.add_argument("--title", type=str, default="Dixit", help="Game window title")
    parser.add_argument("--fullscreen", action="store_true", help="Enable fullscreen mode")
    return parser.parse_args()

def initialize_screen(args, logger):
    """Initialize the Pygame screen."""
    try:
        flags = pygame.FULLSCREEN if args.fullscreen else 0
        screen = pygame.display.set_mode((args.width, args.height), flags)
        pygame.display.set_caption(args.title)
        logger.info(f"Screen initialized with width={args.width}, height={args.height}, fullscreen={args.fullscreen}")
        return screen
    except pygame.error as e:
        logger.error(f"Error initializing screen: {e}", exc_info=True)
        raise RuntimeError("Failed to initialize screen.") from e

def show_error_message(screen, message, duration=5000, logger=None):
    """Display an error message on the screen."""
    try:
        font = pygame.font.Font(None, 50)
        screen.fill((0, 0, 0))
        error_message = font.render(message, True, (255, 0, 0))
        screen.blit(error_message, (screen.get_width() // 2 - error_message.get_width() // 2, screen.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(duration)
        logger.error(f"Displayed error message: {message}")
    except pygame.error as e:
        logger.error(f"Error displaying error message: {e}", exc_info=True)

def main():
    # added .env loader
    load_dotenv()
    # Configure DB
    cnx = db_connect()
    test_sql(cnx)
    # Configure logging
    configure_logging(env='development')
    logger = logging.getLogger(__name__)
    logger.info("Starting the game application.")
    
    # Parse arguments
    args = parse_arguments()
    logger.info(f"Arguments parsed: width={args.width}, height={args.height}, fullscreen={args.fullscreen}")

    # Initialize Pygame
    pygame.init()
    if not pygame.get_init():
        logger.error("Failed to initialize Pygame.")
        raise RuntimeError("Failed to initialize Pygame.")

    # Initialize the screen
    try:
        screen = initialize_screen(args, logger)
    except RuntimeError:
        show_error_message(screen, "Failed to initialize screen.", logger=logger)
        return

    # Initialize ModelManager asynchronously to avoid UI blocking
    logger.info("Initializing ModelManager asynchronously.")
    model_manager = ModelManager()
    model_manager.initialize_model_async(callback=lambda: logger.info("Model loaded successfully"))

    try:
        # Initialize and run the GameManager
        game_manager = GameManager(screen, model_manager)
        game_manager.run()
    except pygame.error as e:
        logger.error(f"Pygame error: {e}", exc_info=True)
        show_error_message(screen, f"Pygame error: {e}", logger=logger)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        show_error_message(screen, f"An error occurred: {e}", logger=logger)
    finally:
        logger.info("Shutting down Pygame and exiting the game.")
        cnx.close()
        pygame.quit()

if __name__ == "__main__":
    main()
