import pygame
import sys
import random
from typing import Optional, List, Tuple
from pygame.locals import QUIT, MOUSEBUTTONDOWN
from model.model_manager import ModelManager
from image_captioning.generate_image_caption import ImageCaptionGenerator
from text_processing.abstractor import Abstractor
from text_processing.text_processor import TextProcessor
from similarity.similarity import ImageTextSimilarity
from ui.rendering import Renderer
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger('game_logic')

class Player(ABC):
    def __init__(
        self,
        name: str,
        player_id: int,
        screen=None,
        font=None,
        model_manager: Optional[ModelManager] = None,
        abstractor: Optional[Abstractor] = None,
        text_processor: Optional[TextProcessor] = None,
        similarity_checker: Optional[ImageTextSimilarity] = None,
        caption_generator: Optional[ImageCaptionGenerator] = None,
    ):
        self.name = name
        self.player_id = player_id
        self.screen = screen
        self.font = font or pygame.font.Font(None, 50)
        self.renderer = Renderer(screen)  # Use Renderer class
        self.hand = []
        self.score = 0  # Initialize the score attribute
        self._model_manager = model_manager
        self._abstractor = abstractor
        self._text_processor = text_processor
        self._similarity_checker = similarity_checker
        self._caption_generator = caption_generator

    @property
    def model_manager(self) -> ModelManager:
        if self._model_manager is None:
            self._model_manager = ModelManager()
        return self._model_manager

    @property
    def abstractor(self) -> Abstractor:
        if self._abstractor is None:
            self._abstractor = Abstractor()
        return self._abstractor

    @property
    def text_processor(self) -> TextProcessor:
        if self._text_processor is None:
            self._text_processor = TextProcessor()
        return self._text_processor

    @property
    def similarity_checker(self) -> ImageTextSimilarity:
        if self._similarity_checker is None:
            self._similarity_checker = ImageTextSimilarity(self.model_manager)
        return self._similarity_checker

    @property
    def caption_generator(self) -> ImageCaptionGenerator:
        if self._caption_generator is None:
            self._caption_generator = ImageCaptionGenerator(self.model_manager)
        return self._caption_generator

    def generate_caption_for_image(self, image_path: str) -> str:
        """Generate a caption for a given image."""
        logger.debug(f"Generating caption for image: {image_path}")
        return self.caption_generator.generate_caption(image_path)

    def compute_similarity(self, image_path: str, text_description: str) -> float:
        """Compute the similarity between an image and a text description."""
        logger.debug(f"Computing similarity between image: {image_path} and text: '{text_description}'")
        return self.similarity_checker.compare_image_and_text(image_path, text_description)

    @abstractmethod
    def storyteller_turn(self) -> Tuple[str, str]:
        """Abstract method to be implemented by subclasses."""
        pass

    @abstractmethod
    def choose_card_based_on_clue(self, clue: str) -> str:
        """Abstract method to be implemented by subclasses."""
        pass

    @abstractmethod
    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        """Abstract method to be implemented by subclasses."""
        pass


