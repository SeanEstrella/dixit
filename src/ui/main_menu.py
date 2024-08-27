import pygame
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEMOTION
from ui.base_screen import BaseScreen
import logging
from typing import List, Optional, Dict, Union, Tuple

logger = logging.getLogger('ui')

class MainMenu(BaseScreen):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.background_color = (0, 0, 128)  # Blue background color
        self.font = self.load_font(74)
        self.button_font = self.load_font(50)
        self.buttons = self.create_buttons([
            {"text": "Start Game", "position": (100, 200)},
            {"text": "Options", "position": (100, 300)},
            {"text": "Quit", "position": (100, 400)},
        ])
        self.highlighted_button = None

    def create_buttons(self, button_configs: List[Dict[str, Union[str, Tuple[int, int]]]]) -> List[Dict[str, Union[str, pygame.Surface, pygame.Rect]]]:
        """Create button surfaces and rectangles based on the configuration provided."""
        buttons = []
        for config in button_configs:
            button_surface = self.button_font.render(config["text"], True, (255, 255, 255))
            button_rect = button_surface.get_rect(topleft=config["position"])
            buttons.append({
                "text": config["text"],
                "surface": button_surface,
                "rect": button_rect,
                "default_color": (255, 255, 255),
                "highlight_color": (255, 255, 0)
            })
        return buttons

    def render(self):
        """Render the main menu."""
        self.render_background(self.background_color)
        self.render_text("Dixit", self.font, (255, 255, 255), (100, 100))
        self.render_buttons()
        pygame.display.flip()

    def render_buttons(self):
        """Render all buttons."""
        for button in self.buttons:
            self.screen.blit(button["surface"], button["rect"])
        logger.debug("Buttons rendered.")

    def handle_events(self) -> Optional[str]:
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

    def handle_mouse_motion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion to highlight buttons."""
        button_changed = False
        for button in self.buttons:
            if button["rect"].collidepoint(mouse_pos):
                if self.highlighted_button != button:
                    button["surface"] = self.button_font.render(button["text"], True, button["highlight_color"])
                    self.highlighted_button = button
                    button_changed = True
            else:
                if self.highlighted_button == button:
                    button["surface"] = self.button_font.render(button["text"], True, button["default_color"])
                    self.highlighted_button = None
                    button_changed = True

        if button_changed:
            self.render_buttons()
            pygame.display.flip()

    def handle_mouse_click(self) -> Optional[str]:
        """Handle mouse click to select the highlighted button."""
        if self.highlighted_button:
            selected_text = self.highlighted_button["text"]
            logger.info(f"Button '{selected_text}' clicked.")
            return selected_text
        return None
