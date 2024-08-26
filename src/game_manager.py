import open_clip
import torch
import sys
import pygame
import threading
from text_processing.description_obfuscator import DescriptionObfuscator
from game_logic.dixit import setup_game, load_images_from_directory, deal_cards
from ui.main_menu import MainMenu
from ui.setup_menu import SetupMenu
from ui.player_name_input_screen import PlayerNameInputScreen
from ui.game_screen import GameScreen
from ui.game_over_screen import GameOverScreen
from enum import Enum, auto
from model_manager import ModelManager
from game_logic.humanAgent import Human


class GameState(Enum):
    """Represents the different states of the game."""

    MAIN_MENU = auto()
    SETUP_MENU = auto()
    PLAYER_NAME_INPUT = auto()
    LOADING = auto()
    GAME_SCREEN = auto()
    GAME_OVER = auto()


class GameManager:
    """Manages the overall game flow and state transitions."""

    def __init__(self, screen):
        """Initializes the GameManager with the provided screen and sets up initial state."""
        self.screen = screen
        self.model_manager = ModelManager()
        self.model, self.transform, self.device = None, None, None
        self.current_storyteller_index = 0
        self.players = []
        self.deck = []
        self.loading_thread = None
        self.loading_complete = False

        # Loading bar setup
        self.loading_bar_width = 400
        self.loading_bar_height = 30
        self.loading_bar_rect = pygame.Rect(
            (screen.get_width() // 2 - self.loading_bar_width // 2),
            (screen.get_height() // 2 - self.loading_bar_height // 2),
            0,
            self.loading_bar_height,
        )
        self.background_color = (0, 0, 128)
        self.loading_font = pygame.font.Font(None, 50)

        # Initialize UI screens
        self.main_menu = MainMenu(screen)
        self.setup_menu = SetupMenu(screen)
        self.player_name_input_screen = None
        self.game_screen = None
        self.game_over_screen = None
        self.current_state = GameState.MAIN_MENU
        self.running = True
        self.player_names = []
        self.num_bots = 0

    def load_model_in_background(self):
        """Loads the model in a separate thread, setting `loading_complete` when done."""
        self.model, self.transform, self.device = self.model_manager.initialize_model()
        self.loading_complete = True

    def start_loading_model(self):
        """Starts the model loading process in a background thread."""
        self.loading_complete = False
        self.loading_thread = threading.Thread(target=self.load_model_in_background)
        self.loading_thread.start()

    def run(self):
        """Main loop that controls the game flow based on the current state."""
        while self.running:
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

            pygame.time.Clock().tick(60)
        pygame.quit()

    def handle_main_menu(self):
        """Handles the main menu screen interactions."""
        self.main_menu.render()
        next_screen = self.main_menu.handle_events()
        if next_screen == "start_game":
            self.current_state = GameState.SETUP_MENU
        elif next_screen == "quit_game":
            self.running = False

    def handle_setup_menu(self):
        """Handles the setup menu screen interactions."""
        self.setup_menu.render()
        next_screen, num_humans, num_bots = self.setup_menu.handle_events()
        if next_screen == "player_name_input_screen":
            self.player_name_input_screen = PlayerNameInputScreen(
                self.screen, num_humans
            )
            self.num_bots = num_bots
            self.current_state = GameState.PLAYER_NAME_INPUT

    def handle_player_name_input(self):
        """Handles the player name input screen interactions."""
        self.player_name_input_screen.render()
        next_screen, player_names = self.player_name_input_screen.handle_events()
        if next_screen == "game_screen":
            self.player_names = player_names
            self.current_state = GameState.LOADING
            self.start_loading_model()

    def handle_loading_screen(self):
        """Handles the loading screen, displaying progress while the model loads."""
        self.update_loading_bar()
        if self.loading_complete:
            self.start_game()

    def handle_game_screen(self):
        """Handles the main game screen interactions."""
        self.game_screen.render()
        next_screen = self.game_screen.handle_events()
        if next_screen == "game_over":
            self.end_game()

    def handle_game_over_screen(self):
        """Handles the game over screen interactions."""
        self.game_over_screen.render()
        next_screen = self.game_over_screen.handle_events()
        if next_screen == "main_menu":
            self.current_state = GameState.MAIN_MENU
        elif next_screen == "quit_game":
            self.running = False

    def render_loading_screen(self, progress):
        """Renders the loading screen with a progress bar."""
        self.screen.fill(self.background_color)
        loading_text = self.loading_font.render(
            "Loading model...", True, (255, 255, 255)
        )
        text_rect = loading_text.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)
        )
        self.screen.blit(loading_text, text_rect)

        self.loading_bar_rect.width = int(self.loading_bar_width * progress)
        pygame.draw.rect(self.screen, (255, 255, 255), self.loading_bar_rect)
        pygame.display.flip()

    def update_loading_bar(self):
        """Updates the loading bar during model loading."""
        for i in range(101):
            if self.loading_complete:
                progress = 1.0
            else:
                progress = i / 100.0
            self.render_loading_screen(progress)
            pygame.time.delay(50)

    def start_game(self):
        """Initializes the game, setting up players, deck, and starting the game screen."""
        self.players = setup_game(self.player_names, self.num_bots, self.screen)
        self.deck = load_images_from_directory("data/cards")
        num_cards = 6
        cur_deck = deal_cards(self.players, self.deck, num_cards)

        self.game_screen = GameScreen(self.screen, self.players, cur_deck, self)
        self.current_state = GameState.GAME_SCREEN

    def get_storyteller(self):
        """Returns the current storyteller."""
        return self.players[self.current_storyteller_index]

    def next_storyteller(self):
        """Advances to the next storyteller."""
        self.current_storyteller_index = (self.current_storyteller_index + 1) % len(
            self.players
        )

    def storyteller_turn(self):
        """Handles the storyteller's turn."""
        storyteller = self.get_storyteller()
        if isinstance(storyteller, Human):
            card = storyteller.choose_card()
            clue = storyteller.input_clue(card)
        else:
            card, clue = storyteller.storyteller_turn(self.screen)
        return card, clue

    def show_error_message(self, message):
        """Displays an error message on the screen."""
        error_font = pygame.font.Font(None, 40)
        error_surface = error_font.render(message, True, (255, 0, 0))
        error_rect = error_surface.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(error_surface, error_rect)
        pygame.display.flip()
        pygame.time.wait(2000)

    def end_game(self):
        """Ends the game and transitions to the game over screen."""
        self.game_over_screen = GameOverScreen(self.screen, self.players)
        self.current_state = GameState.GAME_OVER
