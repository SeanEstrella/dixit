import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION
from ui.base_screen import BaseScreen

class MainMenu(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.background_color = (0, 0, 128)  # Blue background color
        self.font = self.load_font(74)
        self.button_font = self.load_font(50)
        self.buttons = [
            {"text": "Start Game", "position": (100, 200), "font": self.button_font, "color": (255, 255, 255), "center": False},
            {"text": "Options", "position": (100, 300), "font": self.button_font, "color": (255, 255, 255), "center": False},
            {"text": "Quit", "position": (100, 400), "font": self.button_font, "color": (255, 255, 255), "center": False},
        ]
        self.highlighted_button = None
        self.create_button_surfaces()

    def create_button_surfaces(self):
        """Prepare the button surfaces and rectangles."""
        for button in self.buttons:
            button["surface"] = button["font"].render(button["text"], True, button["color"])
            button["rect"] = button["surface"].get_rect(topleft=button["position"])

    def render(self):
        """Render the main menu."""
        self.render_background(self.background_color)
        self.render_text("Dixit", self.font, (255, 255, 255), (100, 100))
        self.render_buttons(self.buttons)
        pygame.display.flip()

    def handle_events(self):
        """Handle main menu events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                self.handle_mouse_motion(event.pos)
            elif event.type == MOUSEBUTTONDOWN:
                return self.handle_mouse_click()
        return None

    def handle_mouse_motion(self, mouse_pos):
        """Handle mouse motion to highlight buttons."""
        for button in self.buttons:
            if button["rect"].collidepoint(mouse_pos):
                if self.highlighted_button != button:
                    button["surface"] = button["font"].render(button["text"], True, (255, 255, 0))
                    self.highlighted_button = button
            else:
                button["surface"] = button["font"].render(button["text"], True, button["color"])

        # Re-render the buttons with updated surfaces
        self.render_buttons(self.buttons)

    def handle_mouse_click(self):
        """Handle mouse click to select the highlighted button."""
        if self.highlighted_button:
            print(f"Button '{self.highlighted_button['text']}' clicked.")
            return self.highlighted_button["text"]
        return None
