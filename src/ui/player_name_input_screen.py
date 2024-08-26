import pygame
import sys
from pygame.locals import QUIT, KEYDOWN, K_BACKSPACE, K_RETURN

MAX_NAME_LENGTH = 15  # Maximum length for a player's name


class PlayerNameInputScreen:
    def __init__(self, screen, num_players):
        self.screen = screen
        self.num_players = num_players
        self.current_player = 0
        self.player_names = []
        self.input_text = ""
        self.font = pygame.font.Font(None, 50)

    def render(self):
        self.screen.fill((0, 0, 128))  # Blue background
        prompt_text = self.font.render(
            f"Enter name for player {self.current_player + 1}:", True, (255, 255, 255)
        )
        self.screen.blit(prompt_text, (100, 100))
        input_text_rendered = self.font.render(self.input_text, True, (255, 255, 255))
        self.screen.blit(input_text_rendered, (100, 150))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.player_names.append(self.input_text)
                    self.input_text = ""
                    self.current_player += 1
                    if self.current_player == self.num_players:
                        return "game_screen", self.player_names
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    self.input_text += event.unicode
        return None, self.player_names
