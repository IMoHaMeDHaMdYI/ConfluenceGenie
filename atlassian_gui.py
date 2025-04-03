import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from atlassian import Confluence
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup
import threading
import markdown
import re
from tkinter.font import Font
import logging
import time
from datetime import datetime
import uuid

# Import model implementations
from model_interface import ModelInterface
from mpnet_model import MPNetModel
from minilm_model import MiniLMModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_requests.log'),
        logging.StreamHandler()
    ]
)

class NetworkLogger:
    def __init__(self):
        self.requests = []
        self.log_file = 'network_requests.json'
        
    def log_request(self, method, url, params=None, response=None, error=None, duration=None):
        request_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "request_id": request_id,
            "timestamp": timestamp,
            "method": method,
            "url": url,
            "params": params,
            "duration_ms": duration,
            "response": response,
            "error": str(error) if error else None
        }
        
        self.requests.append(log_entry)
        
        # Save to file
        with open(self.log_file, 'w') as f:
            json.dump(self.requests, f, indent=2)
        
        # Log to console
        logging.info(f"Request {request_id}: {method} {url}")
        if duration:
            logging.info(f"Duration: {duration}ms")
        if error:
            logging.error(f"Error: {error}")
            
        return request_id

class ChatText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_configure('question', foreground='blue', font=('Helvetica', 10, 'bold'))
        self.tag_configure('answer', foreground='black', font=('Helvetica', 10))
        self.tag_configure('code', background='#f0f0f0', font=('Courier', 10))
        self.tag_configure('bold', font=('Helvetica', 10, 'bold'))
        self.tag_configure('italic', font=('Helvetica', 10, 'italic'))
        self.tag_configure('list', lmargin1=20, lmargin2=20)
        
    def insert_markdown(self, text, tag='answer'):
        # Convert markdown to HTML
        html = markdown.markdown(text)
        
        # Remove HTML tags and keep formatting
        text = re.sub(r'<[^>]+>', '', html)
        
        # Insert the text
        self.insert(tk.END, text + '\n\n', tag)
        
        # Apply formatting
        self._apply_markdown_formatting(text, html)
        
    def _apply_markdown_formatting(self, text, html):
        # Find code blocks
        code_blocks = re.findall(r'<code>(.*?)</code>', html, re.DOTALL)
        for code in code_blocks:
            start = '1.0'
            while True:
                start = self.search(code, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(code)}c"
                self.tag_add('code', start, end)
                start = end
                
        # Find bold text
        bold_text = re.findall(r'<strong>(.*?)</strong>', html)
        for text in bold_text:
            start = '1.0'
            while True:
                start = self.search(text, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(text)}c"
                self.tag_add('bold', start, end)
                start = end
                
        # Find italic text
        italic_text = re.findall(r'<em>(.*?)</em>', html)
        for text in italic_text:
            start = '1.0'
            while True:
                start = self.search(text, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(text)}c"
                self.tag_add('italic', start, end)
                start = end
                
        # Find lists
        list_items = re.findall(r'<li>(.*?)</li>', html)
        for item in list_items:
            start = '1.0'
            while True:
                start = self.search(item, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(item)}c"
                self.tag_add('list', start, end)
                start = end

class AtlassianGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Atlassian Content Explorer")
        self.root.geometry("800x600")
        
        # Variables
        self.server_url = tk.StringVar()
        self.username = tk.StringVar()
        self.api_token = tk.StringVar()
        
        # Initialize Confluence client and logger
        self.confluence = None
        self.page_content = ""
        self.model = None
        self.model_interface = None
        self.all_content = []
        self.network_logger = NetworkLogger()
        
        # Create content storage directory
        self.content_dir = Path("confluence_content")
        self.content_dir.mkdir(exist_ok=True)
        
        # Create and set up the GUI elements
        self.setup_gui()
        
        # Load saved credentials if they exist
        self.load_credentials()
        
    def setup_gui(self):
        # Create main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for Confluence content
        left_panel = ttk.Frame(main_container)
        main_container.add(left_panel, weight=1)
        
        # Right panel for chat
        self.right_panel = ttk.Frame(main_container)
        main_container.add(self.right_panel, weight=1)
        
        # Connection frame
        connection_frame = ttk.LabelFrame(left_panel, text="Connection Settings", padding="5")
        connection_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(connection_frame, text="URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_entry = ttk.Entry(connection_frame, textvariable=self.server_url, width=40)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(connection_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(connection_frame, textvariable=self.username, width=40)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(connection_frame, text="API Token:").grid(row=2, column=0, padx=5, pady=5)
        self.token_entry = ttk.Entry(connection_frame, textvariable=self.api_token, width=40, show="*")
        self.token_entry.grid(row=2, column=1, padx=5, pady=5)
        
        self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_to_confluence)
        self.connect_button.grid(row=3, column=1, pady=10)
        
        # Content frame
        content_frame = ttk.LabelFrame(left_panel, text="Confluence Spaces and Pages", padding="5")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create Treeview
        self.tree = ttk.Treeview(content_frame, columns=("Name", "Type", "ID"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("ID", text="ID")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Grid the tree and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Chat frame
        chat_frame = ttk.LabelFrame(self.right_panel, text="AI Assistant", padding="5")
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
        
        # Setup model selection after all GUI elements are created
        self.setup_model_selection()
        
    def setup_model_selection(self):
        # Add model selection to the GUI
        model_frame = ttk.LabelFrame(self.right_panel, text="Model Selection", padding="5")
        model_frame.pack(fill="x", padx=5, pady=5)
        
        self.model_var = tk.StringVar(value="MPNet")
        ttk.Radiobutton(model_frame, text="MPNet (all-mpnet-base-v2)", 
                       variable=self.model_var, value="MPNet").pack(anchor="w")
        ttk.Radiobutton(model_frame, text="MiniLM (all-MiniLM-L6-v2)", 
                       variable=self.model_var, value="MiniLM").pack(anchor="w")
        
        ttk.Button(model_frame, text="Load Model", 
                  command=self.load_selected_model).pack(pady=5)
        
    def load_selected_model(self):
        try:
            if self.model_var.get() == "MPNet":
                self.model_interface = MPNetModel()
            else:
                self.model_interface = MiniLMModel()
            messagebox.showinfo("Success", f"Loaded {self.model_interface.get_model_name()} model successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def load_credentials(self):
        try:
            config_path = Path.home() / '.confluence_config.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.server_url.set(config.get('server_url', ''))
                    self.username.set(config.get('username', ''))
                    self.api_token.set(config.get('api_token', ''))
        except Exception as e:
            print(f"Error loading credentials: {e}")
    
    def save_credentials(self):
        try:
            config = {
                'server_url': self.server_url.get(),
                'username': self.username.get(),
                'api_token': self.api_token.get()
            }
            config_path = Path.home() / '.confluence_config.json'
            with open(config_path, 'w') as f:
                json.dump(config, f)
            # Set file permissions to be readable only by the user
            config_path.chmod(0o600)
        except Exception as e:
            print(f"Error saving credentials: {e}")
    
    def store_content_for_llm(self, space_name, page_title, content):
        """Store content in a format optimized for LLM search"""
        # Create a structured format that's easy for LLMs to process
        structured_content = f"""
SPACE: {space_name}
PAGE: {page_title}
CONTENT:
{content}
---
"""
        # Append to the content file
        with open(self.content_dir / "confluence_content.txt", "a", encoding="utf-8") as f:
            f.write(structured_content)

    def connect_to_confluence(self):
        try:
            start_time = time.time()
            
            # Clean up URL if needed
            url = self.server_url.get()
            if not url.endswith('/wiki') and 'atlassian.net' in url:
                url = f"{url}/wiki"
            
            self.confluence = Confluence(
                url=url,
                username=self.username.get(),
                password=self.api_token.get(),
                cloud=True
            )
            
            # Log connection attempt
            self.network_logger.log_request(
                method="CONNECT",
                url=url,
                params={"username": self.username.get()},
                duration=(time.time() - start_time) * 1000
            )
            
            # Save credentials after successful connection
            self.save_credentials()
            
            # Clear existing items and content
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.all_content = []
            
            # Clear existing content file
            with open(self.content_dir / "confluence_content.txt", "w", encoding="utf-8") as f:
                f.write("")
            
            # Fetch and display spaces
            start_time = time.time()
            spaces = self.confluence.get_all_spaces(start=0, limit=50)
            self.network_logger.log_request(
                method="GET",
                url=f"{url}/rest/api/space",
                params={"start": 0, "limit": 50},
                response={"count": len(spaces.get('results', []))},
                duration=(time.time() - start_time) * 1000
            )
            
            for space in spaces.get('results', []):
                space_key = space.get('key', '')
                space_name = space.get('name', '')
                
                # Add space to tree
                self.tree.insert("", tk.END, values=(
                    space_name,
                    "Space",
                    space_key
                ))
                
                # Fetch all pages in this space
                start_time = time.time()
                pages = self.confluence.get_all_pages_from_space(space_key, start=0, limit=100)
                self.network_logger.log_request(
                    method="GET",
                    url=f"{url}/rest/api/space/{space_key}/content",
                    params={"start": 0, "limit": 100},
                    response={"count": len(pages)},
                    duration=(time.time() - start_time) * 1000
                )
                
                for page in pages:
                    # Add page to tree
                    self.tree.insert("", tk.END, values=(
                        f"  └─ {page['title']}",
                        "Page",
                        page['id']
                    ))
                    
                    # Fetch and store page content
                    try:
                        start_time = time.time()
                        page_content = self.confluence.get_page_by_id(page['id'], expand='body.storage')
                        self.network_logger.log_request(
                            method="GET",
                            url=f"{url}/rest/api/content/{page['id']}",
                            params={"expand": "body.storage"},
                            response={"title": page['title']},
                            duration=(time.time() - start_time) * 1000
                        )
                        
                        content = page_content.get('body', {}).get('storage', {}).get('value', '')
                        
                        # Parse HTML content and clean it up
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Remove unwanted elements
                        for element in soup.find_all(['script', 'style', 'meta', 'link']):
                            element.decompose()
                        
                        # Clean up the text
                        text_content = []
                        for element in soup.stripped_strings:
                            if element.strip():
                                if element.endswith(('.', '!', '?')):
                                    text_content.append(element + '\n\n')
                                else:
                                    text_content.append(element + ' ')
                        
                        cleaned_content = ''.join(text_content)
                        cleaned_content = '\n'.join(line for line in cleaned_content.split('\n') if line.strip())
                        
                        # Store content for LLM search
                        self.store_content_for_llm(space_name, page['title'], cleaned_content)
                        
                        self.all_content.append(cleaned_content)
                        
                    except Exception as e:
                        self.network_logger.log_request(
                            method="GET",
                            url=f"{url}/rest/api/content/{page['id']}",
                            params={"expand": "body.storage"},
                            error=str(e)
                        )
                        continue
            
            messagebox.showinfo("Success", "Successfully connected to Confluence and loaded all content!")
            
        except Exception as e:
            self.network_logger.log_request(
                method="CONNECT",
                url=url,
                params={"username": self.username.get()},
                error=str(e)
            )
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def on_item_double_click(self, event):
        # Get the selected item
        item = self.tree.selection()[0]
        item_values = self.tree.item(item)['values']
        
        if item_values:  # Make sure we have values
            item_type = item_values[1]  # Type is in the second column
            item_id = item_values[2]    # ID is in the third column
            item_name = item_values[0]  # Name is in the first column
            
            if item_type == "Page":
                self.show_page_content(item_id, item_name)
            else:
                messagebox.showinfo("Info", "Please select a page to view its content")
    
    def show_page_content(self, page_id, title):
        try:
            # Fetch page content
            page = self.confluence.get_page_by_id(page_id, expand='body.storage')
            content = page.get('body', {}).get('storage', {}).get('value', '')
            
            # Create a new window
            content_window = tk.Toplevel(self.root)
            content_window.title(f"Page: {title}")
            content_window.geometry("1000x800")
            
            # Create main container
            main_container = ttk.Frame(content_window)
            main_container.pack(expand=True, fill='both', padx=10, pady=10)
            
            # Create text widget for content
            text_widget = scrolledtext.ScrolledText(main_container, wrap=tk.WORD)
            text_widget.pack(expand=True, fill='both', pady=(0, 10))
            
            # Parse HTML content and clean it up
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'meta', 'link']):
                element.decompose()
            
            # Clean up the text
            text_content = []
            for element in soup.stripped_strings:
                # Skip empty lines and whitespace
                if element.strip():
                    # Add proper spacing between paragraphs
                    if element.endswith(('.', '!', '?')):
                        text_content.append(element + '\n\n')
                    else:
                        text_content.append(element + ' ')
            
            # Join all text with proper spacing
            cleaned_content = ''.join(text_content)
            
            # Remove multiple consecutive newlines
            cleaned_content = '\n'.join(line for line in cleaned_content.split('\n') if line.strip())
            
            # Store the cleaned content for question answering
            self.all_content.append(cleaned_content)
            
            # Insert the cleaned text
            text_widget.insert('1.0', cleaned_content)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch page content: {str(e)}")
    
    def ask_question(self):
        question = self.question_entry.get().strip()
        if not question:
            messagebox.showwarning("Warning", "Please enter a question.")
            return
        
        if not self.all_content:
            messagebox.showwarning("Warning", "Please fetch some content first.")
            return
        
        if self.model_interface is None:
            messagebox.showwarning("Warning", "Please select and load a model first.")
            return
        
        try:
            # Encode the question
            question_embedding = self.model_interface.encode(question, convert_to_tensor=True)
            
            # Find the most relevant content
            best_match = None
            best_score = -1
            
            for content in self.all_content:
                # Split content into chunks to handle large documents
                chunks = [content[i:i+1000] for i in range(0, len(content), 1000)]
                
                for chunk in chunks:
                    content_embedding = self.model_interface.encode(chunk, convert_to_tensor=True)
                    similarity = self.model_interface.get_similarity(question_embedding, content_embedding)
                    score = similarity.item()
                    
                    if score > best_score:
                        best_score = score
                        best_match = chunk
            
            if best_match:
                # Format the response with confidence score
                confidence = best_score * 100
                response = self.model_interface.format_response(best_match, confidence)
                
                # Add to chat history
                self.chat_history.insert_markdown(f"**You:** {question}\n", 'question')
                self.chat_history.insert_markdown(response)
                self.chat_history.see(tk.END)
                
                # Clear the question input
                self.question_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Info", "No relevant content found.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process question: {str(e)}")

def main():
    root = tk.Tk()
    app = AtlassianGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 