import pygame
import sys

class BaseScreen:
    def __init__(self, screen):
        self.screen = screen

    def load_font(self, size):
        """Load the font and handle any errors."""
        try:
            return pygame.font.Font(None, size)
        except pygame.error as e:
            print(f"Error loading font: {e}")
            pygame.quit()
            sys.exit(1)

    def render_background(self, background_color):
        """Render the background with a specified color."""
        self.screen.fill(background_color)

    def render_text(self, text, font, color, position, center=False):
        """Render text on the screen."""
        text_surface = font.render(text, True, color)
        if center:
            rect = text_surface.get_rect(center=position)
        else:
            rect = text_surface.get_rect(topleft=position)
        self.screen.blit(text_surface, rect.topleft)
        return rect

    def render_button(self, button):
        """Render a single button on the screen."""
        button["surface"] = button["font"].render(button["text"], True, button["color"])
        if button["center"]:
            button["rect"] = button["surface"].get_rect(center=button["position"])
        else:
            button["rect"] = button["surface"].get_rect(topleft=button["position"])
        self.screen.blit(button["surface"], button["rect"].topleft)

    def render_buttons(self, buttons):
        """Render all buttons."""
        for button in buttons:
            self.render_button(button)
