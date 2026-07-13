import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from vrchat_api import VRChatAPI

console = Console()

def main():
    console.print(Panel.fit("[bold blue]🛡️ VRChat Group Moderation Tool - v0.1[/bold blue]", border_style="blue"))
    
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
        
        console.print("\n[bold cyan]✨ v0.1 Initialization Complete![/bold cyan]")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Initialization Failed:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
