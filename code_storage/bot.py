import random
import json
from PIL import Image
import open_clip
import torch
import pygame
import logging
from model.model_manager import ModelManager

logging.basicConfig(
    filename="bot_decisions.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class Bot:
    _id_counter = 0

    def __init__(self, model_manager):
        self.id = Bot._id_counter
        Bot._id_counter += 1
        self.name = f"Bot #{self.id}"
        self.hand = []
        self.score = 0
        self.model, self.transform, self.device = model_manager.initialize_model()
        self.captions = self.load_captions()
        self.logger = logging.getLogger(self.name)

    def load_captions(self):
        try:
            with open("data/cards_captions.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading captions: {e}")
            return {}

    def choose_card(self, description, screen):
        best_card = max(
            self.hand,
            key=lambda card: self.compute_similarity(card, description),
            default=None,
        )
        if best_card:
            self.logger.info(f"{self.name} chose card {best_card}")
            self.hand.remove(best_card)
        return best_card

    def compute_similarity(self, card, description):
        try:
            image = Image.open(card).convert("RGB")
            image_input = self.transform(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                text_input = open_clip.tokenize([description]).to(self.device)
                text_features = self.model.encode_text(text_input)
                similarity = torch.nn.functional.cosine_similarity(
                    image_features, text_features
                )

            self.logger.debug(f"Card {card}: similarity score = {similarity.item()}")
            return similarity.item()
        except Exception as e:
            self.logger.error(f"Error processing card {card}: {e}")
            return -float("inf")

    def vote(self, table, description, screen):
        best_vote = max(
            enumerate(table),
            key=lambda item: self.compute_similarity(item[1][1], description),
            default=(None, None),
        )[0]
        self.logger.info(f"{self.name} voted for card {table[best_vote][1]}")
        return best_vote

    def storyteller_turn(self, screen):
        self.logger.info(f"{self.name} is the storyteller!")
        font = pygame.font.Font(None, 50)
        text = font.render(f"{self.name} is the storyteller!", True, (255, 255, 255))
        screen.blit(text, (100, 100))
        pygame.display.flip()
        pygame.time.wait(2000)

        card = random.choice(self.hand)
        clue = self.captions.get(card, "No description available")
        self.logger.debug(f"Clue for card {card}: {clue}")
        self.hand.remove(card)
        return card, clue

    def choose_card_based_on_clue(self, clue, screen):
        return self.choose_card(clue, screen)
