import random
from typing import List, Tuple
from players import Player
from deck import deal_cards

def collect_cards_from_players(players: List[Player], storyteller_card: str, storyteller: Player, clue: str) -> List[Tuple[int, str]]:
    table = [(storyteller.player_id, storyteller_card)]
    for player in players:
        if player != storyteller:
            chosen_card = player.choose_card_based_on_clue(clue)
            table.append((player.player_id, chosen_card))
    random.shuffle(table)
    return table

def collect_votes_from_players(players: List[Player], storyteller: Player, table: List[Tuple[int, str]], clue: str) -> List[int]:
    votes = []
    for player in players:
        if player != storyteller:
            vote = player.vote(table, clue)
            votes.append(vote)
    return votes

def handle_round_end(players: List[Player], votes: List[int], table: List[Tuple[int, str]], storyteller: Player, deck: List[str], discard_pile: List[str], num_cards: int, winning_score: int) -> bool:
    calculate_scores(players, votes, table, storyteller)
    discard_pile.extend([card for _, card in table])
    deck = deal_cards(players, deck, discard_pile, num_cards)
    
    print("\n--- Round Summary ---")
    for player in players:
        print(f"{player.name} has {player.score} points.")

    for player in players:
        if player.score >= winning_score:
            print(f"{player.name} has won the game with {player.score} points!")
            return True

    return False

def calculate_scores(players: List[Player], votes: List[int], table: List[Tuple[int, str]], storyteller: Player) -> None:
    storyteller_card_index = next(
        index for index, (pid, card) in enumerate(table) if pid == storyteller.player_id
    )

    correct_votes = sum(1 for vote in votes if vote == storyteller_card_index)

    if correct_votes == 0 or correct_votes == len(players) - 1:
        for player in players:
            if player != storyteller:
                player.score += 2
                print(f"{player.name} earned 2 points!")
    else:
        storyteller.score += 3
        print(f"{storyteller.name} earned 3 points!")
        for player, vote in zip(players, votes):
            if vote == storyteller_card_index:
                player.score += 3
                print(f"{player.name} earned 3 points for guessing the correct card!")
            else:
                player.score += 1
                print(f"{player.name} earned 1 point for voting!")
