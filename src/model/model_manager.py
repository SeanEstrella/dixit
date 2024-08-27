import torch
import open_clip
import os
import warnings
import logging
import time
import threading

logger = logging.getLogger('model')

class ModelManager:
    _instance = None
    _lock = threading.Lock()

    warnings.filterwarnings(
        "ignore", category=FutureWarning, message=".*weights_only=False.*"
    )

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelManager, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(
        self,
        model_name="coca_ViT-L-14",
        pretrained="mscoco_finetuned_laion2B-s13B-b90k",
        quantize=False
    ):
        if self.__initialized:
            return
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if not torch.cuda.is_available():
            logger.warning("CUDA is not available. The model will run on CPU, which may be slower.")
        self.model_name = model_name
        self.pretrained = pretrained
        self.model = None
        self.tokenizer = None
        self.transform = None
        self.quantize = quantize
        self.__initialized = True
        self.model_loading_complete = False
        logger.info(f"ModelManager initialized with device {self.device}")

    def initialize_model(self):
        with self._lock:
            if self.model is None or self.transform is None:
                logger.info(f"Loading model {self.model_name} with pretrained weights: {self.pretrained}")
                try:
                    start_time = time.time()
                    self.model, _, self.transform = open_clip.create_model_and_transforms(
                        self.model_name, pretrained=self.pretrained
                    )
                    self.model = self.model.to(self.device)
                    self.tokenizer = open_clip.get_tokenizer(self.model_name)
                    if self.quantize:
                        self.apply_quantization()
                    load_duration = time.time() - start_time
                    logger.info(f"Model loaded in {load_duration:.2f} seconds on device: {self.device}.")
                    self.model_loading_complete = True
                except Exception as e:
                    logger.error(f"Error initializing model: {e}", exc_info=True)
                    raise
        return self.model, self.transform, self.device

    def apply_quantization(self):
        """Apply dynamic quantization to reduce model size and improve inference speed."""
        if self.model is None:
            raise ValueError("Model must be initialized before applying quantization.")
        logger.info("Applying quantization to the model.")
        try:
            self.model = torch.quantization.quantize_dynamic(
                self.model, {torch.nn.Linear}, dtype=torch.qint8
            )
            logger.info("Model quantization complete.")
        except Exception as e:
            logger.error(f"Error during model quantization: {e}", exc_info=True)
            raise

    def load_model_weights(self, weights_path):
        """Load custom model weights from a given path."""
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weight file not found: {weights_path}")

        self.initialize_model()

        logger.info(f"Loading model weights from {weights_path}")
        try:
            self.model.load_state_dict(
                torch.load(weights_path, map_location=self.device)
            )
            logger.info("Model weights loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading model weights: {e}", exc_info=True)
            raise

    def save_model_weights(self, save_path):
        """Save the current model weights to a specified path."""
        if self.model is None:
            raise ValueError("Model must be initialized before saving weights.")

        logger.info(f"Saving model weights to {save_path}")
        try:
            torch.save(self.model.state_dict(), save_path)
            logger.info("Model weights saved successfully.")
        except Exception as e:
            logger.error(f"Error saving model weights: {e}", exc_info=True)
            raise

    def get_model(self):
        """Return the initialized model, initializing it if necessary."""
        if self.model is None:
            self.initialize_model()
        return self.model

    def get_transform(self):
        """Return the image transform, initializing the model if necessary."""
        if self.transform is None:
            self.initialize_model()
        return self.transform

    def get_device(self):
        """Return the device (CPU or GPU) that the model is running on."""
        return self.device
    
    def get_tokenizer(self):
        """Return the tokenizer associated with the model."""
        if self.tokenizer is None:
            self.initialize_model()
        return self.tokenizer

    def initialize_model_async(self, callback=None):
        """Initialize the model asynchronously to keep the UI responsive."""
        def load_model():
            try:
                self.initialize_model()
                if callback:
                    callback()
            except Exception as e:
                logger.error(f"Error during async model initialization: {e}", exc_info=True)
                if callback:
                    callback(e)

        thread = threading.Thread(target=load_model)
        thread.start()

    def __enter__(self):
        """Context manager entry: ensure the model is initialized."""
        self.initialize_model()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: clear CUDA cache if necessary."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("CUDA cache cleared.")

    def log_gpu_memory(self):
        """Log the current GPU memory usage."""
        if torch.cuda.is_available():
            logger.info(f"GPU memory allocated: {torch.cuda.memory_allocated()} bytes")
            logger.info(f"GPU memory cached: {torch.cuda.memory_reserved()} bytes")
        else:
            logger.info("GPU is not available; skipping GPU memory logging.")

    def profile_model(self, input_tensor):
        """Profile the model's performance using a given input tensor."""
        if not torch.cuda.is_available():
            logger.warning("Profiling on CPU as GPU is not available.")
        with torch.autograd.profiler.profile(use_cuda=torch.cuda.is_available()) as prof:
            output = self.model(input_tensor.to(self.device))
        logger.info(prof.key_averages().table(sort_by="cuda_time_total"))
        return output

    def benchmark_model(self, input_tensor):
        """Benchmark the model's performance on both GPU and CPU."""
        # Benchmark on GPU
        if torch.cuda.is_available():
            start = time.time()
            output = self.model(input_tensor.to(self.device))
            gpu_time = time.time() - start
            logger.info(f"GPU execution time: {gpu_time:.4f} seconds")

        # Benchmark on CPU
        start = time.time()
        output = self.model(input_tensor.to('cpu'))
        cpu_time = time.time() - start
        logger.info(f"CPU execution time: {cpu_time:.4f} seconds")
        return output
