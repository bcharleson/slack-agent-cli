# Slack MCP Server

A CLI and Model Context Protocol (MCP) server for Slack API integration. Use `slack` from the terminal for scripting and agent workflows, or `slack mcp` for AI assistant integration via stdio MCP.

## Features

### Channel Management
- List all accessible channels (public/private)
- Get channel information and details
- Create new channels
- Archive channels
- Join/leave channels
- Set channel topics
- Fetch channel message history

### Messaging
- Post messages to channels
- Reply to message threads
- Update and delete messages
- Add and remove emoji reactions
- Get message reactions

### Direct Messages (DMs)
- Send direct messages to users
- List DM and group DM conversations
- Fetch DM conversation history
- Open new DM conversations

### Search (requires User Token)
- Search messages across the workspace
- Search files
- Combined search for messages and files

### User Management
- List workspace users
- Get user profile information
- Check user presence/online status
- Look up users by email
- Get bot and team information

## Prerequisites

- Python 3.10 or higher
- A Slack workspace with admin access to create apps
- Slack Bot Token (xoxb-...) for most operations
- Slack User Token (xoxp-...) for search functionality

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/bcharleson/slack-mcp-server.git
cd slack-mcp-server
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

## Slack App Setup

### 1. Create a Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app and select your workspace

### 2. Configure Bot Token Scopes

Navigate to **OAuth & Permissions** and add these Bot Token Scopes:

#### Channels
- `channels:read` - View basic channel info
- `channels:write` - Manage public channels
- `channels:history` - View messages in public channels
- `groups:read` - View private channels
- `groups:write` - Manage private channels
- `groups:history` - View messages in private channels

#### Messaging
- `chat:write` - Send messages
- `reactions:read` - View reactions
- `reactions:write` - Add reactions

#### Direct Messages
- `im:read` - View DM info
- `im:write` - Start DMs
- `im:history` - View DM history
- `mpim:read` - View group DM info
- `mpim:write` - Start group DMs
- `mpim:history` - View group DM history

#### Users
- `users:read` - View users
- `users:read.email` - View user emails

### 3. Configure User Token Scopes (for Search)

If you need search functionality, add these User Token Scopes:

- `search:read` - Search messages and files

### 4. Install the App

1. Click "Install to Workspace"
2. Authorize the app
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
4. If using search, also copy the **User OAuth Token** (starts with `xoxp-`)

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Bot Token for most operations
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Optional: User Token for search functionality
SLACK_USER_TOKEN=xoxp-your-user-token-here
```

You can copy the example file:

```bash
cp .env.example .env
# Then edit .env with your tokens
```

## Usage

### CLI

After installation, the `slack` command exposes grouped subcommands that mirror the MCP tools:

```bash
# Channels
slack channels list
slack channels info C01234567
slack channels history C01234567 --limit 10

# Messages
slack messages post C01234567 "Hello from the CLI"
slack messages reply C01234567 1710000000.000100 "Thread reply"

# DMs
slack dms send U01234567 "Quick note from CLI"
slack dms list

# Search (requires SLACK_USER_TOKEN)
slack search messages "project update in:#general"

# Users / workspace
slack users list
slack users lookup brandon@example.com
slack workspace team

