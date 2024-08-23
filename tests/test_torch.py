import torch
import open_clip

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B/32', pretrained='openai')
model.to(device)

# Sample input
text = ["a diagram", "a dog", "a cat"]
tokenized_text = open_clip.tokenize(text).to(device)

# Forward pass
with torch.no_grad():
    text_features = model.encode_text(tokenized_text)

print(text_features.device)
