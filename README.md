# VRChat Group Moderation Tool

A powerful, open-source tool for managing and moderating VRChat Groups. It features both a modern Graphical User Interface (GUI) and a Command Line Interface (CLI), integrating directly with the VRChat API and your local VRCX database.

## Features

- **Modern GUI**: A dark-themed, sleek interface built with `customtkinter`.
- **CLI Fallback**: A fully-featured command-line alternative (`cli_app.py`) built with `rich` for terminal enthusiasts.
- **VRCX Integration**: Connects to your local VRCX SQLite database to identify recent players and lookup their User IDs based on display names.
- **Advanced Moderation**:
  - Ban / Unban users from your group.
  - Kick users from the group.
  - Search users via the VRChat API.
  - **Mass Ban**: Execute bans on multiple users at once, with automatic rate-limit throttling (1-second delays).
- **Audit Logs & Active Bans**: Fetch and display the group's audit logs and active bans directly inside the app.
- **Local Logging**: Automatically logs every moderation action (bans, kicks, unbans) to a local `moderation.csv` file for your own records.
- **CSV Export**: Export your recently seen players from VRCX into a CSV file.

## Prerequisites

- **Python 3.8+**
- **VRCX**: Needs to be installed and running on your system for local player tracking (reads `%APPDATA%\VRCX\VRCX.sqlite3`).
- **VRChat Account**: An account with enough permissions to moderate the target VRChat Group.

## Installation

1. Clone or download this repository.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

You must configure the tool with your VRChat authentication cookie and the target Group ID.

1. Copy the `.env.example` file and rename it to `.env`.
2. Open `.env` and fill in the values:

```ini
VRCHAT_AUTH_COOKIE=auth=your_auth_cookie_here
VRCHAT_GROUP_ID=grp_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

> **⚠️ Security Warning:**
> **NEVER share your `authCookie`**. It grants full, unrestricted access to your VRChat account, bypassing 2FA. Do not commit your `.env` file to public repositories.

### How to get your `authCookie`:
1. Log into `vrchat.com` on your web browser.
2. Press `F12` to open Developer Tools.
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. Look under **Cookies** -> `https://vrchat.com`.
5. Find the cookie named `auth` and copy its value. 

### How to get your `Group ID`:
1. Go to your group's page on the VRChat website.
2. The URL will look like `https://vrchat.com/home/group/grp_...`
3. Copy the `grp_...` portion.

## Usage

### Graphical Interface (GUI)
Run the following command to launch the modern GUI application (v1.0):
```bash
python gui_app.py
```

### Command Line Interface (CLI)
If you prefer working in the terminal, run the CLI version:
```bash
python cli_app.py
```

## Disclaimer

This tool is not affiliated with, endorsed by, or sponsored by VRChat Inc. Use it responsibly. The VRChat API has strict rate limits; this tool includes automatic delays (1 second) for mass actions to prevent your account from being flagged.
