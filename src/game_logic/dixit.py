import os
import random
from typing import List, Tuple
from game_logic.player import Player, Human, Bot
from model.model_manager import ModelManager

model_manager = ModelManager()


def setup_game(player_names: List[str], num_bots: int, screen, num_players: int) -> List[Player]:
    """
    Initialize the game by setting up human players and bots.

    Args:
        player_names: A list of names for human players.
        num_bots: The number of AI bot players.
        screen: The game screen object.
        num_players: The total number of players.

    Returns:
        A list of Player objects (including both Humans and Bots).
    """
    if num_bots < 0:
        raise ValueError("Number of bots cannot be negative.")
    if len(player_names) == 0:
        raise ValueError("At least one human player is required.")
    if num_players not in {3, 4, 5, 6}:
        raise ValueError("Unsupported number of players. Must be 3, 4, 5, or 6.")

    players = [Human(name=name, player_id=i, screen=screen) for i, name in enumerate(player_names)]
    players.extend(Bot(name=f"Bot #{i+1}", model_manager=model_manager) for i in range(num_bots))

    # Assign voting tokens based on the number of players
    if num_players == 3:
        voting_tokens = list(range(1, 6))
    else:
        voting_tokens = list(range(1, num_players + 1))

    for player in players:
        player.voting_tokens = voting_tokens[:]

    return players


def deal_cards(
    players: List[Player], cur_deck: List[str], num_cards: int = 6
) -> List[str]:
    """
    Deal a specified number of cards to each player.

    Args:
        players: A list of Player objects.
        cur_deck: The current deck of cards.
        num_cards: The number of cards to deal to each player.

    Returns:
        The remaining cards in the deck.
    """
    if not cur_deck:
        raise ValueError("Deck is empty or not initialized.")

    total_needed_cards = len(players) * num_cards
    if len(cur_deck) < total_needed_cards:
        raise ValueError("Not enough cards in the deck to deal to all players.")

    for player in players:
        needed_cards = num_cards - len(player.hand)
        if needed_cards > 0:
            cards_to_deal = min(needed_cards, len(cur_deck))
            player.hand.extend(cur_deck.pop() for _ in range(cards_to_deal))
            if len(player.hand) < num_cards:
                print(f"Warning: Player {player.name} was not dealt a full hand.")

    return cur_deck


def storyteller_turn(storyteller: Human) -> Tuple[str, str]:
    """
    Handle the storyteller's turn to pick a card and provide a clue.

    Args:
        storyteller: The storyteller player.

    Returns:
        A tuple containing the card chosen by the storyteller and the clue provided.

    Raises:
        ValueError: If the storyteller does not have enough cards, does not select a valid card, or provides an invalid clue.
    """
    if not storyteller.hand:
        raise ValueError("Storyteller has no cards to choose from.")

    # The storyteller picks a card and provides a clue
    card, clue = storyteller.storyteller_turn()

    # Validate that a card was selected
    if not card or card not in storyteller.hand:
        raise ValueError("Storyteller must select a valid card from their hand.")

    # Validate that a clue was provided
    if not clue or not isinstance(clue, str) or clue.strip() == "":
        raise ValueError("Storyteller must provide a valid, non-empty clue.")

    # Ensure the card is removed from the storyteller's hand after selection
    storyteller.hand.remove(card)

    return card, clue


def collect_votes(
    players: List[Human],
    storyteller: Human,
    table: List[Tuple[int, str]],
    clue: str,
) -> List[int]:
    """
    Collect votes from all players except the storyteller.

    Args:
        players: A list of Human player objects.
        storyteller: The storyteller player.
        table: The table containing the cards and their corresponding player IDs.
        clue: The clue provided by the storyteller.

    Returns:
        A list of votes from all players except the storyteller.
    """
    if not table or not clue:
        raise ValueError("Table or clue not properly set up for voting.")
    return [player.vote(table, clue) for player in players if player != storyteller]


def collect_cards(
    players: List[Human],
    storyteller_card: str,
    storyteller: Human,
    clue: str,
) -> List[Tuple[int, str]]:
    """
    Collect cards from all players based on the clue given by the storyteller.

    Args:
        players: A list of Human player objects.
        storyteller_card: The card chosen by the storyteller.
        storyteller: The storyteller player.
        clue: The clue provided by the storyteller.

    Returns:
        A list of tuples containing the player ID and their chosen card.
    """
    if not storyteller_card:
        raise ValueError("Storyteller card not selected.")
    if not players:
        raise ValueError("No players available to collect cards from.")

    table = [(storyteller.id, storyteller_card)]
    for player in players:
        if player != storyteller:
            chosen_card = player.choose_card_based_on_clue(clue)
            table.append((player.id, chosen_card))
    random.shuffle(table)
    return table


def load_images_from_directory(directory: str) -> List[str]:
    """
    Load all image files from a directory into a list.

    Args:
        directory: The path to the directory containing the images.

    Returns:
        A list of paths to the image files.
    """
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
