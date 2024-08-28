import random
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List
from model.model_manager import ModelManager
from image_captioning.generate_image_caption import ImageCaptionGenerator
from text_processing.abstractor import Abstractor
from text_processing.text_processor import TextProcessor
from similarity.similarity import ImageTextSimilarity

logger = logging.getLogger('game_logic')

class Player(ABC):
    def __init__(self, name: str, player_id: int, model_manager=None):
        self.name = name
        self.player_id = player_id
        self.hand = []
        self.score = 0
        self._model_manager = model_manager

    @abstractmethod
    def storyteller_turn(self) -> Tuple[str, str]:
        pass

    @abstractmethod
    def choose_card(self) -> Optional[str]:
        pass

    @abstractmethod
    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        pass


class Human(Player):
    def storyteller_turn(self) -> Tuple[str, str]:
        logger.info(f"{self.name} (Storyteller) is choosing a card and inputting a clue.")
        chosen_card = self.choose_card()
        clue = self.input_clue()
        return chosen_card, clue

    def choose_card(self) -> Optional[str]:
        if not self.hand:
            logger.error("No cards left to choose from.")
            return None

        print("Your hand:")
        for index, card in enumerate(self.hand):
            print(f"{index + 1}: {card}")

        while True:
            try:
                choice = int(input("Choose a card by entering its number: ")) - 1
                if 0 <= choice < len(self.hand):
                    chosen_card = self.hand.pop(choice)
                    logger.info(f"Card chosen: {chosen_card}")
                    return chosen_card
                else:
                    print("Invalid choice. Please select a valid card number.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def input_clue(self) -> str:
        clue = input("Enter a clue for your card: ").strip()
        logger.info(f"Clue entered: {clue}")
        return clue

    def choose_card_based_on_clue(self, clue: str) -> str:
        return self.choose_card()

    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        if not table:
            logger.error("No cards on the table to vote on.")
            return None

        print("Cards on the table:")
        for index, (player_id, card) in enumerate(table):
            print(f"{index + 1}: {card}")

        while True:
            try:
                vote = int(input("Vote for the card you think belongs to the storyteller by entering its number: ")) - 1
                if 0 <= vote < len(table):
                    logger.info(f"Vote chosen: {vote}")
                    return vote
                else:
                    print("Invalid choice. Please select a valid card number.")
            except ValueError:
                print("Invalid input. Please enter a number.")


class Bot(Player):
    def __init__(self, name: str, model_manager: ModelManager):
        super().__init__(name=name, player_id=None, model_manager=model_manager)
        self._caption_generator = ImageCaptionGenerator(self._model_manager)
        self._similarity_checker = ImageTextSimilarity(self._model_manager)
        self._abstractor = Abstractor()
        self._text_processor = TextProcessor()

    def storyteller_turn(self) -> Tuple[str, str]:
        card = random.choice(self.hand)
        clue = self.generate_clue(card)
        logger.info(f"Bot {self.name} selected card: {card} with clue: {clue}")
        print(f"{self.name} (Storyteller) selected card: {card} with clue: '{clue}'")
        return card, clue

    def generate_clue(self, card: str) -> str:
        caption = self._caption_generator.generate_caption(card)
        obfuscated_caption = self._text_processor.obfuscate_description(caption, self._abstractor)
        return obfuscated_caption

    def choose_card_based_on_clue(self, clue: str) -> Optional[str]:
        if not self.hand:
            logger.error(f"{self.name} has no cards left to choose from based on the clue.")
            return None

        similarities = [
            (self._similarity_checker.compare_image_and_text(card, clue), card)
            for card in self.hand
        ]

        if not similarities:
            logger.error(f"{self.name} could not find any matching cards based on the clue.")
            return None

        best_match = max(similarities, key=lambda x: x[0])
        self.hand.remove(best_match[1])
        logger.info(f"{self.name} chose card based on clue: {best_match[1]}")
        return best_match[1]

    def vote(self, table: List[Tuple[int, str]], clue: str) -> int:
        similarities = [
            (self._similarity_checker.compare_image_and_text(card, clue), i)
            for i, (_, card) in enumerate(table)
        ]
        best_vote = max(similarities, key=lambda x: x[0])
        logger.info(f"Bot {self.name} voted for card index: {best_vote[1]} based on clue: {clue}")
        return best_vote[1]

    def choose_card(self) -> Optional[str]:
        if not self.hand:
            logger.error("Bot has no cards left to choose from.")
            return None

        chosen_card = random.choice(self.hand)
        self.hand.remove(chosen_card)
        logger.info(f"Bot {self.name} chose card: {chosen_card}")
        return chosen_card
