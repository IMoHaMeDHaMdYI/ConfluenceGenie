import tkinter as tk
from tkinter import scrolledtext
import markdown
from tkinter.font import Font

class ChatText(scrolledtext.ScrolledText):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure tags for different message types
        self.tag_configure("question", foreground="blue")
        self.tag_configure("answer", foreground="black")
        
        # Configure font
        self.font = Font(family="Helvetica", size=12)
        self.configure(font=self.font)
    
    def insert_markdown(self, text, tag=None):
        """Insert text with markdown formatting."""
        # Convert markdown to HTML
        html = markdown.markdown(text)
        
        # Insert the text
        self.insert(tk.END, html, tag)
        
        # Add newline
        self.insert(tk.END, "\n")
        
        # Scroll to the bottom
        self.see(tk.END) 