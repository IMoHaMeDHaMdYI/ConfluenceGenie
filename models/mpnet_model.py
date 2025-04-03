from models.model_interface import ModelInterface

class MPNetModel(ModelInterface):
    def __init__(self):
        super().__init__("all-mpnet-base-v2")
    
    def get_model_name(self):
        return "MPNet (all-mpnet-base-v2)" 