import random
import os
import openai
import logging
from model_manager import ModelManager
from data_manager import DataManager
from similarity import ImageTextSimilarity
from clue_generator import ClueGenerator

logger = logging.getLogger('game_logic')
data_manager = DataManager()

def log_action(data_manager, role, player_name, **kwargs):
    """
    Helper function to log actions for a player or bot.
    """
    data_entry = {'role': role, 'player': player_name, **kwargs}
    data_manager.log_data(data_entry)
    logger.info(f"Data logged: {data_entry}")

class Player:
    def __init__(self, name, player_id):
        self.name = name
        self.player_id = player_id
        self.hand = []
        self.score = 0
        self.selected_card = None

    def storyteller_turn(self):
        raise NotImplementedError

    def choose_card(self):
        if not self.hand:
            logger.error(f"{self.name} has no cards left to choose from.")
            raise ValueError(f"{self.name} has no cards left.")
        raise NotImplementedError

    def vote(self, table, clue):
        raise NotImplementedError

class Human(Player):
    def storyteller_turn(self):
        """
        Handle the turn for a human storyteller.
        Ask for input and return the chosen card and clue.
        """
        card = self.choose_card()
        self.selected_card = card  # Ensure selected card is set
        clue = input("Enter a clue for the chosen card: ")
        log_action(data_manager, 'storyteller', self.name, card=card, clue=clue)
        return card, clue

    def choose_card(self):
        if not self.hand:
            logger.error(f"{self.name} has no cards left to choose from.")
            raise ValueError(f"{self.name} has no cards left.")
        print("\nYour hand:")
        for index, card in enumerate(self.hand):
            print(f"{index + 1}: {card}")
        while True:
            try:
                choice = int(input("Choose a card by entering its number: ")) - 1
                if 0 <= choice < len(self.hand):
                    chosen_card = self.hand.pop(choice)
                    self.selected_card = chosen_card
                    log_action(data_manager, 'player', self.name, action='choose_card', chosen_card=chosen_card)
                    return chosen_card
                else:
                    logger.warning(f"{self.name} made an invalid choice: {choice + 1}")
                    print("Invalid choice. Please select a valid card number.")
            except ValueError:
                logger.error(f"{self.name} input invalid. Prompting again for valid input.")
                print("Invalid input. Please enter a valid number.")

    def vote(self, table, clue):
        print("\nCards on the table:")
        for index, (player_id, card) in enumerate(table):
            print(f"{index + 1}: {card}")
        while True:
            try:
                vote = int(input("Vote for the card you think belongs to the storyteller by entering its number: ")) - 1
                if 0 <= vote < len(table):
                    log_action(data_manager, 'player', self.name, action='vote', vote=vote)
                    return vote
                else:
                    logger.warning(f"{self.name} made an invalid vote choice: {vote + 1}")
                    print("Invalid choice. Please select a valid card number.")
            except ValueError:
                logger.error(f"{self.name} input invalid. Prompting again for valid input.")
                print("Invalid input. Please enter a number.")
                

class Bot(Player):
    def __init__(self, name, player_id=None, model_manager=None, api_key=None):
        super().__init__(name, player_id)
        self.model_manager = model_manager or ModelManager()
        self.similarity_checker = ImageTextSimilarity(self.model_manager)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for OpenAI.")
        openai.api_key = self.api_key

    def storyteller_turn(self, temperature=0.8):
        if not self.hand:
            logger.error(f"{self.name} has no cards left to choose from.")
            return None, None
        card = random.choice(self.hand)
        self.selected_card = card
        clue = self.generate_clue(card, temperature)
        log_action(data_manager, 'storyteller', self.name, card=card, clue=clue)
        return card, clue

    def generate_clue(self, card, temperature):
        try:
            clue_generator = ClueGenerator(api_key=self.api_key)
            clue = clue_generator.generate_clue(card)
            logger.info(f"Generated clue for card '{card}': {clue}")
            return clue
        except Exception as e:
            logger.error(f"Error generating clue for card '{card}': {e}")
            log_action(data_manager, 'storyteller', self.name, card=card, error=str(e))
            return "Fallback Clue"

    def choose_card(self):
        if not self.hand:
            raise ValueError(f"{self.name} has no cards left to choose from.")
        chosen_card = random.choice(self.hand)
        self.hand.remove(chosen_card)
        self.selected_card = chosen_card
        log_action(data_manager, 'player', self.name, action='choose_card', chosen_card=chosen_card)
        return chosen_card

    def player_turn(self, clue, cards):
        logger.info(f"{self.name} (Player) analyzing clue: '{clue}'")
        card_scores = self.rank_cards(clue, cards)
        selected_card = max(card_scores, key=card_scores.get)
        log_action(data_manager, 'player', self.name, clue=clue, selected_card=selected_card)
        return selected_card

    def rank_cards(self, clue, cards):
        card_scores = {}
        for card in cards:
            score = self.similarity_checker.compare_image_and_text(card, clue)
            logger.debug(f"Score for card '{card}' with clue '{clue}': {score}")
            card_scores[card] = score
        return card_scores

    def vote(self, table, clue):
        card_scores = self.rank_cards(clue, [card for player_id, card in table])
        selected_card = max(card_scores, key=card_scores.get)
        selected_card_index = [card for player_id, card in table].index(selected_card)
        log_action(data_manager, 'player', self.name, action='vote', selected_card_index=selected_card_index)
        return selected_card_index