import sys
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from ui.base_screen import BaseScreen
import logging

logger = logging.getLogger('ui')

MAX_PLAYERS = 4
MAX_BOTS = 4

class SetupMenu(BaseScreen):
    def __init__(self, screen):
        super().__init__(screen)
        self.background_color = (0, 0, 128)
        self.font = self.load_font(int(screen.get_height() * 0.05))
        self.num_humans = 0
        self.num_bots = 0
        self.buttons = self.create_buttons(screen)

    def create_buttons(self, screen):
        """Create and initialize button details."""
        buttons = [
            {"text": "Increase Human Players", "position": (screen.get_width() * 0.1, screen.get_height() * 0.35), "font": self.font, "color": (255, 255, 255), "center": False},
            {"text": "Decrease Human Players", "position": (screen.get_width() * 0.1, screen.get_height() * 0.45), "font": self.font, "color": (255, 255, 255), "center": False},
            {"text": "Increase Bot Players", "position": (screen.get_width() * 0.1, screen.get_height() * 0.55), "font": self.font, "color": (255, 255, 255), "center": False},
            {"text": "Decrease Bot Players", "position": (screen.get_width() * 0.1, screen.get_height() * 0.65), "font": self.font, "color": (255, 255, 255), "center": False},
            {"text": "Proceed", "position": (screen.get_width() // 2, screen.get_height() * 0.9), "font": self.font, "color": (255, 255, 255), "center": True},
        ]

        # Create surfaces and rects for each button
        for button in buttons:
            button["surface"] = button["font"].render(button["text"], True, button["color"])
            button["rect"] = button["surface"].get_rect(center=button["position"] if button["center"] else button["position"])
        
        return buttons

    def render(self):
        """Render the setup menu screen."""
        self.render_background(self.background_color)
        self.render_player_counts()
        self.render_buttons(self.buttons)
        pygame.display.flip()

    def render_player_counts(self):
        """Render the current number of human and bot players."""
        screen_width = self.screen.get_width()
        y_offset_top = self.screen.get_height() * 0.1
        text_spacing = self.screen.get_height() * 0.1

        self.render_text(f"Humans: {self.num_humans}", self.font, (255, 255, 255), (screen_width * 0.1, y_offset_top))
        self.render_text(f"Bots: {self.num_bots}", self.font, (255, 255, 255), (screen_width * 0.1, y_offset_top + text_spacing))

    def handle_events(self):
        """Handle events and return the next screen or updated player counts."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(1)
            elif event.type == MOUSEBUTTONDOWN:
                return self.handle_mouse_click(event.pos)

        return None, self.num_humans, self.num_bots

    def handle_mouse_click(self, mouse_pos):
        """Handle mouse clicks and determine which button was clicked."""
        for button in self.buttons:
            if button["rect"] and button["rect"].collidepoint(mouse_pos):
                print(f"Button clicked: {button['text']}")
                return self.handle_button_click(button["text"])
        return None, self.num_humans, self.num_bots

    def handle_button_click(self, button_text):
        """Handle a button click event and update the player counts."""
        if button_text == "Increase Human Players" and self.num_humans < MAX_PLAYERS:
            self.num_humans += 1
        elif button_text == "Decrease Human Players" and self.num_humans > 0:
            self.num_humans -= 1
        elif button_text == "Increase Bot Players" and self.num_bots < MAX_BOTS:
            self.num_bots += 1
        elif button_text == "Decrease Bot Players" and self.num_bots > 0:
            self.num_bots -= 1
        elif button_text == "Proceed":
            return "player_name_input_screen", self.num_humans, self.num_bots

        return None, self.num_humans, self.num_bots
