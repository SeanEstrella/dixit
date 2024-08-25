class Human:
    _id_counter = 0

    def __init__(self, name):
        self.id = Human._id_counter
        Human._id_counter += 1
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