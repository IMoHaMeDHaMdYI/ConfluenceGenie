# Atlassian Data Fetcher

A Python GUI application for macOS that allows you to connect to Atlassian and fetch data using the Atlassian Python API.

## Requirements

- Python 3.x
- macOS
- Atlassian account with API token

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python atlassian_gui.py
   ```

2. Enter your Atlassian credentials:
   - Server URL: Your Atlassian instance URL (e.g., https://your-domain.atlassian.net)
   - Username: Your Atlassian email address
   - API Token: Your Atlassian API token (you can generate this from your Atlassian account settings)

3. Click "Connect" to establish the connection and fetch data

## Features

- Secure connection to Atlassian using API token
- Display of Jira issues in a table format
- Error handling and user feedback
- Modern macOS-native GUI interface

## Note

Make sure to keep your API token secure and never share it with others. 