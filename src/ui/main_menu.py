import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (0, 0, 128)  # Blue background color
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 50)
        
        # Define button properties
        self.buttons = {
            'start_game': {'text': 'Start Game', 'pos': (100, 200)},
            'options': {'text': 'Options', 'pos': (100, 300)},
            'quit_game': {'text': 'Quit', 'pos': (100, 400)}
        }
        self.highlighted_button = None

    def render(self):
        self.screen.fill(self.background_color)
        title_text = self.font.render("Dixit", True, (255, 255, 255))
        self.screen.blit(title_text, (100, 100))

        for key, button in self.buttons.items():
            color = (255, 255, 255) if key != self.highlighted_button else (255, 255, 0)
            if button.get('surface') is None or button['last_color'] != color:
                button['surface'] = self.button_font.render(button['text'], True, color)
                button['last_color'] = color
            button['rect'] = button['surface'].get_rect(topleft=button['pos'])
            self.screen.blit(button['surface'], button['pos'])

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                # Highlight button on hover
                self.highlighted_button = None
                for key, button in self.buttons.items():
                    if button['rect'].collidepoint(event.pos):
                        self.highlighted_button = key
            elif event.type == MOUSEBUTTONDOWN:
                for key, button in self.buttons.items():
                    if button['rect'].collidepoint(event.pos):
                        return key  # Return the button key, e.g., 'start_game', 'options', 'quit_game'

        return None
