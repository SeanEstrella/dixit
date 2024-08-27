import os
import random
import logging
from typing import List, Tuple
from game_logic.player import Player, Human, Bot
from model.model_manager import ModelManager

logger = logging.getLogger('game_logic')

def validate_non_empty_list(items: List, error_message: str):
    """Raise a ValueError if the list is empty."""
    if not items:
        raise ValueError(error_message)

def validate_non_empty_string(value: str, error_message: str):
    """Raise a ValueError if the string is empty or invalid."""
    if not value or not isinstance(value, str) or value.strip() == "":
        raise ValueError(error_message)

def validate_game_setup(player_names: List[str], num_bots: int, num_players: int):
    """Perform validation checks for game setup."""
    if num_bots < 0:
        raise ValueError("Number of bots cannot be negative.")
    if len(player_names) == 0:
        raise ValueError("At least one human player is required.")
    if num_players not in {3, 4, 5, 6}:
        raise ValueError("Unsupported number of players. Must be 3, 4, 5, or 6.")

def create_players(player_names: List[str], num_bots: int, screen, model_manager: ModelManager) -> List[Player]:
    """Create human players and bots."""
    players = [Human(name=name, player_id=i, screen=screen) for i, name in enumerate(player_names)]
    players.extend(Bot(name=f"Bot #{i+1}", model_manager=model_manager) for i in range(num_bots))
    return players

def assign_voting_tokens(players: List[Player], num_players: int):
    """Assign voting tokens to each player."""
    voting_tokens = list(range(1, 6)) if num_players == 3 else list(range(1, num_players + 1))
    for player in players:
        player.voting_tokens = voting_tokens[:]

def setup_game(player_names: List[str], num_bots: int, screen, num_players: int, model_manager: ModelManager) -> List[Player]:
    """Initialize the game by setting up human players and bots."""
    logger.info(f"Setting up game with {len(player_names)} human players and {num_bots} bots.")
    validate_game_setup(player_names, num_bots, num_players)
    players = create_players(player_names, num_bots, screen, model_manager)
    assign_voting_tokens(players, num_players)
    logger.info(f"Game setup complete with {len(players)} players.")
    return players

def deal_cards(players: List[Player], cur_deck: List[str], num_cards: int = 6) -> List[str]:
    """Deal a specified number of cards to each player."""
    logger.info(f"Dealing {num_cards} cards to each player.")
    validate_non_empty_list(cur_deck, "Deck is empty or not initialized.")

    total_needed_cards = len(players) * num_cards
    if len(cur_deck) < total_needed_cards:
        raise ValueError("Not enough cards in the deck to deal to all players.")

    for player in players:
        needed_cards = num_cards - len(player.hand)
        if needed_cards > 0:
            cards_to_deal = min(needed_cards, len(cur_deck))
            player.hand.extend(cur_deck.pop() for _ in range(cards_to_deal))
            if len(player.hand) < num_cards:
                logger.warning(f"Player {player.name} was not dealt a full hand.")

    logger.info(f"Dealing complete. {len(cur_deck)} cards remain in the deck.")
    return cur_deck

def storyteller_turn(storyteller: Human) -> Tuple[str, str]:
    """Handle the storyteller's turn to pick a card and provide a clue."""
    logger.info(f"{storyteller.name} is taking their turn as the storyteller.")
    validate_non_empty_list(storyteller.hand, f"Storyteller {storyteller.name} has no cards to choose from.")

    card, clue = storyteller.storyteller_turn()

    if card not in storyteller.hand:
        raise ValueError(f"Storyteller {storyteller.name} must select a valid card from their hand.")
    validate_non_empty_string(clue, "Storyteller must provide a valid, non-empty clue.")

    storyteller.hand.remove(card)
    logger.info(f"Storyteller {storyteller.name} selected a card and provided a clue.")
    return card, clue

def collect_votes_from_players(players: List[Human], storyteller: Human, table: List[Tuple[int, str]], clue: str) -> List[int]:
    """Collect votes from all players except the storyteller."""
    logger.info(f"Collecting votes based on the clue: {clue}.")
    validate_non_empty_list(table, "Table is not properly set up for voting.")
    validate_non_empty_string(clue, "Clue is not properly set up for voting.")

    votes = [player.vote(table, clue) for player in players if player != storyteller]
    logger.info("Votes collected from all players.")
    return votes

def collect_cards_from_players(players: List[Human], storyteller_card: str, storyteller: Human, clue: str) -> List[Tuple[int, str]]:
    """Collect cards from all players based on the clue given by the storyteller."""
    logger.info(f"Collecting cards from players based on the clue: {clue}.")
    validate_non_empty_string(storyteller_card, "Storyteller card not selected.")
    validate_non_empty_list(players, "No players available to collect cards from.")

    table = [(storyteller.player_id, storyteller_card)]
    for player in players:
        if player != storyteller:
            chosen_card = player.choose_card_based_on_clue(clue)
            table.append((player.player_id, chosen_card))
    
    random.shuffle(table)
    logger.info("Cards collected and shuffled.")
    return table

def load_images_from_directory(directory: str) -> List[str]:
    """Load all image files from a directory into a list."""
    logger.info(f"Loading images from directory: {directory}.")
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")

    image_files = sorted(
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.lower().endswith((".png", ".jpg", ".jpeg"))
    )

    if not image_files:
        raise FileNotFoundError(f"No image files found in directory {directory}.")

    logger.info(f"Loaded {len(image_files)} images from {directory}.")
    return image_files
