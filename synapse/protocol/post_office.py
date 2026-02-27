import json
import os
from datetime import datetime

# Path to the shared message store
POST_OFFICE_FILE = os.path.join(os.path.dirname(__file__), "post_office.json")

def _ensure_file():
    """
    Ensures that the post_office.json file exists.
    If it doesn't exist, initializes it with an empty list.
    """
    if not os.path.exists(POST_OFFICE_FILE):
        with open(POST_OFFICE_FILE, 'w') as f:
            json.dump([], f)

def send_message(message: dict):
    """
    Sends a message by appending it to the post_office.json file.
    Adds a timestamp automatically before saving.
    
    Expected message fields (from schema.json):
    - sender (str)
    - recipient (str)
    - task_id (str)
    - status (str)
    - payload (dict)
    """
    _ensure_file()
    
    # Attach timestamp for reliable ordering
    message["timestamp"] = datetime.utcnow().isoformat()
    
    try:
        # Read current messages
        messages = read_messages()
        
        # Append the new envelope
        messages.append(message)
        
        # Write updated list back to disk
        with open(POST_OFFICE_FILE, 'w') as f:
            json.dump(messages, f, indent=4)
            
    except Exception as e:
        print(f"Error sending message: {e}")

def read_messages() -> list:
    """
    Returns all messages from the post_office.json file.
    """
    _ensure_file()
    try:
        with open(POST_OFFICE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return []

def clear_messages():
    """
    Resets the message store to an empty list.
    """
    with open(POST_OFFICE_FILE, 'w') as f:
        json.dump([], f)
