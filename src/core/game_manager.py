import threading
import pygame
import sys
import logging
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

    def __init__(self, screen):
        self.screen = screen
        self._model_manager = ModelManager()
        self.model = None
        self.transform = None
        self.device = None
        self.current_storyteller_index = 0
        self.players: List[Player] = []
        self.deck = []
        self.loading_thread = None
        self.loading_complete = False
        self.just_dealt = False

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
            print(f"Error loading font: {e}")
            pygame.quit()
            sys.exit(1)

        self.loading_bar_rect = pygame.Rect(
            (screen.get_width() // 2 - GameManager.LOADING_BAR_WIDTH // 2),
            (screen.get_height() // 2 - GameManager.LOADING_BAR_HEIGHT // 2),
            0,
            GameManager.LOADING_BAR_HEIGHT,
        )

    def load_model_in_background(self):
        try:
            self.model, self.transform, self.device = (
                self._model_manager.initialize_model()
            )
        except Exception as e:
            self.show_error_message(f"Model loading failed: {str(e)}")
            self.running = False
        finally:
            self.loading_complete = True

    def start_loading_model(self):
        self.loading_complete = False
        self.loading_thread = threading.Thread(target=self.load_model_in_background)
        self.loading_thread.start()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_state()
            clock.tick(GameManager.FRAME_RATE)
        pygame.quit()

    def handle_state(self):
        logging.debug(f"Handling state: {self.current_state}")
        
        if self.current_state == GameState.MAIN_MENU:
            self.handle_main_menu()
        elif self.current_state == GameState.SETUP_MENU:
            self.handle_setup_menu()
        elif self.current_state == GameState.PLAYER_NAME_INPUT:
            self.handle_player_name_input()
        elif self.current_state == GameState.LOADING:
            self.handle_loading_screen()
        elif self.current_state == GameState.GAME_SCREEN:
            self.handle_game_screen()
        elif self.current_state == GameState.GAME_OVER:
            self.handle_game_over_screen()
        else:
            self.handle_unexpected_state()

    def handle_main_menu(self):
        self.main_menu.render()
        next_screen = self.main_menu.handle_events()
        
        if next_screen == "Start Game":
            self.setup_menu = SetupMenu(self.screen)
            self.current_state = GameState.SETUP_MENU
            logging.info("Transitioning to SETUP_MENU")
        elif next_screen == "Options":
            # Handle options if needed
            logging.info("Options selected (not implemented yet)")
        elif next_screen == "Quit":
            logging.info("Quitting game")
            self.running = False
        else:
            logging.info("No valid selection, staying in MAIN_MENU")

    def handle_setup_menu(self):
        self.setup_menu.render()
        next_screen, num_humans, num_bots = self.setup_menu.handle_events()

        if next_screen == "player_name_input_screen":
            self.player_name_input_screen = PlayerNameInputScreen(
                self.screen, num_humans
            )
            self.num_bots = num_bots
            self.current_state = GameState.PLAYER_NAME_INPUT

    def handle_player_name_input(self):
        self.player_name_input_screen.render()
        next_screen, player_names = self.player_name_input_screen.handle_events()

        if next_screen == "game_screen" and player_names:
            self.player_names = player_names
            self.current_state = GameState.LOADING
            self.start_loading_model()

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
                    pygame.display.flip()  # Ensure display updates immediately after state change
                except Exception as e:
                    self.show_error_message(f"Failed to start the game: {str(e)}")



    def update_loading_bar(self):
        previous_width = self.loading_bar_rect.width
        if self.loading_thread.is_alive():
            progress = min(self.loading_bar_rect.width + 10, GameManager.LOADING_BAR_WIDTH)
            if progress != previous_width:
                self.loading_bar_rect.width = progress

        self.screen.fill(GameManager.BACKGROUND_COLOR)
        pygame.draw.rect(self.screen, (255, 255, 255), self.loading_bar_rect)

        loading_text = self.loading_font.render("Loading...", True, (255, 255, 255))
        text_rect = loading_text.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)
        )
        self.screen.blit(loading_text, text_rect)

        pygame.display.flip()

    def handle_game_screen(self):
        if not self.game_screen:
            self.show_error_message("Game screen not initialized")
            return

        try:
            events = pygame.event.get()
            next_screen = self.game_screen.handle_event(events)
            self.game_screen.render()  # Explicitly render the game screen
            if next_screen == "game_over":
                self.end_game()
            pygame.display.flip()  # Ensure the screen updates after rendering
        except Exception as e:
            self.show_error_message(f"Error during game screen handling: {str(e)}")



    def handle_game_over_screen(self):
        self.game_over_screen.render()
        next_screen = self.game_over_screen.handle_events()
        if next_screen == "main_menu":
            self.current_state = GameState.MAIN_MENU
        elif next_screen == "quit_game":
            self.running = False

    def handle_unexpected_state(self):
        print(f"Unexpected game state: {self.current_state}")
        self.running = False

    def start_game(self):
        try:
            num_players = len(self.player_names) + self.num_bots
            self.players = setup_game(
                self.player_names, self.num_bots, self.screen, num_players
            )

            self.deck = load_images_from_directory("data/cards")

            if len(self.deck) < 6 * len(self.players):
                raise ValueError("Not enough cards in the deck to deal to all players.")

            self.deck = deal_cards(self.players, self.deck, 6)
            self.just_dealt = True

            self.game_screen = GameScreen(self.screen, self.players, self.deck, self)
            self.current_state = GameState.GAME_SCREEN
            self.just_dealt = False
            print("Game screen initialized and state transitioned to GAME_SCREEN.")  # Debug print

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
        print(f"Error: {message}")
        pygame.quit()
        sys.exit(1)
