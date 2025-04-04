import tkinter as tk
from tkinter import ttk, messagebox
from models.mpnet_model import MPNetModel
from models.minilm_model import MiniLMModel
from models.bedrock_model import BedrockModel

class ModelSelection:
    def __init__(self, parent, chat_window):
        self.parent = parent
        self.chat_window = chat_window
        self.model = None
        self.setup_gui()
    
    def setup_gui(self):
        # Add model selection to the GUI
        model_frame = ttk.LabelFrame(self.parent, text="Model Selection", padding="5")
        model_frame.pack(fill="x", padx=5, pady=5)
        
        self.model_var = tk.StringVar(value="MPNet")
        ttk.Radiobutton(model_frame, text="MPNet (all-mpnet-base-v2)", 
                       variable=self.model_var, value="MPNet").pack(anchor="w")
        ttk.Radiobutton(model_frame, text="MiniLM (all-MiniLM-L6-v2)", 
                       variable=self.model_var, value="MiniLM").pack(anchor="w")
        ttk.Radiobutton(model_frame, text="AWS Bedrock (Titan Embed)", 
                       variable=self.model_var, value="Bedrock").pack(anchor="w")
        
        ttk.Button(model_frame, text="Load Model", 
                  command=self.load_selected_model).pack(pady=5)
    
    def load_selected_model(self):
        try:
            if self.model_var.get() == "MPNet":
                self.model = MPNetModel()
            elif self.model_var.get() == "MiniLM":
                self.model = MiniLMModel()
            else:  # Bedrock
                self.model = BedrockModel()
            messagebox.showinfo("Success", f"Loaded {self.model.get_model_name()} model successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def process_question(self, question, content):
        if self.model is None:
            messagebox.showwarning("Warning", "Please select and load a model first.")
            return "No model loaded."
        
        try:
            # Encode the question
            question_embedding = self.model.encode(question, convert_to_tensor=True)
            
            # Find the most relevant content
            best_match = None
            best_score = -1
            
            for chunk in content:
                content_embedding = self.model.encode(chunk, convert_to_tensor=True)
                similarity = self.model.get_similarity(question_embedding, content_embedding)
                score = similarity.item()
                
                if score > best_score:
                    best_score = score
                    best_match = chunk
            
            if best_match:
                # Format the response with confidence score
                confidence = best_score * 100
                return self.model.format_response(best_match, confidence)
            else:
                return "No relevant content found."
                
        except Exception as e:
            return f"Error processing question: {str(e)}" 