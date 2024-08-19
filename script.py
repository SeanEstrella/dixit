import warnings
import open_clip
from PIL import Image
import torch

warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_e16')
tokenizer = open_clip.get_tokenizer('ViT-B-32')

image = Image.open("image.png")
image_input = preprocess(image).unsqueeze(0)

image_features = model.encode_image(image_input)

text_input = tokenizer(["A photo of ballet pointe shoes"])
text_features = model.encode_text(text_input)

similarities = torch.nn.functional.cosine_similarity(image_features, text_features)
print("Similarities:", similarities)
