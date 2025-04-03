import logging
import time
from datetime import datetime
import uuid
import json

class NetworkLogger:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('network_requests.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def log_request(self, method, url, params=None, response=None, error=None):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Log to console and file
            self.logger.info(f"Request {request_id}: {method} {url}")
            
            # Create structured log entry
            log_entry = {
                "id": request_id,
                "timestamp": datetime.now().isoformat(),
                "method": method,
                "url": url,
                "params": params,
                "response": response,
                "error": str(error) if error else None,
                "duration_ms": (time.time() - start_time) * 1000
            }
            
            # Save to JSON file
            with open("network_requests.json", "a") as f:
                json.dump(log_entry, f)
                f.write("\n")
            
            # Log duration
            self.logger.info(f"Duration: {log_entry['duration_ms']}ms")
            
        except Exception as e:
            self.logger.error(f"Error logging request: {str(e)}") 