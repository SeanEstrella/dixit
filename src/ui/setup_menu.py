import pygame
import sys
import logging
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from utils.rendering import render_text
from typing import Tuple, Optional

MAX_PLAYERS = 4
MAX_BOTS = 4

class SetupMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background_color = (0, 0, 128)
        screen_width, screen_height = screen.get_size()
        base_font_size = int(screen_height * 0.05)

        self.font = self._load_font(base_font_size)
        self.buttons = self._initialize_buttons()

        # Initial player counts
        self.num_humans = 0
        self.num_bots = 0

    def _load_font(self, size: int) -> pygame.font.Font:
        """Load the font and handle any errors."""
        try:
            return pygame.font.Font(None, size)
        except pygame.error as e:
            print(f"Error loading font: {e}")
            pygame.quit()
            sys.exit(1)

    def _initialize_buttons(self) -> dict:
        """Initialize the buttons with their text and placeholders for rect."""
        return {
            "increase_humans": {"text": "Increase Human Players", "rect": None},
            "decrease_humans": {"text": "Decrease Human Players", "rect": None},
            "increase_bots": {"text": "Increase Bot Players", "rect": None},
            "decrease_bots": {"text": "Decrease Bot Players", "rect": None},
            "proceed": {"text": "Proceed", "rect": None},
        }

    def render(self):
        """Render the setup menu screen."""
        self.screen.fill(self.background_color)
        self._render_player_counts()
        self._render_buttons()
        pygame.display.flip()

    def _render_player_counts(self):
        """Render the current number of human and bot players."""
        screen_width, screen_height = self.screen.get_size()
        y_offset_top = int(screen_height * 0.1)  # Increased top spacing
        text_spacing = int(screen_height * 0.1)  # Increased spacing between text elements

        render_text(
            self.screen,
            f"Humans: {self.num_humans}",
            self.font,
            (255, 255, 255),
            (int(screen_width * 0.1), y_offset_top),
        )
        render_text(
            self.screen,
            f"Bots: {self.num_bots}",
            self.font,
            (255, 255, 255),
            (int(screen_width * 0.1), y_offset_top + text_spacing),
        )

    def _render_buttons(self):
        """Render all setup menu buttons."""
        screen_width, screen_height = self.screen.get_size()
        y_offset_top = int(screen_height * 0.35)  # Increased distance from the top for buttons
        button_spacing = int(screen_height * 0.15)  # Increased spacing between buttons

        self.buttons["increase_humans"]["rect"] = self._render_button(
            "increase_humans",
            position=(int(screen_width * 0.1), y_offset_top),
        )
        self.buttons["decrease_humans"]["rect"] = self._render_button(
            "decrease_humans",
            position=(
                screen_width - int(screen_width * 0.1) - self.font.size("Decrease Human Players")[0],
                y_offset_top,
            ),
        )
        self.buttons["increase_bots"]["rect"] = self._render_button(
            "increase_bots",
            position=(int(screen_width * 0.1), y_offset_top + button_spacing),
        )
        self.buttons["decrease_bots"]["rect"] = self._render_button(
            "decrease_bots",
            position=(
                screen_width - int(screen_width * 0.1) - self.font.size("Decrease Bot Players")[0],
                y_offset_top + button_spacing,
            ),
        )
        self.buttons["proceed"]["rect"] = self._render_button(
            "proceed", center=True, y_position=screen_height - int(screen_height * 0.1)
        )

    def _render_button(self, key: str, position: Optional[Tuple[int, int]] = None, center: bool = False, y_position: Optional[int] = None) -> pygame.Rect:
        """Render a single button and return its rectangle."""
        # Ensure that only one positioning method is used
        if position is not None and center:
            raise ValueError("Cannot specify both position and center.")

        text_surface = render_text(
            self.screen, self.buttons[key]["text"], self.font, (255, 255, 255), (0, 0)
        )

        if center and y_position is not None:
            rect = text_surface.get_rect(center=(self.screen.get_width() // 2, y_position))
        elif position is not None:
            rect = text_surface.get_rect(topleft=position)
        else:
            raise ValueError("Either position or center must be provided.")

        self.screen.blit(text_surface, rect.topleft)
        return rect

    def handle_events(self) -> Tuple[Optional[str], int, int]:
        """Handle events and return the next screen or updated player counts."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                return self._handle_mouse_click(event.pos)

        return None, self.num_humans, self.num_bots

    def _handle_mouse_click(self, mouse_pos: Tuple[int, int]) -> Tuple[Optional[str], int, int]:
        """Handle mouse clicks and determine which button was clicked."""
        for key, button in self.buttons.items():
            if button["rect"] and button["rect"].collidepoint(mouse_pos):
                logging.info(f"Button clicked: {key}")
                return self._handle_button_click(key)
        return None, self.num_humans, self.num_bots

    def _handle_button_click(self, key: str) -> Tuple[Optional[str], int, int]:
        """Handle a button click event and update the player counts."""
        feedback = None
        if key == "increase_humans":
            if self.num_humans < MAX_PLAYERS:
                self.num_humans += 1
            else:
                feedback = "Maximum human players reached."
        elif key == "decrease_humans":
            if self.num_humans > 0:
                self.num_humans -= 1
            else:
                feedback = "No human players to remove."
        elif key == "increase_bots":
            if self.num_bots < MAX_BOTS:
                self.num_bots += 1
            else:
                feedback = "Maximum bot players reached."
        elif key == "decrease_bots":
            if self.num_bots > 0:
                self.num_bots -= 1
            else:
                feedback = "No bot players to remove."
        elif key == "proceed":
            return "player_name_input_screen", self.num_humans, self.num_bots

        if feedback:
            logging.info(feedback)  # Log feedback for debugging
        return None, self.num_humans, self.num_bots
