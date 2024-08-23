import os
import random
import open_clip
import torch
from PIL import Image

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

model, _, transform = open_clip.create_model_and_transforms(
    model_name="coca_ViT-L-14",
    pretrained="mscoco_finetuned_laion2B-s13B-b90k"
)
model.to(device)


# makes the images (deck) array
def load_images_from_directory(directory):
    initial_deck = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.join(directory, filename)
            initial_deck.append(name)
    return initial_deck

def generate_description(imagePath):
    im = Image.open(imagePath).convert("RGB")
    im = transform(im).unsqueeze(0)
    # query openclip with Image itself
    with torch.no_grad(), torch.cuda.amp.autocast():
            generated = model.generate(im)
    description = (open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", ""))
    return description

def main():
    # Directory where the images are saved
    image_directory = './cards'
    # Initialize all card storage, load images from the directory
    all_cards = {}
    deck = load_images_from_directory(image_directory)
    hand = []
    deck = random.shuffle(deck)

    # Initialize hand with size of 6 
    for x in range(6):
        hand.append(deck.pop())
    
    while (deck.length != 0):
        # Select a card to play the role of the storyteller
        hand = random.shuffle(hand)
        current_card = hand.pop()
        if current_card in all_cards:
            current_description = all_cards[current_card]

        else: 
            current_description = generate_description(current_card)
            all_cards[current_card] = current_description

        print(f"Storyteller selected the following description for {current_card}:")
        print(current_description)
        hand.append(deck.pop())


if __name__ == "__main__":
    main()