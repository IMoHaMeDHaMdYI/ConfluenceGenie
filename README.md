# ConfluenceGenie

A Python GUI application that allows you to connect to Atlassian Confluence, fetch content, and interact with it using AI models.

## Features

- Connect to Atlassian Confluence using API token authentication
- Browse Confluence spaces and pages in a hierarchical tree view
- View page content in a separate window
- Store content in a structured format optimized for AI processing
- Support for multiple AI models (MPNet, MiniLM, AWS Bedrock)
- Chat interface for asking questions about the content
- Optional space ID filtering to fetch data from a specific space only

## Requirements

- Python 3.x
- Atlassian Confluence account with API token
- For AWS Bedrock integration: AWS account with Bedrock access

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/IMoHaMeDHaMdYI/ConfluenceGenie.git
   cd ConfluenceGenie
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Enter your Confluence credentials:
   - URL: Your Confluence instance URL (e.g., https://your-domain.atlassian.net)
   - Username: Your Atlassian email address
   - API Token: Your Atlassian API token (you can generate this from your Atlassian account settings)
   - Space ID (optional): If you want to fetch data from a specific space only

3. Click "Connect" to establish the connection and fetch data

4. Browse spaces and pages:
   - Double-click on a space to expand it and view its pages
   - Double-click on a page to view its content in a separate window

5. Select an AI model and ask questions about the content in the chat interface

## Project Structure

- `main.py`: Entry point for the application
- `gui/`: Contains files for the main window, chat interface, and model selection
- `models/`: Includes the model interface and implementations for MPNet, MiniLM, and AWS Bedrock
- `confluence/`: Contains the API client and content manager
- `utils/`: Includes logging and chat text utilities
- `config/`: Contains the settings file

## Security Note

Make sure to keep your API token secure and never share it with others. The application stores your credentials locally in a `credentials.json` file for convenience, but this file is not encrypted.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 