class Human(Player):
    def __init__(self, name: str, player_id: int, screen):
        super().__init__(name=name, player_id=player_id, screen=screen)
        self.selected_card_index = None
        self.selected_vote_index = None

    def storyteller_turn(self) -> Tuple[str, str]:
        """Handles the storyteller's turn by allowing the player to choose a card and input a clue."""
        logger.info(f"{self.name} (Storyteller) is choosing a card and inputting a clue.")
        chosen_card = self.choose_card()
        clue = self.input_clue()
        return chosen_card, clue

    def choose_card(self) -> Optional[str]:
        """Allows the human player to choose a card from their hand."""
        if not self.hand:
            logger.error("No cards left to choose from.")
            return None

        while self.selected_card_index is None:
            self._render_with_background(self.render_hand)
            pygame.display.flip()
            self.handle_events_card_selection()

        if not (0 <= self.selected_card_index < len(self.hand)):
            logger.error(f"Selected card index {self.selected_card_index} is out of range.")
            return None

        chosen_card = self.hand.pop(self.selected_card_index)
        logger.info(f"Card chosen: {chosen_card}")
        self.selected_card_index = None
        return chosen_card

    def input_clue(self) -> str:
        """Allows the human player to input a clue for the chosen card."""
        clue = self._input_text("Enter a clue for your card:")
        logger.info(f"Clue entered: {clue}")
        return clue

    def choose_card_based_on_clue(self, clue: str) -> str:
        """Allows the human player to choose a card based on the given clue."""
        return self.choose_card()

    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        """Allows the human player to vote on which card they think is the storyteller's card."""
        if not table:
            logger.error("No cards on the table to vote on.")
            return None

        while self.selected_vote_index is None:
            self._render_with_background(lambda: self.render_table(table))
            pygame.display.flip()
            self.handle_events_vote_selection(table)

        chosen_vote = self.selected_vote_index
        logger.info(f"Vote chosen: {chosen_vote}")
        self.selected_vote_index = None
        return chosen_vote

    def render_hand(self):
        """Renders the human player's hand on the screen."""
        self.renderer.render_hand(self.hand, self.selected_card_index)

    def render_table(self, table: List[Tuple[int, str]]):
        """Renders the voting table on the screen."""
        y_offset = 200
        self.renderer.render_text(
            f"{self.name}, vote for the card you think is the storyteller's card:", 
            self.font, (255, 255, 255), (100, 100)
        )
        for i, (player_id, card) in enumerate(table):
            card_rect = self.renderer.render_text(f"Card {i + 1}: {card}", self.font, (255, 255, 255), (100, y_offset))
            if self.selected_vote_index == i:
                pygame.draw.rect(self.screen, (255, 255, 0), card_rect.inflate(10, 10), 2)
            y_offset += 50

    def handle_events_card_selection(self):
        """Handles mouse events for card selection."""
        self._handle_mouse_events(self.handle_card_click)

    def handle_events_vote_selection(self, table: List[Tuple[int, str]]):
        """Handles mouse events for vote selection."""
        self._handle_mouse_events(lambda pos: self.handle_vote_click(pos, table))

    def _handle_mouse_events(self, click_handler):
        """Handles generic mouse events for clicking on objects."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                click_handler(event.pos)

    def handle_card_click(self, mouse_pos):
        """Handles the logic when a card is clicked."""
        self.selected_card_index = self._handle_click(self.hand, mouse_pos)

    def handle_vote_click(self, mouse_pos, table: List[Tuple[int, str]]):
        """Handles the logic when a vote is clicked."""
        self.selected_vote_index = self._handle_click([card for _, card in table], mouse_pos)

    def _handle_click(self, items, mouse_pos):
        """Helper function to handle clicking logic."""
        x_offset = 50
        y_position = self.screen.get_height() * 0.75 if items == self.hand else 200
        for i, item in enumerate(items):
            card_rect = self.renderer.render_card(item, (x_offset, y_position))
            if card_rect.collidepoint(mouse_pos):
                logger.debug(f"Item clicked: {item} at index {i}")
                return i
            x_offset += card_rect.width + 20
        return None

    def _render_with_background(self, render_function):
        """Renders the background and then executes the provided rendering function."""
        self.renderer.render_background("data/images/background.jpg")
        render_function()

    def _input_text(self, prompt: str) -> str:
        """Handles text input for user prompts."""
        clue = ""
        input_active = True
        while input_active:
            self.renderer.render_background("data/images/background.jpg")
            self.renderer.render_text(prompt, self.font, (255, 255, 255), (100, 100))
            self.renderer.render_text(clue, self.font, (255, 255, 255), (100, 150))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        clue = clue[:-1]
                    else:
                        clue += event.unicode
        return clue


class Bot(Player):
    def __init__(self, name: str, model_manager: ModelManager):
        super().__init__(
            name=name,
            player_id=None, 
            model_manager=model_manager,
            screen=None,
            font=None,
            abstractor=None,
            text_processor=None,
            similarity_checker=None,
            caption_generator=None,
        )
        self._caption_generator = ImageCaptionGenerator(self.model_manager)
        self._similarity_checker = ImageTextSimilarity(self.model_manager)
        self._abstractor = Abstractor()
        self._text_processor = TextProcessor()
        
    def storyteller_turn(self) -> Tuple[str, str]:
        """Bot selects a card and generates a clue."""
        card = random.choice(self.hand)
        clue = self.generate_clue(card)
        logger.info(f"Bot {self.name} selected card: {card} with clue: {clue}")
        return card, clue

    def generate_clue(self, card: str) -> str:
        """Generate a clue for the bot's card using the abstractor and other cards."""
        caption = self.caption_generator.generate_caption(card)
        obfuscated_caption = self.text_processor.obfuscate_description(caption, self.abstractor)
        return obfuscated_caption

    def choose_card_based_on_clue(self, clue: str) -> str:
        """Bot chooses a card based on the given clue using similarity checking."""
        similarities = [
            (self.similarity_checker.compare_image_and_text(card, clue), card)
            for card in self.hand
        ]
        best_match = max(similarities, key=lambda x: x[0])
        self.hand.remove(best_match[1])
        logger.info(f"Bot {self.name} chose card based on clue: {best_match[1]}")
        return best_match[1]

    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        """Bot votes on which card they think is the storyteller's card using similarity checking."""
        similarities = [
            (self.similarity_checker.compare_image_and_text(card, clue), i)
            for i, (_, card) in enumerate(table)
        ]
        best_vote = max(similarities, key=lambda x: x[0])
        logger.info(f"Bot {self.name} voted for card index: {best_vote[1]} based on clue: {clue}")
        return best_vote[1]
