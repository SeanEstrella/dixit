import os
import random
import logging
from players import Player
from typing import List, Tuple

CARDSPATH = "/home/seane/Development/dixit/data/images/cards"

logger = logging.getLogger('game_logic')

def setup_deck() -> Tuple[List[str], List[str]]:
    # image_directory = input("Enter the directory path for image cards: ")
    image_directory = CARDSPATH
    deck = load_images_from_directory(image_directory)
    discard_pile = []
    random.shuffle(deck)
    return deck, discard_pile

def load_images_from_directory(directory: str) -> List[str]:
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    image_files = sorted(
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.lower().endswith((".png", ".jpg", ".jpeg"))
    )
    if not image_files:
        raise FileNotFoundError(f"No image files found in directory {directory}.")
    return image_files

def deal_cards(players: List['Player'], cur_deck: List[str], discard_pile: List[str], num_cards: int) -> List[str]:
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
                logger.warning(f"{player.name} was not dealt a full hand due to insufficient cards.")

    if not cur_deck and not discard_pile:
        logger.warning("Deck and discard pile are empty. No more cards can be dealt.")

    return cur_deck
