import pygame
import argparse
from game_manager import GameManager


def parse_arguments():
    parser = argparse.ArgumentParser(description="Dixit Game Configuration")
    parser.add_argument("--width", type=int, default=1024, help="Screen width")
    parser.add_argument("--height", type=int, default=768, help="Screen height")
    parser.add_argument("--title", type=str, default="Dixit", help="Game window title")
    return parser.parse_args()


def main():
    args = parse_arguments()

    pygame.init()

    screen = pygame.display.set_mode((args.width, args.height))
    pygame.display.set_caption(args.title)

    try:
        # Initialize and run the game manager
        game_manager = GameManager(screen)
        game_manager.run()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
