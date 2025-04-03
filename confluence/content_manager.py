from pathlib import Path

class ContentManager:
    def __init__(self):
        self.content_dir = Path("confluence_content")
        self.content_dir.mkdir(exist_ok=True)
        self.content_file = self.content_dir / "confluence_content.txt"
    
    def store_content(self, content):
        """Store content in a structured format for LLM processing."""
        with open(self.content_file, "a", encoding="utf-8") as f:
            f.write(f"CONTENT:\n{content}\n---\n")
    
    def clear_content(self):
        """Clear the content file."""
        with open(self.content_file, "w", encoding="utf-8") as f:
            f.write("")
    
    def get_all_content(self):
        """Get all stored content."""
        try:
            with open(self.content_file, "r", encoding="utf-8") as f:
                return f.read().split("---\n")
        except FileNotFoundError:
            return [] 