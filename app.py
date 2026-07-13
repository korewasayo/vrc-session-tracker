import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from vrchat_api import VRChatAPI
from vrcx_reader import VRCXReader
import utils

console = Console()

def show_menu(console, api, vrcx, group_name, display_name):
    while True:
        console.print(f"\n[bold blue]╔══════════════════════════════════════════════╗[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]     🛡️  [bold white]VRChat Group Moderation Tool[/bold white]        [bold blue]║[/bold blue]")
        # Pad strings to maintain border alignment (roughly)
        console.print(f"[bold blue]║[/bold blue]     Group: [bold magenta]{group_name[:28]:<28}[/bold magenta] [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]     Logged as: [bold green]{display_name[:24]:<24}[/bold green] [bold blue]║[/bold blue]")
        console.print(f"[bold blue]╠══════════════════════════════════════════════╣[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  1. 🔍 Search user (VRCX)                    [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  2. 🚫 Ban user from group                   [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  3. ✅ Unban user                            [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  4. 👢 Kick member from group                [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  5. 🕐 Recent players (VRCX)                 [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  6. 👥 Group members                         [bold blue]║[/bold blue]")
        console.print(f"[bold blue]║[/bold blue]  0. ❌ Exit                                  [bold blue]║[/bold blue]")
        console.print(f"[bold blue]╚══════════════════════════════════════════════╝[/bold blue]")
        
        choice = console.input("\n[bold yellow]Choose an option:[/bold yellow] ")
        
        if choice == "0":
            console.print("[bold green]Exiting...[/bold green]")
            break
            
        elif choice == "1":
            if not vrcx:
                console.print("[bold red]❌ VRCX is not connected.[/bold red]")
                continue
            name = console.input("[bold cyan]Enter display name to search:[/bold cyan] ")
            results = vrcx.search_player(name)
            if not results:
                console.print("[bold yellow]No players found matching that name.[/bold yellow]")
                continue
            
            table = Table(title=f"Search Results for '{name}'", show_header=True, header_style="bold magenta")
            table.add_column("User ID", style="dim", width=45)
            table.add_column("Display Name")
            table.add_column("Last Seen")
            for player in results[:20]:
                table.add_row(player["userId"], player["displayName"], utils.format_timestamp(player["last_seen"]))
            console.print(table)
            
        elif choice == "2":
            user_input = console.input("[bold cyan]Enter User ID or Display Name to Ban:[/bold cyan] ")
            
            target_id = user_input
            if not utils.validate_user_id(user_input) and vrcx:
                results = vrcx.search_player(user_input)
                if len(results) == 1:
                    target_id = results[0]["userId"]
                    console.print(f"[bold green]Found matching user:[/bold green] {results[0]['displayName']} ({target_id})")
                elif len(results) > 1:
                    console.print("[bold yellow]Multiple users found. Please use exact User ID instead.[/bold yellow]")
                    continue
                else:
                    console.print("[bold red]❌ User not found in VRCX history. Please provide a valid User ID.[/bold red]")
                    continue
            
            if not utils.validate_user_id(target_id):
                console.print("[bold red]❌ Invalid User ID format.[/bold red]")
                continue
                
            try:
                with console.status("[bold green]Fetching user info...[/bold green]"):
                    target_info = api.get_user_info(target_id)
                target_name = target_info.get("displayName", target_id)
            except Exception as e:
                console.print(f"[bold red]❌ Failed to get user info: {e}[/bold red]")
                continue
                
            if utils.confirm_action(f"Are you sure you want to BAN '{target_name}' from the group?"):
                try:
                    with console.status(f"[bold red]Banning {target_name}...[/bold red]"):
                        api.ban_user(target_id)
                    console.print(f"[bold green]✅ Successfully banned {target_name}.[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]❌ Failed to ban: {e}[/bold red]")
            else:
                console.print("[bold yellow]Action cancelled.[/bold yellow]")
                
        elif choice == "3":
            user_input = console.input("[bold cyan]Enter User ID to Unban:[/bold cyan] ")
            if not utils.validate_user_id(user_input):
                console.print("[bold red]❌ Invalid User ID format.[/bold red]")
                continue
                
            if utils.confirm_action(f"Are you sure you want to UNBAN user '{user_input}'?"):
                try:
                    with console.status("[bold green]Unbanning user...[/bold green]"):
                        api.unban_user(user_input)
                    console.print(f"[bold green]✅ Successfully unbanned user.[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]❌ Failed to unban: {e}[/bold red]")
            else:
                console.print("[bold yellow]Action cancelled.[/bold yellow]")
                
        elif choice == "4":
            user_input = console.input("[bold cyan]Enter User ID or Display Name to Kick:[/bold cyan] ")
            
            target_id = user_input
            if not utils.validate_user_id(user_input) and vrcx:
                results = vrcx.search_player(user_input)
                if len(results) == 1:
                    target_id = results[0]["userId"]
                    console.print(f"[bold green]Found matching user:[/bold green] {results[0]['displayName']} ({target_id})")
                elif len(results) > 1:
                    console.print("[bold yellow]Multiple users found. Please use exact User ID instead.[/bold yellow]")
                    continue
                else:
                    console.print("[bold red]❌ User not found in VRCX history. Please provide a valid User ID.[/bold red]")
                    continue
            
            if not utils.validate_user_id(target_id):
                console.print("[bold red]❌ Invalid User ID format.[/bold red]")
                continue
                
            try:
                with console.status("[bold green]Fetching user info...[/bold green]"):
                    target_info = api.get_user_info(target_id)
                target_name = target_info.get("displayName", target_id)
            except Exception as e:
                console.print(f"[bold red]❌ Failed to get user info: {e}[/bold red]")
                continue
                
            if utils.confirm_action(f"Are you sure you want to KICK '{target_name}' from the group?"):
                try:
                    with console.status(f"[bold yellow]Kicking {target_name}...[/bold yellow]"):
                        api.kick_member(target_id)
                    console.print(f"[bold green]✅ Successfully kicked {target_name}.[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]❌ Failed to kick: {e}[/bold red]")
            else:
                console.print("[bold yellow]Action cancelled.[/bold yellow]")

        elif choice == "5":
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
            
            for player in recent[:50]:
                table.add_row(
                    player["userId"],
                    player["displayName"],
                    utils.format_timestamp(player["last_seen"])
                )
            
            console.print(table)
            
        elif choice == "6":
            try:
                with console.status("[bold green]Fetching group members...[/bold green]"):
                    members = api.get_members(n=100)
                if not members:
                    console.print("[bold yellow]No members found or error fetching.[/bold yellow]")
                    continue
                    
                table = Table(title="Group Members (Top 100)", show_header=True, header_style="bold magenta")
                table.add_column("User", width=30)
                table.add_column("Role")
                table.add_column("Joined At")
                
                for member in members:
                    user = member.get("user", {})
                    name = user.get("displayName", "Unknown")
                    role = member.get("roleId", "Unknown")
                    joined = utils.format_timestamp(member.get("createdAt", ""))
                    table.add_row(name, role, joined)
                    
                console.print(table)
            except Exception as e:
                console.print(f"[bold red]❌ Failed to get members: {e}[/bold red]")
        else:
            console.print("[bold red]❌ Invalid option![/bold red]")

def main():
    console.print(Panel.fit("[bold blue]🛡️ VRChat Group Moderation Tool - v0.3[/bold blue]", border_style="blue"))
    
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
        
        console.print("\n[bold cyan]✨ v0.3 Initialization Complete![/bold cyan]")
        
        # Start interactive menu
        show_menu(console, api, vrcx, group_name, display_name)
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Initialization Failed:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
