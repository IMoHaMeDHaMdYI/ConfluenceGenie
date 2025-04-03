from models.model_interface import ModelInterface

class MiniLMModel(ModelInterface):
    def __init__(self):
        super().__init__("all-MiniLM-L6-v2")
    
    def get_model_name(self):
        return "MiniLM (all-MiniLM-L6-v2)" 