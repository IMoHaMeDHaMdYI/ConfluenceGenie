from abc import ABC, abstractmethod
from sentence_transformers import util

class ModelInterface(ABC):
    @abstractmethod
    def get_model_name(self) -> str:
        """Returns the name of the model."""
        pass
    
    @abstractmethod
    def encode(self, text: str, convert_to_tensor: bool = True):
        """Encodes the given text into embeddings."""
        pass
    
    @abstractmethod
    def get_similarity(self, query_embedding, content_embedding):
        """Calculates similarity between query and content embeddings."""
        pass
    
    @abstractmethod
    def format_response(self, content: str, confidence: float) -> str:
        """Formats the response with the given content and confidence score."""
        pass 