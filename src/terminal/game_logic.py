import logging
from typing import List
from model.model_manager import ModelManager
from players import Player, Human, Bot
from deck import setup_deck, deal_cards
from scoring import collect_cards_from_players, collect_votes_from_players, handle_round_end

logger = logging.getLogger('game_logic')

WINNING_SCORE = 30
NUM_CARDS = 6

def terminal_game_loop():
    model_manager = ModelManager()
    players = setup_players(model_manager)
    deck, discard_pile = setup_deck()

    storyteller = players[0]

    while True:
        print(f"\nNew Round: {storyteller.name} is the storyteller.")
        deck = deal_cards(players, deck, discard_pile, NUM_CARDS)

        card, clue = storyteller.storyteller_turn()
        table = collect_cards_from_players(players, card, storyteller, clue)
        votes = collect_votes_from_players(players, storyteller, table, clue)

        game_over = handle_round_end(players, votes, table, storyteller, deck, discard_pile)

        if game_over:
            break

        storyteller = rotate_storyteller(players, storyteller)

    print("Game Over! Thanks for playing!")


def setup_players(model_manager: ModelManager) -> List[Player]:
    player_names = input("Enter player names, separated by commas: ").split(',')
    player_names = [name.strip() for name in player_names if name.strip()]
    num_bots = int(input("Enter the number of bots: "))

    players = [Human(name=name, player_id=i) for i, name in enumerate(player_names)]
    players.extend(Bot(name=f"Bot #{i+1}", model_manager=model_manager) for i in range(num_bots))
    
    return players


def rotate_storyteller(players: List[Player], current_storyteller: Player) -> Player:
    next_index = (players.index(current_storyteller) + 1) % len(players)
    return players[next_index]
