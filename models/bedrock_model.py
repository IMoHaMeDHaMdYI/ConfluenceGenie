import boto3
import json
import numpy as np
from models.model_interface import ModelInterface

class BedrockModel(ModelInterface):
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.model_id = 'amazon.titan-embed-text-v1'
    
    def get_model_name(self):
        return "AWS Bedrock (Titan Embed)"
    
    def encode(self, text, convert_to_tensor=True):
        # Prepare the input for the model
        body = json.dumps({
            "inputText": text
        })
        
        # Call Bedrock API
        response = self.bedrock.invoke_model(
            body=body,
            modelId=self.model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response.get('body').read())
        embedding = np.array(response_body['embedding'])
        
        if convert_to_tensor:
            import torch
            return torch.tensor(embedding)
        return embedding
    
    def get_similarity(self, embedding1, embedding2):
        # Convert to numpy arrays if they're tensors
        if hasattr(embedding1, 'numpy'):
            embedding1 = embedding1.numpy()
        if hasattr(embedding2, 'numpy'):
            embedding2 = embedding2.numpy()
        
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        similarity = dot_product / (norm1 * norm2)
        
        # Convert back to tensor if needed
        import torch
        return torch.tensor(similarity) 