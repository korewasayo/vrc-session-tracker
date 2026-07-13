import re
from datetime import datetime

def validate_user_id(user_id):
    """Verify if the ID matches the usr_xxx format."""
    return bool(re.match(r"^usr_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", user_id))

def validate_group_id(group_id):
    """Verify if the ID matches the grp_xxx format."""
    return bool(re.match(r"^grp_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", group_id))

def confirm_action(message):
    """Display a confirmation prompt."""
    while True:
        choice = input(f"⚠️  {message} (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            return True
        if choice in ['n', 'no']:
            return False

def format_timestamp(ts_string):
    """Format an ISO timestamp to human-readable format."""
    if not ts_string:
        return "Unknown"
    try:
        # Assuming format like "2024-05-14T20:45:00.000Z"
        ts_string = ts_string.replace('Z', '+00:00')
        dt = datetime.fromisoformat(ts_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ts_string
