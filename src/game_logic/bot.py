
class Bot: 
    _id_counter_ = 0
    def __init__(self, name):
        self.id = Player._id_counter
        Player._id_counter += 1
        self.name = f'Bot #{self.id}'
        self.hand = []
        self.score = 0
        
    def choose_card(self):
        print(f"{self.name}, choose a card from your hand:")
        for i, card in enumerate(self.hand):
            print(f"{i + 1}: Card {card}")
        choice = int(input("Enter the number of the card: ")) - 1
        return self.hand.pop(choice)

    def vote(self, table):
        print(f"{self.name}, vote for the card you think is the storyteller's card:")
        for i, card in enumerate(table):
            print(f"{i + 1}: Card {card[1]}")
        vote = int(input("Enter the number of the card: ")) - 1
        return vote

    # does the choosing card component inside of this function because storyteller and player card choice is different
    # does not do any obfuscation on hint right now 
    def storyteller_turn(self):
        print(f"\n{self.name} is the storyteller!")
        self.hand = random.shuffle(self.hand)
        card = self.hand.pop()
        image = Image.open(card).convert("RGB")
        image = transform(im).unsqueeze(0)
        # query openclip with Image itself
        with torch.no_grad(), torch.cuda.amp.autocast():
                generated = model.generate(im)
        clue = (open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", ""))
        return card, clue

# temporary code storage ignore everything beneath this comment for the time being
import os
import random
import open_clip
import torch
from PIL import Image

class Player:
    _id_counter = 0

    def __init__(self, name):
        self.id = Player._id_counter
        Player._id_counter += 1
        self.name = name
        self.hand = []
        self.score = 0

    def choose_card(self):
        print(f"{self.name}, choose a card from your hand:")
        for i, card in enumerate(self.hand):
            print(f"{i + 1}: Card {card}")
        choice = int(input("Enter the number of the card: ")) - 1
        return self.hand.pop(choice)

    def vote(self, table):
        print(f"{self.name}, vote for the card you think is the storyteller's card:")
        for i, card in enumerate(table):
            print(f"{i + 1}: Card {card[1]}")
        vote = int(input("Enter the number of the card: ")) - 1
        return vote

    def storyteller_turn(self):
        print(f"\n{self.name} is the storyteller!")
        card = self.choose_card()
        clue = input("Enter a clue for your card: ")
        return card, clue

class Bot: 
    _id_counter_ = 0
    def __init__(self, name):
        self.id = Player._id_counter
        Player._id_counter += 1
        self.name = f'Bot #{self.id}'
        self.hand = []
        self.score = 0
        
    def choose_card(self):
        print(f"{self.name}, choose a card from your hand:")
        for i, card in enumerate(self.hand):
            print(f"{i + 1}: Card {card}")
        choice = int(input("Enter the number of the card: ")) - 1
        return self.hand.pop(choice)

    def vote(self, table):
        print(f"{self.name}, vote for the card you think is the storyteller's card:")
        for i, card in enumerate(table):
            print(f"{i + 1}: Card {card[1]}")
        vote = int(input("Enter the number of the card: ")) - 1
        return vote

    # does the choosing card component inside of this function because storyteller and player card choice is different
    # does not do any obfuscation on hint right now 
    def storyteller_turn(self):
        print(f"\n{self.name} is the storyteller!")
        self.hand = random.shuffle(self.hand)
        card = self.hand.pop()
        image = Image.open(card).convert("RGB")
        image = transform(im).unsqueeze(0)
        # query openclip with Image itself
        with torch.no_grad(), torch.cuda.amp.autocast():
                generated = model.generate(im)
        clue = (open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", ""))
        return card, clue

def setup_game(num_players):
    players = []
    for i in range(num_players):
        name = input(f"Enter name for player {i + 1}: ")
        players.append(Player(name))
    return players

def deal_cards(players, cur_deck):
    deck = random.shuffle(cur_deck)
    for player in players:
        while player.hand.length < num_cards:
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
            storyteller_card, clue = storyteller.storyteller_turn()
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