import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from ui.base_screen import BaseScreen  # Import BaseScreen
import logging

logger = logging.getLogger('ui')

class GameOverScreen(BaseScreen):
    def __init__(self, screen, players):
        super().__init__(screen)  # Initialize BaseScreen
        self.players = players
        self.background_color = (0, 0, 128)  # Blue background color
        self.font = self.load_font(int(screen.get_height() * 0.08))  # Use BaseScreen's load_font method
        self.button_font = self.load_font(int(screen.get_height() * 0.06))  # Use BaseScreen's load_font method
        self.buttons = {
            "play_again": {
                "text": "Play Again",
                "pos": (screen.get_width() * 0.3, screen.get_height() * 0.7),
            },
            "quit_game": {
                "text": "Quit Game",
                "pos": (screen.get_width() * 0.6, screen.get_height() * 0.7),
            },
        }

    def render(self):
        self.render_background(self.background_color)  # Use BaseScreen's render_background method

        # Display the final scores
        y_offset = self.screen.get_height() * 0.2
        for player in self.players:
            score_text = f"{player.name}: {player.score} points"
            self.render_text(score_text, self.font, (255, 255, 255), (self.screen.get_width() * 0.1, y_offset))  # Use BaseScreen's render_text method
            y_offset += self.font.get_height() + 20

        # Display the winner
        winner_text = f"Winner: {self.get_winner()}"
        self.render_text(winner_text, self.font, (255, 215, 0), (self.screen.get_width() * 0.1, y_offset + 20))  # Use BaseScreen's render_text method

        # Draw the buttons
        for key, button in self.buttons.items():
            button_rect = self.render_text(button["text"], self.button_font, (255, 255, 255), button["pos"])  # Use BaseScreen's render_text method
            button["rect"] = button_rect  # Store the rect for event handling

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                for key, button in self.buttons.items():
                    if button["rect"].collidepoint(event.pos):
                        return key  # Return the action (play_again or quit_game)

        return None

    def get_winner(self):
        max_score = max(player.score for player in self.players)
        winners = [player.name for player in self.players if player.score == max_score]
        return ", ".join(winners) if len(winners) > 1 else winners[0]
