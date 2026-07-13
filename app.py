import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from vrchat_api import VRChatAPI
from vrcx_reader import VRCXReader

console = Console()

def show_menu(console, api, vrcx, group_name, display_name):
    while True:
        console.print(f"\n[bold blue]=== 🛡️  VRChat Group Moderation Tool ===[/bold blue]")
        console.print(f"Group: [bold magenta]{group_name}[/bold magenta] | Logged in as: [bold green]{display_name}[/bold green]")
        console.print("1. 🕐 Recent players (VRCX)")
        console.print("0. ❌ Exit")
        
        choice = console.input("\n[bold yellow]Choose an option:[/bold yellow] ")
        
        if choice == "0":
            console.print("[bold green]Exiting...[/bold green]")
            break
        elif choice == "1":
            if not vrcx:
                console.print("[bold red]❌ VRCX is not connected.[/bold red]")
                continue
                
            with console.status("[bold green]Reading history...[/bold green]"):
                recent = vrcx.get_recent_players(hours=24)
                
            if not recent:
                console.print("[bold yellow]No players found in the last 24h.[/bold yellow]")
                continue
                
            table = Table(title="Recent Players (24h)", show_header=True, header_style="bold magenta")
            table.add_column("User ID", style="dim", width=45)
            table.add_column("Display Name")
            table.add_column("Last Seen")
            
            # Limit display to 50 to not flood the terminal
            for player in recent[:50]:
                table.add_row(
                    player["userId"],
                    player["displayName"],
                    player["last_seen"]
                )
            
            console.print(table)
        else:
            console.print("[bold red]❌ Invalid option![/bold red]")

def main():
    console.print(Panel.fit("[bold blue]🛡️ VRChat Group Moderation Tool - v0.2[/bold blue]", border_style="blue"))
    
    # Load .env
    load_dotenv()
    
    auth_cookie = os.getenv("VRCHAT_AUTH_COOKIE")
    group_id = os.getenv("VRCHAT_GROUP_ID")
    
    if not auth_cookie or not group_id:
        console.print("[bold red]❌ Error:[/bold red] Missing configuration.")
        console.print("Please copy [bold].env.example[/bold] to [bold].env[/bold] and fill in VRCHAT_AUTH_COOKIE and VRCHAT_GROUP_ID.")
        sys.exit(1)
        
    api = VRChatAPI()
    
    try:
        # Verify Auth
        with console.status("[bold green]Verifying authentication...[/bold green]"):
            user_info = api.verify_auth()
            
        display_name = user_info.get("displayName", "Unknown")
        console.print(f"✅ Logged in as [bold green]{display_name}[/bold green]")
        
        # Verify Group
        with console.status("[bold green]Fetching group info...[/bold green]"):
            group_info = api.get_group_info()
            
        group_name = group_info.get("name", "Unknown Group")
        member_count = group_info.get("memberCount", 0)
        console.print(f"✅ Group: [bold magenta]{group_name}[/bold magenta] ({member_count} members)")
        
        # Verify VRCX Database
        with console.status("[bold green]Connecting to VRCX Database...[/bold green]"):
            try:
                vrcx = VRCXReader()
                known_players = vrcx.get_known_players(limit=100)
                console.print(f"✅ VRCX Database: [bold yellow]{len(known_players)}[/bold yellow] known players")
            except Exception as e:
                console.print(f"⚠️ Warning: Could not connect to VRCX ({str(e)})")
                vrcx = None
        
        console.print("\n[bold cyan]✨ v0.2 Initialization Complete![/bold cyan]")
        
        # Start interactive menu
        show_menu(console, api, vrcx, group_name, display_name)
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Initialization Failed:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
