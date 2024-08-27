import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION
from utils.rendering import render_text

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.background_color = (0, 0, 128)
        self.font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 50)
        self.buttons = {
            "start_game": {
                "text": "Start Game",
                "pos": (100, 200),
                "surface": None,
                "rect": None,
                "last_color": None,
            },
            "options": {
                "text": "Options",
                "pos": (100, 300),
                "surface": None,
                "rect": None,
                "last_color": None,
            },
            "quit_game": {
                "text": "Quit",
                "pos": (100, 400),
                "surface": None,
                "rect": None,
                "last_color": None,
            },
        }
        self.highlighted_button = None
        self.create_button_surfaces()

    def create_button_surfaces(self):
        """Create surfaces and rects for each button."""
        for key, button in self.buttons.items():
            button["surface"] = self.button_font.render(button["text"], True, (255, 255, 255))
            button["rect"] = button["surface"].get_rect(topleft=button["pos"])
            print(f"Button '{key}' rect created at: {button['rect']}")  # Debug print

    def render(self):
        """Render the main menu."""
        self.screen.fill(self.background_color)
        self.render_title()
        self.render_buttons()
        pygame.display.flip()

    def render_title(self):
        """Render the title of the game."""
        render_text(self.screen, "Dixit", self.font, (255, 255, 255), (100, 100))

    def render_buttons(self):
        """Render all buttons on the main menu."""
        for key, button in self.buttons.items():
            color = (255, 255, 255) if key != self.highlighted_button else (255, 255, 0)
            if button["last_color"] != color:
                button["surface"] = self.button_font.render(button["text"], True, color)
                button["rect"] = button["surface"].get_rect(topleft=button["pos"])
                button["last_color"] = color
            self.screen.blit(button["surface"], button["rect"].topleft)

    def handle_events(self):
        """Handle main menu events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            elif event.type == MOUSEBUTTONDOWN:
                result = self.handle_mouse_click()
                if result:
                    return result
        return None

    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion to highlight buttons."""
        self.highlighted_button = None
        for key, button in self.buttons.items():
            if button["rect"].collidepoint(mouse_pos):
                self.highlighted_button = key

    def handle_mouse_click(self):
        """Handle mouse click to select the highlighted button."""
        if self.highlighted_button:
            print(f"Button '{self.highlighted_button}' clicked.")  # Debug print
            return self.highlighted_button
        return None
