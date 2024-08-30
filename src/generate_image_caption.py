import os
import warnings
import logging
import torch
import open_clip
import json
from PIL import Image
from typing import Optional

warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*weights_only=False.*"
)

logger = logging.getLogger('image_captioning')


class ImageCaptionGenerator:
    def __init__(self, model_manager):
        """
        Initialize the ImageCaptionGenerator with a centralized ModelManager.

        Args:
            model_manager: The ModelManager instance managing the model and device.
        """
        self.model = model_manager.get_model()
        self.transform = model_manager.get_transform()
        self.device = model_manager.get_device()
        logger.info(f"ImageCaptionGenerator initialized with model on device: {self.device}")

    def generate_caption(self, image_path: str) -> Optional[str]:
        """
        Generate a caption for the given image.

        Args:
            image_path: The path to the image file.

        Returns:
            The generated caption as a string, or None if an error occurs.
        """
        image = self._load_image(image_path)
        if image is None:
            return None

        image_tensor = self._prepare_image_tensor(image, image_path)
        if image_tensor is None:
            return None

        return self._generate_caption_from_tensor(image_tensor, image_path)

    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load an image from the given path."""
        try:
            image = Image.open(image_path).convert("RGB")
            logger.info(f"Image {image_path} loaded successfully.")
            return image
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

    def _prepare_image_tensor(self, image: Image.Image, image_path: str) -> Optional[torch.Tensor]:
        """Transform the image into a tensor suitable for model input."""
        try:
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            logger.debug(f"Image tensor created for {image_path}, shape: {image_tensor.shape}.")
            return image_tensor
        except Exception as e:
            logger.error(f"Failed to transform image {image_path} into tensor: {e}")
            return None

    def _generate_caption_from_tensor(self, image_tensor: torch.Tensor, image_path: str) -> Optional[str]:
        """Generate a caption from the image tensor using the model."""
        try:
            with torch.no_grad(), torch.autocast(device_type=self.device.type):
                generated = self.model.generate(image_tensor)
            caption = (
                open_clip.decode(generated[0])
                .split("<end_of_text>")[0]
                .replace("<start_of_text>", "")
            )
            logger.info(f"Caption generated for {image_path}: {caption}")
            return caption.strip()
        except Exception as e:
            logger.error(f"Error generating caption for {image_path}: {e}")
            return None


def generate_captions_for_all_images(directory: str, model_manager) -> dict:
    """
    Generate captions for all image files in the specified directory.

    Args:
        directory: The path to the directory containing the images.
        model_manager: The centralized ModelManager instance.

    Returns:
        A dictionary mapping image paths to their generated captions.
    """
    logger.info(f"Generating captions for all images in directory: {directory}")
    caption_generator = ImageCaptionGenerator(model_manager)
    captions = {}

    for filename in os.listdir(directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(directory, filename)
            caption = caption_generator.generate_caption(image_path)
            if caption:
                captions[image_path] = caption
                logger.debug(f"Caption generated for {filename}: {caption}")
            else:
                logger.warning(f"Caption generation failed for {filename}.")

    logger.info(f"Caption generation completed for directory: {directory}")
    return captions


def save_captions_to_file(captions: dict, output_file: str):
    """
    Save the generated captions to a JSON file.

    Args:
        captions: The dictionary of captions to save.
        output_file: The path to the JSON file to save the captions.
    """
    try:
        with open(output_file, "w") as f:
            json.dump(captions, f, indent=4)
        logger.info(f"All captions have been generated and saved to {output_file}.")
    except Exception as e:
        logger.error(f"Failed to save captions to {output_file}: {e}")


if __name__ == "__main__":
    from src.main import model_manager  # Import the centralized ModelManager

    logging.basicConfig(level=logging.INFO)
    
    cards_directory = "data/images/cards"
    captions = generate_captions_for_all_images(cards_directory, model_manager)
    save_captions_to_file(captions, "data/json/cards_captions.json")
