import warnings
import logging
import torch
from PIL import Image

# Suppress specific FutureWarning related to `weights_only=False`
warnings.filterwarnings(
    "ignore", category=FutureWarning, message=".*weights_only=False.*"
)

logger = logging.getLogger('similarity')

class ImageTextSimilarity:
    def __init__(self, model_manager):
        """
        Initialize the ImageTextSimilarity with a centralized ModelManager.

        Args:
            model_manager: The ModelManager instance managing the model and device.
        """
        self.model = model_manager.get_model()
        self.preprocess = model_manager.get_transform()
        self.tokenizer = model_manager.get_tokenizer()
        self.device = model_manager.get_device()
        logger.info(f"ImageTextSimilarity initialized with model on device: {self.device}")

    def encode_image(self, image_path: str):
        """Encode an image into a feature vector."""
        try:
            image = Image.open(image_path).convert("RGB")
            logger.info(f"Image {image_path} loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        logger.debug(f"Image tensor created for {image_path}.")

        try:
            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
            logger.info(f"Image features encoded successfully for {image_path}.")
            return image_features
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}", exc_info=True)
            return None

    def encode_text(self, text: str):
        """Encode a text description into a feature vector."""
        try:
            text_input = self.tokenizer([text]).to(self.device)
            logger.debug(f"Text tokenized for encoding: {text}")

            with torch.no_grad():
                text_features = self.model.encode_text(text_input)
            logger.info(f"Text features encoded successfully for text: {text}.")
            return text_features
        except Exception as e:
            logger.error(f"Error encoding text: {text}: {e}", exc_info=True)
            return None

    def compute_similarity(self, image_features, text_features):
        """Compute the cosine similarity between image and text feature vectors."""
        if image_features is None or text_features is None:
            logger.warning("One or both feature sets are None, returning zero similarity.")
            return 0.0

        try:
            similarities = torch.nn.functional.cosine_similarity(image_features, text_features)
            logger.debug(f"Cosine similarity computed successfully.")
            return similarities
        except Exception as e:
            logger.error("Error computing similarity:", exc_info=True)
            return 0.0

    def compare_image_and_text(self, image_path: str, text_description: str) -> float:
        """High-level method to compare an image with a text description."""
        logger.info(f"Comparing image '{image_path}' with text '{text_description}'")
        image_features = self.encode_image(image_path)
        text_features = self.encode_text(text_description)
        similarity_score = self.compute_similarity(image_features, text_features)
        logger.info(f"Similarity score for image '{image_path}' and text '{text_description}': {similarity_score.item()}")
        return similarity_score.item()


if __name__ == "__main__":
    from src.main import model_manager  # Import the centralized ModelManager

    logging.basicConfig(level=logging.INFO)

    similarity_checker = ImageTextSimilarity(model_manager)

    image_path = "../data/image.png"  # Update this to your actual image path
    text_description = "A photo of ballet pointe shoes"

    similarity = similarity_checker.compare_image_and_text(image_path, text_description)
    print(f"Similarity score: {similarity}")
