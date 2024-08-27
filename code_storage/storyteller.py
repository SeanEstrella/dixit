import os
import random
import open_clip
import torch
from PIL import Image
import pygame
from model.model_manager import ModelManager


class StorytellerBot:
    def __init__(self, model, transform, device, screen):
        self.model = model
        self.transform = transform
        self.device = device
        self.screen = screen
        self.font = pygame.font.Font(None, 50)
        self.all_cards = {}

    def load_images_from_directory(self, directory):
        """Load image file paths from a directory."""
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist.")

        initial_deck = [
            os.path.join(directory, filename)
            for filename in os.listdir(directory)
            if filename.endswith((".png", ".jpg", ".jpeg"))
        ]
        random.shuffle(initial_deck)
        return initial_deck

    def generate_image_description(self, image_path):
        """Generate a description for the provided image using the loaded model."""
        try:
            im = Image.open(image_path).convert("RGB")
            im = self.transform(im).unsqueeze(0).to(self.device)
            with torch.no_grad(), torch.cuda.amp.autocast():
                generated = self.model.generate(im)
            description = (
                open_clip.decode(generated[0])
                .split("<end_of_text>")[0]
                .replace("<start_of_text>", "")
            )
        except Exception as e:
            print(f"Error generating description for {image_path}: {e}")
            description = "No description available"
        return description

    def display_description(self, description):
        """Display the generated description on the screen."""
        text = self.font.render(
            f"Generated description: {description}", True, (255, 255, 255)
        )
        self.screen.fill((0, 0, 128))
        self.screen.blit(text, (100, 100))
        pygame.display.flip()
        pygame.time.wait(3000)

    def storyteller_turn(self, hand):
        """Handle the storyteller bot's turn to select a card and generate a clue."""
        if not hand:
            raise ValueError(
                "The hand is empty. Cannot proceed with the storyteller's turn."
            )

        current_card = hand.pop()
        if current_card in self.all_cards:
            current_description = self.all_cards[current_card]
        else:
            current_description = self.generate_image_description(current_card)
            self.all_cards[current_card] = current_description

        self.display_description(current_description)
        return current_card, current_description

    def run_storyteller_turn(self, deck, hand_size=6):
        """Run the storyteller bot's turn by selecting cards and generating descriptions."""
        hand = [deck.pop() for _ in range(hand_size)]

        while deck:
            current_card, description = self.storyteller_turn(hand)
            hand.append(deck.pop())

        return hand
