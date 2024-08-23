import torch
import open_clip

def initialize_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, _, transform = open_clip.create_model_and_transforms("coca_ViT-L-14", pretrained="mscoco_finetuned_laion2B-s13B-b90k")
    model = model.to(device)
    return model, transform, device