from atlassian import Confluence
from bs4 import BeautifulSoup
import re
import json

class ConfluenceClient:
    def __init__(self):
        self.client = None
    
    def connect(self, url, username, api_token):
        self.client = Confluence(
            url=url,
            username=username,
            password=api_token
        )
    
    def get_spaces(self):
        if not self.client:
            raise Exception("Not connected to Confluence")
        
        try:
            spaces = self.client.get_all_spaces()
            if isinstance(spaces, str):
                # If spaces is a string, try to parse it as JSON
                spaces = json.loads(spaces)
            
            # Ensure spaces is a list
            if not isinstance(spaces, list):
                spaces = [spaces]
            
            return [{"name": space.get("name", ""), "key": space.get("key", "")} for space in spaces]
        except Exception as e:
            raise Exception(f"Error getting spaces: {str(e)}")
    
    def get_pages(self, space_key):
        if not self.client:
            raise Exception("Not connected to Confluence")
        
        pages = self.client.get_all_pages_from_space(space_key, limit=100)
        return [{"title": page["title"], "id": page["id"]} for page in pages]
    
    def get_page_content(self, page_id):
        if not self.client:
            raise Exception("Not connected to Confluence")
        
        page = self.client.get_page_by_id(page_id, expand='body.storage')
        html_content = page['body']['storage']['value']
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # Clean up the text
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
        text = text.strip()  # Remove leading/trailing whitespace
        
        return text 
    
    def get_space(self, space_key):
        """Get details for a specific space."""
        if not self.client:
            raise Exception("Not connected to Confluence")
        
        try:
            space = self.client.get_space(space_key)
            return space
        except Exception as e:
            raise Exception(f"Error getting space {space_key}: {str(e)}") 