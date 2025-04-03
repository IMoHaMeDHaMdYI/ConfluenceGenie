# Application settings
APP_TITLE = "Atlassian Content Explorer"
APP_GEOMETRY = "800x600"

# Model settings
DEFAULT_MODEL = "MPNet"
MODEL_OPTIONS = {
    "MPNet": "all-mpnet-base-v2",
    "MiniLM": "all-MiniLM-L6-v2"
}

# Content settings
CONTENT_DIR = "confluence_content"
CONTENT_FILE = "confluence_content.txt"

# Logging settings
LOG_FILE = "network_requests.log"
JSON_LOG_FILE = "network_requests.json"

# API settings
API_TIMEOUT = 30  # seconds
MAX_PAGES_PER_SPACE = 100 