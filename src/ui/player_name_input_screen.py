import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_BACKSPACE, K_RETURN
from ui.base_screen import BaseScreen  # Import the BaseScreen
import logging

logger = logging.getLogger('ui')

MAX_NAME_LENGTH = 15  # Maximum length for a player's name

class PlayerNameInputScreen(BaseScreen):
    def __init__(self, screen, num_players):
        super().__init__(screen)  # Initialize BaseScreen
        self.num_players = num_players
        self.current_player = 0
        self.player_names = []
        self.input_text = ""
        self.font = self.load_font(50)  # Use BaseScreen's load_font method
        self.background_color = (0, 0, 128)  # Blue background color
        self.text_color = (255, 255, 255)  # White text color

    def render(self):
        """Render the player name input screen."""
        self.render_background(self.background_color)  # Use BaseScreen's render_background method
        self.render_prompt()
        self.render_input_text()
        pygame.display.flip()

    def render_prompt(self):
        """Render the prompt text."""
        prompt_text = f"Enter name for player {self.current_player + 1}:"
        self.render_text(prompt_text, self.font, self.text_color, (100, 100))  # Use BaseScreen's render_text method

    def render_input_text(self):
        """Render the current input text."""
        self.render_text(self.input_text, self.font, self.text_color, (100, 150))  # Use BaseScreen's render_text method

    def handle_events(self):
        """Handle player name input events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                logger.info("Game quit during player name input.")
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                self.handle_keydown(event)

        # Determine if all names have been entered
        if self.current_player == self.num_players:
            return "game_screen", self.player_names
        return None, self.player_names

    def handle_keydown(self, event):
        """Handle keydown events."""
        if event.key == K_RETURN:
            self.submit_name()
        elif event.key == K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            if len(self.input_text) < MAX_NAME_LENGTH:
                self.input_text += event.unicode

    def submit_name(self):
        """Submit the current player's name."""
        if self.input_text:  # Prevent empty names
            self.player_names.append(self.input_text[:MAX_NAME_LENGTH])
            logger.info(f"Player {self.current_player + 1} name submitted: {self.input_text[:MAX_NAME_LENGTH]}")
            self.input_text = ""
            self.current_player += 1
