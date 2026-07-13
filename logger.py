import csv
import os
from datetime import datetime

LOG_FILE = "moderation.csv"

def log_action(action_type, target_id, target_name="Unknown"):
    """
    Log a moderation action to a local CSV file.
    Creates the file and header if it doesn't exist.
    """
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "action", "target_id", "target_name"])
        
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, action_type, target_id, target_name])

def export_recent_players_to_csv(players, filename="recent_players.csv"):
    """
    Export a list of player dicts to a CSV file.
    """
    if not players:
        return False
        
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["userId", "displayName", "last_seen"])
        
        for player in players:
            writer.writerow([
                player.get("userId", ""),
                player.get("displayName", ""),
                player.get("last_seen", "")
            ])
            
    return True
