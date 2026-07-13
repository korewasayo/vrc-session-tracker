import os
import sqlite3
import json
from datetime import datetime, timedelta

class VRCXReader:
    def __init__(self, db_path=None):
        if not db_path:
            # Auto-detect %APPDATA%\VRCX\VRCX.sqlite3
            appdata = os.getenv("APPDATA")
            if appdata:
                db_path = os.path.join(appdata, "VRCX", "VRCX.sqlite3")
            else:
                db_path = "VRCX.sqlite3"
                
        self.db_path = db_path
        
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"VRCX database not found at: {self.db_path}")

    def _get_connection(self):
        """Connect to the database in read-only mode."""
        # URI format for read-only connection
        db_uri = f"file:{self.db_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def get_tables(self):
        """List all available tables in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            return [row["name"] for row in cursor.fetchall()]

    def get_known_players(self, limit=100):
        """Return a list of unique known players."""
        # VRCX generally stores detailed data in 'gamelog_player' or inside 'data' in 'gamelog'
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Attempt 1: Check if gamelog table exists
                # We use a generic query in case the exact schema is unknown
                # (VRCX usually uses 'user' or 'gamelog' tables)
                tables = self.get_tables()
                if "gamelog" in tables:
                    cursor.execute("""
                        SELECT data, created_at 
                        FROM gamelog 
                        WHERE type IN ('OnPlayerJoined', 'OnPlayerLeft') 
                        ORDER BY created_at DESC 
                        LIMIT ?
                    """, (limit * 10,)) # Search more rows because we need unique ones
                    
                    players = {}
                    for row in cursor.fetchall():
                        try:
                            data = json.loads(row["data"])
                            user_id = data.get("userId") or data.get("user", {}).get("id")
                            display_name = data.get("displayName") or data.get("user", {}).get("displayName")
                            
                            if user_id and display_name and user_id not in players:
                                players[user_id] = {
                                    "userId": user_id,
                                    "displayName": display_name,
                                    "last_seen": row["created_at"]
                                }
                            if len(players) >= limit:
                                break
                        except json.JSONDecodeError:
                            continue
                            
                    return list(players.values())
        except sqlite3.Error as e:
            print(f"Error reading VRCX DB: {e}")
        return []

    def get_recent_players(self, hours=24):
        """Get players seen in the last X hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat() + "Z"
        
        recent_players = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Verify existence of gamelog
                if "gamelog" in self.get_tables():
                    cursor.execute("""
                        SELECT data, created_at 
                        FROM gamelog 
                        WHERE type IN ('OnPlayerJoined', 'OnPlayerLeft') 
                        AND created_at >= ?
                        ORDER BY created_at DESC
                    """, (cutoff_str,))
                    
                    players_map = {}
                    for row in cursor.fetchall():
                        try:
                            data = json.loads(row["data"])
                            user_id = data.get("userId") or data.get("user", {}).get("id")
                            display_name = data.get("displayName") or data.get("user", {}).get("displayName")
                            
                            if user_id and display_name and user_id not in players_map:
                                players_map[user_id] = {
                                    "userId": user_id,
                                    "displayName": display_name,
                                    "last_seen": row["created_at"]
                                }
                        except json.JSONDecodeError:
                            continue
                    
                    recent_players = list(players_map.values())
        except sqlite3.Error:
            pass
            
        return recent_players

    def search_player(self, name):
        """Search for a displayName in the history."""
        name_lower = name.lower()
        results = {}
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if "gamelog" in self.get_tables():
                    cursor.execute("""
                        SELECT data, created_at 
                        FROM gamelog 
                        WHERE type IN ('OnPlayerJoined', 'OnPlayerLeft')
                        AND data LIKE ?
                        ORDER BY created_at DESC
                        LIMIT 500
                    """, (f"%{name}%",))
                    
                    for row in cursor.fetchall():
                        try:
                            data = json.loads(row["data"])
                            user_id = data.get("userId") or data.get("user", {}).get("id")
                            display_name = data.get("displayName") or data.get("user", {}).get("displayName")
                            
                            if user_id and display_name and name_lower in display_name.lower() and user_id not in results:
                                results[user_id] = {
                                    "userId": user_id,
                                    "displayName": display_name,
                                    "last_seen": row["created_at"]
                                }
                        except json.JSONDecodeError:
                            continue
        except sqlite3.Error:
            pass
            
        return list(results.values())

    def get_player_history(self, user_id):
        """Get all occurrences of a player."""
        history = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if "gamelog" in self.get_tables():
                    cursor.execute("""
                        SELECT type, data, created_at 
                        FROM gamelog 
                        WHERE type IN ('OnPlayerJoined', 'OnPlayerLeft')
                        AND data LIKE ?
                        ORDER BY created_at DESC
                    """, (f"%{user_id}%",))
                    
                    for row in cursor.fetchall():
                        try:
                            data = json.loads(row["data"])
                            row_user_id = data.get("userId") or data.get("user", {}).get("id")
                            if row_user_id == user_id:
                                history.append({
                                    "action": row["type"],
                                    "timestamp": row["created_at"],
                                    "location": data.get("location", "Unknown")
                                })
                        except json.JSONDecodeError:
                            continue
        except sqlite3.Error:
            pass
            
        return history
