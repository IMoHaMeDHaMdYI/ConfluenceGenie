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
        
        # Space ID (optional)
        ttk.Label(connection_frame, text="Space ID (optional):").grid(row=3, column=0, padx=5, pady=5)
        self.space_id_entry = ttk.Entry(connection_frame, width=40)
        self.space_id_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Connect button
        self.connect_button = ttk.Button(connection_frame, text="Connect", 
                                       command=self.connect_to_confluence)
        self.connect_button.grid(row=4, column=1, pady=10)
    
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
                self.space_id_entry.insert(0, credentials.get("space_id", ""))
                logging.info("Credentials loaded successfully")
        except FileNotFoundError:
            logging.info("No saved credentials found")
        except Exception as e:
            logging.error(f"Error loading credentials: {str(e)}")
    
    def connect_to_confluence(self):
        url = self.url_entry.get().strip()
        username = self.username_entry.get().strip()
        api_token = self.token_entry.get().strip()
        space_id = self.space_id_entry.get().strip()
        
        if not all([url, username, api_token]):
            messagebox.showerror("Error", "Please fill in all required fields.")
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
            
            # Clear existing content
            self.content_manager.clear_content()
            
            # If space_id is provided, only fetch data from that space
            if space_id:
                try:
                    # Get space details
                    space = self.confluence_client.get_space(space_id)
                    if space:
                        space_item = self.tree.insert("", "end", values=(space["name"], "Space", space["key"]))
                        # Add a dummy item to make the space expandable
                        self.tree.insert(space_item, "end", values=("Loading...", "", ""))
                        
                        # Fetch and save all pages in this space
                        pages = self.confluence_client.get_pages(space["key"])
                        for page in pages:
                            # Save page content
                            content = self.confluence_client.get_page_content(page["id"])
                            page_url = f"{url}/pages/viewpage.action?pageId={page['id']}"
                            self.content_manager.store_content(content, page["title"], space["name"], page_url)
                except Exception as e:
                    logging.error(f"Error fetching data for space {space_id}: {str(e)}")
                    messagebox.showerror("Error", f"Error fetching data for space {space_id}: {str(e)}")
                    return
            else:
                # Fetch and display all spaces
                spaces = self.confluence_client.get_spaces()
                for space in spaces:
                    space_item = self.tree.insert("", "end", values=(space["name"], "Space", space["key"]))
                    # Add a dummy item to make the space expandable
                    self.tree.insert(space_item, "end", values=("Loading...", "", ""))
                    
                    # Fetch and save all pages in this space
                    try:
                        pages = self.confluence_client.get_pages(space["key"])
                        for page in pages:
                            # Save page content
                            content = self.confluence_client.get_page_content(page["id"])
                            page_url = f"{url}/pages/viewpage.action?pageId={page['id']}"
                            self.content_manager.store_content(content, page["title"], space["name"], page_url)
                    except Exception as e:
                        logging.error(f"Error fetching pages for space {space['name']}: {str(e)}")
            
            # Save credentials
            logging.info("Saving credentials")
            with open("credentials.json", "w") as f:
                json.dump({
                    "url": url,
                    "username": username,
                    "api_token": api_token,
                    "space_id": space_id
                }, f)
            logging.info("Credentials saved successfully")
            
            messagebox.showinfo("Success", "Connected to Confluence successfully!")
            
        except Exception as e:
            logging.error(f"Failed to connect: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
    
    def on_item_double_click(self, event):
        # Check if there's a selected item
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        item_type = self.tree.item(item, "values")[1]
        item_id = self.tree.item(item, "values")[2]
        
        if item_type == "Space":
            # Check if the space is already expanded
            if self.tree.get_children(item):
                # If the first child is "Loading...", fetch the pages
                if self.tree.item(self.tree.get_children(item)[0], "values")[0] == "Loading...":
                    # Remove the loading item
                    self.tree.delete(self.tree.get_children(item)[0])
                    
                    # Fetch and display pages
                    pages = self.confluence_client.get_pages(item_id)
                    for page in pages:
                        self.tree.insert(item, "end", values=(page["title"], "Page", page["id"]))
        
        elif item_type == "Page":
            # Open the page in a separate window
            page_title = self.tree.item(item, "values")[0]
            self.open_page_window(item_id, page_title)

    def open_page_window(self, page_id, page_title):
        # Create a new window
        page_window = tk.Toplevel(self.root)
        page_window.title(f"Page: {page_title}")
        page_window.geometry("800x600")
        
        # Create a text widget to display the content
        text_widget = tk.Text(page_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Fetch and display the page content
        content = self.confluence_client.get_page_content(page_id)
        
        # Get the space name
        space_name = "Unknown Space"
        parent_item = self.tree.parent(self.tree.selection()[0])
        if parent_item:
            space_name = self.tree.item(parent_item, "values")[0]
        
        # Get the page URL
        url = self.url_entry.get().strip()
        if not url.startswith("https://"):
            url = "https://" + url
        if url.endswith("/"):
            url = url[:-1]
        page_url = f"{url}/pages/viewpage.action?pageId={page_id}"
        
        # Clear existing content and store new content
        self.content_manager.clear_content()
        self.content_manager.store_content(content, page_title, space_name, page_url)
        self.chat_window.update_content(content)
        
        # Display content in the new window
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only 