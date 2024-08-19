import os
import random
import open_clip
import torch
from PIL import Image

model, _, transform = open_clip.create_model_and_transforms(
  model_name="coca_ViT-L-14",
  pretrained="mscoco_finetuned_laion2B-s13B-b90k"
)


# makes the images (deck) array
def load_images_from_directory(directory):
    all_cards = []
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            name = os.path.join(directory, filename)
            all_cards.append(name)
    return all_cards

def generate_description(imagePath):
    im = Image.open(imagePath).convert("RGB")
    im = transform(im).unsqueeze(0)
    # query openclip with imagepath
    description = (open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", ""))
    return description

def main():
    # Directory where the images are saved
    image_directory = './cards'
    # Initialize all card storage, load images from the directory
    all_cards = {}
    deck = load_images_from_directory(image_directory)
    hand = []
    shuffled_deck = random.shuffle(deck)
    for x in range(5):
        

    while(true):

        # Generate descriptions for each image
        with torch.no_grad(), torch.cuda.amp.autocast():
            generated = model.generate(im)

    
        description = generate_description(path)
    # Select a card to play the role of the storyteller
    
    
    print(f"Storyteller selected the description for {selected_image}:")
    print(storyteller_description)

if __name__ == "__main__":
    main()