# Output formatting
slack --pretty channels list
slack --output json --quiet channels list
```

Global options:

- `--bot-token` / `SLACK_BOT_TOKEN`
- `--user-token` / `SLACK_USER_TOKEN`
- `--output json|pretty` (default: `json`)
- `--pretty` shorthand
- `--quiet` for exit-code-only automation

### MCP server

Start the stdio MCP server:

```bash
slack mcp
```

Legacy entrypoint (MCP only):

```bash
slack-mcp-server
```

### Running the Server (development)

#### As a Python Module

```bash
source venv/bin/activate
python -m slack_mcp_server.cli mcp
```

#### Using the Entry Point

```bash
source venv/bin/activate
slack-mcp-server
```

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "slack": {
      "command": "/path/to/slack-mcp-server/venv/bin/python",
      "args": ["-m", "slack_mcp_server"],
      "cwd": "/path/to/slack-mcp-server",
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

Replace `/path/to/slack-mcp-server` with the actual path to your installation.

### Cursor IDE Configuration

Add to your Cursor MCP settings (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "slack-mcp": {
      "command": "/path/to/slack-mcp-server/venv/bin/slack",
      "args": ["mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

Or with a global install:

```json
{
  "mcpServers": {
    "slack-mcp": {
      "command": "slack",
      "args": ["mcp"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token",
        "SLACK_USER_TOKEN": "xoxp-your-user-token"
      }
    }
  }
}
```

## Available Tools

### Channel Tools

| Tool | Description |
|------|-------------|
| `list_channels` | List all accessible channels |
| `get_channel_info` | Get details about a specific channel |
| `create_channel` | Create a new channel |
| `archive_channel` | Archive a channel |
| `get_channel_history` | Fetch message history |
| `join_channel` | Join a channel |
| `leave_channel` | Leave a channel |
| `set_channel_topic` | Set channel topic |

### Message Tools

| Tool | Description |
|------|-------------|
| `post_message` | Post a message to a channel |
| `reply_to_thread` | Reply in a thread |
| `get_thread_replies` | Get all replies in a thread |
| `add_reaction` | Add emoji reaction |
| `remove_reaction` | Remove emoji reaction |
| `get_message_reactions` | Get reactions on a message |
| `update_message` | Update an existing message |
| `delete_message` | Delete a message |

### DM Tools

| Tool | Description |
|------|-------------|
| `send_dm` | Send a direct message |
| `list_conversations` | List DM conversations |
| `get_dm_history` | Fetch DM history |
| `open_dm` | Open a DM conversation |

### Search Tools (requires User Token)

| Tool | Description |
|------|-------------|
| `search_messages` | Search messages |
| `search_files` | Search files |
| `search_all` | Search both messages and files |

### User Tools

| Tool | Description |
|------|-------------|
| `list_users` | List workspace users |
| `get_user_info` | Get user details |
| `get_user_presence` | Check if user is online |
| `lookup_user_by_email` | Find user by email |
| `get_user_profile` | Get detailed profile |
| `get_bot_info` | Get bot identity |
| `get_team_info` | Get workspace info |

## Testing

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m slack_mcp_server
```

This opens a web interface to test all available tools interactively.

### Manual Testing

1. Start the server
2. Use Claude Desktop or another MCP client
3. Try basic commands:
   - "List all channels in the workspace"
   - "Get the history of #general channel"
   - "Send a message to #test-channel saying Hello!"

## Troubleshooting

### "SLACK_BOT_TOKEN is not set"

Ensure your `.env` file exists and contains the token, or set it in your MCP client configuration.

### "Search requires a User Token"

Search operations require a User Token (`SLACK_USER_TOKEN`). Add User Token scopes to your Slack app and include the token.

### "channel_not_found"

The bot may not have access to the channel. Ensure:
1. The channel exists
2. The bot is a member of private channels
3. The channel ID is correct (use `list_channels` to find IDs)

### "missing_scope"

Your Slack app is missing required permissions. Check the OAuth scopes section above and add the missing scopes in your Slack app settings.

## Development

### Project Structure

```
slack-mcp-server/
├── src/
│   └── slack_mcp_server/
│       ├── cli/
│       │   └── main.py            # Click CLI + `slack mcp`
│       ├── core/
│       │   └── output.py          # JSON/pretty output helpers
│       ├── operations/            # Shared handlers for CLI + MCP
│       │   ├── channels.py
│       │   ├── messages.py
│       │   ├── search.py
│       │   └── users.py
│       ├── tools/                   # MCP tool registration
│       ├── utils/
│       │   └── slack_client.py
│       └── server.py              # FastMCP stdio server
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

### Adding New Tools

1. Create or edit a file in `src/slack_mcp_server/tools/`
2. Define tools using the `@mcp.tool()` decorator
3. Register the tools in the server by calling the registration function

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

