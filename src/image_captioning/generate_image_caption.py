import os
import warnings
import open_clip
import torch
from PIL import Image

warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*weights_only=False.*"
)


class ImageCaptionGenerator:
    def __init__(
        self,
        model_name="coca_ViT-L-14",
        pretrained="mscoco_finetuned_laion2B-s13B-b90k",
        device=None,
    ):
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model, _, self.transform = open_clip.create_model_and_transforms(
            model_name, pretrained=pretrained
        )
        self.model = self.model.to(self.device)

    def generate_caption(self, image_path):
        """Generate a caption for the given image."""
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"Failed to load image {image_path}: {e}")
            return None

        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad(), torch.autocast(device_type=self.device.type):
            generated = self.model.generate(image_tensor)

        caption = (
            open_clip.decode(generated[0])
            .split("<end_of_text>")[0]
            .replace("<start_of_text>", "")
        )
        return caption


def generate_captions_for_all_cards(directory):
    """Generate captions for all image files in the specified directory."""
    caption_generator = ImageCaptionGenerator()
    captions = {}

    for filename in os.listdir(directory):
        if filename.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory, filename)
            caption = caption_generator.generate_caption(image_path)
            captions[image_path] = caption
            print(f"Generated Caption for {filename}: {caption}")

    return captions


if __name__ == "__main__":
    cards_directory = "data/cards"
    captions = generate_captions_for_all_cards(cards_directory)

    import json

    with open("data/cards_captions.json", "w") as f:
        json.dump(captions, f, indent=4)

    print("All captions have been generated and saved.")
