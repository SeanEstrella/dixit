import warnings
import open_clip
import torch
from PIL import Image
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning, message=".*weights_only=False.*")

class ImageCaptionGenerator:
    def __init__(self, model_name="coca_ViT-L-14", pretrained="mscoco_finetuned_laion2B-s13B-b90k", device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model, _, self.transform = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
        self.model = self.model.to(self.device)

    def generate_caption(self, image_path):
        """Generate a caption for the given image."""
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad(), torch.autocast(device_type=self.device.type):
            generated = self.model.generate(image_tensor)
        
        caption = open_clip.decode(generated[0]).split("<end_of_text>")[0].replace("<start_of_text>", "")
        return caption

if __name__ == "__main__":
    current_path = Path.cwd()
    print("Current Path:", current_path)

    # List and print all child paths (files and directories)
    print("\nChild Paths:")
    for child in current_path.iterdir():
        print(child)
    image_path = "data/image.png"
    caption_generator = ImageCaptionGenerator()
    
    caption = caption_generator.generate_caption(image_path)
    print("Generated Caption:", caption)
