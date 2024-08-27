import pygame
import argparse
from core.game_manager import GameManager
import logging


def parse_arguments():
    parser = argparse.ArgumentParser(description="Dixit Game Configuration")
    parser.add_argument("--width", type=int, default=1024, help="Screen width")
    parser.add_argument("--height", type=int, default=768, help="Screen height")
    parser.add_argument("--title", type=str, default="Dixit", help="Game window title")
    return parser.parse_args()


def main():
    args = parse_arguments()

    # Initialize Pygame
    pygame.init()
    if not pygame.get_init():
        raise RuntimeError("Failed to initialize Pygame.")

    # Set up the screen and game window title
    try:
        screen = pygame.display.set_mode((args.width, args.height))
        pygame.display.set_caption(args.title)
    except pygame.error as e:
        print(f"Error initializing screen: {e}")
        logging.error(f"Error initializing screen: {e}")
        return

    # Set up logging for error tracking
    logging.basicConfig(filename="game_errors.log", level=logging.ERROR)

    try:
        # Initialize and run the GameManager
        game_manager = GameManager(screen)
        game_manager.run()
    except pygame.error as e:
        logging.error(f"Pygame error: {e}", exc_info=True)
        show_error_message(screen, args.height, f"Pygame error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        show_error_message(screen, args.height, f"An error occurred: {e}")
    finally:
        pygame.quit()


def show_error_message(screen, screen_height, message):
    """Helper function to display an error message on the screen."""
    try:
        font = pygame.font.Font(None, 50)
    except pygame.error as e:
        print(f"Error loading font: {e}")
        return
    
    screen.fill((0, 0, 0))
    error_message = font.render(message, True, (255, 0, 0))
    screen.blit(error_message, (50, screen_height // 2))
    pygame.display.flip()
    pygame.time.wait(5000)


if __name__ == "__main__":
    main()
