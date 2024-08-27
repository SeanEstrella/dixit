import threading
import pygame
import sys
import logging
import time
from typing import List
from enum import Enum, auto
from model.model_manager import ModelManager
from game_logic.player import Player
from game_logic.dixit import setup_game, load_images_from_directory, deal_cards
from ui.main_menu import MainMenu
from ui.setup_menu import SetupMenu
from ui.player_name_input_screen import PlayerNameInputScreen
from ui.game_screen import GameScreen
from ui.game_over_screen import GameOverScreen
from ui.rendering import Renderer  # Import Renderer class

logger = logging.getLogger('core')

class GameState(Enum):
    MAIN_MENU = auto()
    SETUP_MENU = auto()
    PLAYER_NAME_INPUT = auto()
    LOADING = auto()
    GAME_SCREEN = auto()
    GAME_OVER = auto()

class GameManager:
    LOADING_BAR_WIDTH = 400
    LOADING_BAR_HEIGHT = 30
    LOADING_FONT_SIZE = 50
    BACKGROUND_COLOR = (0, 0, 128)
    FRAME_RATE = 60

    def __init__(self, screen, model_manager: ModelManager):
        self.screen = screen
        self._model_manager = model_manager
        self.model = None
        self.transform = None
        self.device = None
        self.current_storyteller_index = 0
        self.players: List[Player] = []
        self.deck = []
        self.loading_thread = None
        self.loading_complete = False
        self.loading_progress = 0
        self.loading_lock = threading.Lock()
        self.last_render_log_time = 0
        self.log_interval = 1
        self.last_logged_message = ""
        self.repeated_log_count = 0
        self.last_logged_state = None

        # Renderer instance
        self.renderer = Renderer(screen)

        # Initialize UI components
        self.main_menu = MainMenu(screen)
        self.setup_menu = None
        self.player_name_input_screen = None
        self.game_screen = None
        self.game_over_screen = None
        self.current_state = GameState.MAIN_MENU
        self.running = True
        self.player_names: List[str] = []
        self.num_bots = 0

        # Loading screen attributes
        try:
            self.loading_font = pygame.font.Font(None, GameManager.LOADING_FONT_SIZE)
        except pygame.error as e:
            logger.error(f"Error loading font: {e}")
            pygame.quit()
            sys.exit(1)

        self.loading_bar_rect = pygame.Rect(
            (screen.get_width() // 2 - GameManager.LOADING_BAR_WIDTH // 2),
            (screen.get_height() // 2 - GameManager.LOADING_BAR_HEIGHT // 2),
            0,
            GameManager.LOADING_BAR_HEIGHT,
        )

    def load_model_in_background(self):
        with self.loading_lock:
            try:
                if not self.loading_complete:
                    logger.info("Starting model loading in the background.")
                    self.loading_progress = 10

                    self.model, self.transform, self.device = self._model_manager.initialize_model()
                    self.loading_progress = 90

                    # Simulating finalization process
                    time.sleep(1)
                    self.loading_progress = 100
                    logger.info("Model loading completed.")
                else:
                    logger.info("Model already loaded, skipping reload.")
            except Exception as e:
                self.show_error_message(f"Model loading failed: {str(e)}")
                self.running = False
            finally:
                self.loading_complete = True

    def start_loading_model(self):
        if not self.loading_complete:
            self.loading_complete = False
            self.loading_progress = 0
            self.loading_thread = threading.Thread(target=self.load_model_in_background)
            self.loading_thread.start()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_state()
            clock.tick(GameManager.FRAME_RATE)
        pygame.quit()

    def handle_state(self):
        logger.debug(f"Handling state: {self.current_state}")
        state_handlers = {
            GameState.MAIN_MENU: self.handle_main_menu,
            GameState.SETUP_MENU: self.handle_setup_menu,
            GameState.PLAYER_NAME_INPUT: self.handle_player_name_input,
            GameState.LOADING: self.handle_loading_screen,
            GameState.GAME_SCREEN: self.handle_game_screen,
            GameState.GAME_OVER: self.handle_game_over_screen,
        }
        handler = state_handlers.get(self.current_state, self.handle_unexpected_state)
        handler()

    def handle_main_menu(self):
        self.main_menu.render()
        next_screen = self.main_menu.handle_events()

        if next_screen == "Start Game":
            self.setup_menu = SetupMenu(self.screen)
            self.current_state = GameState.SETUP_MENU
            logger.info("Transitioning to SETUP_MENU")
        elif next_screen == "Options":
            logger.info("Options selected (not implemented yet)")
        elif next_screen == "Quit":
            logger.info("Quitting game")
            self.running = False
        else:
            logger.debug("No valid selection, staying in MAIN_MENU")

    def handle_setup_menu(self):
        self.setup_menu.render()
        next_screen, num_humans, num_bots = self.setup_menu.handle_events()

        if next_screen == "player_name_input_screen":
            self.player_name_input_screen = PlayerNameInputScreen(
                self.screen, num_humans
            )
            self.num_bots = num_bots
            self.current_state = GameState.PLAYER_NAME_INPUT
            logger.info("Transitioning to PLAYER_NAME_INPUT")

    def handle_player_name_input(self):
        self.player_name_input_screen.render()
        next_screen, player_names = self.player_name_input_screen.handle_events()

        if next_screen == "game_screen" and player_names:
            self.player_names = player_names
            self.current_state = GameState.LOADING
            self.start_loading_model()
            logger.info("Transitioning to LOADING state")

    def handle_loading_screen(self):
        self.update_loading_bar()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not self.loading_thread.is_alive():
            self.loading_thread.join()
            if self.loading_complete:
                try:
                    self.start_game()
                    self.current_state = GameState.GAME_SCREEN
                    logger.info("Transitioning to GAME_SCREEN state")
                except Exception as e:
                    self.show_error_message(f"Failed to start the game: {str(e)}")
            else:
                logger.error("Loading thread finished but model loading incomplete.")
                self.show_error_message("Model loading failed.")

    def update_loading_bar(self):
        # Update loading bar using the Renderer class
        self.loading_bar_rect.width = (
            GameManager.LOADING_BAR_WIDTH * self.loading_progress // 100
        )
        self.renderer.render_loading_bar(self.loading_progress, self.loading_bar_rect)
        self.renderer.render_loading_screen(
            self.loading_font, "Loading...", self.loading_progress,
            (self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)
        )
        pygame.display.flip()

    def handle_game_screen(self):
        if not self.game_screen:
            self.show_error_message("Game screen not initialized")
            return

        try:
            events = pygame.event.get()
            next_screen = self.game_screen.handle_event(events)
            self.game_screen.render()

            if next_screen == "game_over":
                self.end_game()

            pygame.display.flip()

            if self.current_state != self.last_logged_state:
                logger.info(f"Rendering GameScreen in state: {self.current_state}")
                self.last_logged_state = self.current_state

        except Exception as e:
            logger.critical(f"Critical error during game screen handling: {str(e)}", exc_info=True)
            pygame.quit()
            sys.exit(1)

    def handle_game_over_screen(self):
        self.game_over_screen.render()
        next_screen = self.game_over_screen.handle_events()
        if next_screen == "main_menu":
            self.current_state = GameState.MAIN_MENU
        elif next_screen == "quit_game":
            self.running = False

    def handle_unexpected_state(self):
        logger.error(f"Unexpected game state: {self.current_state}")
        self.running = False

    def start_game(self):
        try:
            num_players = len(self.player_names) + self.num_bots
            self.players = setup_game(
                self.player_names, self.num_bots, self.screen, num_players, self._model_manager
            )

            self.deck = load_images_from_directory("data/images/cards")

            if len(self.deck) < 6 * len(self.players):
                raise ValueError("Not enough cards in the deck to deal to all players.")

            self.deck = deal_cards(self.players, self.deck, 6)
            self.just_dealt = True

            self.game_screen = GameScreen(self.screen, self.players, self.deck, self)
            self.current_state = GameState.GAME_SCREEN
            self.just_dealt = False
            logger.info("Game screen initialized and state transitioned to GAME_SCREEN.")

        except Exception as e:
            self.show_error_message(f"Failed to start the game: {str(e)}")
            self.running = False

    def get_storyteller(self) -> Player:
        return self.players[self.current_storyteller_index]

    def next_storyteller(self):
        self.current_storyteller_index = (self.current_storyteller_index + 1) % len(
            self.players
        )

    def end_game(self):
        self.game_over_screen = GameOverScreen(self.screen, self.players)
        self.current_state = GameState.GAME_OVER

    def show_error_message(self, message: str):
        logger.error(f"Error: {message}")
        self.renderer.render_text(message, self.loading_font, (255, 0, 0), (self.screen.get_width() // 2, self.screen.get_height() // 2), center=True)
        pygame.display.flip()
        time.sleep(3)  # Display the error message for 3 seconds
        pygame.quit()
        sys.exit(1)
