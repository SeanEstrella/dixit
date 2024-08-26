import os
import random
import open_clip
import torch
from PIL import Image
import pygame
from model_manager import ModelManager

model_manager = ModelManager()
model, transform, device = model_manager.initialize_model()


def load_images_from_directory(directory):
    initial_deck = []
    for filename in os.listdir(directory):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            name = os.path.join(directory, filename)
            initial_deck.append(name)
    return initial_deck


def generate_description(imagePath, screen):
    try:
        im = Image.open(imagePath).convert("RGB")
        im = transform(im).unsqueeze(0).to(device)
        with torch.no_grad(), torch.cuda.amp.autocast():
            generated = model.generate(im)
        description = (
            open_clip.decode(generated[0])
            .split("<end_of_text>")[0]
            .replace("<start_of_text>", "")
        )
    except Exception as e:
        print(f"Error generating description for {imagePath}: {e}")
        description = "No description available"

    font = pygame.font.Font(None, 50)
    text = font.render(f"Generated description: {description}", True, (255, 255, 255))
    screen.blit(text, (100, 100))
    pygame.display.flip()
    pygame.time.wait(3000)

    return description


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dixit - Storyteller")

    image_directory = "./cards"
    all_cards = {}
    deck = load_images_from_directory(image_directory)
    random.shuffle(deck)
    hand = [deck.pop() for _ in range(6)]

    while deck:
        random.shuffle(hand)
        current_card = hand.pop()
        if current_card in all_cards:
            current_description = all_cards[current_card]
        else:
            current_description = generate_description(current_card, screen)
            all_cards[current_card] = current_description

        font = pygame.font.Font(None, 50)
        text = font.render(
            f"Storyteller selected card: {current_card}", True, (255, 255, 255)
        )
        screen.blit(text, (100, 100))
        pygame.display.flip()
        pygame.time.wait(3000)

        hand.append(deck.pop())


if __name__ == "__main__":
    main()
