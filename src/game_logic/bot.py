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