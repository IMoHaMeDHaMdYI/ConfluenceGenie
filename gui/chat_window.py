import tkinter as tk
from tkinter import ttk, messagebox
from utils.chat_text import ChatText

class ChatWindow:
    def __init__(self, parent):
        self.parent = parent
        self.content = []
        self.setup_gui()
    
    def setup_gui(self):
        # Chat frame
        chat_frame = ttk.LabelFrame(self.parent, text="AI Assistant", padding="5")
        chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chat history
        self.chat_history = ChatText(chat_frame, wrap=tk.WORD)
        self.chat_history.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Question input frame
        question_frame = ttk.Frame(chat_frame)
        question_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(question_frame, text="Question:").pack(side="left", padx=5)
        self.question_entry = ttk.Entry(question_frame)
        self.question_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        self.ask_button = ttk.Button(question_frame, text="Ask", command=self.ask_question)
        self.ask_button.pack(side="right", padx=5)
        
        # Bind Enter key to ask question
        self.question_entry.bind('<Return>', lambda e: self.ask_question())
    
    def update_content(self, new_content):
        self.content.append(new_content)
    
    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question.")
            return
        
        if not self.content:
            messagebox.showwarning("Warning", "Please fetch some content first.")
            return
        
        # Add question to chat
        self.chat_history.insert(tk.END, f"\nYou: {question}\n\n", "question")
        
        # Process question and get answer
        answer = self.process_question(question)
        
        # Add answer to chat
        self.chat_history.insert(tk.END, f"{answer}\n\n", "answer")
        self.chat_history.see(tk.END)
        
        # Clear question entry
        self.question_entry.delete(0, tk.END)
    
    def process_question(self, question):
        # This method will be implemented by the model selection component
        return "Answer processing will be handled by the selected model." 