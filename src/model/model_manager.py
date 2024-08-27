import torch
import open_clip
import os
import warnings


class ModelManager:
    _instance = None

    warnings.filterwarnings(
        "ignore", category=FutureWarning, message=".*weights_only=False.*"
    )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(
        self,
        model_name="coca_ViT-L-14",
        pretrained="mscoco_finetuned_laion2B-s13B-b90k",
    ):
        if self.__initialized:
            return
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        self.pretrained = pretrained
        self.model = None
        self.transform = None
        self.__initialized = True

    def initialize_model(self):
        if self.model is None or self.transform is None:
            print(
                f"Loading model {self.model_name} with pretrained weights: {self.pretrained}"
            )
            try:
                self.model, _, self.transform = open_clip.create_model_and_transforms(
                    self.model_name, pretrained=self.pretrained
                )
                self.model = self.model.to(self.device)
            except Exception as e:
                print(f"Error initializing model: {e}")
                raise
        return self.model, self.transform, self.device

    def load_model_weights(self, weights_path):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weight file not found: {weights_path}")

        if self.model is None:
            self.initialize_model()

        print(f"Loading model weights from {weights_path}")
        try:
            self.model.load_state_dict(
                torch.load(weights_path, map_location=self.device)
            )
        except Exception as e:
            print(f"Error loading model weights: {e}")
            raise

    def save_model_weights(self, save_path):
        if self.model is None:
            raise ValueError("Model must be initialized before saving weights.")

        print(f"Saving model weights to {save_path}")
        try:
            torch.save(self.model.state_dict(), save_path)
        except Exception as e:
            print(f"Error saving model weights: {e}")
            raise

    def get_model(self):
        if self.model is None:
            self.initialize_model()
        return self.model

    def get_transform(self):
        if self.transform is None:
            self.initialize_model()
        return self.transform

    def get_device(self):
        return self.device

    def __enter__(self):
        self.initialize_model()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Perform any necessary cleanup (e.g., freeing GPU memory)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
