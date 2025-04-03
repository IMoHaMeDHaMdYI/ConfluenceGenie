from sentence_transformers import SentenceTransformer, util
from model_interface import ModelInterface

class MPNetModel(ModelInterface):
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')
    
    def get_model_name(self) -> str:
        return "MPNet (all-mpnet-base-v2)"
    
    def encode(self, text: str, convert_to_tensor: bool = True):
        return self.model.encode(text, convert_to_tensor=convert_to_tensor)
    
    def get_similarity(self, query_embedding, content_embedding):
        return util.pytorch_cos_sim(query_embedding, content_embedding)
    
    def format_response(self, content: str, confidence: float) -> str:
        return f"Based on the content, here's what I found:\n\n{content}\n\n_Confidence: {confidence:.1f}%_" 