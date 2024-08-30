import os
import random
import logging
from players import Player
from typing import List, Tuple

CARDSPATH = "data/images/cards"

logger = logging.getLogger('game_logic')

def setup_deck() -> Tuple[List[str], List[str]]:
    """
    Setup the deck by loading images and shuffling the deck.
    Returns a tuple of the deck and the discard pile.
    """
    deck = load_images_from_directory(CARDSPATH)
    discard_pile = []
    random.shuffle(deck)
    logger.info(f"Deck initialized with {len(deck)} cards.")
    return deck, discard_pile

def load_images_from_directory(directory: str) -> List[str]:
    """
    Load all image files from the specified directory.
    Only files with extensions .png, .jpg, or .jpeg are considered valid cards.
    """
    if not os.path.exists(directory):
        logger.error(f"Directory {directory} does not exist.")
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    
    image_files = sorted(
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    
    if not image_files:
        logger.error(f"No image files found in directory {directory}.")
        raise FileNotFoundError(f"No image files found in directory {directory}.")
    
    logger.info(f"Loaded {len(image_files)} cards from {directory}.")
    return image_files

def deal_cards(players: List[Player], cur_deck: List[str], discard_pile: List[str], num_cards: int) -> List[str]:
    """
    Deal cards to players, ensuring each player has the specified number of cards.
    Refill the deck with the discard pile if needed.
    """
    total_needed_cards = len(players) * num_cards
    
    if len(cur_deck) < total_needed_cards and discard_pile:
        logger.info("Reshuffling discard pile into the deck.")
        cur_deck.extend(discard_pile)
        random.shuffle(cur_deck)
        discard_pile.clear()

    for player in players:
        needed_cards = num_cards - len(player.hand)
        if needed_cards > 0:
            available_cards = min(needed_cards, len(cur_deck))
            player.hand.extend(cur_deck.pop() for _ in range(available_cards))
            if len(player.hand) < num_cards:
                logger.warning(f"{player.name} was not dealt a full hand due to insufficient cards. Hand size: {len(player.hand)}")

    if not cur_deck and not discard_pile:
        logger.warning("Deck and discard pile are empty. No more cards can be dealt.")

    logger.info(f"Dealing complete. Remaining cards in deck: {len(cur_deck)}")
    return cur_deck

def initialize_deck() -> List[str]:
    """
    Initialize a deck of cards for the game if the images are not being used.
    Fallback example with card placeholders.
    """
    deck = [f"Card{i}" for i in range(1, 85)]
    random.shuffle(deck)
    logger.info(f"Initialized fallback deck with {len(deck)} cards.")
    return deck
