import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN


class GameOverScreen:
    def __init__(self, screen, players):
        self.screen = screen
        self.players = players
        self.background_color = (0, 0, 128)  # Blue background color
        self.font = pygame.font.Font(None, int(screen.get_height() * 0.08))
        self.button_font = pygame.font.Font(None, int(screen.get_height() * 0.06))
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
        self.screen.fill(self.background_color)

        # Display the final scores
        y_offset = self.screen.get_height() * 0.2
        for player in self.players:
            score_text = self.font.render(
                f"{player.name}: {player.score} points", True, (255, 255, 255)
            )
            self.screen.blit(score_text, (self.screen.get_width() * 0.1, y_offset))
            y_offset += self.font.get_height() + 20

        # Display the winner
        winner_text = self.font.render(
            f"Winner: {self.get_winner()}", True, (255, 215, 0)
        )
        self.screen.blit(winner_text, (self.screen.get_width() * 0.1, y_offset + 20))

        # Draw the buttons
        for key, button in self.buttons.items():
            text_surface = self.button_font.render(
                button["text"], True, (255, 255, 255)
            )
            button["rect"] = text_surface.get_rect(topleft=button["pos"])
            self.screen.blit(text_surface, button["pos"])

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
