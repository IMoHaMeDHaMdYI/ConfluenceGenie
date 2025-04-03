from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import torch

class ModelInterface(ABC):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.model.to(self.device)
    
    @abstractmethod
    def get_model_name(self):
        pass
    
    def encode(self, text, convert_to_tensor=True):
        return self.model.encode(text, convert_to_tensor=convert_to_tensor)
    
    def get_similarity(self, embedding1, embedding2):
        return torch.nn.functional.cosine_similarity(embedding1, embedding2)
    
    def format_response(self, content, confidence):
        return f"Answer (Confidence: {confidence:.2f}%):\n{content}" 