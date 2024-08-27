import pygame
import logging
from typing import List, Tuple, Optional, Union

logger = logging.getLogger('ui')

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.image_cache = {}  # Cache for images to optimize loading times

    def render_background(self, background: Union[str, Tuple[int, int, int], Tuple[int, int, int, int]]):
        """Render the background with either a specified image or a solid color."""
        if isinstance(background, str):
            background_image = self._load_image(background)
            if background_image:
                self.screen.blit(background_image, (0, 0))
                logger.debug("Background image rendered successfully.")
            else:
                self._render_fallback_background()
        elif isinstance(background, tuple):
            if len(background) == 3 or len(background) == 4:
                self.screen.fill(background)
                logger.debug("Background color rendered successfully.")
            else:
                logger.error("Invalid RGB(A) tuple for background color.")
                self._render_fallback_background()
        else:
            logger.error("Invalid background parameter passed to render_background.")
            self._render_fallback_background()

    def render_hand(self, hand: List[str], selected_card_index: Optional[int] = None):
        """Render the player's hand of cards."""
        x_offset = 50
        y_position = self.screen.get_height() * 0.75
        card_positions = []
        for i, card_path in enumerate(hand):
            card_rect = self.render_card(card_path, (x_offset, y_position))
            card_positions.append(card_rect)
            if selected_card_index == i:
                pygame.draw.rect(self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2)
            x_offset += card_rect.width + 20
        return card_positions

    def render_card(self, card_path: str, position: Tuple[int, int]):
        """Render a single card, using caching to optimize performance."""
        cache_key = (card_path, int(self.screen.get_width() * 0.1), int(self.screen.get_height() * 0.2))
        if cache_key not in self.image_cache:
            card_image = self._load_image(card_path)
            if card_image:
                card_image = pygame.transform.scale(card_image, (cache_key[1], cache_key[2]))
                self.image_cache[cache_key] = card_image
            else:
                return pygame.Rect(position[0], position[1], 0, 0)

        card_rect = self.image_cache[cache_key].get_rect(topleft=position)
        self.screen.blit(self.image_cache[cache_key], card_rect)
        logger.debug(f"Card {card_path} rendered successfully.")
        return card_rect

    def render_text(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int], position: Tuple[int, int], center: bool = False):
        """Render text on the screen with an optional centering feature."""
        text_surface = font.render(text, True, color)
        if center:
            position = text_surface.get_rect(center=position).topleft
        self.screen.blit(text_surface, position)
        logger.debug(f"Text '{text}' rendered successfully at position {position}.")
        return text_surface.get_rect(topleft=position)

    def render_loading_bar(self, progress: int, bar_rect: pygame.Rect, bar_color: Tuple[int, int, int] = (255, 255, 255), background_color: Tuple[int, int, int] = (0, 0, 0)):
        """Render a loading bar with a specified progress."""
        self.screen.fill(background_color)
        pygame.draw.rect(self.screen, bar_color, bar_rect)
        logger.debug(f"Loading bar rendered with progress: {progress}%.")

    def render_loading_screen(self, loading_font: pygame.font.Font, loading_text: str, progress: int, screen_center: Tuple[int, int]):
        """Render the loading screen with text and a loading bar."""
        text_surface = loading_font.render(loading_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=screen_center)
        self.screen.blit(text_surface, text_rect)
        logger.debug(f"Loading screen rendered with text: {loading_text}.")

    def render_table(self, table: List[Tuple[int, str]], font: pygame.font.Font, selected_vote_index: Optional[int] = None):
        """Render the table of cards for voting."""
        y_offset = 200
        card_rects = []
        for i, (player_id, card) in enumerate(table):
            card_rect = self.render_text(f"Card {i + 1}: {card}", font, (255, 255, 255), (100, y_offset))
            card_rects.append(card_rect)
            if selected_vote_index == i:
                pygame.draw.rect(self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2)
            y_offset += 50
        return card_rects

    def render_selected_cards(self, selected_cards: List[str], x_percentage: float = 0.05, y_percentage: float = 0.3):
        """Render the selected cards on the table."""
        x_offset = self.screen.get_width() * x_percentage
        y_position = self.screen.get_height() * y_percentage
        card_width = self.screen.get_width() * 0.1
        card_height = self.screen.get_height() * 0.2

        for card_path in selected_cards:
            card_image = self.render_card(card_path, (x_offset, y_position))
            x_offset += card_image.width + 20

    def _load_image(self, path: str) -> Optional[pygame.Surface]:
        """Load an image from a given path, with error handling."""
        try:
            return pygame.image.load(path)
        except pygame.error as e:
            logger.error(f"Error loading image {path}: {e}")
            return None

    def _render_fallback_background(self):
        """Render a fallback background (black screen) if an error occurs."""
        self.screen.fill((0, 0, 0))
        logger.debug("Fallback background rendered.")
