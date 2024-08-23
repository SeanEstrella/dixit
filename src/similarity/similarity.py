import warnings
import open_clip
from PIL import Image
import torch

warnings.filterwarnings("ignore", category=FutureWarning, message=".*weights_only=False.*")

class ImageTextSimilarity:
    def __init__(self, model_name='ViT-B-32', pretrained='laion2b_e16', device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
        self.tokenizer = open_clip.get_tokenizer(model_name)
        
        self.model.to(self.device)

    def encode_image(self, image_path):
        """Encode an image into a feature vector."""
        image = Image.open(image_path)
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
        
        return image_features

    def encode_text(self, text):
        """Encode a text description into a feature vector."""
        text_input = self.tokenizer([text]).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.encode_text(text_input)
        
        return text_features

    def compute_similarity(self, image_features, text_features):
        """Compute the cosine similarity between image and text feature vectors."""
        similarities = torch.nn.functional.cosine_similarity(image_features, text_features)
        return similarities

    def compare_image_and_text(self, image_path, text_description):
        """High-level method to compare an image with a text description."""
        image_features = self.encode_image(image_path)
        text_features = self.encode_text(text_description)
        similarity_score = self.compute_similarity(image_features, text_features)
        return similarity_score.item()
    
if __name__ == "__main__":
    similarity_checker = ImageTextSimilarity()

    image_path = "../data/image.png"
    text_description = "A photo of ballet pointe shoes"
    
    similarity = similarity_checker.compare_image_and_text(image_path, text_description)
    print(f"Similarity score: {similarity}")
