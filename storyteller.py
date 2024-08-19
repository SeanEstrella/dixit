import os
import random
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# makes the images (deck) array
def load_images_from_directory(directory):
    all_cards = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.join(directory, filename)
            all_cards.append([name, ""])
    return all_cards

def generate_description(imagePath):
    path = imagePath
    # query openclip with imagepath
    return description

def main():
    # Directory where the images are saved
    image_directory = './images'
    # Load images from the directory
    deck = load_images_from_directory(image_directory)
    all_cards = deck

    while(true):

        # Generate descriptions for each image
        description = generate_description(path)
    # Select a card to play the role of the storyteller
    
    
    print(f"Storyteller selected the description for {selected_image}:")
    print(storyteller_description)

if __name__ == "__main__":
    main()