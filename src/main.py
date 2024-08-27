import pygame
import argparse
from utils.logger import configure_logging
import logging
import os
from core.game_manager import GameManager
from model.model_manager import ModelManager

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
        pygame.quit()

if __name__ == "__main__":
    main()
