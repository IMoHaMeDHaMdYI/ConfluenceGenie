import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from confluence.client import ConfluenceClient
from confluence.content_manager import ContentManager
from gui.chat_window import ChatWindow
from gui.model_selection import ModelSelection
from utils.logger import NetworkLogger
import json
import logging

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Atlassian Content Explorer")
        self.root.geometry("800x600")
        
        # Initialize components
        self.confluence_client = ConfluenceClient()
        self.content_manager = ContentManager()
        self.network_logger = NetworkLogger()
        
        # Create content storage directory
        self.content_dir = Path("confluence_content")
        self.content_dir.mkdir(exist_ok=True)
        
        # Setup GUI
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
        
        # Right panel for chat and model selection
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)
        
        # Setup connection frame
        self.setup_connection_frame(left_panel)
        
        # Setup content frame
        self.setup_content_frame(left_panel)
        
        # Setup chat and model selection
        self.chat_window = ChatWindow(right_panel)
        self.model_selection = ModelSelection(right_panel, self.chat_window)
    
    def setup_connection_frame(self, parent):
        connection_frame = ttk.LabelFrame(parent, text="Connection Settings", padding="5")
        connection_frame.pack(fill="x", padx=5, pady=5)
        
        # URL
        ttk.Label(connection_frame, text="URL:").grid(row=0, column=0, padx=5, pady=5)
        self.url_entry = ttk.Entry(connection_frame, width=40)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Username
        ttk.Label(connection_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(connection_frame, width=40)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # API Token
        ttk.Label(connection_frame, text="API Token:").grid(row=2, column=0, padx=5, pady=5)
        self.token_entry = ttk.Entry(connection_frame, width=40, show="*")
        self.token_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Connect button
        self.connect_button = ttk.Button(connection_frame, text="Connect", 
                                       command=self.connect_to_confluence)
        self.connect_button.grid(row=3, column=1, pady=10)
    
    def setup_content_frame(self, parent):
        content_frame = ttk.LabelFrame(parent, text="Confluence Spaces and Pages", padding="5")
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
    
    def load_credentials(self):
        try:
            with open("credentials.json", "r") as f:
                credentials = json.load(f)
                logging.info("Loading saved credentials")
                self.url_entry.insert(0, credentials.get("url", ""))
                self.username_entry.insert(0, credentials.get("username", ""))
                self.token_entry.insert(0, credentials.get("api_token", ""))
                logging.info("Credentials loaded successfully")
        except FileNotFoundError:
            logging.info("No saved credentials found")
        except Exception as e:
            logging.error(f"Error loading credentials: {str(e)}")
    
    def connect_to_confluence(self):
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        api_token = self.token_entry.get().strip()
        
        if not all([url, username, api_token]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        try:
            # Clean up URL if necessary
            if not url.startswith("https://"):
                url = "https://" + url
            if url.endswith("/"):
                url = url[:-1]
            
            # Connect to Confluence
            self.confluence_client.connect(url, username, api_token)
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch and display spaces
            spaces = self.confluence_client.get_spaces()
            for space in spaces:
                self.tree.insert("", "end", values=(space["name"], "Space", space["key"]))
            
            # Save credentials
            logging.info("Saving credentials")
            with open("credentials.json", "w") as f:
                json.dump({
                    "url": url,
                    "username": username,
                    "api_token": api_token
                }, f)
            logging.info("Credentials saved successfully")
            
            messagebox.showinfo("Success", "Connected to Confluence successfully!")
            
        except Exception as e:
            logging.error(f"Failed to connect: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        item_type = self.tree.item(item, "values")[1]
        item_id = self.tree.item(item, "values")[2]
        
        if item_type == "Space":
            # Clear existing items
            for child in self.tree.get_children():
                self.tree.delete(child)
            
            # Fetch and display pages
            pages = self.confluence_client.get_pages(item_id)
            for page in pages:
                self.tree.insert("", "end", values=(page["title"], "Page", page["id"]))
        
        elif item_type == "Page":
            # Fetch and display page content
            content = self.confluence_client.get_page_content(item_id)
            self.content_manager.store_content(content)
            self.chat_window.update_content(content) 