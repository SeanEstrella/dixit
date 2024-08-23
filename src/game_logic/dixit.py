import os
import random
import open_clip
import torch
from PIL import Image
from game_logic.player import Player


def setup_game(num_players):
    players = []
    for i in range(num_players):
        name = input(f"Enter name for player {i + 1}: ")
        players.append(Player(name))
    return players

def deal_cards(players, cur_deck):
    deck = random.shuffle(cur_deck)
    for player in players:
        for _ in range(num_cards):
            player.hand.append(deck.pop())
    return deck

def storyteller_turn(storyteller):
    print(f"\n{storyteller.name} is the storyteller!")
    card = storyteller.choose_card()
    clue = input("Enter a clue for your card: ")
    return card, clue

def collect_cards(players, storyteller_card, storyteller):
    table = [(storyteller.id, storyteller_card)]
    played_cards = [(storyteller.id, storyteller_card)]
    for player in players:
        if player != storyteller:
            chosen_card = player.choose_card()
            table.append((player.id, chosen_card))
            played_cards.append((player.id, chosen_card))
    random.shuffle(table)
    return table, played_cards

def score_round(players, storyteller, storyteller_card, table, votes):
    storyteller_card_index = next(i for i, (player_id, card) in enumerate(table) if card == storyteller_card)
    correct_votes = votes.count(storyteller_card_index)

    if correct_votes == 0 or correct_votes == len(players) - 1:
        # If all or none of the players found the storyteller's image
        for player in players:
            if player != storyteller:
                player.score += 2
    else:
        # Storyteller and those who found the correct image score 3 points
        storyteller.score += 3
        for player, vote in zip(players, votes):
            if vote == storyteller_card_index and player != storyteller:
                player.score += 3

    # Each player, except the storyteller, scores 1 point for each vote on their card
    for i, player in enumerate(players):
        if player != storyteller:
            player_votes = sum(1 for vote in votes if table[vote][0] == player.id)
            player.score += player_votes

def play_game(players):
    while True:
        for storyteller in players:
            storyteller_card, clue = storyteller_turn(storyteller)
            print(f"\nClue: {clue}\n")
            table, played_cards = collect_cards(players, storyteller_card, storyteller)
            votes = []
            for player in players:
                if player != storyteller:
                    votes.append(player.vote(table))
            score_round(players, storyteller, storyteller_card, table, votes)
            print("\nScores:")
            for player in players:
                print(f"{player.name}: {player.score} points")

            cont = input("\nPlay another round? (y/n): ")
            if cont.lower() != 'y':
                print("\nFinal Scores:")
                for player in players:
                    print(f"{player.name}: {player.score} points")
                return
            
            deal_cards(players, 1)

# makes the images (deck) array
def load_images_from_directory(directory):
    initial_deck = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.join(directory, filename)
            initial_deck.append(name)
    return initial_deck


if __name__ == "__main__":
    print("Welcome to Dixit!")
    num_players = int(input("Enter number of players: "))
    players = setup_game(num_players)

    # deck initialization 
    all_cards = {}
    deck = load_images_from_directory("./cards")
    cur_deck = deal_cards(players, 6)
    play_game(players)
