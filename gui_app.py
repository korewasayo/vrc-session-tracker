import os
import sys
import threading
import customtkinter as ctk
import tkinter.messagebox as messagebox
from dotenv import load_dotenv
from datetime import datetime

from vrchat_api import VRChatAPI
from vrcx_reader import VRCXReader
import utils
import logger

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("VRChat Group Moderation Tool v1.0")
        self.geometry("900x750")
        self.configure(fg_color="#0D0D1A")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0, minsize=150)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#12122B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        # Sidebar Border
        self.sidebar_border = ctk.CTkFrame(self, width=2, fg_color="#7C3AED", corner_radius=0)
        self.sidebar_border.grid(row=0, column=0, sticky="nse")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="🛡️ VRC Mod Tool", font=ctk.CTkFont(size=20, weight="bold"), text_color="#B794F6")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        btn_style = {
            "fg_color": "transparent",
            "hover_color": "#1A1A3E",
            "text_color": "#E8E0FF",
            "border_width": 1,
            "border_color": "#7C3AED",
            "corner_radius": 6
        }

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard, **btn_style)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_vrcx = ctk.CTkButton(self.sidebar_frame, text="VRCX Players", command=self.show_vrcx, **btn_style)
        self.btn_vrcx.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_moderation = ctk.CTkButton(self.sidebar_frame, text="Moderation", command=self.show_moderation, **btn_style)
        self.btn_moderation.grid(row=3, column=0, padx=20, pady=10)

        self.btn_logs = ctk.CTkButton(self.sidebar_frame, text="Logs & Bans", command=self.show_logs, **btn_style)
        self.btn_logs.grid(row=4, column=0, padx=20, pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Initializing...", text_color="#00FF41")
        self.status_label.grid(row=6, column=0, padx=20, pady=20)

        # Main View Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Console Panel
        self.console_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0A0A0A", border_width=1, border_color="#2D2B55")
        self.console_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        self.console_header = ctk.CTkFrame(self.console_frame, corner_radius=0, fg_color="#12122B", height=24)
        self.console_header.pack(fill="x")
        ctk.CTkLabel(self.console_header, text="⌨ CONSOLE", font=("Consolas", 12, "bold"), text_color="#00FF41").pack(side="left", padx=10)
        ctk.CTkButton(self.console_header, text="Clear", font=("Consolas", 10, "bold"), width=50, height=20, fg_color="transparent", hover_color="#1A1A3E", text_color="#00FF41", command=self.clear_console).pack(side="right", padx=10)

        self.console_textbox = ctk.CTkTextbox(self.console_frame, fg_color="#0A0A0A", text_color="#00FF41", font=("Consolas", 12))
        self.console_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.console_textbox.configure(state="disabled")

        self.log_to_console("System initialized.")
        
        # Initialize Services
        self.api = None
        self.vrcx = None
        self.group_name = ""
        self.display_name = ""
        
        # Load env in background
        threading.Thread(target=self.init_services, daemon=True).start()

    def log_to_console(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        msg = f"[{ts}] > {text}\n"
        self.after(0, self._append_console, msg)
        
    def _append_console(self, msg):
        self.console_textbox.configure(state="normal")
        self.console_textbox.insert("end", msg)
        self.console_textbox.see("end")
        self.console_textbox.configure(state="disabled")

    def clear_console(self):
        self.console_textbox.configure(state="normal")
        self.console_textbox.delete("1.0", "end")
        self.console_textbox.configure(state="disabled")

    def init_services(self):
        load_dotenv()
        auth_cookie = os.getenv("VRCHAT_AUTH_COOKIE")
        group_id = os.getenv("VRCHAT_GROUP_ID")

        if not auth_cookie or not group_id:
            self.update_status("❌ Missing .env config", "#FF3366")
            self.log_to_console("ERROR: Missing .env configuration.")
            return

        self.update_status("Connecting to API...", "#E8E0FF")
        self.log_to_console("Connecting to VRChat API...")
        try:
            self.api = VRChatAPI()
            user_info = self.api.verify_auth()
            self.display_name = user_info.get("displayName", "Unknown")
            
            group_info = self.api.get_group_info()
            self.group_name = group_info.get("name", "Unknown Group")
            
            self.log_to_console(f"Connected as {self.display_name} | Group: {self.group_name}")
            
            self.update_status("Connecting to VRCX...", "#E8E0FF")
            self.log_to_console("Connecting to VRCX Database...")
            try:
                self.vrcx = VRCXReader()
                # Test connection
                self.vrcx.get_known_players(limit=1)
                self.log_to_console("VRCX Database connected successfully.")
            except Exception as e:
                self.vrcx = None
                self.log_to_console(f"WARNING: VRCX Error: {e}")
                
            self.update_status("✅ Connected", "#00FF41")
            self.after(0, self.show_dashboard)
            
        except Exception as e:
            self.update_status("❌ API Connection Failed", "#FF3366")
            self.log_to_console(f"ERROR: API Connection Failed: {e}")
            messagebox.showerror("Error", f"Failed to initialize: {e}")

    def update_status(self, text, color="#E8E0FF"):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E8E0FF")
        title.pack(pady=20, padx=20, anchor="w")
        
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A3E", corner_radius=10)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text=f"Logged in as: {self.display_name}", font=("Arial", 16), text_color="#E8E0FF").pack(pady=10, padx=10, anchor="w")
        ctk.CTkLabel(info_frame, text=f"Managing Group: {self.group_name}", font=("Arial", 16), text_color="#E8E0FF").pack(pady=10, padx=10, anchor="w")
        
        vrcx_status = "Connected" if self.vrcx else "Not Found"
        vrcx_color = "#00FF41" if self.vrcx else "#FF3366"
        ctk.CTkLabel(info_frame, text=f"VRCX Status: {vrcx_status}", font=("Arial", 16), text_color=vrcx_color).pack(pady=10, padx=10, anchor="w")
        self.log_to_console("Dashboard loaded.")

    def show_vrcx(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="VRCX Recent Players", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E8E0FF")
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        if not self.vrcx:
            ctk.CTkLabel(self.main_frame, text="VRCX Database not found or not connected.", text_color="#FF3366").pack(pady=20)
            self.log_to_console("VRCX view failed: Database not connected.")
            return
            
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        btn_export = ctk.CTkButton(btn_frame, text="Export to CSV", fg_color="#7C3AED", hover_color="#6D28D9", text_color="#E8E0FF", command=self.export_vrcx_csv)
        btn_export.pack(side="left")
        
        self.vrcx_list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1A1A3E", corner_radius=10)
        self.vrcx_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Header
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.vrcx_list_frame, text="Display Name", font=header_font, text_color="#9B8EC4", width=200, anchor="w").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.vrcx_list_frame, text="User ID", font=header_font, text_color="#9B8EC4", width=300, anchor="w").grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkLabel(self.vrcx_list_frame, text="Last Seen", font=header_font, text_color="#9B8EC4", width=150, anchor="w").grid(row=0, column=2, padx=10, pady=5)
        
        self.log_to_console("Loading VRCX players...")
        threading.Thread(target=self._load_vrcx_data, daemon=True).start()

    def _load_vrcx_data(self):
        self.update_status("Loading VRCX data...", "#E8E0FF")
        recent = self.vrcx.get_recent_players(hours=24)
        self.after(0, self._render_vrcx_data, recent)
        
    def _render_vrcx_data(self, recent):
        self.update_status("✅ Connected", "#00FF41")
        if not recent:
            ctk.CTkLabel(self.vrcx_list_frame, text="No players found in the last 24h.", text_color="#E8E0FF").grid(row=1, column=0, columnspan=3, pady=20)
            self.log_to_console("VRCX loaded: 0 players found.")
            return
            
        for i, player in enumerate(recent[:100], start=1):
            ctk.CTkLabel(self.vrcx_list_frame, text=player["displayName"], text_color="#E8E0FF", width=200, anchor="w").grid(row=i, column=0, padx=10, pady=2)
            id_entry = ctk.CTkEntry(self.vrcx_list_frame, width=300, fg_color="transparent", text_color="#E8E0FF", border_width=0)
            id_entry.insert(0, player["userId"])
            id_entry.configure(state="readonly")
            id_entry.grid(row=i, column=1, padx=10, pady=2)
            ts = utils.format_timestamp(player["last_seen"])
            ctk.CTkLabel(self.vrcx_list_frame, text=ts, text_color="#E8E0FF", width=150, anchor="w").grid(row=i, column=2, padx=10, pady=2)
            
        self.log_to_console(f"VRCX loaded: {len(recent)} players found.")

    def export_vrcx_csv(self):
        self.log_to_console("Exporting VRCX data to CSV...")
        recent = self.vrcx.get_recent_players(hours=24)
        import time
        filename = f"recent_players_{int(time.time())}.csv"
        if logger.export_recent_players_to_csv(recent, filename):
            self.log_to_console(f"SUCCESS: Exported {len(recent)} players to {filename}")
            messagebox.showinfo("Export Successful", f"Exported {len(recent)} players to {filename}")
        else:
            self.log_to_console("ERROR: Could not export data.")
            messagebox.showerror("Export Failed", "Could not export data.")

    def show_moderation(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="Moderation Panel", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E8E0FF")
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Single User Action Frame
        single_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A3E", corner_radius=10)
        single_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(single_frame, text="User ID or Display Name:", font=ctk.CTkFont(weight="bold"), text_color="#E8E0FF").pack(pady=(10, 0), padx=10, anchor="w")
        
        self.mod_user_entry = ctk.CTkEntry(single_frame, width=400, placeholder_text="usr_... or Exact Name", fg_color="#0D0D1A", border_color="#7C3AED", text_color="#E8E0FF")
        self.mod_user_entry.pack(pady=10, padx=10, anchor="w")
        
        btn_row = ctk.CTkFrame(single_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_row, text="🔎 Search API", width=100, fg_color="#7C3AED", hover_color="#6D28D9", text_color="#E8E0FF", command=self.action_search).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="🚫 Ban", width=100, fg_color="#FF1744", hover_color="#D50000", text_color="#FFFFFF", command=self.action_ban).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="👢 Kick", width=100, fg_color="#FF6D00", hover_color="#E65100", text_color="#FFFFFF", command=self.action_kick).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="✅ Unban", width=100, fg_color="#00E676", hover_color="#00C853", text_color="#000000", command=self.action_unban).pack(side="left", padx=5)
        
        # Mass Ban Frame
        mass_frame = ctk.CTkFrame(self.main_frame, fg_color="#1A1A3E", corner_radius=10)
        mass_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(mass_frame, text="Mass Ban (Comma-separated User IDs):", font=ctk.CTkFont(weight="bold"), text_color="#E8E0FF").pack(pady=(10, 0), padx=10, anchor="w")
        
        self.mass_ban_textbox = ctk.CTkTextbox(mass_frame, height=100, fg_color="#0A0A0A", text_color="#00FF41", font=("Consolas", 12), border_width=1, border_color="#7C3AED")
        self.mass_ban_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkButton(mass_frame, text="📋 Execute Mass Ban", fg_color="#FF1744", hover_color="#D50000", text_color="#FFFFFF", command=self.action_mass_ban).pack(pady=(0, 10), padx=10, anchor="e")
        
        self.log_to_console("Moderation panel loaded.")

    def _get_target_id(self, user_input):
        target_id = user_input
        if not utils.validate_user_id(user_input) and self.vrcx:
            results = self.vrcx.search_player(user_input)
            if len(results) == 1:
                target_id = results[0]["userId"]
                return target_id, results[0]["displayName"]
            elif len(results) > 1:
                self.log_to_console(f"WARNING: Multiple users found in VRCX for '{user_input}'. Use exact User ID.")
                messagebox.showwarning("Warning", "Multiple users found in VRCX history. Please use exact User ID instead.")
                return None, None
        return target_id, "Unknown"

    def action_search(self):
        query = self.mod_user_entry.get().strip()
        if not query:
            return
        self.log_to_console(f"SEARCH > Query: '{query}'")
        threading.Thread(target=self._async_search, args=(query,), daemon=True).start()
        
    def _async_search(self, query):
        self.update_status("Searching API...", "#E8E0FF")
        try:
            results = self.api.search_users(query, n=10)
            self.update_status("✅ Connected", "#00FF41")
            if not results:
                self.log_to_console("SEARCH > No users found.")
                messagebox.showinfo("Search Results", "No users found.")
                return
            
            self.log_to_console(f"SEARCH > Found {len(results)} users.")
            for u in results:
                self.log_to_console(f"  - {u.get('displayName')} ({u.get('id')})")
                
            msg = "\n".join([f"{u.get('displayName')} ({u.get('id')})" for u in results])
            messagebox.showinfo(f"Top results for '{query}'", msg)
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"ERROR: Search failed - {e}")
            messagebox.showerror("Search Failed", str(e))

    def action_ban(self):
        user_input = self.mod_user_entry.get().strip()
        if not user_input: return
        target_id, target_name = self._get_target_id(user_input)
        if not target_id: return
        
        if not utils.validate_user_id(target_id):
            self.log_to_console(f"ERROR: Invalid User ID format '{target_id}'")
            messagebox.showerror("Error", "Invalid User ID format.")
            return
            
        if messagebox.askyesno("Confirm Ban", f"Are you sure you want to BAN '{target_id}' from the group?"):
            threading.Thread(target=self._async_ban, args=(target_id, target_name), daemon=True).start()

    def _async_ban(self, target_id, target_name):
        self.update_status(f"Banning {target_id}...", "#FF1744")
        self.log_to_console(f"BAN > Executing ban for {target_id}...")
        try:
            self.api.ban_user(target_id)
            logger.log_action("BAN", target_id, target_name)
            self.update_status("✅ Connected", "#00FF41")
            self.log_to_console(f"BAN > SUCCESS: {target_id} banned. ✓")
            messagebox.showinfo("Success", f"Successfully banned {target_id}")
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"BAN > ERROR: Failed to ban {target_id} - {e}")
            messagebox.showerror("Ban Failed", str(e))
            
    def action_kick(self):
        user_input = self.mod_user_entry.get().strip()
        if not user_input: return
        target_id, target_name = self._get_target_id(user_input)
        if not target_id: return
        
        if not utils.validate_user_id(target_id):
            self.log_to_console(f"ERROR: Invalid User ID format '{target_id}'")
            messagebox.showerror("Error", "Invalid User ID format.")
            return
            
        if messagebox.askyesno("Confirm Kick", f"Are you sure you want to KICK '{target_id}' from the group?"):
            threading.Thread(target=self._async_kick, args=(target_id, target_name), daemon=True).start()

    def _async_kick(self, target_id, target_name):
        self.update_status(f"Kicking {target_id}...", "#FF6D00")
        self.log_to_console(f"KICK > Executing kick for {target_id}...")
        try:
            self.api.kick_member(target_id)
            logger.log_action("KICK", target_id, target_name)
            self.update_status("✅ Connected", "#00FF41")
            self.log_to_console(f"KICK > SUCCESS: {target_id} kicked. ✓")
            messagebox.showinfo("Success", f"Successfully kicked {target_id}")
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"KICK > ERROR: Failed to kick {target_id} - {e}")
            messagebox.showerror("Kick Failed", str(e))

    def action_unban(self):
        target_id = self.mod_user_entry.get().strip()
        if not target_id: return
        
        if not utils.validate_user_id(target_id):
            self.log_to_console(f"ERROR: Invalid User ID format '{target_id}'")
            messagebox.showerror("Error", "Invalid User ID format.")
            return
            
        if messagebox.askyesno("Confirm Unban", f"Are you sure you want to UNBAN '{target_id}'?"):
            threading.Thread(target=self._async_unban, args=(target_id,), daemon=True).start()

    def _async_unban(self, target_id):
        self.update_status(f"Unbanning {target_id}...", "#00E676")
        self.log_to_console(f"UNBAN > Executing unban for {target_id}...")
        try:
            self.api.unban_user(target_id)
            logger.log_action("UNBAN", target_id)
            self.update_status("✅ Connected", "#00FF41")
            self.log_to_console(f"UNBAN > SUCCESS: {target_id} unbanned. ✓")
            messagebox.showinfo("Success", f"Successfully unbanned {target_id}")
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"UNBAN > ERROR: Failed to unban {target_id} - {e}")
            messagebox.showerror("Unban Failed", str(e))

    def action_mass_ban(self):
        text = self.mass_ban_textbox.get("1.0", "end").strip()
        if not text: return
        ids_to_ban = [x.strip() for x in text.split(",") if x.strip()]
        valid_ids = [uid for uid in ids_to_ban if utils.validate_user_id(uid)]
        
        if not valid_ids:
            self.log_to_console("MASS BAN > ERROR: No valid User IDs provided.")
            messagebox.showerror("Error", "No valid User IDs provided.")
            return
            
        if messagebox.askyesno("Confirm Mass Ban", f"Are you sure you want to MASS BAN {len(valid_ids)} users?"):
            self.log_to_console(f"MASS BAN > Initiating mass ban for {len(valid_ids)} users...")
            threading.Thread(target=self._async_mass_ban, args=(valid_ids,), daemon=True).start()

    def _async_mass_ban(self, valid_ids):
        success_count = 0
        for uid in valid_ids:
            self.update_status(f"Banning {uid}...", "#FF1744")
            self.log_to_console(f"MASS BAN > Banning {uid}...")
            try:
                self.api.ban_user(uid)
                logger.log_action("BAN", uid)
                success_count += 1
                self.log_to_console(f"MASS BAN > {uid} banned ✓")
                import time
                if uid != valid_ids[-1]:
                    time.sleep(1)
            except Exception as e:
                self.log_to_console(f"MASS BAN > ERROR for {uid}: {e}")
        
        self.update_status("✅ Connected", "#00FF41")
        self.log_to_console(f"MASS BAN > Complete. {success_count}/{len(valid_ids)} banned.")
        messagebox.showinfo("Mass Ban Complete", f"Successfully banned {success_count}/{len(valid_ids)} users.")

    def show_logs(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="Logs & Bans", font=ctk.CTkFont(size=24, weight="bold"), text_color="#E8E0FF")
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkButton(btn_frame, text="Load Active Bans", fg_color="#7C3AED", hover_color="#6D28D9", text_color="#E8E0FF", command=lambda: threading.Thread(target=self._load_bans, daemon=True).start()).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Load Audit Logs", fg_color="#7C3AED", hover_color="#6D28D9", text_color="#E8E0FF", command=lambda: threading.Thread(target=self._load_audit, daemon=True).start()).pack(side="left", padx=5)
        
        self.log_list_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="#1A1A3E", corner_radius=10)
        self.log_list_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.log_to_console("Logs & Bans panel loaded.")
        
    def _load_bans(self):
        self.update_status("Loading Active Bans...", "#E8E0FF")
        self.log_to_console("LOGS > Fetching active bans...")
        try:
            bans = self.api.get_bans(n=100)
            self.after(0, self._render_bans, bans)
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"LOGS > ERROR fetching bans: {e}")
            messagebox.showerror("Error", str(e))
            
    def _render_bans(self, bans):
        self.update_status("✅ Connected", "#00FF41")
        for widget in self.log_list_frame.winfo_children():
            widget.destroy()
            
        if isinstance(bans, dict):
            bans = bans.get("results", [])
            
        if not bans:
            ctk.CTkLabel(self.log_list_frame, text="No active bans found.", text_color="#E8E0FF").pack(pady=20)
            self.log_to_console("LOGS > 0 active bans found.")
            return
            
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.log_list_frame, text="Target Name / ID", font=header_font, text_color="#9B8EC4", width=300, anchor="w").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkLabel(self.log_list_frame, text="Banned At", font=header_font, text_color="#9B8EC4", width=200, anchor="w").grid(row=0, column=1, padx=10, pady=5)
        
        for i, ban in enumerate(bans, start=1):
            user = ban.get("user", {})
            name = user.get("displayName", ban.get("userId", "Unknown"))
            banned_at = utils.format_timestamp(ban.get("createdAt", ""))
            
            ctk.CTkLabel(self.log_list_frame, text=name, text_color="#E8E0FF", width=300, anchor="w").grid(row=i, column=0, padx=10, pady=2)
            ctk.CTkLabel(self.log_list_frame, text=banned_at, text_color="#E8E0FF", width=200, anchor="w").grid(row=i, column=1, padx=10, pady=2)
            
        self.log_to_console(f"LOGS > Loaded {len(bans)} active bans.")

    def _load_audit(self):
        self.update_status("Loading Audit Logs...", "#E8E0FF")
        self.log_to_console("LOGS > Fetching audit logs...")
        try:
            logs = self.api.get_audit_logs(n=50)
            self.after(0, self._render_audit, logs)
        except Exception as e:
            self.update_status("❌ Error", "#FF3366")
            self.log_to_console(f"LOGS > ERROR fetching audit logs: {e}")
            messagebox.showerror("Error", str(e))
            
    def _render_audit(self, logs):
        self.update_status("✅ Connected", "#00FF41")
        for widget in self.log_list_frame.winfo_children():
            widget.destroy()
            
        if isinstance(logs, dict):
            logs = logs.get("results", [])
            
        if not logs:
            ctk.CTkLabel(self.log_list_frame, text="No audit logs found.", text_color="#E8E0FF").pack(pady=20)
            self.log_to_console("LOGS > 0 audit logs found.")
            return
            
        header_font = ctk.CTkFont(weight="bold")
        ctk.CTkLabel(self.log_list_frame, text="Time", font=header_font, text_color="#9B8EC4", width=150, anchor="w").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(self.log_list_frame, text="Actor", font=header_font, text_color="#9B8EC4", width=150, anchor="w").grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(self.log_list_frame, text="Action", font=header_font, text_color="#9B8EC4", width=150, anchor="w").grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(self.log_list_frame, text="Target", font=header_font, text_color="#9B8EC4", width=200, anchor="w").grid(row=0, column=3, padx=5, pady=5)
        
        for i, log in enumerate(logs, start=1):
            if not isinstance(log, dict):
                continue
            time_val = utils.format_timestamp(log.get("created_at", ""))
            actor = log.get("actorDisplayName", "Unknown")
            action = log.get("eventType", "Unknown")
            target = log.get("targetId", "Unknown")
            
            ctk.CTkLabel(self.log_list_frame, text=time_val, text_color="#E8E0FF", width=150, anchor="w").grid(row=i, column=0, padx=5, pady=2)
            ctk.CTkLabel(self.log_list_frame, text=actor, text_color="#E8E0FF", width=150, anchor="w").grid(row=i, column=1, padx=5, pady=2)
            ctk.CTkLabel(self.log_list_frame, text=action, text_color="#E8E0FF", width=150, anchor="w").grid(row=i, column=2, padx=5, pady=2)
            ctk.CTkLabel(self.log_list_frame, text=target, text_color="#E8E0FF", width=200, anchor="w").grid(row=i, column=3, padx=5, pady=2)
            
        self.log_to_console(f"LOGS > Loaded {len(logs)} audit events.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
