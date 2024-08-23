

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