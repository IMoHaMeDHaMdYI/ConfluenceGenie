from pathlib import Path
import re

class ContentManager:
    def __init__(self):
        self.content_dir = Path("confluence_content")
        self.content_dir.mkdir(exist_ok=True)
        self.content_file = self.content_dir / "confluence_content.txt"
    
    def store_content(self, content, page_title=None, space_name=None, page_url=None):
        """Store content in a structured format for LLM processing."""
        try:
            # Clean and structure the content
            cleaned_content = self._clean_content(content)
            
            # Create metadata section
            metadata = f"SPACE: {page_title or 'Untitled'}\n"
            if page_url:
                metadata += f"URL: {page_url}\n"
            metadata += "---\n"
            
            # Create sections
            sections = self._extract_sections(cleaned_content)
            sections_text = "\n\n".join(sections)
            
            # Combine metadata and content
            full_content = f"{metadata}\n{sections_text}\n\n---\n\n"
            
            # Append to file
            with open(self.content_file, "a", encoding="utf-8") as f:
                f.write(full_content)
                
        except Exception as e:
            print(f"Error storing content: {str(e)}")
    
    def _clean_content(self, content):
        """Clean the content for better LLM processing."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        # Remove special characters
        content = re.sub(r'[^\w\s.,;:!?()\-\'"]', ' ', content)
        return content.strip()
    
    def _extract_sections(self, content):
        """Extract sections from content for better searchability."""
        sections = []
        # Split by common section markers
        parts = re.split(r'\n\s*(?:#{1,6}\s+|\d+\.\s+|[A-Z][^a-z]*:)', content)
        
        for part in parts:
            if part.strip():
                sections.append(part.strip())
        
        return sections
    
    def clear_content(self):
        """Clear the content file."""
        with open(self.content_file, "w", encoding="utf-8") as f:
            f.write("")
    
    def get_all_content(self):
        """Get all stored content."""
        try:
            with open(self.content_file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "" 